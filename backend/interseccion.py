import random

from pygame.display import get_active

from backend.semaforo import Semaforo
from backend.vehiculo import Vehiculo
from backend.spawn_vehiculo import SpawnVehicle

class Intersection:
    """
    Gestiona la lógica del entorno usando una grilla.
    """

    def __init__(self, grid_size=40):
        self.grid_size = grid_size
        self.center_cell = grid_size // 2  # Casilla central de la intersección

        # Crear grilla
        self.grid = [[0 for _ in range(self.grid_size)]for _ in range(self.grid_size)]


        self.semaforo = Semaforo()
        self.vehicles = []

        # Configuración de generación de tráfico
        self.base_spawn_interval = 3  # Spawn cada N steps
        self.current_hour = 7  # Hora inicial simulada (6:00 AM)
        self.current_minute = 0
        self.current_second = 0

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
        x = spawn_pos[0]
        y = spawn_pos[1]

        if self.grid[y][x] != 1:
            vehicle = self.spawn.spawn_vehicle(spawn_pos, direction)

            self.vehicles.append(vehicle)

            print(f"vehiculo spawneado en {y, x} hacia {direction} a las {self.current_hour}:{self.current_minute}:{self.current_second}")
            self.grid[y][x] = 1
        else:
            print(f"Ya hay un vehiculo en {y, x}, no fue posible aparecer otro")

    # Cuenta vehículos esperando en cada dirección y los categoriza.
    def get_traffic_levels(self):
        counts = {'norte': 0, 'sur': 0, 'este': 0, 'oeste': 0}

        border_offset = self.grid_size // 4 + 6
        min_c = border_offset
        max_c = self.grid_size - border_offset - 1

        # Contar vehículos esperando ANTES de la intersección
        for auto in self.vehicles:
            x, y = auto.get_position()
            direction = auto.get_direction()

            # Verificar si el vehículo está esperando en el borde
            if direction == 'este' and x < min_c:
                counts['este'] += 1
            elif direction == 'oeste' and x > max_c:
                counts['oeste'] += 1
            elif direction == 'norte' and y > max_c:
                counts['norte'] += 1
            elif direction == 'sur' and y < min_c:
                counts['sur'] += 1

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
        levels = self.get_traffic_levels()

        return levels['norte'], levels['sur'], levels['este'], levels['oeste'], self.semaforo.state, self.semaforo.get_time_category()

    # Retorna el tamaño de la grilla
    def get_size(self):
        return self.grid_size

    # Retorna el valor de la posicion señalada de la grilla
    def get_position(self, x, y):
        return self.grid[y][x]

    # Obtener lista de vehículos que están en la intersección
    def get_vehicles_in_intersection(self):
        vehicles = []
        border_offset = self.grid_size // 4 + 6
        min_c = border_offset
        max_c = self.grid_size - border_offset - 1

        for auto in self.vehicles:
            x, y = auto.get_position()
            if min_c <= x <= max_c and min_c <= y <= max_c:
                vehicles.append(auto)
        return vehicles

    def can_cross(self, vehiculo):
        direction = vehiculo.get_direction()
        x,y = vehiculo.get_position()
        border_offset = self.grid_size//4 + 6

        # Verificar sólo si el auto está a punto de cruzar
        if direction == 'norte' and y != self.grid_size - border_offset:
            return True
        if direction == 'sur' and y != border_offset - 1:
            return True
        if direction == 'este' and x != border_offset - 1:
            return True
        if direction == 'oeste' and x != self.grid_size - border_offset:
            return True

        blockers = {
            'norte': ['este','oeste'],
            'sur': ['este', 'oeste'],
            'este': ['norte', 'sur'],
            'oeste': ['norte', 'sur']
        }
        interseccion_autos = self.get_vehicles_in_intersection()

        for auto in interseccion_autos:
            if auto is vehiculo:
                continue

            if auto.get_direction() in blockers[direction]:
                return False
        return True

    def get_waiting_vehicles_count(self):
        waiting_count = 0
        border_offset = self.grid_size // 4 + 6
        min_c = border_offset
        max_c = self.grid_size - border_offset - 1

        for auto in self.vehicles:
            x, y = auto.get_position()
            if auto.get_direction() == 'este' and x < min_c:
                waiting_count +=1
                continue
            elif auto.get_direction() == 'oeste' and x > max_c:
                waiting_count +=1
                continue
            elif auto.get_direction() == 'norte' and y > max_c:
                waiting_count +=1
                continue
            elif auto.get_direction() == 'sur' and y < min_c:
                waiting_count +=1
                continue
        return waiting_count


    def calculate_reward(self, accion_tomada, moved_this_step):
        waiting_vehicles = self.get_waiting_vehicles_count()
        wait_penalty = -0.5 * waiting_vehicles

        # Premio al pasar autos
        pass_reward = moved_this_step * 2.0

        # Penalización por cambiar de fase
        change_penalty = -3.0 if accion_tomada == 1 else 0.0

        raw_reward = wait_penalty + pass_reward + change_penalty

        # acotar recompensa por step para estabilidad
        reward = max(-20.0, min(20.0, raw_reward))

        return reward

    # Calcular steps
    def step(self):
        # Avanzar el tiempo simulado
        # 1 step = 1 minuto
        self.current_second += 1
        if self.current_second >= 60:
            self.current_minute += 1
            self.current_second = 0

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
        moved_this_step = 0

        for vehiculo in self.vehicles:
            # Guardar posición antigua
            old_x, old_y = vehiculo.get_position()

            # Tomar x e y del vehículo actual
            x,y = vehiculo.get_position()
            # Posición en la que los autos se detendrán
            border_offset = self.grid_size//4 + 6

            # Verificar que no hay un vehículo en la casilla donde se está avanzando
            if vehiculo.get_direction() == 'norte' and y != 0:
                # Verificar en su casilla correspondiente si el semáforo está detenido o no
                if self.semaforo.is_green('norte') or  y != self.grid_size - border_offset:
                    # Si hay un vehículo atravezando el cruce, no pasar hasta que hayan pasado los vehículos
                    if self.can_cross(vehiculo):
                        y -= 1
                        # En este caso el vehículo no está en una orilla, por lo que comparamos y avanzamos
                        if self.grid[y][x] != 1:
                            vehiculo.move(self.grid_size)
            elif vehiculo.get_direction() == 'sur' and y != self.grid_size - 1:
                if self.semaforo.is_green('sur') or y != border_offset - 1:
                    if self.can_cross(vehiculo):
                        y += 1
                        if self.grid[y][x] != 1:
                            vehiculo.move(self.grid_size)
            elif vehiculo.get_direction() == 'este' and x != self.grid_size - 1:
                if self.semaforo.is_green('este') or x != border_offset - 1:
                    if self.can_cross(vehiculo):
                        x += 1
                        if self.grid[y][x] != 1:
                            vehiculo.move(self.grid_size)
            elif vehiculo.get_direction() == 'oeste' and x != 0:
                if self.semaforo.is_green('oeste') or x != self.grid_size - border_offset:
                    if self.can_cross(vehiculo):
                        x -= 1
                        if self.grid[y][x] != 1:
                            vehiculo.move(self.grid_size)
            else:
                # Caso en el que el vehículo esté en una orilla de la grilla, donde no podemos comparar para x o y +-1
                if not vehiculo.move(self.grid_size):
                    self.vehicles.remove(vehiculo)
                    print(f"vehículo {vehiculo} destrozado")

            new_x, new_y = vehiculo.get_position()
            if (new_x, new_y) != (old_x, old_y):
                moved_this_step += 1




        # Actualizar grilla
        self.update_grid()

        # Actualizar semáforo
        self.semaforo.update()
        return moved_this_step

    def update_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.grid[i][j] = 0
        for auto in self.vehicles:
            x,y = auto.get_position()
            self.grid[y][x] = 1
    # Para animación visual
    def update(self, dt):
        pass

    def reset(self):
        # reiniciar el entorno (?
        return 0

    def apply_action(self, action):
        # action: 0 = mantener fase actual, 1 = cambiar fase
        if action == 1:
            # Intentar cambiar
            changed = self.semaforo.change_state()
            if changed:
                self.phase_changes += 1
            return changed
        else:
            # Mantener fase actual (no hacer nada)
            return False

    # Para DEBUG
    def __repr__(self):
        waiting = self.get_waiting_vehicles_count()
        return f"Intersection(grid={self.grid_size}x{self.grid_size}, vehicles={len(self.vehicles)}, waiting={waiting})"