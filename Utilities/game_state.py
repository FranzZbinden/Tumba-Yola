
# Room-scoped gameplay logic.
# This module owns turn validation, attack application, and win detection.

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from Utilities import utilities as uc
from Utilities import server_utilities as suc

@dataclass
class Outbound: # server -> client
    attacker_lines: List[str]
    defender_lines: List[str]
    broadcast_lines: List[str]
    game_over: bool


    # Battleship-like state over a `Room`:
    # - `room.boards[pid]` is the *defender* board for that player:
    #     0 empty, 1 ship, 2 miss, 3 hit
    # - current_turn is the player id allowed to attack.
class GameState:
    def __init__(self, room):
        self.room = room
        self.current_turn = 0
        self.hit_counts = {0: 0, 1: 0}  # hits landed on opponent ships
        self.total_ship_cells = getattr(room, "total_ship_cells", 18)
        self.closed = False


    # Lines to send when the room is ready for this player:
    # - fleet|...
    # - matrix|...
    # - turn|...
    def start_payload_for(self, player_id: int) -> List[str]:

        fleet_json = uc.normalize_fleet_for_wire(self.room.fleets[player_id])
        matrix_str = uc.matrix_to_string(self.room.boards[player_id])
        return [
            f"fleet|{fleet_json}\n",
            f"matrix|{matrix_str}\n",
            f"turn|{self.current_turn}\n",
        ]

    def handle_attack(self, attacker_id: int, pos: Tuple[int, int]) -> Outbound:
        if self.closed:
            return Outbound(
                attacker_lines=["error|Game already ended\n"],
                defender_lines=[],
                broadcast_lines=[],
                game_over=True,
            )

        if attacker_id not in (0, 1):
            return Outbound(
                attacker_lines=["error|Invalid player id\n"],
                defender_lines=[],
                broadcast_lines=[],
                game_over=False,
            )

        if attacker_id != self.current_turn:
            return Outbound(
                attacker_lines=["error|Not your turn\n"],
                defender_lines=[],
                broadcast_lines=[],
                game_over=False,
            )

        defender_id = 1 - attacker_id
        board = self.room.boards[defender_id]

        r, c = pos
        if r < 0 or c < 0 or r >= len(board) or c >= len(board[0]):
            return Outbound(
                attacker_lines=["error|Invalid coordinates\n"],
                defender_lines=[],
                broadcast_lines=[],
                game_over=False,
            )

        try:
            new_val = suc.apply_attack_to_cell(board, pos)  # mutates defender board
        except ValueError as e:
            return Outbound(
                attacker_lines=[f"error|{e}\n"],
                defender_lines=[],
                broadcast_lines=[],
                game_over=False,
            )

        outcome = "hit" if new_val == 3 else "miss"
        attacker_lines = [f"update|{outcome}|{r},{c}\n"]
        defender_lines = [f"matrix|{uc.matrix_to_string(board)}\n"]

        if new_val == 3:
            self.hit_counts[attacker_id] += 1
            if self.hit_counts[attacker_id] >= self.total_ship_cells:
                attacker_lines.append("win|You won\n")
                self.closed = True
                return Outbound(
                    attacker_lines=attacker_lines,
                    defender_lines=defender_lines,
                    broadcast_lines=[],
                    game_over=True,
                )

        # Advance turn
        self.current_turn = defender_id
        broadcast_lines = [f"turn|{self.current_turn}\n"]
        return Outbound(
            attacker_lines=attacker_lines,
            defender_lines=defender_lines,
            broadcast_lines=broadcast_lines,
            game_over=False,
        )


