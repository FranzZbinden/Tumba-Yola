import pygame

# Screen Size
width = 500
height = 500

clientNumber = 0 # How many clients are active (unsure)

window = pygame.display.set_mode((width, height))     
pygame.display.set_caption("Client")



class Player ():
    def __init__(self, x, y, width, height, color): 
        self.x = x 
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rectangle = (x,y,width,height)  #tuple for knowing the location of the player, and size (width,height) of the player
        self.vel = 3


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

        self.rectangle = (self.x,self.y,self.width,self.height)


def redrawWindow(window, player):
    window.fill((255,255,255))
    player.draw(window)
    pygame.display.update()


def main():
    run = True
    p = Player(50, 50, 100, 100, (0, 255, 0))   # Test player
    clock = pygame.time.Clock()


    while run:
        clock.tick(60)  # Limits fps 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(window, p)

main()