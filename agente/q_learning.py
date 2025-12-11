import numpy as np
import pickle
import os


class QLearning:
    """
    Espacio de estados: ~486 estados
    - 4 direcciones con 3 niveles de tráfico cada una (3^4 = 81)
    - 2 fases de semáforo
    - 3 categorías de tiempo desde último cambio
    Total: 81 × 2 × 3 = 486 estados

    Espacio de acciones: 2 acciones
    - 0: Mantener fase actual
    - 1: Cambiar fase
    """

    def __init__(self, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        """
            alpha: Tasa de aprendizaje (learning rate)
            gamma: Factor de descuento
            epsilon: Probabilidad inicial de exploración
            epsilon_decay: Decaimiento de epsilon por episodio
            epsilon_min: Epsilon mínimo
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Tabla Q: diccionario de (estado, acción)
        self.q_table = {}

        # Métricas de entrenamiento
        self.total_steps = 0
        self.episodes_completed = 0

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def set_q_value(self, state, action, value):
        self.q_table[(state, action)] = value

    # Selecciona una acción usando política epsilon-greedy.
    def get_action(self, state, training=True):
        # Durante entrenamiento, exploración con epsilon-greedy
        if training and np.random.random() < self.epsilon:
            return np.random.randint(0, 2)  # Exploración: acción aleatoria

        # Explotación: elegir mejor acción
        q0 = self.get_q_value(state, 0)
        q1 = self.get_q_value(state, 1)

        if q0 > q1:
            return 0
        elif q1 > q0:
            return 1
        else:
            return np.random.randint(0, 2)  # Empate: elegir al azar

    # Actualiza la tabla Q usando la ecuación de Q-Learning.
    def update(self, state, action, reward, next_state, done=False):
        """
            state: Estado actual
            action: Acción tomada
            reward: Recompensa recibida
            next_state: Siguiente estado
            done: Si el episodio terminó
        """
        current_q = self.get_q_value(state, action)

        if done:
            # Si el estado es el ultimo, no hay valor futuro
            target = reward
        else:
            # Calcular máximo valor Q del siguiente estado
            next_q0 = self.get_q_value(next_state, 0)
            next_q1 = self.get_q_value(next_state, 1)
            max_next_q = max(next_q0, next_q1)

            # Ecuación de Q-Learning
            target = reward + self.gamma * max_next_q

        # Actualización
        new_q = current_q + self.alpha * (target - current_q)
        self.set_q_value(state, action, new_q)

        self.total_steps += 1

    # Reduce epsilon después de cada episodio.
    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self.episodes_completed += 1

    # Guarda la tabla Q en un archivo.
    def save(self, filepath="models/q_table.pkl"):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            'q_table': self.q_table,
            'epsilon': self.epsilon,
            'total_steps': self.total_steps,
            'episodes_completed': self.episodes_completed,
            'alpha': self.alpha,
            'gamma': self.gamma
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        print(f"Tabla Q guardada en {filepath}")
        print(f"Estados en tabla: {len(self.q_table) // 2}")

    # Carga la tabla Q desde un archivo pickle
    def load(self, filepath="models/q_table.pkl"):
        if not os.path.exists(filepath):
            print(f"No se encontró archivo en {filepath}")
            return False

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        self.q_table = data['q_table']
        self.epsilon = data['epsilon']
        self.total_steps = data['total_steps']
        self.episodes_completed = data['episodes_completed']
        self.alpha = data['alpha']
        self.gamma = data['gamma']

        print(f"Tabla Q cargada desde {filepath}")
        print(f"Estados en tabla: {len(self.q_table) // 2}")
        print(f"Episodios completados: {self.episodes_completed}")

        return True

    def get_stats(self):
        return {
            'total_steps': self.total_steps,
            'episodes': self.episodes_completed,
            'epsilon': self.epsilon,
            'q_table_size': len(self.q_table) // 2,
            'alpha': self.alpha,
            'gamma': self.gamma
        }

    # Para DEBUG
    def __repr__(self):
        return (f"QLearning(states={len(self.q_table) // 2}, "
                f"episodes={self.episodes_completed}, "
                f"epsilon={self.epsilon:.3f})")