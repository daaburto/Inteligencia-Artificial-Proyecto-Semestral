import sys
import numpy as np
import matplotlib.pyplot as plt
from backend.interseccion import Intersection
from q_learning import QLearning


class TrafficSimulator:
    """Simulador para entrenar y evaluar el agente Q-Learning."""

    def __init__(self, grid_size=40):
        self.grid_size = grid_size
        self.agent = QLearning(
            alpha=0.1,  # Tasa de aprendizaje
            gamma=0.95,  # Factor de descuento
            epsilon=1.0,  # Exploración inicial
            epsilon_decay=0.995,
            epsilon_min=0.01
        )

    def reset_environment(self):
        """Reinicia el entorno para un nuevo episodio."""
        env = Intersection(grid_size=self.grid_size)
        return env

    def train(self, num_episodes=500, max_steps_per_episode=86400,
              save_interval=50, verbose=True):
        """
        Entrena el agente durante múltiples episodios.

        Args:
            num_episodes: Número de episodios de entrenamiento
            max_steps_per_episode: Pasos máximos por episodio
            save_interval: Guardar modelo cada N episodios
            verbose: Mostrar progreso
        """
        episode_rewards = []
        episode_wait_times = []

        for episode in range(num_episodes):
            env = self.reset_environment()
            state = env.get_state()

            total_reward = 0
            total_wait_time = 0

            for step in range(max_steps_per_episode):
                # Seleccionar acción
                action = self.agent.get_action(state, training=True)

                # Aplicar acción
                env.apply_action(action)

                # Avanzar entorno
                moved = env.step()

                # Obtener nuevo estado y recompensa
                next_state = env.get_state()
                reward = env.calculate_reward(action, moved)

                # Actualizar agente
                done = (step == max_steps_per_episode - 1)
                self.agent.update(state, action, reward, next_state, done)

                # Acumular métricas
                total_reward += reward
                total_wait_time += env.get_waiting_vehicles_count()

                state = next_state

            # Reducir epsilon
            self.agent.decay_epsilon()

            # Guardar métricas
            avg_wait_time = total_wait_time / max_steps_per_episode
            episode_rewards.append(total_reward)
            episode_wait_times.append(avg_wait_time)

            # Mostrar progreso
            if verbose and (episode + 1) % 10 == 0:
                recent_rewards = np.mean(episode_rewards[-10:])
                recent_wait = np.mean(episode_wait_times[-10:])
                print(f"Episodio {episode + 1}/{num_episodes} | "
                      f"Recompensa promedio: {recent_rewards:.2f} | "
                      f"Espera promedio: {recent_wait:.2f} | "
                      f"Epsilon: {self.agent.epsilon:.3f}")

            # Guardar modelo periódicamente
            if (episode + 1) % save_interval == 0:
                self.agent.save()

        # Guardar modelo final
        self.agent.save()

        return episode_rewards, episode_wait_times

    def evaluate(self, num_episodes=10, max_steps=1000):
        """
        Evalúa el agente entrenado sin exploración.

        Returns:
            dict: Métricas de evaluación
        """
        episode_wait_times = []
        episode_vehicle_counts = []

        print("\n=== Evaluación del Agente ===")

        for episode in range(num_episodes):
            env = self.reset_environment()
            state = env.get_state()

            total_wait_time = 0
            total_vehicles = 0

            for step in range(max_steps):
                # Seleccionar mejor acción (sin exploración)
                action = self.agent.get_action(state, training=False)

                # Aplicar y avanzar
                env.apply_action(action)
                env.step()

                # Métricas
                total_wait_time += env.get_waiting_vehicles_count()
                total_vehicles += len(env.vehicles)

                state = env.get_state()

            avg_wait_time = total_wait_time / max_steps
            avg_vehicles = total_vehicles / max_steps

            episode_wait_times.append(avg_wait_time)
            episode_vehicle_counts.append(avg_vehicles)

            print(f"Episodio {episode + 1}: "
                  f"Espera promedio = {avg_wait_time:.2f}, "
                  f"Vehículos promedio = {avg_vehicles:.2f}")

        results = {
            'avg_wait_time': np.mean(episode_wait_times),
            'std_wait_time': np.std(episode_wait_times),
            'avg_vehicles': np.mean(episode_vehicle_counts),
            'std_vehicles': np.std(episode_vehicle_counts)
        }

        print(f"\n=== Resultados Finales ===")
        print(f"Tiempo de espera promedio: {results['avg_wait_time']:.2f} ± {results['std_wait_time']:.2f}")
        print(f"Vehículos promedio: {results['avg_vehicles']:.2f} ± {results['std_vehicles']:.2f}")

        return results

    def compare_with_baseline(self, num_episodes=10, max_steps=1000):
        """
        Compara el agente entrenado con un semáforo de tiempo fijo.
        """
        print("\n=== Comparación: Agente vs. Baseline ===")

        # Evaluar agente entrenado
        print("\n--- Agente Q-Learning ---")
        agent_results = self.evaluate(num_episodes, max_steps)

        # Evaluar baseline (cambio fijo cada 30 steps)
        print("\n--- Semáforo Tiempo Fijo (30s) ---")
        baseline_wait_times = []

        for episode in range(num_episodes):
            env = self.reset_environment()
            total_wait_time = 0

            for step in range(max_steps):
                # Cambiar cada 30 steps
                if step % 30 == 0 and step > 0:
                    env.apply_action(1)  # Cambiar
                else:
                    env.apply_action(0)  # Mantener

                env.step()
                total_wait_time += env.get_waiting_vehicles_count()

            avg_wait_time = total_wait_time / max_steps
            baseline_wait_times.append(avg_wait_time)

            print(f"Episodio {episode + 1}: Espera promedio = {avg_wait_time:.2f}")

        baseline_avg = np.mean(baseline_wait_times)
        baseline_std = np.std(baseline_wait_times)

        print(f"\nBaseline - Tiempo de espera promedio: {baseline_avg:.2f} ± {baseline_std:.2f}")

        # Comparación
        improvement = ((baseline_avg - agent_results['avg_wait_time']) / baseline_avg) * 100
        print(f"\n=== Mejora del Agente: {improvement:.2f}% ===")

        return agent_results, baseline_avg, baseline_std

    def plot_training_progress(self, episode_rewards, episode_wait_times):
        """Grafica el progreso del entrenamiento."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Suavizar curvas con media móvil
        window = 20
        smoothed_rewards = np.convolve(episode_rewards,
                                       np.ones(window) / window,
                                       mode='valid')
        smoothed_wait = np.convolve(episode_wait_times,
                                    np.ones(window) / window,
                                    mode='valid')

        # Recompensas
        ax1.plot(episode_rewards, alpha=0.3, label='Recompensa')
        ax1.plot(range(window - 1, len(episode_rewards)),
                 smoothed_rewards, label='Media móvil')
        ax1.set_xlabel('Episodio')
        ax1.set_ylabel('Recompensa total')
        ax1.set_title('Progreso de Entrenamiento - Recompensas')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Tiempos de espera
        ax2.plot(episode_wait_times, alpha=0.3, label='Espera')
        ax2.plot(range(window - 1, len(episode_wait_times)),
                 smoothed_wait, label='Media móvil')
        ax2.set_xlabel('Episodio')
        ax2.set_ylabel('Vehículos esperando (promedio)')
        ax2.set_title('Progreso de Entrenamiento - Tiempo de Espera')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('training_progress.png', dpi=300)
        print("\nGráfica guardada en 'training_progress.png'")
        plt.show()


def main():
    """Función principal de entrenamiento."""
    print("=== Entrenamiento de Agente Q-Learning ===\n")

    simulator = TrafficSimulator(grid_size=40)

    # Entrenar
    print("Iniciando entrenamiento...\n")
    rewards, wait_times = simulator.train(
        num_episodes=500,
        max_steps_per_episode=1000,
        save_interval=50,
        verbose=True
    )

    # Graficar progreso
    simulator.plot_training_progress(rewards, wait_times)

    # Evaluar y comparar
    simulator.compare_with_baseline(num_episodes=10, max_steps=1000)

    print("\n¡Entrenamiento completado!")


if __name__ == "__main__":
    main()