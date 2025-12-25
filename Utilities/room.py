# Class room
# Created: 12/23/2025
# Last Modified:

from Utilities import server_utilities as uc

class Room:
    def __init__(self, room_id, host_client, board_size: int = 10, ship_lengths=(3, 4, 5, 6)):
        self.room_id = room_id
        self.clients = [host_client, None]  # host is player 
        self.total_ship_cells = sum(ship_lengths)

        self.boards = {}    # for boards - 2D list
        self.fleets = {}    # for rendering - list

        for p_id in (0, 1):
            board, fleet = uc.generate_fleet(board_size, ship_lengths)
            self.boards[p_id] = board
            self.fleets[p_id] = fleet

        # Optional gameplay state fields (handy for server-side turn logic)
        # self.current_turn = 0
        # self.hit_counts = {0: 0, 1: 0}
        # self.closed = False

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
