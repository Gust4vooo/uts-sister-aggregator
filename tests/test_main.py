import pytest
import os
import time
import asyncio
from fastapi.testclient import TestClient
from src import main, database

app = main.app
TEST_DB_FILE = "./test_dedup_store.db"

@pytest.fixture
def test_client_factory():
    def create_client():
        main.stats = {
            "received": 0,
            "unique_processed": 0,
            "duplicate_dropped": 0,
            "topics": set(),
            "start_time": time.time()
        }
        main.processed_events.clear()
        main.internal_queue = asyncio.Queue()

        database.DB_FILE = TEST_DB_FILE
        return TestClient(app)

    yield create_client

    # Hapus database setelah semua tes selesai
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


# UNIT TESTS  (7 total)

# 1. Tes publish satu event valid
def test_publish_single_valid_event(test_client_factory):
    with test_client_factory() as client:
        response = client.post("/publish", json={
            "topic": "user_signup",
            "event_id": "unique-id-1",
            "source": "pytest",
            "payload": {"data": "value"}
        })
        assert response.status_code == 200
        assert response.json() == {"status": "events queued", "count": 1}


# 2. Tes publish batch event valid
def test_publish_batch_valid_events(test_client_factory):
    with test_client_factory() as client:
        events = [
            {"topic": "batch_test", "event_id": "batch-1", "source": "pytest", "payload": {}},
            {"topic": "batch_test", "event_id": "batch-2", "source": "pytest", "payload": {}}
        ]
        response = client.post("/publish", json=events)
        assert response.status_code == 200
        assert response.json() == {"status": "events queued", "count": 2}


# 3. Tes validasi skema event (field wajib)
def test_publish_invalid_schema_fails(test_client_factory):
    with test_client_factory() as client:
        response = client.post("/publish", json={
            "event_id": "invalid-id-1",
            "source": "pytest",
            "payload": {}
        })
        assert response.status_code == 422


# 4. Tes deduplikasi dan konsistensi /stats
def test_deduplication_and_stats_consistency(test_client_factory):
    with test_client_factory() as client:
        event = {"topic": "dedup_test", "event_id": "dedup-id-123", "source": "pytest", "payload": {}}
        client.post("/publish", json=event)
        client.post("/publish", json=event)
        time.sleep(0.1)
        stats = client.get("/stats").json()
        assert stats["received"] == 2
        assert stats["unique_processed"] == 1
        assert stats["duplicate_dropped"] == 1


# 5. Tes konsistensi endpoint /events
def test_get_events_endpoint_consistency(test_client_factory):
    with test_client_factory() as client:
        event1 = {"topic": "topic-a", "event_id": "id-a1", "source": "pytest", "payload": {}}
        event2 = {"topic": "topic-b", "event_id": "id-b1", "source": "pytest", "payload": {}}
        client.post("/publish", json=[event1, event2])
        time.sleep(0.1)
        response_all = client.get("/events")
        assert len(response_all.json()) == 2
        response_a = client.get("/events?topic=topic-a")
        data_a = response_a.json()
        assert len(data_a) == 1
        assert data_a[0]["event_id"] == "id-a1"


# 6. Tes persistensi dedup store setelah restart
def test_persistence_of_dedup_store(test_client_factory):
    event = {"topic": "persistence", "event_id": "persistent-id-456", "source": "pytest", "payload": {}}

    # Sesi pertama: event diproses
    with test_client_factory() as client1:
        client1.post("/publish", json=event)
        time.sleep(0.1)
        stats1 = client1.get("/stats").json()
        assert stats1["unique_processed"] == 1

    # Sesi kedua (simulasi restart): event sama di-drop
    with test_client_factory() as client2:
        client2.post("/publish", json=event)
        time.sleep(0.1)
        stats2 = client2.get("/stats").json()
        assert stats2["received"] == 1
        assert stats2["unique_processed"] == 0
        assert stats2["duplicate_dropped"] == 1


# 7. Tes performa batch kecil (stress test ringan)
def test_small_stress_performance(test_client_factory):
    with test_client_factory() as client:
        events_batch = [
            {"topic": "stress", "source": "pytest", "payload": {}} for _ in range(100)
        ]
        start_time = time.time()
        response = client.post("/publish", json=events_batch)
        duration = time.time() - start_time
        assert response.status_code == 200
        assert duration < 1.0
