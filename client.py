from socket_ import Socket_
from Utilities import utilities as uc
from Utilities import client_gui as client_gui
import sys
import pygame as p
from pathlib import Path
DEFAULT_SERVER_IP = "150.136.155.41"
PORT = 55555

def main():
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

    gui = client_gui.ClientGUI()
    # Audio path 
    p.mixer.init()
    audio_dir = Path(__file__).parent / "source_files" / "audio"
    p.mixer.music.load(str(audio_dir / "pirate_7.mp3"))
    p.mixer.music.play(loops=10, start=10, fade_ms=2000)
    miss_sfx = p.mixer.Sound(str(audio_dir / "miss.mp3"))
    hit_sfx = p.mixer.Sound(str(audio_dir / "crash.mp3"))
    hover_sfx = p.mixer.Sound(str(audio_dir / "hover_sound.mp3"))

    TOTAL_SHIP_CELLS = uc.TOTAL_SHIP_CELLS

    while True:
        # New match local state
        gui.reset_for_new_match()
        top_matrix = uc.create_matrix()
        bottom_matrix = uc.create_matrix()
        fleet_json = None
        prep_game_status = True
        turn = None
        last_hover = None
        restart_match = False
        p.event.clear()

        # New connection == new matchmaking
        try:
            n = uc.connect_socket(server_ip, port)
        except Exception as e:
            print(e)
            gui.shutdown()
            return
        client_id = n.player_id

        # Pump initial messages from server 
        # This ensures the first draw shows clean boards.
        for _ in range(5):
            if n.get_fleet() is None and n.get_matrix() is None:
                break
            maybe_fleet = n.get_fleet()
            if maybe_fleet:
                fleet_json = maybe_fleet
                uc.procces_boats_sprites(None, fleet_json, gui.bottom_buttons)
            updated_str_matrix = n.get_matrix()
            if updated_str_matrix:
                bottom_matrix = uc.string_to_matrix(updated_str_matrix)
            new_turn = n.get_turn()
            if new_turn is not None:
                turn = new_turn

        run = True
        while run:
            # Non-blocking updates from server
            new_turn = n.get_turn()
            if new_turn is not None:
                if turn is None and new_turn == client_id:
                    gui.show_toast("YOU START", duration_ms=3000, color=(60, 220, 90))
                elif new_turn == client_id and turn != client_id:
                    gui.show_toast("YOUR TURN", duration_ms=1000, color=(60, 220, 90))
                turn = new_turn

            if fleet_json is None:
                maybe_fleet = n.get_fleet()
                if maybe_fleet:
                    fleet_json = maybe_fleet
                    uc.procces_boats_sprites(None, fleet_json, gui.bottom_buttons)

            win_msg = n.get_win()
            if win_msg:
                p.mixer.music.fadeout(2500)
                choice = gui.show_end_screen(top_matrix, bottom_matrix, message="YOU WIN")
                p.event.clear()  
                n.close()
                if choice == "next_match":
                    # Restart outer loop in the same process/window
                    p.mixer.music.play(loops=10, start=10, fade_ms=600)
                    restart_match = True
                    run = False
                    continue
                gui.shutdown()
                return

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
                    choice = gui.show_end_screen(top_matrix, bottom_matrix, message="YOU LOSE")
                    p.event.clear()  
                    n.close()
                    if choice == "next_match":
                        p.mixer.music.play(loops=10, start=10, fade_ms=600)
                        restart_match = True
                        run = False
                        continue
                    gui.shutdown()
                    return

            events = gui.process_events()
            if events["quit"]:
                run = False
            if events.get("resize"):
                w, h = events["resize"]
                gui.handle_resize(w, h)
            hover = events.get("hover")
            if hover != last_hover:
                if hover is not None and hover_sfx is not None:
                    hover_sfx.play()
                last_hover = hover

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
                    print(reply)

            gui.draw(top_matrix, bottom_matrix)
            prep_game_status = False

        # End of one match loop 
        try:
            n.close()
        except Exception:
            pass
        if restart_match:
            continue
        gui.shutdown()
        return


if __name__ == "__main__":
    main()

