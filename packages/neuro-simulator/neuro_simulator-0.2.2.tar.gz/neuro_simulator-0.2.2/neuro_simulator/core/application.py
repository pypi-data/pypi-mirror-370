# neuro_simulator/core/application.py
"""Main application file: FastAPI app instance, events, and websockets."""

import asyncio
import json
import logging
import random
import re
import time
from pathlib import Path
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState

# --- Core Imports ---
from .config import config_manager, AppSettings
from ..core.agent_factory import create_agent

# --- API Routers ---
from ..api.agent import router as agent_router
from ..api.stream import router as stream_router
from ..api.system import router as system_router

# --- Services and Utilities ---
from ..services.audience import AudienceChatbotManager, get_dynamic_audience_prompt
from ..services.audio import synthesize_audio_segment
from ..services.stream import live_stream_manager
from ..utils.logging import configure_server_logging, server_log_queue, agent_log_queue
from ..utils.process import process_manager
from ..utils.queue import (
    add_to_audience_buffer,
    add_to_neuro_input_queue,
    get_recent_audience_chats,
    is_neuro_input_queue_empty,
    get_all_neuro_input_chats
)
from ..utils.state import app_state
from ..utils.websocket import connection_manager

# --- Logger Setup ---
logger = logging.getLogger(__name__.replace("neuro_simulator", "server", 1))

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Neuro-Sama Simulator API",
    version="2.0.0",
    description="Backend for the Neuro-Sama digital being simulator."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config_manager.settings.server.client_origins + ["http://localhost:8080", "https://dashboard.live.jiahui.cafe"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-API-Token"],
)

app.include_router(agent_router)
app.include_router(stream_router)
app.include_router(system_router)

# --- Background Task Definitions ---

chatbot_manager: AudienceChatbotManager = None

async def broadcast_events_task():
    """Broadcasts events from the live_stream_manager's queue to all clients."""
    while True:
        try:
            event = await live_stream_manager.event_queue.get()
            await connection_manager.broadcast(event)
            live_stream_manager.event_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in broadcast_events_task: {e}", exc_info=True)

async def fetch_and_process_audience_chats():
    """Generates a batch of audience chat messages."""
    if not chatbot_manager or not chatbot_manager.client:
        return
    try:
        dynamic_prompt = await get_dynamic_audience_prompt()
        raw_chat_text = await chatbot_manager.client.generate_chat_messages(
            prompt=dynamic_prompt, 
            max_tokens=config_manager.settings.audience_simulation.max_output_tokens
        )
        
        parsed_chats = []
        for line in raw_chat_text.split('\n'):
            line = line.strip()
            if ':' in line:
                username_raw, text = line.split(':', 1)
                username = username_raw.strip()
                if username in config_manager.settings.audience_simulation.username_blocklist:
                    username = random.choice(config_manager.settings.audience_simulation.username_pool)
                if username and text.strip(): 
                    parsed_chats.append({"username": username, "text": text.strip()})
            elif line: 
                parsed_chats.append({"username": random.choice(config_manager.settings.audience_simulation.username_pool), "text": line})
        
        chats_to_broadcast = parsed_chats[:config_manager.settings.audience_simulation.chats_per_batch]
        
        for chat in chats_to_broadcast: 
            add_to_audience_buffer(chat)
            add_to_neuro_input_queue(chat)
            broadcast_message = {"type": "chat_message", **chat, "is_user_message": False}
            await connection_manager.broadcast(broadcast_message)
            await asyncio.sleep(random.uniform(0.1, 0.4))
    except Exception as e:
        logger.error(f"Error in fetch_and_process_audience_chats: {e}", exc_info=True)

async def generate_audience_chat_task():
    """Periodically triggers the audience chat generation task."""
    while True:
        try:
            asyncio.create_task(fetch_and_process_audience_chats())
            await asyncio.sleep(config_manager.settings.audience_simulation.chat_generation_interval_sec)
        except asyncio.CancelledError:
            break

