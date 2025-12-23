# Class that manages the rooms
# Created: 12/23/2025
# Last Modified:

from Utilities.room import Room


class RoomManager:
    def __init__(self):
        self.rooms = {}          # room_id -> Room
        self.client_room = {}    # client -> room_id
        self.next_room_id = 1    # start at 1 

    def create_room(self, host_client):
        self.leave(host_client)        # if already in a room, remove first (optional safety)

        room_id = self.next_room_id
        self.next_room_id += 1  # uses current room id and add +1 for next room id

        room = Room(room_id, host_client)
        self.rooms[room_id] = room
        self.client_room[host_client] = room_id

        return room, 0  # host is player 0

    def join_room(self, joiner_client, room_id):
        self.leave(joiner_client)         # if already in a room, remove first (optional safety)

        room = self.rooms.get(room_id)    # gets room from room_id
        if room is None:
            return None, None, "ROOM_NOT_FOUND"

        if room.is_full():
            return None, None, "ROOM_FULL"

        try:
            player_index = room.add_joiner(joiner_client)  # returns 1
        except ValueError:
            return None, None, "ROOM_FULL"

        self.client_room[joiner_client] = room_id
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

        return room_id, idx # returns the room_id the client just left, and the index for the client that left

    # returns the room the given client
    def get_room_of(self, client):
        room_id = self.client_room.get(client)
        if room_id is None:
            return None
        return self.rooms.get(room_id)
