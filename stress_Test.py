import requests
import json
import time
import uuid
import random

# Konfigurasi
API_URL = "http://localhost:8080/publish"
TOTAL_EVENTS = 5000
DUPLICATE_PERCENTAGE = 0.2 

def generate_event():
    return {
        "topic": random.choice(["login", "logout", "payment", "profile_update"]),
        "source": "stress_test_script",
        "payload": {"user_id": random.randint(1, 1000)}
    }

def run_test():
    print("Memulai Stress Test...")
    print(f"   - Target URL: {API_URL}")
    print(f"   - Total Events: {TOTAL_EVENTS}")
    print(f"   - Duplikasi: {int(DUPLICATE_PERCENTAGE * 100)}%")
    print("-" * 30)

    events_to_send = []
    
    # 1. Buat event unik
    num_unique = int(TOTAL_EVENTS * (1 - DUPLICATE_PERCENTAGE))
    for _ in range(num_unique):
        event = generate_event()
        event["event_id"] = str(uuid.uuid4())
        events_to_send.append(event)
        
    # 2. Ambil beberapa event unik untuk dijadikan duplikat
    num_duplicates = TOTAL_EVENTS - num_unique
    duplicates_source = random.choices(events_to_send, k=num_duplicates)
    events_to_send.extend(duplicates_source)
    
    # 3. Acak urutan semua event
    random.shuffle(events_to_send)
    
    start_time = time.time()
    
    batch_size = 100
    for i in range(0, len(events_to_send), batch_size):
        batch = events_to_send[i:i+batch_size]
        try:
            response = requests.post(
                API_URL, 
                data=json.dumps(batch), 
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()
            print(f"   Mengirim batch {i//batch_size + 1} dari {len(events_to_send)//batch_size}... Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"\n❌ Error: Tidak dapat terhubung ke server. Pastikan container Docker berjalan.")
            print(f"   Detail: {e}")
            return 

    end_time = time.time()
    
    duration = end_time - start_time
    throughput = TOTAL_EVENTS / duration
    
    print("-" * 30)
    print("Test Selesai!")
    print(f"\nHasil Pengujian:")
    print(f"   - Waktu Eksekusi Total: {duration:.2f} detik")
    print(f"   - Throughput: {throughput:.2f} events/detik")

if __name__ == "__main__":
    run_test()