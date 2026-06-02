import asyncio
import json
import string
import random
import argparse
from collections import defaultdict

try:
    import websockets
except ImportError:
    print("Install websockets: pip install websockets")
    raise

rooms: dict[str, list] = defaultdict(list)
player_room: dict = {}
player_name: dict = {}
player_color: dict = {}


def generate_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def cleanup(websocket):
    if websocket in player_room:
        code = player_room.pop(websocket)
        player_name.pop(websocket, None)
        player_color.pop(websocket, None)
        if code in rooms:
            for ws in rooms[code]:
                if ws != websocket and ws.open:
                    try:
                        await ws.send(json.dumps({"type": "opponent_disconnected"}))
                    except Exception:
                        pass
            rooms[code] = [ws for ws in rooms[code] if ws != websocket]
            if not rooms[code]:
                del rooms[code]


async def handler(websocket):
    print(f"[+] New connection from {websocket.remote_address}")
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "create":
                code = generate_code()
                while code in rooms and len(rooms[code]) > 0:
                    code = generate_code()

                rooms[code].append(websocket)
                player_room[websocket] = code
                player_name[websocket] = msg.get("name", "Player 1")
                player_color[websocket] = "white"

                await websocket.send(
                    json.dumps(
                        {
                            "type": "room_created",
                            "code": code,
                            "color": "white",
                        }
                    )
                )
                print(f"[Room {code}] Created by {player_name[websocket]}")

            elif msg_type == "join":
                code = msg.get("code", "").upper().strip()
                name = msg.get("name", "Player 2")

                if code not in rooms or len(rooms[code]) >= 2:
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Комната не найдена или уже заполнена",
                            }
                        )
                    )
                    continue

                if len(rooms[code]) >= 2:
                    await websocket.send(
                        json.dumps(
                            {"type": "error", "message": "Комната уже заполнена"}
                        )
                    )
                    continue

                rooms[code].append(websocket)
                player_room[websocket] = code
                player_name[websocket] = name
                player_color[websocket] = "black"

                await websocket.send(
                    json.dumps(
                        {
                            "type": "room_joined",
                            "code": code,
                            "color": "black",
                            "opponent": player_name.get(rooms[code][0], "Player 1"),
                        }
                    )
                )

                host = rooms[code][0]
                if host.open:
                    await host.send(
                        json.dumps(
                            {
                                "type": "opponent_joined",
                                "opponent": name,
                            }
                        )
                    )

                print(f"[Room {code}] {name} joined")

                for ws in rooms[code]:
                    if ws.open:
                        await ws.send(
                            json.dumps(
                                {
                                    "type": "game_start",
                                    "white": player_name.get(
                                        rooms[code][0], "Player 1"
                                    ),
                                    "black": name,
                                }
                            )
                        )

            elif msg_type in ("move", "resign", "chat", "offer_draw", "accept_draw"):
                code = player_room.get(websocket)
                if not code or code not in rooms:
                    continue

                for ws in rooms[code]:
                    if ws != websocket and ws.open:
                        fwd = dict(msg)
                        fwd["from_color"] = player_color.get(websocket, "?")
                        await ws.send(json.dumps(fwd))

            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        addr = websocket.remote_address
        await cleanup(websocket)
        print(f"[-] Disconnected {addr}")


async def main(host: str, port: int):
    print(f"♟ Chess Relay Server starting on ws://{host}:{port}")
    print(f"   Players connect and share room codes to play.\n")

    async with websockets.serve(handler, host, port):
        await asyncio.Future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chess Master Relay Server")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)"
    )
    parser.add_argument("--port", type=int, default=8765, help="Port (default: 8765)")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\nServer stopped.")
