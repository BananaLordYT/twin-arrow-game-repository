"""Small public WebSocket matchmaker and message relay for Twin Arrow Arena."""

import asyncio
import json
import os

from websockets.legacy.server import serve


waiting_player = None
match_lock = asyncio.Lock()
waiting_events = {}
partners = {}


async def send_message(websocket, message):
    await websocket.send(json.dumps(message, separators=(",", ":")))


async def handler(websocket):
    global waiting_player
    peer = None
    paired_event = None

    async with match_lock:
        if waiting_player is not None and not waiting_player.closed:
            peer = waiting_player
            waiting_player = None
            partners[peer] = websocket
            partners[websocket] = peer
            await send_message(peer, {"type": "matched", "player": 1})
            await send_message(websocket, {"type": "matched", "player": 2})
            waiting_events.pop(peer).set()
        else:
            waiting_player = websocket
            paired_event = asyncio.Event()
            waiting_events[websocket] = paired_event
            await send_message(websocket, {"type": "waiting"})

    try:
        if peer is None:
            # The first player waits until another client joins the queue.
            joined = asyncio.create_task(paired_event.wait())
            disconnected = asyncio.create_task(websocket.wait_closed())
            done, pending = await asyncio.wait(
                (joined, disconnected), return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            if websocket.closed:
                return
            peer = partners.get(websocket)
        if peer is None:
            return

        async for message in websocket:
            if peer.closed:
                break
            await peer.send(message)
    except Exception:
        pass
    finally:
        partners.pop(websocket, None)
        waiting_events.pop(websocket, None)
        if peer is not None:
            partners.pop(peer, None)
            try:
                await send_message(peer, {"type": "opponent_disconnected"})
                await peer.close()
            except Exception:
                pass
        async with match_lock:
            if waiting_player is websocket:
                waiting_player = None
                event = waiting_events.pop(websocket, None)
                if event:
                    event.set()


async def main():
    port = int(os.environ.get("PORT", "10000"))
    async with serve(handler, "0.0.0.0", port, max_size=64_000, ping_interval=20):
        print(f"Twin Arrow matchmaker listening on port {port}", flush=True)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
