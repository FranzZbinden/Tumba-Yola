import pygame
from network import Network

# Screen Size
width = 750
height = 750

clientNumber = 0 

window = pygame.display.set_mode((width, height))     
pygame.display.set_caption("Client")


# constructor player
class Player ():
    def __init__(self, x, y, width, height, color): 
        self.x = x 
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rectangle = (x,y,width,height)  #tuple for knowing the location of the player, and size (width,height) of the player
        self.vel = 3 # velocity

    def atack(self):
        pass

    # draw player?
    def draw(self, window):
        pygame.draw.rect(window, self.color, self.rectangle)

    # Updates the atribution rectangle of the object initialized with left, right, up, down
    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.vel

        if keys[pygame.K_RIGHT]:
            self.x += self.vel

        if keys[pygame.K_UP]:
            self.y -= self.vel

        if keys[pygame.K_DOWN]:
            self.y += self.vel

        self.update()

    def update(self):
        self.rectangle = (self.x,self.y,self.width,self.height)


# from string to tuple position
def read_pos(str):
    str = str.split(",")
    return int(str[0]), int(str[1])

# from tuple position to str position
def make_pos(tup):
    return str(tup[0]) + "," + str(tup[1])

# draw players in window 
def redrawWindow(window, player, player2):
    window.fill((255,255,255))
    player.draw(window)
    player2.draw(window)
    pygame.display.update()


def main():
    run = True
    n = Network()
    startPos = read_pos(n.getPos()) # recives string, convert to tuple and sets the value to startPos
    p = Player(startPos[0], startPos[1], 100, 100, (0, 255, 0))   # Test player
    p2 = Player(0, 0, 100, 100, (0, 255, 0))   # Test player2
    clock = pygame.time.Clock()


    while run: 
        clock.tick(60)  # Limits fps 

        p2Pos = read_pos(n.send(make_pos((p.x,p.y))))
        p2.x = p2Pos[0]
        p2.y = p2Pos[1]
        p2.update()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(window, p, p2)

main()