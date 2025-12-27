from socket_ import Socket_
from Utilities import utilities as uc
from Utilities import client_gui as client_gui
from Utilities import end_screen
import sys
import pygame as p
from pathlib import Path


DEFAULT_SERVER_IP = "place server id HERE, (temporary)"
PORT = 55555


def main():
    # Allow running with no args during dev (hard-coded server IP) -for now
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        server_ip = DEFAULT_SERVER_IP
    else:
        server_ip = sys.argv[1].strip()

    port = PORT
    if len(sys.argv) >= 3 and sys.argv[2].strip():
        try:
            port = int(sys.argv[2].strip())
        except ValueError:
            print("Invalid port; using default:", PORT)
            port = PORT

    top_matrix = uc.create_matrix()
    bottom_matrix = uc.create_matrix()

    n = Socket_(server_ip, port=port)
    client_id = n.player_id
    if client_id is None:
        print("Failed to connect to server (no player_id received)")
        sys.exit(1)

    gui = client_gui.ClientGUI()
    fleet_json = None
    prep_game_status = True
    TOTAL_SHIP_CELLS = 18

    # Audio path
    p.mixer.init()
    audio_dir = Path(__file__).parent / "source_files" / "sprites" / "Audio"
    p.mixer.music.load(str(audio_dir / "pirate_7.mp3"))
    p.mixer.music.play(loops=10, start=10, fade_ms=2000)
    miss_sfx = p.mixer.Sound(str(audio_dir / "miss.mp3"))
    hit_sfx = p.mixer.Sound(str(audio_dir / "crash.mp3"))

    turn = None
    run = True
    while run:
        # Non-blocking updates from server
        new_turn = n.get_turn()
        if new_turn is not None:
            turn = new_turn

        if fleet_json is None:
            maybe_fleet = n.get_fleet()
            if maybe_fleet:
                fleet_json = maybe_fleet
                uc.procces_boats_sprites(None, fleet_json, gui.bottom_buttons)

        win_msg = n.get_win()
        if win_msg:
            p.mixer.music.fadeout(2500)
            end_screen.show_end_screen("You won")
            break

        updated_str_matrix = n.get_matrix()
        if updated_str_matrix:
            new_bottom = uc.string_to_matrix(updated_str_matrix)
            changed = uc.first_changed_value(bottom_matrix, new_bottom)
            if changed == 2 and prep_game_status is False:
                miss_sfx.play()
            elif changed == 3 and prep_game_status is False:
                hit_sfx.play()
            bottom_matrix = new_bottom

            # Loss detection 
            hits = sum(1 for row in bottom_matrix for v in row if v == 3)
            if hits >= TOTAL_SHIP_CELLS:
                p.mixer.music.fadeout(2500)
                end_screen.show_end_screen("You Lose")
                break

        events = gui.process_events()
        if events["quit"]:
            run = False

        if events.get("top_click") is not None and turn == client_id:
            pos_str = uc.make_pos(events["top_click"])
            reply = n.send(f"attack|{pos_str}")
            if reply and reply.startswith("update|"):
                _, outcome, coord = reply.split("|", 2)
                r_str, c_str = coord.split(",")
                r, c = int(r_str), int(c_str)
                if outcome == "hit":
                    top_matrix[r][c] = 3
                    hit_sfx.play()
                else:
                    top_matrix[r][c] = 2
                    miss_sfx.play()
            elif reply and reply.startswith("error|"):
                # Not your turn / invalid cell, etc.
                print(reply)

        gui.draw(top_matrix, bottom_matrix)
        prep_game_status = False

    try:
        p.mixer.music.stop()
    except Exception:
        pass
    gui.shutdown()


if __name__ == "__main__":
    main()

