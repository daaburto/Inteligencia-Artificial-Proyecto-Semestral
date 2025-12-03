import random

from pygame.display import get_active

from backend.semaforo import Semaforo
from backend.vehiculo import Vehiculo
from backend.spawn_vehiculo import SpawnVehicle

class Intersection:
    """
    Gestiona la lógica del entorno usando una grilla.
    """

    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.center_cell = grid_size // 2  # Casilla central de la intersección

        # Crear grilla
        self.grid = [[0 for _ in range(self.grid_size)]for _ in range(self.grid_size)]


        self.semaforo = Semaforo()
        self.vehicles = []

        # Configuración de generación de tráfico
        self.base_spawn_interval = 3  # Spawn cada N steps
        self.current_hour = 6  # Hora inicial simulada (6:00 AM)
        self.current_minute = 0

        # Métricas
        self.total_wait_time = 0
        self.phase_changes = 0
        self.total_steps = 0
        self.spawn_counter = 0

        # Spawn de vehículos, lógica a parte
        self.spawn = SpawnVehicle()

    # Genera un nuevo vehículo en una dirección aleatoria.
    def spawn_vehicle(self):
        direction = random.choice(['norte', 'sur', 'este', 'oeste'])
        spawn_pos = self.spawn.get_spawn_position(direction, self.center_cell, self.grid_size)
        col = spawn_pos[0]
        row = spawn_pos[1]

        if self.grid[row][col] != 1:
            vehicle = self.spawn.spawn_vehicle(spawn_pos)

            self.vehicles.append(vehicle)

            print(f"vehiculo spawneado en {col, row} a las {self.current_hour}:{self.current_minute}")
            self.grid[row][col] = 1
        else:
            print(f"Ya hay un vehiculo en {col, row}, no fue posible aparecer otro")

    # Cuenta vehículos esperando en cada dirección y los categoriza.
    def get_traffic_levels(self):
        counts = {'norte': 0, 'sur': 0, 'este': 0, 'oeste': 0}

        # Manejar self.vehicles

        levels = {}
        for direction, count in counts.items():
            if count <= 5:
                levels[direction] = 0  # bajo
            elif count <= 10:
                levels[direction] = 1  # medio
            else:
                levels[direction] = 2  # alto

        return levels

    # Retorna el estado del entorno para el agente.
    def get_state(self):
        # TODO: get_traffic_levels()
        levels = self.get_traffic_levels()

        return levels['norte'], levels['sur'], levels['este'], levels['oeste'], self.semaforo.state, self.semaforo.get_time_category()

    # Retorna el tamaño de la grilla
    def get_size(self):
        return self.grid_size

    # Retorna el valor de la posicion señalada de la grilla
    def get_position(self, x, y):
        return self.grid[x][y]


    def get_waiting_vehicles_count(self):
        # Contar vehiculos
        return 0


    def calculate_reward(self):
        # calcular recompensa del agente (?
        return 0

    # Calcular steps
    def step(self):
        # Avanzar el tiempo simulado
        # 1 step = 1 minuto
        self.current_minute += 1

        if self.current_minute >= 60:
            self.current_hour += 1
            self.current_minute = 0

        if self.current_hour >= 24:
            # Reiniciar día
            self.current_hour = 0

        # Spawn de vehículos
        self.spawn_counter += 1
        spawn_interval = self.spawn.get_spawn_interval(self.current_hour)

        if self.spawn_counter >= spawn_interval:
            self.spawn_vehicle()
            self.spawn_counter = 0

        # Mover vehículos
        #...

        # Actualizar semáforo
        # ...

        # Obtener nuevo estado
        # ...

        # Calcular reward
        # ...

        return 0

    # Para animación visual
    def update(self, dt):
        pass

    def reset(self):
        # reiniciar el entorno (?
        return 0

    # Para DEBUG
    def __repr__(self):
        waiting = self.get_waiting_vehicles_count()
        return f"Intersection(grid={self.grid_size}x{self.grid_size}, vehicles={len(self.vehicles)}, waiting={waiting})"