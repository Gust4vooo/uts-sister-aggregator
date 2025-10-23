import asyncio
from datetime import datetime, timezone
from typing import List, Union, Dict
import time
import uuid
import logging
from contextlib import asynccontextmanager

from src import database
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

# model
class Event(BaseModel):
    topic: str
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str
    payload: Dict

# Konfigurasi logging dasar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lifespan Manager untuk Startup dan Shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kode ini berjalan saat STARTUP
    logging.info("Initializing database...")
    database.init_db()
    worker_task = asyncio.create_task(event_processor())
    
    yield # Aplikasi berjalan setelah ini
    
    # Kode ini berjalan saat SHUTDOWN
    logging.info("Shutting down... cancelling worker task.")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        logging.info("Worker task cancelled successfully.")

# State sementara dan Inisialisasi Aplikasi
app = FastAPI(title="Event Aggregator Service", lifespan=lifespan)
internal_queue = asyncio.Queue()
processed_events: List[Event] = []
stats = {
    "received": 0,
    "unique_processed": 0,
    "duplicate_dropped": 0,
    "topics": set(),
    "start_time": time.time()
}

# API endpoints
@app.post("/publish")
async def publish_event(data: Union[Event, List[Event]]):
    events_to_process = data if isinstance(data, list) else [data]
    for event in events_to_process:
        await internal_queue.put(event)
        stats["received"] += 1
        stats["topics"].add(event.topic)
    return {"status": "events queued", "count": len(events_to_process)}

@app.get("/events")
async def get_events(topic: str = None):
    if topic:
        return [e for e in processed_events if e.topic == topic]
    return processed_events

@app.get("/stats")
async def get_stats():
    uptime = time.time() - stats["start_time"]
    return {
        "received": stats["received"],
        "unique_processed": stats["unique_processed"],
        "duplicate_dropped": stats["duplicate_dropped"],
        "topics": list(stats["topics"]),
        "uptime_seconds": uptime
    }

# Worker untuk memproses event
async def event_processor():
    logging.info("Event processor started")
    while True:
        try:
            event = await internal_queue.get()
            
            is_dup = database.is_duplicate(event.topic, event.event_id)
            
            if not is_dup:
                logging.info(f"Processing new event: (topic={event.topic}, id={event.event_id})")
                processed_events.append(event)
                stats["unique_processed"] += 1
            else:
                logging.warning(f"Duplicate event dropped: (topic={event.topic}, id={event.event_id})")
                stats["duplicate_dropped"] += 1
                
            internal_queue.task_done()
        except asyncio.CancelledError:
            logging.info("Event processor stopping.")
            break