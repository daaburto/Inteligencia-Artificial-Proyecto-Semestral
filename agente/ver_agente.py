import pygame
from backend.interseccion import Intersection
from q_learning import QLearning


class GameWithAgent:
    """Visualización del agente Q-Learning controlando el semáforo."""

    def __init__(self, grid_size=20, show_grid=False):
        pygame.init()
        self.screen_size = 800
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        pygame.display.set_caption("Semáforo Inteligente - Q-Learning")
        self.clock = pygame.time.Clock()
        self.running = True

        self.show_grid = show_grid
        self.tick = 0

        # Cargar agente entrenado
        self.agent = QLearning()
        if not self.agent.load("models/q_table.pkl"):
            print("ADVERTENCIA: No se pudo cargar el agente. Usando agente sin entrenar.")

        # Entorno
        self.interseccion = Intersection(grid_size=grid_size)

        # Imágenes
        self.__background = pygame.image.load("../resources/interseccion.png").convert()
        self.__cars = [
            pygame.image.load("../resources/car1.png").convert_alpha(),
            pygame.image.load("../resources/car2.png").convert_alpha(),
            pygame.image.load("../resources/car3.png").convert_alpha(),
            pygame.image.load("../resources/car4.png").convert_alpha(),
            pygame.image.load("../resources/car5.png").convert_alpha()
        ]
        for i in range(len(self.__cars)):
            self.__cars[i] = pygame.transform.scale(self.__cars[i], (40, 40))

        self.__trafficlight_img = [
            pygame.image.load("../resources/Semaforo_rojo.png"),
            pygame.image.load("../resources/Semaforo_amarillo.png"),
            pygame.image.load("../resources/Semaforo_verde.png")
        ]
        for i in range(len(self.__trafficlight_img)):
            self.__trafficlight_img[i] = pygame.transform.scale(self.__trafficlight_img[i], (200, 200))

        # Fuente para mostrar información
        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)

        # Métricas
        self.total_steps = 0
        self.total_wait_time = 0
        self.phase_changes = 0

    def run(self):
        """Loop principal del juego."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        """Maneja eventos de Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Pausar/reanudar con espacio
                    self.running = not self.running
                elif event.key == pygame.K_g:
                    # Toggle grid
                    self.show_grid = not self.show_grid

    def update(self):
        """Actualiza la simulación."""
        self.tick += 1 / 60

        if self.tick >= 1:  # 1 step por segundo
            self.tick = 0

            # Obtener estado
            state = self.interseccion.get_state()

            # Agente decide acción (sin exploración)
            action = self.agent.get_action(state, training=False)

            # Aplicar acción
            if self.interseccion.apply_action(action):
                if action == 1:
                    self.phase_changes += 1

            # Avanzar simulación
            self.interseccion.step()

            # Actualizar métricas
            self.total_steps += 1
            self.total_wait_time += self.interseccion.get_waiting_vehicles_count()

    def draw(self):
        """Dibuja la escena."""
        self.screen.fill((30, 30, 30))
        self.screen.blit(self.__background, (0, 0))

        # Tamaños
        grid_size = self.interseccion.get_size()
        rec_size = self.screen_size / grid_size

        # Dibujar vehículos
        for auto in self.interseccion.vehicles:
            car_image = self.__cars[auto.image - 1]
            x, y = auto.get_position()
            cx = x * rec_size
            cy = y * rec_size

            # Rotar según dirección
            if auto.get_direction() == "sur":
                car_image = pygame.transform.rotate(car_image, 180)
                cx = (x * rec_size) - 0.8 * rec_size
            elif auto.get_direction() == "este":
                car_image = pygame.transform.rotate(car_image, -90)
                cy = (y * rec_size) + (0.5 * rec_size)
            elif auto.get_direction() == "oeste":
                car_image = pygame.transform.rotate(car_image, 90)
                cy = (y * rec_size) - (0.5 * rec_size)
            else:  # norte
                cx = (x * rec_size) + 0.8 * rec_size

            self.screen.blit(car_image, (cx, cy))

        # Dibujar semáforo
        if self.interseccion.semaforo.is_green("norte"):
            self.screen.blit(self.__trafficlight_img[2], (10.4 * rec_size, 2.5 * rec_size))
        else:
            self.screen.blit(self.__trafficlight_img[0], (10.4 * rec_size, 2.5 * rec_size))

        # Dibujar grilla (opcional)
        if self.show_grid:
            for i in range(grid_size):
                for j in range(grid_size):
                    x = rec_size * i
                    y = rec_size * j
                    rec_color = (60, 60, 120)
                    if self.interseccion.get_position(i, j) == 1:
                        rec_color = (120, 40, 20)
                    pygame.draw.rect(self.screen, rec_color,
                                     (x, y, rec_size - 30, rec_size - 30),
                                     border_radius=15)

        # Dibujar información del agente
        self.draw_info()

        pygame.display.flip()

    def draw_info(self):
        """Dibuja información del agente en pantalla."""
        info_x = 10
        info_y = 10

        # Estado del semáforo
        state = self.interseccion.get_state()
        phase_text = "NORTE-SUR" if state[4] == 0 else "ESTE-OESTE"
        phase_surface = self.font.render(f"Fase: {phase_text}", True, (255, 255, 255))
        self.screen.blit(phase_surface, (info_x, info_y))

        # Métricas
        metrics = [
            f"Vehículos: {len(self.interseccion.vehicles)}",
            f"Esperando: {self.interseccion.get_waiting_vehicles_count()}",
            f"Steps: {self.total_steps}",
            f"Cambios: {self.phase_changes}"
        ]

        if self.total_steps > 0:
            avg_wait = self.total_wait_time / self.total_steps
            metrics.append(f"Espera promedio: {avg_wait:.2f}")

        for i, text in enumerate(metrics):
            surface = self.font_small.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (info_x, info_y + 35 + i * 22))

        # Niveles de tráfico
        levels_text = f"Tráfico N:{state[0]} S:{state[1]} E:{state[2]} O:{state[3]}"
        levels_surface = self.font_small.render(levels_text, True, (200, 200, 200))
        self.screen.blit(levels_surface, (info_x, info_y + 170))

        # Instrucciones
        instructions = [
            "G: Toggle Grid",
            "ESC: Salir"
        ]
        for i, text in enumerate(instructions):
            surface = self.font_small.render(text, True, (150, 150, 150))
            self.screen.blit(surface, (self.screen_size - 150, 10 + i * 22))


if __name__ == "__main__":
    game = GameWithAgent(grid_size=20, show_grid=False)
    game.run()