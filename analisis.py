"""
analisis.py - comparacion de rendimiento: Quadtree vs fuerza bruta.

Ejecutar desde la carpeta del proyecto:
    python analisis.py

Usa quadtree.py sin cambios de logica (insertar y buscar). Las funciones
de busqueda por radio y de vecino mas cercano estan definidas aqui,
igual que en test.py.

Genera:
    resultados.csv             tiempos por tamano de n
    graficas/comparacion.png   graficas del analisis

Ambos metodos estan en Python puro para que la comparacion sea justa.
Los tiempos dependen de la maquina: reportalas en el README.
"""
import csv
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from quadtree import Quadtree, Punto, Rectangulo

ANCHO = 10000
ALTO = 10000
RADIO = 500
CARPETA = "graficas"
TAMANOS = [100, 300, 1000, 3000, 10000, 30000, 100000]
CONSULTAS = 200
REPETICIONES = 3
CAPACIDAD = 16
TOLERANCIA = 1e-9


def generar_puntos(n, semilla=1):
    rng = np.random.default_rng(semilla)
    xs = rng.uniform(0, ANCHO, n)
    ys = rng.uniform(0, ALTO, n)
    return [Punto(float(x), float(y)) for x, y in zip(xs, ys)]


def construir(puntos, capacidad=CAPACIDAD):
    qt = Quadtree(Rectangulo(0, 0, ANCHO, ALTO), capacidad)
    for p in puntos:
        qt.insertar(p)
    return qt


def dist2(a, b):
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2


def fuerza_bruta_radio(puntos, centro, radio):
    r2 = radio * radio
    return [p for p in puntos if dist2(p, centro) <= r2]


def fuerza_bruta_vecino(puntos, consulta):
    return min(puntos, key=lambda p: dist2(p, consulta))


def buscar_radio_qt(qt, centro, radio):
    """Busca la caja que envuelve al circulo y filtra por distancia real."""
    caja = Rectangulo(centro.x - radio, centro.y - radio, 2 * radio, 2 * radio)
    candidatos = []
    qt.buscar(caja, candidatos)
    r2 = radio * radio
    return [p for p in candidatos if dist2(p, centro) <= r2]


def vecino_qt(qt, punto, radio_inicial=500, radio_max=20000):
    """Duplica el radio hasta encontrar puntos. El minimo dentro de un
    radio r es el vecino global, porque cualquier punto mas cercano
    tambien estaria dentro de r."""
    r = radio_inicial
    while r <= radio_max:
        dentro = buscar_radio_qt(qt, punto, r)
        if dentro:
            return min(dentro, key=lambda p: dist2(p, punto))
        r *= 2
    return None


def medir(funcion, consultas):
    """Tiempo promedio por consulta (segundos). Toma el mejor de REPETICIONES."""
    mejores = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        for c in consultas:
            funcion(c)
        mejores.append(time.perf_counter() - inicio)
    return min(mejores) / len(consultas)


def experimento(n, consultas):
    puntos = generar_puntos(n)

    inicio = time.perf_counter()
    qt = construir(puntos)
    t_construccion = time.perf_counter() - inicio

    # Antes de medir: ambos metodos deben dar el mismo resultado
    for c in consultas[:20]:
        obtenido = sorted((p.x, p.y) for p in buscar_radio_qt(qt, c, RADIO))
        esperado = sorted((p.x, p.y) for p in fuerza_bruta_radio(puntos, c, RADIO))
        assert obtenido == esperado, f"radio distinto en n={n}"
        d_qt = dist2(vecino_qt(qt, c), c)
        d_bf = dist2(fuerza_bruta_vecino(puntos, c), c)
        assert abs(d_qt - d_bf) < TOLERANCIA, f"vecino distinto en n={n}"

    return {
        "n": n,
        "construccion_s": t_construccion,
        "radio_bf_s": medir(lambda c: fuerza_bruta_radio(puntos, c, RADIO), consultas),
        "radio_qt_s": medir(lambda c: buscar_radio_qt(qt, c, RADIO), consultas),
        "vecino_bf_s": medir(lambda c: fuerza_bruta_vecino(puntos, c), consultas),
        "vecino_qt_s": medir(lambda c: vecino_qt(qt, c), consultas),
    }


