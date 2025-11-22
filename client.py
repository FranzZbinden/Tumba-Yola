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

    while run: 
        updated_str_matrix = n.get_matrix()
        if updated_str_matrix:
            bottom_matrix = uc.string_to_matrix(updated_str_matrix)

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