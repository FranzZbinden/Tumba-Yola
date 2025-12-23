# Class room
# Created: 12/23/2025
# Last Modified:

class Room:
    def __init__(self, room_id, host_client):
        self.room_id = room_id
        self.clients = [host_client, None]  # host is player 

    # Adds the joiner client, not the host client
    def add_joiner(self, client):
        if self.clients[1] is None:
            self.clients[1] = client
            return 1
        raise ValueError("Room is full")

    # Removes the given client
    def remove_client(self, client):
        if self.clients[0] is client:
            self.clients[0] = None
            return 0
        if self.clients[1] is client:
            self.clients[1] = None
            return 1
        return None

    # Returns true if full
    def is_full(self):
        return self.clients[0] is not None and self.clients[1] is not None

    # Returns true if empty
    def is_empty(self):
        return self.clients[0] is None and self.clients[1] is None

    # Returns the opposite client from given client
    def get_other_client(self, client):
        if self.clients[0] is client:
            return self.clients[1]
        if self.clients[1] is client:
            return self.clients[0]
        return None
