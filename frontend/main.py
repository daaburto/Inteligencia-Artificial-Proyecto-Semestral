import pygame

from backend.interseccion import Intersection
# TRAINING_MODE = 0;  Useful for visualization, few steps per minute
# TRAINING_MODE = 1; Used to train the model, a lot of steps per minute
class Game:
    def __init__(self, MODE, GRID):
        pygame.init()
        self.screen_size = 800
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        self.clock = pygame.time.Clock()
        self.running = True

        self.TRAINING_MODE = MODE
        self.__GRID = GRID
        self.tick = 0

        self.font_minecraft = pygame.font.Font("../resources/fonts/minecraft.ttf", 30)

        # Objetos
        self.interseccion = Intersection()

        # Imagenes
        self.__background = pygame.image.load("../resources/interseccion.png").convert()
        self.__cars = [
            pygame.image.load("../resources/car1.png").convert_alpha(),
            pygame.image.load("../resources/car2.png").convert_alpha(),
            pygame.image.load("../resources/car3.png").convert_alpha(),
            pygame.image.load("../resources/car4.png").convert_alpha(),
            pygame.image.load("../resources/car5.png").convert_alpha()]
        for i in range(len(self.__cars)):
            self.__cars[i] = pygame.transform.scale(self.__cars[i], (20,20))

        self.__trafficlight_img = [
            pygame.image.load("../resources/Semaforo_rojo.png"),
            pygame.image.load("../resources/Semaforo_amarillo.png"),
            pygame.image.load("../resources/Semaforo_verde.png")]
        for i in range(len(self.__trafficlight_img)):
            self.__trafficlight_img[i] = pygame.transform.scale(self.__trafficlight_img[i], (200,200))


    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(240)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.TRAINING_MODE:
            self.interseccion.step()
        else:
            self.tick += 1/1000
            if self.tick >= 1:
                self.tick = 0
                self.interseccion.step()


    def draw(self):
        self.screen.fill((30,30,30))
        self.screen.blit(self.__background, (0,0))

        # Tamaños
        grid_size = self.interseccion.get_size()
        rec_size = self.screen_size/grid_size

        # Dibujar autos en pantalla
        for auto in self.interseccion.vehicles:
            # Imagen del auto
            if auto.image == 1:
                car_image = self.__cars[0]
            elif auto.image == 2:
                car_image = self.__cars[1]
            elif auto.image == 3:
                car_image = self.__cars[2]
            elif auto.image == 4:
                car_image = self.__cars[3]
            else:
                car_image = self.__cars[4]

            # Posición del auto
            x, y = auto.get_position()
            cx = x * rec_size
            cy = y * rec_size
            if auto.get_direction() == "sur":
                car_image = pygame.transform.rotate(car_image, 180)
                cx = (x*rec_size) - 2.2*rec_size
            elif auto.get_direction() == "este":
                car_image = pygame.transform.rotate(car_image, -90)
                cy = (y*rec_size) + (0.8*rec_size)
            elif auto.get_direction() == "oeste":
                car_image = pygame.transform.rotate(car_image, 90)
                cy = (y * rec_size) - (1.8*rec_size)
            else:
                cx = (x * rec_size) + 1 * rec_size
            self.screen.blit(car_image, (cx, cy))
        # Dibujar semáforo
        if self.interseccion.semaforo.is_green("norte"):
            self.screen.blit(self.__trafficlight_img[2], (20*rec_size, 5.5*rec_size))
        else:
            self.screen.blit(self.__trafficlight_img[0], (20 * rec_size, 5.5 * rec_size))

        # Dibujar hora
        hora = self.font_minecraft.render(f"{self.interseccion.current_hour}:{self.interseccion.current_minute}:{self.interseccion.current_second}", True, (255,255,255))
        self.screen.blit(hora, (1*rec_size, 1*rec_size))

        # Dibujar grilla para ver posiciones exactar de autos
        # No es necesaria dibujarla al visualizar
        if self.__GRID:
            for i in range(grid_size):
                for j in range(grid_size):
                    x = rec_size*i
                    y = rec_size*j
                    rec_color = (60, 60, 120)
                    if self.interseccion.get_position(i,j) == 1:
                        rec_color = (120,40,20)

                    pygame.draw.rect(self.screen, rec_color, (x,y,rec_size-30,rec_size-30), border_radius = 15)


        pygame.display.flip()
if __name__ == "__main__":
    Game(1, 0).run()