async def neuro_response_cycle():
    """The core response loop for the agent."""
    await app_state.live_phase_started_event.wait()
    agent = await create_agent()
    is_first_response = True

    while True:
        try:
            if is_first_response:
                add_to_neuro_input_queue({"username": "System", "text": config_manager.settings.neuro_behavior.initial_greeting})
                is_first_response = False
            elif is_neuro_input_queue_empty():
                await asyncio.sleep(1)
                continue
            
            current_queue_snapshot = get_all_neuro_input_chats()
            sample_size = min(config_manager.settings.neuro_behavior.input_chat_sample_size, len(current_queue_snapshot))
            selected_chats = random.sample(current_queue_snapshot, sample_size)
            
            response_result = await asyncio.wait_for(agent.process_messages(selected_chats), timeout=20.0)
            
            response_text = response_result.get("final_response", "").strip()
            if not response_text:
                continue

            async with app_state.neuro_last_speech_lock:
                app_state.neuro_last_speech = response_text

            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', response_text.replace('\n', ' ')) if s.strip()]
            if not sentences: continue

            synthesis_tasks = [synthesize_audio_segment(s) for s in sentences]
            synthesis_results = await asyncio.gather(*synthesis_tasks, return_exceptions=True)
            
            speech_packages = [
                {"segment_id": i, "text": sentences[i], "audio_base64": res[0], "duration": res[1]}
                for i, res in enumerate(synthesis_results) if not isinstance(res, Exception)
            ]

            if not speech_packages: continue

            live_stream_manager.set_neuro_speaking_status(True)
            for package in speech_packages:
                await connection_manager.broadcast({"type": "neuro_speech_segment", **package, "is_end": False})
                await asyncio.sleep(package['duration'])
            
            await connection_manager.broadcast({"type": "neuro_speech_segment", "is_end": True})
            live_stream_manager.set_neuro_speaking_status(False)
            await asyncio.sleep(config_manager.settings.neuro_behavior.post_speech_cooldown_sec)

        except asyncio.TimeoutError:
            logger.warning("Agent response timed out, skipping this cycle.")
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            live_stream_manager.set_neuro_speaking_status(False)
            break
        except Exception as e:
            logger.error(f"Critical error in neuro_response_cycle: {e}", exc_info=True)
            live_stream_manager.set_neuro_speaking_status(False)
            await asyncio.sleep(10)

# --- Application Lifecycle Events ---

@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup."""
    global chatbot_manager
    configure_server_logging()
    
    chatbot_manager = AudienceChatbotManager()

    async def metadata_callback(settings: AppSettings):
        await live_stream_manager.broadcast_stream_metadata()
    
    config_manager.register_update_callback(metadata_callback)
    config_manager.register_update_callback(chatbot_manager.handle_config_update)
    
    try:
        await create_agent()
        logger.info(f"Successfully initialized agent type: {config_manager.settings.agent_type}")
    except Exception as e:
        logger.critical(f"Agent initialization failed on startup: {e}", exc_info=True)
    
    logger.info("FastAPI application has started.")

@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown."""
    if process_manager.is_running:
        process_manager.stop_live_processes()
    logger.info("FastAPI application has shut down.")

# --- WebSocket Endpoints ---

@app.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        await connection_manager.send_personal_message(live_stream_manager.get_initial_state_for_client(), websocket)
        await connection_manager.send_personal_message({"type": "update_stream_metadata", **config_manager.settings.stream_metadata.model_dump()}, websocket)
        
        initial_chats = get_recent_audience_chats(config_manager.settings.performance.initial_chat_backlog_limit)
        for chat in initial_chats:
            await connection_manager.send_personal_message({"type": "chat_message", **chat, "is_user_message": False}, websocket)
            await asyncio.sleep(0.01)
        
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            if data.get("type") == "user_message":
                user_message = {"username": data.get("username", "User"), "text": data.get("message", "").strip()}
                if user_message["text"]:
                    add_to_audience_buffer(user_message)
                    add_to_neuro_input_queue(user_message)
                    await connection_manager.broadcast({"type": "chat_message", **user_message, "is_user_message": True})
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(websocket)

@app.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        for log_entry in list(server_log_queue): await websocket.send_json({"type": "server_log", "data": log_entry})
        for log_entry in list(agent_log_queue): await websocket.send_json({"type": "agent_log", "data": log_entry})
        
        agent = await create_agent()
        initial_context = await agent.get_message_history()
        await websocket.send_json({"type": "agent_context", "action": "update", "messages": initial_context})
        
        while websocket.client_state == WebSocketState.CONNECTED:
            if server_log_queue: await websocket.send_json({"type": "server_log", "data": server_log_queue.popleft()})
            if agent_log_queue: await websocket.send_json({"type": "agent_log", "data": agent_log_queue.popleft()})
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        pass
    finally:
        logger.info("Admin WebSocket client disconnected.")

# --- Server Entrypoint ---

def run_server(host: str = None, port: int = None):
    """Runs the FastAPI server with Uvicorn."""
    import uvicorn
    server_host = host or config_manager.settings.server.host
    server_port = port or config_manager.settings.server.port
    
    uvicorn.run(
        "neuro_simulator.core.application:app",
        host=server_host,
        port=server_port,
        reload=False
    )