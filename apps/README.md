#  Resilient News Broker

A fault-tolerant, real-time news ingestion system designed to handle unreliable data streams, eliminate duplicates, and ensure reliable persistence even under failures.

---

##  Overview

This project implements a **resilient event-driven pipeline** that connects to a chaotic WebSocket news source, processes incoming data, removes duplicates using machine learning techniques, and persists it into MongoDB.

The system is built to handle real-world challenges such as:

* Network instability (frequent disconnects)
* Malformed JSON data
* Duplicate or noisy headlines
* Database downtime
* Bursty traffic

---

##  System Architecture

```id="m7v48p"
WebSocket Server (Chaos Mode)
        ↓
   Ingester (Retry + Backoff)
        ↓
 Parser + Validator (Pydantic)
        ↓
 Deduplicator (TF-IDF + Cosine Similarity)
        ↓
 Buffer (Circuit Breaker + Drop Strategy)
        ↓
 DB Worker (Async Consumer + Retry)
        ↓
 MongoDB (Persistent Storage)
```

---

##  Key Features

###  Fault-Tolerant Ingestion

* Persistent WebSocket connection
* Exponential backoff with jitter
* Automatic reconnection after failures
* Immediate handshake authentication

---

###  Intelligent Deduplication

* Implemented using **TF-IDF + cosine similarity (scikit-learn)**
* Detects semantic similarity (not just exact matches)
* Maintains a **sliding window** to control memory usage

---

###  Resilient Buffer (Circuit Breaker)

* In-memory bounded buffer
* Prevents data loss when database is slow or unavailable
* Implements **priority-based drop strategy**:

  * Priority 1 → always preserved
  * Priority 3 → dropped first

---

###  Asynchronous MongoDB Persistence

* Uses **Motor (async MongoDB driver)**
* Non-blocking DB writes via background worker
* Automatic retry on failure

---

###  Observability & Metrics

* Logs meaningful system events:

  * reconnects
  * drops
  * malformed data
* Metrics printed every 60 seconds:

```id="1s7f5k"
Stored: X | Deduplicated: Y | Buffered: Z
```

---

##  Configuration

All system parameters are centralized in `config.py`:

* WebSocket URL and authentication token
* MongoDB connection details
* Buffer capacity
* Deduplication threshold and window size

This allows easy tuning and environment-based configuration.

---

##  Chaos Handling

The system is designed to survive unstable conditions:

| Failure Scenario | Handling Strategy         |
| ---------------- | ------------------------- |
| Connection drops | Exponential backoff retry |
| Malformed JSON   | Safe parsing + logging    |
| Duplicate data   | ML-based deduplication    |
| DB failure       | Buffer + retry            |
| Burst traffic    | Async processing          |

---

##  Design Decisions

### 1. Async Architecture

* Built using `asyncio` for non-blocking processing
* Separate tasks for ingestion, buffering, and persistence

---

### 2. Separation of Concerns

* Ingester → network handling
* Deduplicator → data intelligence
* Buffer → resilience
* DB Worker → persistence

---

### 3. Circuit Breaker Pattern

* Buffer acts as fallback during DB failure
* Prevents system-wide crashes

---

### 4. ML-Based Deduplication

* Chose TF-IDF over simple string matching
* Better handling of semantic similarity in short text

---

## Trade-offs

* TF-IDF is recomputed when sliding window updates (acceptable due to small window size)
* In-memory buffer (can be replaced with Redis for large-scale systems)

---

## How to Run

### 1. Install dependencies

```id="e1wqpu"
pip install -r requirements.txt
```

---

### 2. Start the source server

```id="9v1k2m"
python infrastructure/scripts/assignment_source_server.py
```

---

### 3. Run the broker

```id="oz1k92"
python -m apps.news_broker_submission.main
```

---

## Project Structure

```id="z1v9qe"
apps/news_broker_submission/
├── main.py            # Application entry point
├── ingester.py        # WebSocket client with retry logic
├── deduplicator.py    # ML-based deduplication
├── buffer.py          # Circuit breaker + drop strategy
├── db.py              # MongoDB integration
├── config.py          # Centralized configuration
├── models.py          # Pydantic schemas
```

---

## Challenges Solved

* Reliable streaming under unstable network conditions
* Handling malformed and inconsistent data safely
* Eliminating duplicate events using semantic similarity
* Preventing data loss during downstream failures
* Managing backpressure with bounded buffers

---

## Conclusion

This project demonstrates:

* Strong understanding of **async programming**
* Real-world **fault-tolerant system design**
* Practical use of **machine learning in data pipelines**
* Clean, modular, and scalable backend architecture

---

## 👨‍💻 Author

**Asutosh Sidhya**
