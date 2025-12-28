# Class that manages rooms
# Created: 12/23/2025

from Utilities.room import Room
from collections import deque

class RoomManager:
    def __init__(self):
        self.rooms = {}          # room_id -> Room
        self.client_room = {}    # client -> room_id
        self.next_room_id = 1    # start at 1 
        # FIFO matchmaking queue of room_ids that are waiting for a second player
        self._waiting_rooms = deque()

    def _remove_waiting(self, room_id: int) -> None:
        # Remove all occurrences 
        if not self._waiting_rooms:
            return
        self._waiting_rooms = deque(rid for rid in self._waiting_rooms if rid != room_id)

    # Drop stale/invalid waiting rooms from the left side of the queue.
    # A waiting room is valid if it exists and is not full and has a host client connected.
    def _prune_waiting(self) -> None:
        while self._waiting_rooms:
            rid = self._waiting_rooms[0]
            room = self.rooms.get(rid)
            if room is None:
                self._waiting_rooms.popleft()
                continue
            # Host must exist; joiner must be empty
            if room.clients[0] is None or room.is_full():
                self._waiting_rooms.popleft()
                continue
            break


    # Automatically pair clients in FIFO order.
    # Returns:
    #   (room, player_index, status)
    #     - status: "WAITING" if client is first in a room, "OK" if paired immediately
    def matchmake(self, client, board_size: int = 10, ship_lengths=(3, 4, 5, 6)):
        # If already in a room or queued, remove first
        self.leave(client)

        self._prune_waiting()
        if not self._waiting_rooms:
            room_id = self.next_room_id
            self.next_room_id += 1
            room = Room(room_id, client, board_size=board_size, ship_lengths=ship_lengths)
            self.rooms[room_id] = room
            self.client_room[client] = room_id
            self._waiting_rooms.append(room_id)
            return room, 0, "WAITING"

        # Join the oldest waiting room
        room_id = self._waiting_rooms.popleft()
        room = self.rooms.get(room_id)
        if room is None or room.is_full() or room.clients[0] is None:
            return self.matchmake(client, board_size=board_size, ship_lengths=ship_lengths)

        try:
            player_index = room.add_joiner(client)  # returns 1
        except ValueError:
            # Room filled unexpectedly; try matchmaking again.
            return self.matchmake(client, board_size=board_size, ship_lengths=ship_lengths)

        self.client_room[client] = room_id
        return room, player_index, "OK"

    # Removes given clint from its room
    def leave(self, client):
        room_id = self.client_room.pop(client, None)    # remove and get room_id
        if room_id is None:
            return None, None

        room = self.rooms.get(room_id)
        if room is None:
            return None, None

        idx = room.remove_client(client)

        if room.is_empty():
            for c in room.clients:  # remove any remaining mappings 
                if c is not None:
                    self.client_room.pop(c, None)
            self.rooms.pop(room_id, None)
            self._remove_waiting(room_id)
        else:
            # If room has exactly one player now, it becomes a waiting room again.
            if not room.is_full() and room.clients[0] is not None:
                self._remove_waiting(room_id)
                self._waiting_rooms.append(room_id)
            else:
                self._remove_waiting(room_id)

        return room_id, idx # returns the room_id the client just left, and the index for the client that left