def cruce(resultados, clave_bf, clave_qt):
    """Menor n a partir del cual el Quadtree es mas rapido en todos los n mayores."""
    n_cruce = None
    for r in reversed(resultados):
        if r[clave_qt] < r[clave_bf]:
            n_cruce = r["n"]
        else:
            break
    return n_cruce


def graficar(resultados, cruce_radio, cruce_vecino):
    os.makedirs(CARPETA, exist_ok=True)
    ns = [r["n"] for r in resultados]
    fig, ejes = plt.subplots(2, 2, figsize=(13, 10))

    filas = [
        ("Busqueda por radio", "radio_bf_s", "radio_qt_s", cruce_radio),
        ("Vecino mas cercano", "vecino_bf_s", "vecino_qt_s", cruce_vecino),
    ]
    for fila, (nombre, bf, qt, n_cruce) in enumerate(filas):
        # Tiempos absolutos, log-log
        ax = ejes[fila][0]
        ax.loglog(ns, [r[bf] * 1e3 for r in resultados], "o-", label="Fuerza bruta")
        ax.loglog(ns, [r[qt] * 1e3 for r in resultados], "s-", label="Quadtree")
        ax.set_xlabel("n (puntos)")
        ax.set_ylabel("tiempo por consulta (ms)")
        ax.set_title(f"{nombre}: tiempo")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()

        # Speedup = t_fuerza_bruta / t_quadtree
        ax = ejes[fila][1]
        speedup = [r[bf] / r[qt] for r in resultados]
        ax.semilogx(ns, speedup, "o-", color="green", label="speedup")
        ax.axhline(1, color="black", linestyle="--", label="empate (1x)")
        if n_cruce is not None:
            ax.axvline(n_cruce, color="red", linestyle=":", label=f"cruce ~ {n_cruce}")
        ax.set_xlabel("n (puntos, escala log)")
        ax.set_ylabel("speedup = t_fuerza_bruta / t_quadtree")
        ax.set_title(f"{nombre}: por encima de 1x el Quadtree gana")
        ax.grid(True, alpha=0.3)
        ax.legend()

    fig.tight_layout()
    fig.savefig(os.path.join(CARPETA, "comparacion.png"), dpi=130)
    plt.close(fig)


def main():
    consultas = generar_puntos(CONSULTAS, semilla=42)

    resultados = []
    for n in TAMANOS:
        print(f"Midiendo n = {n} ...", flush=True)
        resultados.append(experimento(n, consultas))

    print()
    print(f"{'n':>7} | {'radio BF ms':>12} {'radio QT ms':>12} {'speedup':>8} "
          f"| {'vecino BF ms':>13} {'vecino QT ms':>13} {'speedup':>8}")
    for r in resultados:
        print(f"{r['n']:>7} | {r['radio_bf_s']*1e3:>12.4f} {r['radio_qt_s']*1e3:>12.4f} "
              f"{r['radio_bf_s']/r['radio_qt_s']:>8.2f} | "
              f"{r['vecino_bf_s']*1e3:>13.4f} {r['vecino_qt_s']*1e3:>13.4f} "
              f"{r['vecino_bf_s']/r['vecino_qt_s']:>8.2f}")

    cruce_radio = cruce(resultados, "radio_bf_s", "radio_qt_s")
    cruce_vecino = cruce(resultados, "vecino_bf_s", "vecino_qt_s")
    print()
    print(f"Quadtree supera a fuerza bruta en radio desde n ~ {cruce_radio}")
    print(f"Quadtree supera a fuerza bruta en vecino mas cercano desde n ~ {cruce_vecino}")

    with open("resultados.csv", "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        escritor.writeheader()
        escritor.writerows(resultados)

    graficar(resultados, cruce_radio, cruce_vecino)
    print("\nGuardado: resultados.csv y graficas/comparacion.png")


if __name__ == "__main__":
    main()