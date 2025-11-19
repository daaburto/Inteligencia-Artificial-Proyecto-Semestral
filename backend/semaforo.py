class Semaforo:
    """
    Controla las fases del semáforo en una intersección.

    Solo maneja 2 estados (verde/rojo) no hay un amarrillo.
    El tiempo mínimo de fase simula el periodo de transición entre las fases (como un amarillo).

    0 = Verde Norte-Sur (Rojo Este-Oeste)
    1 = Verde Este-Oeste (Rojo Norte-Sur)
    """

    def __init__(self):
        # Estado actual del semáforo
        self.state = 0

        # Tiempo transcurrido desde el último cambio de estado (en steps)
        self.time_since_change = 0.0

        # Tiempo mínimo por estado
        # Durante estos primeros 5 segundos NO se puede cambiar de estado
        self.min_state_duration = 5.0

    def can_change_state(self):
        return self.time_since_change >= self.min_state_duration

    def change_state(self):
        if self.can_change_state():
            self.state = 1 - self.state  # Toggle entre 0 y 1
            self.time_since_change = 0.0
            return True
        return False

    # Actualiza el contador
    def update(self):
        self.time_since_change += 1

    # Retorna las direcciones que tienen luz verde
    def get_green_directions(self):
        if self.state == 0:
            return ['norte', 'sur']
        else:
            return ['este', 'oeste']

    # Verifica si una dirección específica tiene luz verde
    def is_green(self, direction):
        return direction in self.get_green_directions()

    # Categoriza el tiempo transcurrido
    def get_time_category(self):
        if self.time_since_change <= 10:
            return 0  # reciente
        elif self.time_since_change <= 20:
            return 1  # medio
        else:
            return 2  # prolongado

    # Para DEBUG
    def __repr__(self):
        green_dirs = self.get_green_directions()
        return f"Semaforo(state={self.state}, green={green_dirs}, time={self.time_since_change})"