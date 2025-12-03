class Vehiculo:
    def __init__(self, position):
        self.position = position

    def get_position(self):
        return self.position

# Capacidad para moverse
# Necesita saber posición actual, para ver si un espacio está ocupado o no
# Dirección a la que va?