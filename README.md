# uts-sister-aggregator

# UTS Sistem Terdistribusi: Pub-Sub Log Aggregator

Proyek ini adalah implementasi layanan *Pub-Sub log aggregator* sebagai bagian dari Ujian Tengah Semester mata kuliah Sistem Terdistribusi. Layanan ini dibangun untuk menerima *event* (log), memprosesnya secara asinkron, dan memastikan setiap *event* unik hanya diproses sekali (*idempotency*) melalui mekanisme deduplikasi yang persisten.

Seluruh layanan dirancang untuk berjalan di dalam container Docker yang terisolasi.

## Fitur Utama

-   **Arsitektur Asinkron**: Dibangun menggunakan **FastAPI** dan **asyncio** untuk menangani volume request yang tinggi secara efisien.
-   **Idempotent Consumer**: Menjamin bahwa *event* dengan `(topic, event_id)` yang sama hanya akan diproses satu kali, bahkan jika diterima berkali-kali.
-   **Deduplikasi Persisten**: Menggunakan **SQLite** sebagai *dedup store* yang tahan terhadap *restart* atau *crash* pada container, memastikan tidak ada data yang diproses ulang.
-   **Terkontainerisasi**: Sepenuhnya berjalan di dalam **Docker**, memastikan portabilitas dan kemudahan dalam proses *build* dan eksekusi.
-   **Teruji (Unit Tested)**: Dilengkapi dengan 7 unit test menggunakan **Pytest** untuk memvalidasi fungsionalitas inti, termasuk logika deduplikasi dan persistensi.

---

## Cara Menjalankan Aplikasi

Pastikan sudah menginstal **Docker Desktop** atau Docker Engine dan layanannya sedang berjalan.

### 1. Build Docker Image

Buka terminal di direktori utama proyek, lalu jalankan perintah berikut untuk membangun *image* Docker:

```bash
docker build -t uts-aggregator .
```

### 2. Jalankan Container

Setelah proses *build* selesai, jalankan container dari *image* yang telah dibuat dengan perintah:

```bash
docker run -d -p 8080:8000 -v ./src:/app/src --name my-aggregator uts-aggregator
```

Penjelasan perintah:
-   `-d`: Menjalankan container di *background* (*detached mode*).
-   `-p 8080:8000`: Memetakan port **8080** di mesin Anda ke port **8000** di dalam container.
-   `-v ./src:/app/src`: **(Penting)** Membuat *volume* yang menyinkronkan folder `src` lokal dengan folder `/app/src` di container. Ini memastikan file database `dedup_store.db` tersimpan di mesin Anda dan tidak hilang saat container dihentikan.
-   `--name my-aggregator`: Memberi nama pada container agar mudah dikelola.

Aplikasi sekarang dapat diakses melalui `http://localhost:8080`.

---

## API Endpoints

Berikut adalah daftar *endpoint* API yang tersedia:

### 1. Publish Event
-   **Endpoint**: `POST /publish`
-   **Deskripsi**: Menerima satu atau *batch* (banyak) *event* untuk dimasukkan ke dalam antrian pemrosesan.
-   **Contoh cURL (Single Event)**:
    ```bash
    curl -X POST "http://localhost:8080/publish" -H "Content-Type: application/json" -d '{
        "topic": "user_activity",
        "event_id": "unique-event-001",
        "source": "web-client",
        "payload": {"action": "login", "user": "andi"}
    }'
    ```

### 2. Get Processed Events
-   **Endpoint**: `GET /events`
-   **Deskripsi**: Mengembalikan daftar semua *event* unik yang telah berhasil diproses.
-   **Contoh cURL (Semua Event)**:
    ```bash
    curl http://localhost:8080/events
    ```
-   **Contoh cURL (Filter berdasarkan Topic)**:
    ```bash
    curl "http://localhost:8080/events?topic=user_activity"
    ```

### 3. Get Statistics
-   **Endpoint**: `GET /stats`
-   **Deskripsi**: Menampilkan statistik operasional layanan secara *real-time*.
-   **Contoh cURL**:
    ```bash
    curl http://localhost:8080/stats
    ```
-   **Contoh Respons**:
    ```json
    {
        "received": 10,
        "unique_processed": 7,
        "duplicate_dropped": 3,
        "topics": ["user_activity", "payment"],
        "uptime_seconds": 123.45
    }
    ```

---

## Cara Menjalankan Unit Test

Untuk menjalankan unit test secara lokal, pastikan Anda sudah membuat *virtual environment* dan menginstal semua dependensi.

1.  **Instal dependensi**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Jalankan Pytest**:
    ```bash
    pytest -v
    ```

---

## Link Video Demo

Video demonstrasi yang menunjukkan proses *build*, *run*, pengujian fungsionalitas, dan simulasi *crash* dapat diakses melalui link berikut:

**[Link menyusul..]**

---

## Teknologi yang Digunakan

-   **Bahasa**: Python 3.11
-   **Framework**: FastAPI
-   **Server**: Uvicorn
-   **Database**: SQLite
-   **Kontainerisasi**: Docker
-   **Testing**: Pytest