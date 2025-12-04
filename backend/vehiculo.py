import random

class Vehiculo:
    def __init__(self, position, direction):
        self.__position = [position[0], position[1]]
        self.__direction = direction
        self.image = random.randint(1,5)

    def get_position(self):
        return self.__position
    def get_direction(self):
        return self.__direction

    def move(self, grid_size):
        match self.__direction:
            case 'norte':
                if self.__position[1] == 0:
                    return False
                self.__position[1] -= 1
                return True
            case 'sur':
                if self.__position[1] == grid_size - 1:
                    return False
                self.__position[1] += 1
                return True
            case 'este':
                if self.__position[0] == grid_size - 1:
                    return False
                self.__position[0] += 1
                return True
            case 'oeste':
                if self.__position[0] == 0:
                    return False
                self.__position[0] -= 1
                return True


# Capacidad para moverse
# Necesita saber posición actual, para ver si un espacio está ocupado o no
# Dirección a la que va?