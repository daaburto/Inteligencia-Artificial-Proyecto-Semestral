import random
from semaforo import Semaforo

class Intersection:
    """
    Gestiona la lógica del entorno usando una grilla.
    """

    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.center_cell = grid_size // 2  # Casilla central de la intersección

        self.semaforo = Semaforo()
        self.vehicles = []

        # Configuración de generación de tráfico
        self.base_spawn_interval = 3  # Spawn cada N steps
        self.current_hour = 6  # Hora inicial simulada (6:00 AM)

        # Métricas
        self.total_wait_time = 0
        self.phase_changes = 0
        self.total_steps = 0

    # Determina si es hora punta (7-9 AM o 5-8 PM)
    def is_rush_hour(self):
        return (7 <= self.current_hour < 9) or (17 <= self.current_hour < 20)

    # Retorna el intervalo de spawn según la hora.
    # En las horas punta genera vehículos más frecuentemente.
    def get_spawn_interval(self):
        if self.is_rush_hour():
            return max(1, int(self.base_spawn_interval * 0.5))  # Spawn más rápido
        return self.base_spawn_interval

    # Retorna la posición inicial en la grilla según dirección.
    # Los vehículos spawean en el borde de la grilla.
    def get_spawn_position(self, direction):
        if direction == 'norte':
            return self.center_cell, self.grid_size - 1
        elif direction == 'sur':
            return self.center_cell, 0
        elif direction == 'este':
            return 0, self.center_cell
        else:  # oeste
            return self.grid_size - 1, self.center_cell

    # Genera un nuevo vehículo en una dirección aleatoria.
    def spawn_vehicle(self):
        direction = random.choice(['norte', 'sur', 'este', 'oeste'])

        # vehicle = Vehicle() # falta el manejo de veiculos

        #self.vehicles.append(vehicle)

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

    def get_waiting_vehicles_count(self):
        # Contar vehiculos
        return 0


    def calculate_reward(self):
        # calcular recompensa del agente (?
        return 0


    def step(self):
        # hace una accion en el etorno y actualiza (?
        return 0

    def reset(self):
        # reiniciar el entorno (?
        return 0

    # Para DEBUG
    def __repr__(self):
        waiting = self.get_waiting_vehicles_count()
        return f"Intersection(grid={self.grid_size}x{self.grid_size}, vehicles={len(self.vehicles)}, waiting={waiting})"