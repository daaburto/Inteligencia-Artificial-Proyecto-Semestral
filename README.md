# Semáforo Inteligente

## Configuración del proyecto
Sigue estos pasos para configurar y ejecutar la aplicación:

### 1. Clonar el repositorio
```bash
git clone https://github.com/daaburto/Inteligencia-Artificial-Proyecto-Semestral.git
```
### 2. Crear y activar un entorno virtual
```bash
python -m venv venv
.\venv\Scripts\Activate  # En Windows
# source venv/bin/activate  # En Linux/Mac
```

### 3. Instalar dependencias
Instala las dependencias listadas en `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Entrenar agente
Inicia la aplicación para entrenar al agente con:
```bash
python train_agent.py
```

Tener en cuenta que el agente no se entrena de forma gráfica, sino que sólo se corre el backend del programa.

Luego de ejecutarlo y entrenarlo un rato, se mostrará en pantalla gráficos que dirán los resultados del modelo, los gráficos son:
- Recompensa
- Flujo de tráfico
- Tiempo de espera
- Cambio de fase

### 5. Observar cruce (Opcional)
Si bien el cruce de main no está entrenado, se puede ver cómo funciona el flujo de vehículos, teniendo un tiempo fijo del semáforo, inicia la aplicación con:
```bash
python main.py
```

### Representación Visual
En la interfaz gráfica se puede observar un único semáforo, el cual funciona de la siguiente manera:

Verde: El tráfico avanza de norte a sur y viceversa

Rojo: El tráfico avanza de este a oeste y viceversa


## Notas adicionales
- **Entorno virtual**: Siempre activa el entorno virtual (`.\venv\Scripts\Activate`) antes de ejecutar `python laberinto.py`.
- `main.py`: Este no es el modelo entrenado, sino simplemente la implementación del cruce con un semáforo fijo de 15 steps
- Código hecho y testeado en Windows