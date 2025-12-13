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
            alpha=0.1,
            gamma=0.95,
            epsilon=1.0,
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
        """
        episode_rewards = []
        episode_wait_times = []
        # ✨ NUEVAS MÉTRICAS
        episode_throughput = []  # Vehículos que pasaron
        episode_phase_changes = []  # Cambios de fase
        episode_total_vehicles = []  # Total de vehículos en sistema

        for episode in range(num_episodes):
            env = self.reset_environment()
            state = env.get_state()

            total_reward = 0
            total_wait_time = 0
            total_moved = 0  # ✨ Nueva métrica
            total_vehicles_sum = 0  # ✨ Nueva métrica

            for step in range(max_steps_per_episode):
                # Seleccionar acción
                action = self.agent.get_action(state, training=True)

                # Aplicar acción
                env.apply_action(action)

                # Avanzar entorno
                moved = env.step()
                total_moved += moved  # ✨ Acumular

                # Obtener nuevo estado y recompensa
                next_state = env.get_state()
                reward = env.calculate_reward(action, moved)

                # Actualizar agente
                done = (step == max_steps_per_episode - 1)
                self.agent.update(state, action, reward, next_state, done)

                # Acumular métricas
                total_reward += reward
                total_wait_time += env.get_waiting_vehicles_count()
                total_vehicles_sum += len(env.vehicles)  # ✨ Nueva métrica

                state = next_state

            # Reducir epsilon
            self.agent.decay_epsilon()

            # Guardar métricas
            avg_wait_time = total_wait_time / max_steps_per_episode
            avg_throughput = total_moved / max_steps_per_episode  # ✨ Nueva
            avg_vehicles = total_vehicles_sum / max_steps_per_episode  # ✨ Nueva

            episode_rewards.append(total_reward)
            episode_wait_times.append(avg_wait_time)
            episode_throughput.append(avg_throughput)  # ✨ Nueva
            episode_phase_changes.append(env.phase_changes)  # ✨ Nueva
            episode_total_vehicles.append(avg_vehicles)  # ✨ Nueva

            # Mostrar progreso con más info
            if verbose and (episode + 1) % 10 == 0:
                recent_rewards = np.mean(episode_rewards[-10:])
                recent_wait = np.mean(episode_wait_times[-10:])
                recent_throughput = np.mean(episode_throughput[-10:])  # ✨
                recent_changes = np.mean(episode_phase_changes[-10:])  # ✨

                print(f"Episodio {episode + 1}/{num_episodes} | "
                      f"Reward: {recent_rewards:.2f} | "
                      f"Espera: {recent_wait:.2f} | "
                      f"Throughput: {recent_throughput:.2f} | "  # ✨
                      f"Cambios: {recent_changes:.1f} | "  # ✨
                      f"ε: {self.agent.epsilon:.3f}")

            # Guardar modelo periódicamente
            if (episode + 1) % save_interval == 0:
                self.agent.save()

        # Guardar modelo final
        self.agent.save()

        return {
            'rewards': episode_rewards,
            'wait_times': episode_wait_times,
            'throughput': episode_throughput,
            'phase_changes': episode_phase_changes,
            'total_vehicles': episode_total_vehicles
        }

    def evaluate(self, num_episodes=10, max_steps=1000):
        """Evalúa el agente entrenado sin exploración."""
        episode_wait_times = []
        episode_vehicle_counts = []
        episode_throughput = []  # ✨ Nueva

        print("\n=== Evaluación del Agente ===")

        for episode in range(num_episodes):
            env = self.reset_environment()
            state = env.get_state()

            total_wait_time = 0
            total_vehicles = 0
            total_moved = 0  # ✨ Nueva

            for step in range(max_steps):
                action = self.agent.get_action(state, training=False)
                env.apply_action(action)
                moved = env.step()

                total_moved += moved  # ✨
                total_wait_time += env.get_waiting_vehicles_count()
                total_vehicles += len(env.vehicles)

                state = env.get_state()

            avg_wait_time = total_wait_time / max_steps
            avg_vehicles = total_vehicles / max_steps
            avg_throughput = total_moved / max_steps  # ✨

            episode_wait_times.append(avg_wait_time)
            episode_vehicle_counts.append(avg_vehicles)
            episode_throughput.append(avg_throughput)  # ✨

            print(f"Episodio {episode + 1}: "
                  f"Espera = {avg_wait_time:.2f}, "
                  f"Vehículos = {avg_vehicles:.2f}, "
                  f"Throughput = {avg_throughput:.2f}")  # ✨

        results = {
            'avg_wait_time': np.mean(episode_wait_times),
            'std_wait_time': np.std(episode_wait_times),
            'avg_vehicles': np.mean(episode_vehicle_counts),
            'std_vehicles': np.std(episode_vehicle_counts),
            'avg_throughput': np.mean(episode_throughput),  # ✨
            'std_throughput': np.std(episode_throughput)  # ✨
        }

        print(f"\n=== Resultados Finales ===")
        print(f"Tiempo de espera: {results['avg_wait_time']:.2f} ± {results['std_wait_time']:.2f}")
        print(f"Vehículos promedio: {results['avg_vehicles']:.2f} ± {results['std_vehicles']:.2f}")
        print(f"Throughput: {results['avg_throughput']:.2f} ± {results['std_throughput']:.2f}")  # ✨

        return results

    def compare_with_baseline(self, num_episodes=10, max_steps=1000):
        """Compara el agente entrenado con un semáforo de tiempo fijo."""
        print("\n=== Comparación: Agente vs. Baseline ===")

        # Evaluar agente entrenado
        print("\n--- Agente Q-Learning ---")
        agent_results = self.evaluate(num_episodes, max_steps)

        # Evaluar baseline (cambio fijo cada 30 steps)
        print("\n--- Semáforo Tiempo Fijo (30s) ---")
        baseline_wait_times = []
        baseline_throughput = []  # ✨

        for episode in range(num_episodes):
            env = self.reset_environment()
            total_wait_time = 0
            total_moved = 0  # ✨

            for step in range(max_steps):
                if step % 30 == 0 and step > 0:
                    env.apply_action(1)  # Cambiar
                else:
                    env.apply_action(0)  # Mantener

                moved = env.step()
                total_moved += moved  # ✨
                total_wait_time += env.get_waiting_vehicles_count()

            avg_wait_time = total_wait_time / max_steps
            avg_throughput = total_moved / max_steps  # ✨
            baseline_wait_times.append(avg_wait_time)
            baseline_throughput.append(avg_throughput)  # ✨

            print(f"Episodio {episode + 1}: "
                  f"Espera = {avg_wait_time:.2f}, "
                  f"Throughput = {avg_throughput:.2f}")  # ✨

        baseline_avg_wait = np.mean(baseline_wait_times)
        baseline_std_wait = np.std(baseline_wait_times)
        baseline_avg_throughput = np.mean(baseline_throughput)  # ✨

        print(f"\nBaseline - Espera: {baseline_avg_wait:.2f} ± {baseline_std_wait:.2f}")
        print(f"Baseline - Throughput: {baseline_avg_throughput:.2f}")  # ✨

        # Comparación
        wait_improvement = ((baseline_avg_wait - agent_results['avg_wait_time']) / baseline_avg_wait) * 100
        throughput_improvement = ((agent_results[
                                       'avg_throughput'] - baseline_avg_throughput) / baseline_avg_throughput) * 100  # ✨

        print(f"\n=== Resultados ===")
        print(f"Mejora en espera: {wait_improvement:.2f}%")
        print(f"Mejora en throughput: {throughput_improvement:.2f}%")  # ✨

        return agent_results, baseline_avg_wait, baseline_std_wait

    def plot_training_progress(self, metrics):
        """Grafica el progreso del entrenamiento con todas las métricas."""
        window = 20

        # ========================================
        # GRÁFICA 1: Recompensas y Tiempo de Espera
        # ========================================
        fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Recompensas
        rewards = metrics['rewards']
        smoothed_rewards = np.convolve(rewards, np.ones(window) / window, mode='valid')

        ax1.plot(rewards, alpha=0.3, label='Recompensa')
        ax1.plot(range(window - 1, len(rewards)), smoothed_rewards, label='Media móvil')
        ax1.set_xlabel('Episodio')
        ax1.set_ylabel('Recompensa total')
        ax1.set_title('Recompensas')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Tiempo de espera
        wait_times = metrics['wait_times']
        smoothed_wait = np.convolve(wait_times, np.ones(window) / window, mode='valid')

        ax2.plot(wait_times, alpha=0.3, label='Espera')
        ax2.plot(range(window - 1, len(wait_times)), smoothed_wait, label='Media móvil')
        ax2.set_xlabel('Episodio')
        ax2.set_ylabel('Vehículos esperando (promedio)')
        ax2.set_title('Tiempo de Espera')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('training_progress.png', dpi=300)
        print("\nGráfica 1 guardada: 'training_progress.png'")
        plt.show()

        # ========================================
        # GRÁFICA 2: Flujo de Tráfico y Cambios de Fase
        # ========================================
        fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(10, 8))

        # Flujo de tráfico
        throughput = metrics['throughput']
        smoothed_throughput = np.convolve(throughput, np.ones(window) / window, mode='valid')

        ax3.plot(throughput, alpha=0.3, label='Flujo', color='green')
        ax3.plot(range(window - 1, len(throughput)), smoothed_throughput,
                 label='Media móvil', color='darkgreen')
        ax3.set_xlabel('Episodio')
        ax3.set_ylabel('Vehículos pasando (promedio)')
        ax3.set_title('Flujo de Tráfico')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Cambios de fase
        changes = metrics['phase_changes']
        smoothed_changes = np.convolve(changes, np.ones(window) / window, mode='valid')

        ax4.plot(changes, alpha=0.3, label='Cambios', color='orange')
        ax4.plot(range(window - 1, len(changes)), smoothed_changes,
                 label='Media móvil', color='darkorange')
        ax4.set_xlabel('Episodio')
        ax4.set_ylabel('Número de cambios de fase')
        ax4.set_title('Cambios de Fase')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('training_flow_changes.png', dpi=300)
        print("Gráfica 2 guardada: 'training_flow_changes.png'")
        plt.show()


def main():
    """Función principal de entrenamiento."""
    print("=== Entrenamiento de Agente Q-Learning ===\n")

    simulator = TrafficSimulator(grid_size=40)

    # Entrenar
    print("Iniciando entrenamiento...\n")
    metrics = simulator.train(
        num_episodes=500,
        max_steps_per_episode=1000,
        save_interval=50,
        verbose=True
    )

    # Graficar progreso
    simulator.plot_training_progress(metrics)

    # Evaluar y comparar
    simulator.compare_with_baseline(num_episodes=10, max_steps=1000)

    print("\n¡Entrenamiento completado!")


if __name__ == "__main__":
    main()