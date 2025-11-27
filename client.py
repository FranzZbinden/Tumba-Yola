from socket_ import Socket_
import utilities as uc
import client_gui as client_gui

clientNumber = 0 
top_matrix = uc.create_matrix() # <<---- TOP BOARD 
bottom_matrix = uc.create_matrix() # <<---- botton BOARD 

def main():
    global top_matrix, bottom_matrix
    run = True
    n = Socket_()
    gui = client_gui.ClientGUI()
    fleet_json = None

    while run: 
        # Try to capture initial fleet payload once and assign sprites into buttons
        if fleet_json is None:
            maybe_fleet = n.get_fleet()
            if maybe_fleet:
                fleet_json = maybe_fleet
                uc.procces_boats_sprites(None, fleet_json, gui.bottom_buttons)

        updated_str_matrix = n.get_matrix() # recives self updated matrix
        if updated_str_matrix:
            bottom_matrix = uc.string_to_matrix(updated_str_matrix) # converts to 2d list

        events = gui.process_events() # Checks for events, button down or close-game.
        if events["quit"]:
            run = False
        if events.get("top_click") is not None:
            pos_str = uc.make_pos(events["top_click"])
            reply = n.send(f"attack|{pos_str}")
            # Expect single-line response: update|hit|r,c|<matrix> or update|miss|r,c|<matrix>
            if reply and reply.startswith("update|"):
                _, outcome, coord, _matrix_str = reply.split("|", 3)
                r_str, c_str = coord.split(",")
                r, c = int(r_str), int(c_str)
                top_matrix[r][c] = 3 if outcome == "hit" else 2

        gui.draw(top_matrix, bottom_matrix)
    gui.shutdown()
main()