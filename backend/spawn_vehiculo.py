import random
from backend.vehiculo import Vehiculo

class SpawnVehicle:
    def __init__(self):
        # Configuración de generación de tráfico
        self.base_spawn_interval = 6  # Spawn cada N steps

        # Métricas
        self.total_wait_time = 0
        self.phase_changes = 0
        self.total_steps = 0

    # Determina si es hora punta (7-9 AM o 5-8 PM)
    def is_rush_hour(self, current_hour):
        return (7 <= current_hour < 9) or (17 <= current_hour < 20)

    # Retorna el intervalo de spawn según la hora.
    # En las horas punta genera vehículos más frecuentemente.
    def get_spawn_interval(self, current_hour):
        if self.is_rush_hour(current_hour):
            return max(1, int(self.base_spawn_interval * 0.3))  # Spawn más rápido
        return self.base_spawn_interval

    # Retorna la posición inicial en la grilla según dirección.
    # Los vehículos spawnean en el borde de la grilla.
    def get_spawn_position(self, direction, center_cell, grid_size):
        if direction == 'norte':
            return center_cell, grid_size - 1
        elif direction == 'sur':
            return center_cell - 1, 0
        elif direction == 'este':
            return 0, center_cell
        else:  # oeste
            return grid_size - 1, center_cell - 1

    # Genera un nuevo vehículo
    def spawn_vehicle(self, spawn_pos, direction):
        vehicle = Vehiculo(spawn_pos, direction)
        return vehicle