"""WebSocket ECG simulator server.

Replaces an Arduino + Bluetooth pulse sensor for development and demo.
Streams JSON messages to any connected Flutter client at the configured
sample rate. Accepts mode-change messages from clients to switch between
physiological scenarios on the fly.

Run:
    python ecg_server.py --mode normal --port 8765 --rate 250

Outgoing messages (server -> client):
    { "type": "ecg_sample", "ts": 1746205823.412, "mv": -0.12 }
    { "type": "beat", "ts": 1746205823.892, "rr_ms": 856, "instant_bpm": 70.1 }

Incoming messages (client -> server):
    { "type": "set_mode", "mode": "exercise" }
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import time
from typing import Set

import websockets
from websockets.legacy.server import WebSocketServerProtocol

from ecg_synth import VALID_MODES, EcgGenerator

LOG = logging.getLogger("ecg_server")


class EcgServer:
    def __init__(self, mode: str, sample_rate: int) -> None:
        self.generator = EcgGenerator(mode=mode, sample_rate=sample_rate)
        self.sample_rate = sample_rate
        self.clients: Set[WebSocketServerProtocol] = set()
        self._broadcast_task: asyncio.Task | None = None

    async def handle_client(self, websocket: WebSocketServerProtocol) -> None:
        self.clients.add(websocket)
        peer = websocket.remote_address
        LOG.info("client connected: %s (total=%d)", peer, len(self.clients))
        try:
            await websocket.send(json.dumps({
                "type": "hello",
                "sample_rate": self.sample_rate,
                "mode": self.generator.mode,
                "modes": list(VALID_MODES),
            }))
            async for raw in websocket:
                self._handle_inbound(raw)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            LOG.info("client disconnected: %s (total=%d)", peer, len(self.clients))

    def _handle_inbound(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            LOG.warning("invalid json from client: %r", raw[:80])
            return
        if msg.get("type") == "set_mode":
            mode = msg.get("mode")
            try:
                self.generator.set_mode(mode)
                LOG.info("mode switched to %s by client", mode)
            except ValueError as e:
                LOG.warning("rejected mode change: %s", e)

    async def _broadcast(self, payload: str) -> None:
        if not self.clients:
            return
        dead = []
        for client in self.clients:
            try:
                await client.send(payload)
            except websockets.exceptions.ConnectionClosed:
                dead.append(client)
        for d in dead:
            self.clients.discard(d)

    async def broadcast_loop(self) -> None:
        loop = asyncio.get_event_loop()
        sample_interval = 1.0 / self.sample_rate
        next_deadline = loop.time()
        while True:
            mv, beat = self.generator.next_sample()
            now = time.time()
            await self._broadcast(json.dumps({
                "type": "ecg_sample",
                "ts": now,
                "mv": round(mv, 5),
            }))
            if beat is not None:
                await self._broadcast(json.dumps({
                    "type": "beat",
                    "ts": now,
                    "rr_ms": round(beat.rr_ms, 2),
                    "instant_bpm": round(beat.instant_bpm, 2),
                }))
            next_deadline += sample_interval
            sleep_for = next_deadline - loop.time()
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            else:
                next_deadline = loop.time()


async def main() -> None:
    parser = argparse.ArgumentParser(description="ECG WebSocket simulator")
    parser.add_argument("--host", default="0.0.0.0",
                        help="bind address (default: 0.0.0.0 — accepts LAN connections)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--mode", default="normal", choices=VALID_MODES)
    parser.add_argument("--rate", type=int, default=250, help="samples per second")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    server = EcgServer(mode=args.mode, sample_rate=args.rate)
    LOG.info("starting ECG simulator on ws://%s:%d (mode=%s, rate=%dHz)",
             args.host, args.port, args.mode, args.rate)

    async with websockets.serve(server.handle_client, args.host, args.port):
        await server.broadcast_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nshutting down")
