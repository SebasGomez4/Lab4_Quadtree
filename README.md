# Sebastian Gómez Quintero
# Quadtree: sistema de logística de entregas

Implementación de un Quadtree para 10.000 puntos de entrega en un plano de 10.000 × 10.000 m, comparada contra fuerza bruta.

## Archivos

- `quadtree.py`: implementación del Quadtree. Escrito por el autor. La lógica de vecinos más cercanos se desarrolló con apoyo de IA generativa.
- `test.py`: pruebas unitarias y verificación visual. Generado con apoyo de IA generativa.
- `analisis.py`: experimento de rendimiento y gráficas. Generado con apoyo de IA generativa.
- `graficas/`: figuras generadas por `test.py` y `analisis.py`.
- `resultados.csv`: tiempos medidos por tamaño de entrada.

## Respuestas a las preguntas del laboratorio

**1. ¿Qué puntos de entrega están a un radio de 500 m de un punto dado?**

Se construye la caja cuadrada de lado 1.000 m centrada en el punto, se buscan con el Quadtree los puntos que caen dentro de esa caja, y de ellos se conservan los que cumplen `(x − x₀)² + (y − y₀)² ≤ 500²`. La caja es solo un filtro grueso que reduce candidatos; el resultado final se determina con la distancia euclidiana.

**2. ¿Cuál es el punto de entrega más cercano a una ubicación dada?**

Se busca primero dentro de un radio de 500 m. Si no hay puntos, se duplica el radio (1.000 m, 2.000 m, …) hasta encontrar al menos uno. El punto más cercano entre los encontrados es el más cercano de todo el conjunto, porque cualquier punto más cercano también estaría dentro de ese radio. Esta búsqueda no usa branch and bound: en los scripts se recorre la caja completa en cada radio.

## Unidades

Las coordenadas se generan directamente en metros. El radio de 500 m equivale a 500 unidades y la distancia es euclidiana en metros. No hay conversión geográfica: a la escala de una ciudad, la aproximación del plano es despreciable.

## Ejecución

Requiere Python 3 con `numpy` y `matplotlib`. Antes de ejecutar, `quadtree.py` debe tener el bloque de demostración dentro de `if __name__ == "__main__":`, para que importarlo no corra la demo.

```
python test.py
python analisis.py
```

## Decisiones de diseño

- **Espacio.** Plano de 10.000 × 10.000 m, distancia euclidiana.
- **Capacidad de hoja.** 16 puntos.
- **Dimensiones.** Solo 2D. La versión K-dimensional no está implementada.

## Limitaciones conocidas

- Si se insertan más puntos idénticos que la capacidad de una hoja, la subdivisión no termina. Con los datos aleatorios del laboratorio no ocurre.
- El vecino más cercano fuera de 500 m se resuelve duplicando el radio, no con branch and bound. Su costo crece con la distancia al vecino.

## Análisis comparativo

Se miden tiempos promedio por consulta sobre 200 consultas fijas, para n en {100, 300, 1.000, 3.000, 10.000, 30.000, 100.000}. Cada medición es el mejor de 3 repeticiones. Ambos métodos están en Python puro.

Resultados: [completar con la tabla de `resultados.csv`]

Tamaño a partir del cual el Quadtree es más rápido que fuerza bruta:
- Búsqueda por radio: [completar]
- Vecino más cercano: [completar]

Las gráficas están en `graficas/comparacion.png`. La columna izquierda muestra los tiempos en escala log-log. La columna derecha muestra el *speedup*, que es el tiempo de fuerza bruta dividido por el tiempo del Quadtree. Por encima de 1 el Quadtree es más rápido.

## Uso de IA generativa

Se utilizó IA generativa (Claude) en las siguientes actividades:

- Consulta de conceptos.
- Contraste de teoría.
- Consulta de fuentes de información.
- Consulta de sintaxis de Python y equivalencias con Java.
- Desarrollo de la lógica de vecinos más cercanos en `quadtree.py`.
- Generación de `test.py` (pruebas unitarias, adaptadores de radio y vecino más cercano, y verificación visual).
- Generación de `analisis.py` (experimento y gráficas) y apoyo en el análisis comparativo frente a fuerza bruta.
