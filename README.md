# UTS Sistem Terdistribusi: Pub-Sub Log Aggregator

**Tema**: Pub-Sub Log Aggregator  
**Penulis**: Gusti Muhammad Risandha

Proyek ini adalah implementasi layanan *Pub-Sub log aggregator* sebagai bagian dari Ujian Tengah Semester mata kuliah Sistem Terdistribusi. Layanan ini dibangun untuk menerima *event* (log), memprosesnya secara asinkron, dan memastikan setiap *event* unik hanya diproses sekali (*idempotency*) melalui mekanisme deduplikasi yang persisten.

Seluruh layanan dirancang untuk berjalan di dalam container Docker yang terisolasi.

## Fitur Utama

-   **Arsitektur Asinkron**: Dibangun menggunakan **FastAPI** dan **asyncio** untuk menangani volume request yang tinggi secara efisien.
-   **Idempotent Consumer**: Menjamin bahwa *event* dengan `(topic, event_id)` yang sama hanya akan diproses satu kali, bahkan jika diterima berkali-kali.
-   **Deduplikasi Persisten**: Menggunakan **SQLite** sebagai *dedup store* yang tahan terhadap *restart* atau *crash* pada container, memastikan tidak ada data yang diproses ulang.
-   **Terkontainerisasi**: Sepenuhnya berjalan di dalam **Docker**, memastikan portabilitas dan kemudahan dalam proses *build* dan eksekusi.
-   **Teruji (Unit Tested)**: Dilengkapi dengan 7 unit test menggunakan **Pytest** untuk memvalidasi fungsionalitas inti, termasuk logika deduplikasi dan persistensi.
-   **Bonus Docker Compose**: Menyediakan konfigurasi untuk menjalankan layanan *aggregator* dan *publisher* secara bersamaan dalam jaringan internal.

---

## Cara Menjalankan Aplikasi

Pastikan Anda sudah menginstal **Docker Desktop** atau Docker Engine dan layanannya sedang berjalan. Proyek ini dapat dijalankan dengan dua cara:

### Opsi 1: Menjalankan Service Aggregator Saja (Tugas Wajib)

Cara ini hanya akan menjalankan layanan *aggregator* utama. Anda perlu mengirim *event* secara manual menggunakan cURL atau Postman.

1.  **Build Docker Image**:
    ```bash
    docker build -t uts-aggregator .
    ```

2.  **Jalankan Container**:
    ```bash
    docker run -d -p 8080:8000 -v ./src:/app/src --name my-aggregator uts-aggregator
    ```

Aplikasi dapat diakses melalui `http://localhost:8080`.

### Opsi 2: Menjalankan dengan Publisher (Bonus Docker Compose)

Cara ini akan menjalankan **kedua** layanan secara bersamaan: `aggregator` (penerima) dan `publisher` (pengirim *event* otomatis). Ini adalah cara terbaik untuk melihat sistem beraksi secara terus-menerus.

1.  **Jalankan dengan Docker Compose**:
    Buka terminal di direktori utama proyek, lalu jalankan satu perintah ini:
    ```bash
    docker-compose up --build
    ```
    Perintah ini akan membangun *image* yang diperlukan dan memulai kedua *container*. Terminal Anda akan menampilkan log dari kedua layanan secara *real-time*.

2.  **Verifikasi**:
    Setelah beberapa detik, Anda akan melihat log *publisher* yang mengirim *event* dan log *aggregator* yang memprosesnya. Untuk memverifikasi dari luar, buka terminal baru dan cek *endpoint* statistik:
    ```bash
    curl http://localhost:8080/stats
    ```
    Anda akan melihat angka `received` dan `unique_processed` terus bertambah secara otomatis.

3.  **Menghentikan Layanan**:
    Untuk menghentikan semua layanan, kembali ke terminal tempat Anda menjalankan `docker-compose up` dan tekan `Ctrl + C`.

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

**https://youtu.be/ao911qAEM_c**

---

## Teknologi yang Digunakan

-   **Bahasa**: Python 3.11
-   **Framework**: FastAPI
-   **Server**: Uvicorn
-   **Database**: SQLite
-   **Kontainerisasi**: Docker, Docker Compose
-   **Testing**: Pytest