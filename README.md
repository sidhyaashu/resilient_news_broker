# InvestCode Backend Assignment: Resilient News Broker

Welcome to the InvestCode Backend Engineering Challenge.

## Context
InvestCode relies on consistent, clean, and real-time data. Our primary news feed is a firehose: it is bursty, redundant, and occasionally the connection drops. 

Your task is to build a **"Resilient News Broker"** that connects to our internal mock source, cleans/deduplicates the data, and ensures it reaches our database without loss—even during simulated outages.

---

## Repository Structure

```text
├── README.md                  # This file
├── requirements.txt           # Dependencies
├── infrastructure/
│   └── scripts/
│       └── assignment_source_server.py  # Run this to start the feed
└── src/
    ├── models.py              # Pydantic Schemas
    ├── ingester.py            # WebSocket Handlers (Needs Implementation)
    ├── deduplicator.py         # Fuzzy matching (Needs Implementation)
    ├── buffer.py              # Bounded Buffer / Drop Strategy (Needs Implementation)
    └── main.py                # App entry point
```

---

## 1. Getting Started

### Prerequisites
- Python 3.10+
- `pip`

### Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Source Feed**:
   ```bash
   python infrastructure/scripts/assignment_source_server.py
   ```
   *The feed listens on `ws://localhost:8888/ws`.*

4. **Run your Broker**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:.
   python src/main.py
   ```

---

## 2. Functional Requirements

### A. Fault-Tolerant Ingestion (`src/ingester.py`)
- Maintain a persistent WebSocket connection to `ws://localhost:8888/ws`.
- Perform handshake by sending `{"token": "test-session-chaos"}` immediately upon connecting.
- Implement **Exponential Backoff** for reconnection when drops occur.
- Handle malformed JSON gracefully.

### B. Intelligent Deduplication (`src/deduplicator.py`)
- Standard headlines are noisy (e.g., "Apple Shares Jump" vs "AAPL stock spikes").
- Implement a **Sliding Window Fuzzy Deduplicator**.
- Use a similarity metric (like Levenshtein distance) with a threshold to filter duplicates.

### C. Resilient Persistence & Buffer (`src/buffer.py`)
- Implement an **In-Memory Bounded Buffer** for slow/down downstream layers.
- If the buffer fills up, implement a **Drop Strategy**: Priority 1 items are kept, Priority 3 items are dropped first.
- Periodically report metrics every 60 seconds (Completed/Buffered count).

---

## 3. Evaluation Criteria

We look for:
- **Concurrency & Asyncio performance**: Correct use of async loops without blocking.
- **Edge Case Rigor**: Ability to stay alive amidst the Chaos stream flags (disconnects, broken JSON).
- **Clean Architecture**: Separating data mapping (`models.py`) from ingestion strategies.
- **Observability**: Quality of logs and metric formats.

Good luck!
