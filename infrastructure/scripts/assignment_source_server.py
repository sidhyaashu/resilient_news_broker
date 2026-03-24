#!/usr/bin/env python3
"""
InvestCode - Resilient News Broker Assignment
Mock Source Server (The "Firehose")

This script simulates a high-volume, bursty, and unreliable news stream.
Candidates must connect to this stream, handle authentication, and survive
the "Chaos" mode.

Usage:
    python assignment_source_server.py
"""

import asyncio
import json
import random
import time
from datetime import datetime
import websockets
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

HOST = "0.0.0.0"
PORT = 8888
REQUIRED_TOKEN = "test-session-chaos"

# Pre-defined headline templates to simulate similarity and noise
HEADLINE_TEMPLATES = [
    "AAPL stock jumps {val}% after earnings result",
    "Apple Inc. shares surge post-earnings: up {val}%",
    "Tech giant AAPL sees {val}% rise in pre-market",
    "Federal Reserve announces interest rate hike of {val} bps",
    "Fed lifts rates by {val} basis points to combat inflation",
    "Markets react as Fed hikes interest rates by {val} bps",
    "Oil prices edge higher amid supply concerns",
    "Crude oil prices rise on expected supply crunch",
    "S&P 500 futures trade flat before opening bell",
    "Wall Street futures steady ahead of market open",
    "Earnings Alert: {company} beating expectations",
    "{company} reports record revenue for Q1",
    "Unrelated local news about traffic on highway {val}",
]

COMPANIES = ["MSFT", "GOOGL", "AMZN", "META", "TSLA"]

def generate_headline():
    """Generates a random headline, sometimes duplicating concepts."""
    template = random.choice(HEADLINE_TEMPLATES)
    val = random.randint(1, 15)
    company = random.choice(COMPANIES)
    return template.format(val=val, company=company)

def generate_malformed_json(headline, priority):
    """Generates malformed JSON strings standard parsers will fail on."""
    choice = random.randint(0, 2)
    timestamp = datetime.utcnow().isoformat()
    if choice == 0:
        # Missing quote on a key
        return f'{{headline: "{headline}", "priority": {priority}, "timestamp": "{timestamp}"}}'
    elif choice == 1:
        # Trailing comma
        return f'{{"headline": "{headline}", "priority": {priority}, "timestamp": "{timestamp}",}}'
    else:
        # Unclosed bracket or similar
        return f'{{"headline": "{headline}", "priority": {priority}, "timestamp": "{timestamp}"'

async def handle_client(websocket):
    """Handles continuous connection stream for one client."""
    remote_addr = websocket.remote_address
    # In websockets 12+, path can be accessed via websocket.path
    try:
        path = websocket.path
    except AttributeError:
        # Fallback if attribute naming differs
        path = "/ws" 

    logger.info(f"New connection from {remote_addr} on path {path}")

    if path != "/ws":
        logger.warning(f"Invalid path: {path}. Closing.")
        await websocket.close(1008, "Invalid Path")
        return

    try:
        # 1. Handshake Phase
        logger.info(f"Waiting for handshake from {remote_addr}")
        handshake_data = await asyncio.wait_for(websocket.recv(), timeout=5.0)
        auth = json.loads(handshake_data)

        if auth.get("token") != REQUIRED_TOKEN:
            logger.warning(f"Auth failed for {remote_addr}: invalid token")
            await websocket.send(json.dumps({"error": "Unauthorized", "code": 401}))
            await websocket.close(1008, "Auth Failed")
            return

        logger.info(f"Auth successful for {remote_addr}. Starting stream...")
        await websocket.send(json.dumps({"status": "connected", "mode": "chaos"}))

        # 2. Streaming Phase
        message_count = 0
        while True:
            # Simulate "Chaos" - Randomly drop connection
            # Higher probability of drop after 5 messages
            if message_count > 5 and random.random() < 0.15:
                # 15% chance to drop connection abruptly
                logger.warning(f"SIMULATING CHAOS: Dropping connection to {remote_addr}")
                # We just return or break to simulate abrupt close
                break

            # Generate item
            headline = generate_headline()
            priority = random.randint(1, 3) # 1: High, 2: Medium, 3: Low
            
            # 10% chance to send malformed JSON
            if random.random() < 0.10:
                logger.debug("Simulating Malformed JSON")
                msg = generate_malformed_json(headline, priority)
            else:
                msg = json.dumps({
                    "headline": headline,
                    "priority": priority,
                    "timestamp": datetime.utcnow().isoformat()
                })

            await websocket.send(msg)
            message_count += 1
            
            # Burstiness: sleep 0.1s to 2.0s
            sleep_time = random.uniform(0.1, 1.5)
            await asyncio.sleep(sleep_time)

    except asyncio.TimeoutError:
        logger.warning(f"Handshake timeout for {remote_addr}")
        await websocket.close(1001, "Timeout")
    except json.JSONDecodeError:
        logger.warning(f"Invalid handshake JSON from {remote_addr}")
        await websocket.close(1001, "Invalid Handshake Format")
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Connection closed by {remote_addr}")
    except Exception as e:
        logger.error(f"Unexpected error handling {remote_addr}: {e}")
    finally:
        logger.info(f"Connection with {remote_addr} ended")

async def main():
    logger.info(f"Starting Assignment Source Server on ws://{HOST}:{PORT}/ws")
    async with websockets.serve(handle_client, HOST, PORT):
        # Keep serving forever
        await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
