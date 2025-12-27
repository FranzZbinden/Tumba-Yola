
# Multi-room server.
# The server is responsible for networking + threading.

import socket
import threading

from Utilities import server_utilities as su
from Utilities import utilities as uc
from Utilities.game_state import GameState
from Utilities.room_manager import RoomManager

LOCAL_IP = su.get_local_ip()
PORT = 55555

manager = RoomManager()
manager_lock = threading.Lock()

# Room-scoped locks and game state
room_locks: dict[int, threading.Lock] = {}
room_states: dict[int, GameState] = {}


def _safe_send(conn, line: str) -> None:
    try:
        conn.sendall(line.encode("utf-8"))
    except Exception:
        pass


def _parse_attack(payload: str):
    parts = payload.split(",")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def client_worker(conn, addr, room_id: int, player_id: int) -> None:
    buf = bytearray()
    print(f"[room {room_id}] player {player_id} connected from {addr}")

    while True:
        try:
            chunk = conn.recv(4096)
            if not chunk:
                break
            buf.extend(chunk)
            while True:
                i = buf.find(b"\n")
                if i == -1:
                    break
                line = buf[:i].decode("utf-8", errors="replace").strip()
                del buf[: i + 1]
                if not line:
                    continue

                t, sep, payload = line.partition("|")
                if not sep:
                    _safe_send(conn, "error|Invalid message format\n")
                    continue

                if t == "attack":
                    pos = _parse_attack(payload)
                    if pos is None:
                        _safe_send(conn, "error|Invalid Coordinates\n")
                        continue

                    # Snapshot state/lock under manager lock
                    with manager_lock:
                        room = manager.rooms.get(room_id)
                        state = room_states.get(room_id)
                        lock = room_locks.get(room_id)

                    if room is None or state is None or lock is None:
                        _safe_send(conn, "error|Room not ready\n")
                        continue

                    with lock:
                        out = state.handle_attack(player_id, pos)

                        # Identify sockets (may have disconnected)
                        attacker_conn = room.clients[player_id]
                        defender_conn = room.clients[1 - player_id]

                        if attacker_conn is not None:
                            for ln in out.attacker_lines:
                                _safe_send(attacker_conn, ln)
                        if defender_conn is not None:
                            for ln in out.defender_lines:
                                _safe_send(defender_conn, ln)
                        for ln in out.broadcast_lines:
                            if room.clients[0] is not None:
                                _safe_send(room.clients[0], ln)
                            if room.clients[1] is not None:
                                _safe_send(room.clients[1], ln)
                    continue

                _safe_send(conn, "error|Unknown type\n")

        except Exception:
            break

    # Disconnect cleanup vvvvv
    print(f"[room {room_id}] player {player_id} disconnected")
    with manager_lock:
        room = manager.rooms.get(room_id)
        manager.leave(conn)
        # If room still exists and has the other player, notify them
        if room is not None:
            other = room.get_other_client(conn)
            if other is not None:
                _safe_send(other, "error|Opponent disconnected\n")

        # If room removed, drop state/lock
        if room_id not in manager.rooms:
            room_states.pop(room_id, None)
            room_locks.pop(room_id, None)

    try:
        conn.close()
    except Exception:
        pass


def _ensure_room_runtime(room_id: int, room) -> None:
    if room_id not in room_locks:
        room_locks[room_id] = threading.Lock()
    if room_id not in room_states:
        room_states[room_id] = GameState(room)


def _send_start_payload(room_id: int, room) -> None:
    state = room_states[room_id]
    # Per-player payload
    for pid in (0, 1):
        c = room.clients[pid]
        if c is None:
            continue
        for ln in state.start_payload_for(pid):
            _safe_send(c, ln)

    # Optional "ready" marker for UIs, -to implement...
    if room.clients[0] is not None:
        _safe_send(room.clients[0], "status|OK\n")
    if room.clients[1] is not None:
        _safe_send(room.clients[1], "status|OK\n")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    su.bind_safe(s, LOCAL_IP, PORT)
    s.listen()
    print(f"Server started on {LOCAL_IP}:{PORT}. Waiting for connections...")

    while True:
        conn, addr = s.accept()
        print("Connected to:", addr)

        with manager_lock:
            room, player_index, status = manager.matchmake(conn, board_size=10, ship_lengths=(3, 4, 5, 6))
            room_id = room.room_id
            _ensure_room_runtime(room_id, room)

        # Welcome lines (Socket_.connect waits for ack|)
        _safe_send(conn, f"ack|You are player: {player_index}\n")
        _safe_send(conn, f"room|{room_id}\n")
        _safe_send(conn, f"status|{status}\n")

        # Spawn receiver thread for this connection
        threading.Thread(
            target=client_worker,
            args=(conn, addr, room_id, player_index),
            daemon=True,
        ).start()

        # If matched, send full game start payload to both
        if status == "OK":
            with manager_lock:
                room_live = manager.rooms.get(room_id)
            if room_live is not None and room_live.is_full():
                with room_locks[room_id]:
                    _send_start_payload(room_id, room_live)
