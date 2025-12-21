from socket_ import Socket_
from Utilities import utilities as uc
from Utilities import client_gui as client_gui
import sys
from Utilities import end_screen
import pygame as p

top_matrix = uc.create_matrix() # <<---- Top BOARD 
bottom_matrix = uc.create_matrix() # <<---- Botton BOARD 

def main():
    global top_matrix, bottom_matrix
    run = True
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Usage: python client.py <server_ip>")
        sys.exit(1)
    server_ip = sys.argv[1].strip()
    n = Socket_(server_ip)
    client_id = n.player_id

    if client_id is None:
        print("Failed to connect to server (no player_id received)")
        sys.exit(1)

    turn = n.get_turn()

    gui = client_gui.ClientGUI()
    fleet_json = None
    prep_game_status = True
    TOTAL_SHIP_CELLS = 18
    
    p.mixer.init()
    p.mixer.music.load(uc.MUSIC) #"source_files/sprites/Audio/pirate_7.mp3"
    p.mixer.music.play(loops=10, start=10, fade_ms=2000)

    miss_sfx = p.mixer.Sound("source_files\sprites\Audio\miss.mp3")
    hit_sfx = p.mixer.Sound("source_files\sprites\Audio\crash.mp3")

    while run: 
        new_turn = n.get_turn()
        if new_turn is not None:
            turn = new_turn
        if turn == client_id:
            print("Is your turn")
        else:
            print("Is not your turn")
        
        # Try to capture initial fleet payload once and assign sprites into buttons
        if fleet_json is None:
            maybe_fleet = n.get_fleet()
            if maybe_fleet:
                fleet_json = maybe_fleet
                uc.procces_boats_sprites(None, fleet_json, gui.bottom_buttons)

        # Check for win - from server
        win_msg = n.get_win()
        if win_msg:
            end_screen.show_end_screen("You won")
            break

        updated_str_matrix = n.get_matrix() # recives self updated matrix
        if updated_str_matrix:
            new_bottom = uc.string_to_matrix(updated_str_matrix)
            if uc.first_changed_value(bottom_matrix,new_bottom) == 2 and prep_game_status == False:
                miss_sfx.play()
            elif uc.first_changed_value(bottom_matrix,new_bottom) == 3 and prep_game_status == False:
                hit_sfx.play()
            bottom_matrix = uc.string_to_matrix(updated_str_matrix) # converts to 2d list
            # Detect loss (all ship cells have been hit)
            hits = sum(1 for row in bottom_matrix for v in row if v == 3)
            if hits >= TOTAL_SHIP_CELLS:
                p.mixer.music.fadeout(2500)
                end_screen.show_end_screen("You Lose")
                break

        events = gui.process_events() # Checks for events, button down or close-game.
        if events["quit"]:
            run = False
        if events.get("top_click") is not None and turn == client_id:
            pos_str = uc.make_pos(events["top_click"])

            reply = n.send(f"attack|{pos_str}") # message

            # Expect single-line response
            if reply and reply.startswith("update|"):
                # Server replies: update|hit/miss|r,c
                _, outcome, coord = reply.split("|", 2)
                r_str, c_str = coord.split(",")
                r, c = int(r_str), int(c_str)
                if outcome == "hit":
                    top_matrix[r][c] = 3
                    hit_sfx.play()
                else:
                    top_matrix[r][c] = 2
                    miss_sfx.play()


        gui.draw(top_matrix, bottom_matrix)
        prep_game_status = False
    p.mixer.music.stop()
    gui.shutdown()
main()