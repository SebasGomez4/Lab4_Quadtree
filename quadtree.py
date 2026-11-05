import numpy as np
import matplotlib.pyplot as plt
np.random.seed(1)
ancho = 10000
alto = 10000
puntos = 10000
x = np.random.uniform(0, ancho, puntos)
y = np.random.uniform(0, alto, puntos)
centro = (5000, 5000)
radio = 500

class Punto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Rectangulo:
    def __init__(self, x, y, ancho, alto):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto

    def contiene(self, punto):
        return (self.x <= punto.x <= self.x + self.ancho) and (self.y <= punto.y <= self.y + self.alto)

    def interseccion(self, rango):
        return not (rango.x > self.x + self.ancho or
                    rango.x + rango.ancho < self.x or
                    rango.y > self.y + self.alto or
                    rango.y + rango.alto < self.y)

class Quadtree:
    def __init__(self, limite, capacidad):
        self.limite = limite
        self.capacidad = capacidad
        self.puntos = []
        self.dividido = False

    def subdividir(self):
        x = self.limite.x
        y = self.limite.y
        ancho = self.limite.ancho / 2
        alto = self.limite.alto / 2

        sw = Rectangulo(x, y, ancho, alto)
        self.suroeste = Quadtree(sw, self.capacidad)

        se = Rectangulo(x + ancho, y, ancho, alto)
        self.sureste = Quadtree(se, self.capacidad)

        nw = Rectangulo(x, y + alto, ancho, alto)
        self.noroeste = Quadtree(nw, self.capacidad)

        ne = Rectangulo(x + ancho, y + alto, ancho, alto)
        self.noreste = Quadtree(ne, self.capacidad)

        self.dividido = True

    def insertar(self, punto):
        if not self.limite.contiene(punto):
            return False

        if len(self.puntos) < self.capacidad:
            self.puntos.append(punto)
            return True
        else:
            if not self.dividido:
                self.subdividir()

            if (self.noreste.insertar(punto) or
                self.noroeste.insertar(punto) or
                self.sureste.insertar(punto) or
                self.suroeste.insertar(punto)):
                return True
    def buscar(self, rango, encontrados):
        if not self.limite.interseccion(rango):
            return

        for punto in self.puntos:
            if rango.contiene(punto):
                encontrados.append(punto)

        if self.dividido:
            self.noreste.buscar(rango, encontrados)
            self.noroeste.buscar(rango, encontrados)
            self.sureste.buscar(rango, encontrados)
            self.suroeste.buscar(rango, encontrados)

    def vecinos_mas_cercanos(self, punto, radio, encontrados):
        rango = Rectangulo(punto.x - radio, punto.y - radio, 2 * radio, 2 * radio)

        self.buscar(rango, encontrados)
        puntos_filtrados = []
        distancias = []
        for p in encontrados:
            distancia = np.sqrt((punto.x - p.x) ** 2 + (punto.y - p.y) ** 2)
            if distancia <= radio:
                puntos_filtrados.append(p)
                distancias.append(distancia)
        if len(puntos_filtrados) == 0:
            print(f"No se encontraron vecinos dentro del radio {radio} para el punto ({punto.x}, {punto.y}).")
            return
        array_puntos = np.array(puntos_filtrados)
        array_distancias = np.array(distancias)
        indices_ordenados = np.argsort(array_distancias)
        print(f"El top 3 de vecinos más cercanos al punto ({punto.x}, {punto.y}) dentro del radio {radio} son:")
        for i, vecino in enumerate(array_puntos[indices_ordenados][:3]):
            print(f"  {i+1}. ({vecino.x}, {vecino.y})")



    def mostrar(self):
        plt.gca().add_patch(plt.Rectangle((self.limite.x, self.limite.y), 
                                           self.limite.ancho, 
                                           self.limite.alto,
                                           fill=None,
                                           edgecolor='black'))
        for punto in self.puntos:
            plt.plot(punto.x, punto.y, 'ro')
        
        if self.dividido:
            self.noreste.mostrar()
            self.noroeste.mostrar()
            self.sureste.mostrar()
            self.suroeste.mostrar()
if __name__ == "__main__":
    limite_raiz = Rectangulo(0, 0, ancho, alto)
    qt = Quadtree(limite_raiz, capacidad=16)

    for i in range(puntos):
        p = Punto(x[i], y[i])
        qt.insertar(p)

    print("¡Puntos insertados exitosamente en el Quadtree!")
    #Digite el x, y, ancho y alto del rango de búsqueda
    rango_busqueda = Rectangulo(1000, 1100, 2000, 2000)
    puntos_encontrados = []
    qt.buscar(rango_busqueda, puntos_encontrados)
    print(f"Puntos encontrados en este rango: {len(puntos_encontrados)}")

    punto_consulta = Punto(5000, 5000)
    radio_consulta = 500
    encontrados = []
    qt.vecinos_mas_cercanos(punto_consulta, radio_consulta, encontrados)

    # Dibujar el árbol y mostrar el mapa
    plt.figure(figsize=(8, 8))
    qt.mostrar()
    plt.title("Quadtree con 10,000 puntos")
    plt.show()