# All Problems in This Assignment


---

#  1. WebSocket Connection Problem

### Problem:

* Server randomly disconnects you
* Connection is not stable

### You must solve:

* Detect disconnection
* Reconnect automatically
* Avoid spamming reconnects

### Required Concept:

* **Exponential Backoff**

---

#  2. Handshake Authentication Problem

### Problem:

Server expects:

```json
{"token": "test-session-chaos"}
```

If:

* you send late ❌
* you send wrong ❌

👉 connection is closed

### You must solve:

* Send handshake immediately after connect
* Handle auth failure response

---

#  3. Infinite Streaming Problem

### Problem:

* Data never stops
* You are consuming an infinite stream

### You must solve:

* Process continuously
* Avoid memory leaks
* Avoid blocking event loop

---

#  4. Malformed JSON Problem

### Problem:

Server sends broken JSON like:

* Missing quotes
* Trailing commas
* Half messages

### You must solve:

* Catch `JSONDecodeError`
* Skip invalid messages
* Log them

👉 **DO NOT crash**

---

#  5. Data Validation Problem

### Problem:

Even valid JSON may be:

* Missing fields
* Invalid priority

### You must solve:

* Use Pydantic validation
* Catch `ValidationError`
* Skip bad data

---

#  6. Duplicate News Problem (Core Logic)

### Problem:

Same news → different text

Examples:

* "Apple stock jumps"
* "AAPL shares surge"

### You must solve:

* Detect semantic similarity
* Avoid storing duplicates

---

### Sub-problems:

* What similarity metric?
* What threshold?
* How many past items to compare?

---

#  7. Sliding Window Problem

### Problem:

If you store all history:

* memory grows forever ❌

### You must solve:

* Keep only last N headlines
* Remove old ones

---

#  8. Bursty Traffic Problem

### Problem:

Server sends:

* Sometimes 1 msg/sec
* Sometimes 10 msg/sec

### You must solve:

* Handle variable load
* Ensure no blocking

---

#  9. Database Failure Problem (Simulated)

### Problem:

DB can be:

* slow
* unavailable
* failing

### You must solve:

* Do NOT lose data
* Do NOT block system

---

#  10. Buffer Overflow Problem

### Problem:

Buffer has limited size (e.g. 100)

If DB is down:
👉 buffer fills up

---

### You must solve:

* Decide what to drop
* Keep important data

---

#  11. Drop Strategy Problem

### Problem:

Not all data is equal

Priority:

* 1 = High
* 3 = Low

---

### You must solve:

When buffer full:

* Drop priority 3 first
* Keep priority 1

---

#  12. Backpressure Problem (Advanced)

### Problem:

Producer (server) is faster than consumer

👉 System overload

---

### You must solve:

* Use buffer properly
* Prevent system crash

---

#  13. Concurrency Problem

### Problem:

You are doing multiple things:

* receiving data
* processing
* storing

---

### You must solve:

* Use `asyncio` correctly
* Avoid blocking calls

---

#  14. Retry Logic Problem

### Problem:

Failures happen repeatedly

---

### You must solve:

* Retry safely
* Avoid infinite tight loops

---

#  15. Observability Problem

### Problem:

You don’t know what system is doing

---

### You must solve:

Log:

```text
Stored: X | Deduplicated/Dropped: Y | Buffered: Z
```

---

#  16. Graceful Degradation Problem

### Problem:

System is partially failing

---

### You must solve:

* Continue working even if:

  * DB fails
  * network fails
  * data is bad

---

#  17. Memory Management Problem

### Problem:

* Buffer grows
* History grows

---

### You must solve:

* Limit buffer size
* Limit dedup window

---

#  18. Message Ordering Problem (Implicit)

### Problem:

Async systems can reorder messages

---

### You must be careful:

* Don’t break logic due to async timing

---

#  19. Logging Problem

### Problem:

Too much logs ❌
Too little logs ❌

---

### You must solve:

* Log meaningful events:

  * reconnect
  * drop
  * duplicate
  * errors

---

#  20. System Stability Problem (MOST IMPORTANT)

### Problem:

System runs for long time

---

### You must ensure:

* No crashes
* No memory leaks
* No deadlocks

---

#  FINAL SUMMARY

---

## 4 BIG categories:

---

### 1. NETWORK PROBLEMS

* disconnects
* retries
* handshake

---

### 2. DATA PROBLEMS

* malformed JSON
* invalid schema
* duplicates

---

### 3. SYSTEM PROBLEMS

* buffering
* overflow
* prioritization

---

### 4. ARCHITECTURE PROBLEMS

* async handling
* resilience
* observability