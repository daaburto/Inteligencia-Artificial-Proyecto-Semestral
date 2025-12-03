import pygame

from backend.interseccion import Intersection
# TRAINING_MODE = 0;  Useful for visualization, few steps per minute
# TRAINING_MODE = 1; Used to train the model, a lot of steps per minute
class Game:
    def __init__(self, MODE):
        pygame.init()
        self.screen_size = 800
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        self.clock = pygame.time.Clock()
        self.running = True

        self.TRAINING_MODE = MODE
        self.tick = 0

        # Objetos
        self.interseccion = Intersection()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.TRAINING_MODE:
            self.interseccion.step()
        else:
            self.tick += 1/100
            if self.tick >= 1:
                self.tick = 0
                self.interseccion.step()


    def draw(self):
        self.screen.fill((30,30,30))

        # Dibujar la grilla en pantalla
        grid_size = self.interseccion.get_size()
        rec_size = self.screen_size/grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                x = rec_size*i
                y = rec_size*j
                rec_color = (60, 60, 120)
                if self.interseccion.get_position(i,j) == 1:
                    rec_color = (120,40,20)

                pygame.draw.rect(self.screen, rec_color, (x,y,rec_size,rec_size), border_radius = 15)


        pygame.display.flip()
if __name__ == "__main__":
    Game(0).run()