# ============================================================================
# SIMULADOR TECNIPLUS - ESTRUCTURAS BÁSICAS
# ============================================================================

import random

# Generar número aleatorio de distribución uniforme U(a,b)
def uniforme(min_val, max_val):
    """Genera un número aleatorio con distribución uniforme entre min_val y max_val"""
    return min_val + (max_val - min_val) * random.random()

# ============================================================================
# CLASE CLIENTE
# ============================================================================
class Cliente:
    def __init__(self, id, tiempo_llegada):
        self.id = id
        self.tiempo_llegada = tiempo_llegada
        self.tiempo_inicio_servicio = None
        self.tiempo_fin_servicio = None
        self.tecnico_asignado = None
        self.tiene_descuento = False
        self.estado = 'esperando'  # 'esperando', 'siendo_atendido', 'completado'

    def __str__(self):
        return f"Cliente {self.id} - Estado: {self.estado}"

# ============================================================================
# CLASE TECNICO
# ============================================================================
class Tecnico:
    def __init__(self, nombre, tipo, porcentaje, tiempo_min, tiempo_max, precio):
        self.nombre = nombre
        self.tipo = tipo  # 'aprendiz' o 'experimentado'
        self.porcentaje = porcentaje  # probabilidad de ser asignado
        self.tiempo_min = tiempo_min #hay que ingresarlo como parametro
        self.tiempo_max = tiempo_max #hay que ingresarlo como parametro
        self.precio = precio 
        self.estado = 'libre'  # 'libre', 'ocupado'
        self.cliente_actual = None
        self.tiempo_fin_servicio = None
        self.cola = []  # Cola propia del técnico
    
    def esta_libre(self):
        return self.estado == 'libre'

    def __str__(self):
        if self.cliente_actual:
            return f"{self.nombre} - {self.estado} (con Cliente {self.cliente_actual.id})"
        else:
            return f"{self.nombre} - {self.estado}"

# ============================================================================
# CLASE SIMULACION
# ============================================================================
class Simulacion:
    def __init__(self):
        self.tecnicos = [] #vector de todos los tecnico
        self.clientes = [] #vector de todos los clientes
        self.eventos_futuros = [] #aca se van almacenando los eventos que van a ocurrir
        self.costo_total_cupones = 0 #Acumula el costo de descuentos aplicados cuando un cliente espera más de 30 minutos.
        self.tiempo_actual = 0 #aca se va acumulando el tiempo
        #self.cola_espera = [] #los clientes que estan en cola se guardan aca pero se mezclan

    def agregar_tecnico(self, nombre, tipo, porcentaje, tiempo_min, tiempo_max, precio):
        tecnico = Tecnico(nombre, tipo, porcentaje, tiempo_min, tiempo_max, precio)
        self.tecnicos.append(tecnico)

    def agregar_cliente(self, id):
        if self.clientes:
            # Si ya hay clientes, sumamos un tiempo aleatorio entre 2 y 12 al último tiempo de llegada
            ultimo_tiempo = self.clientes[-1].tiempo_llegada
            tiempo_llegada = ultimo_tiempo + uniforme(2, 12)
        else:
            # Primer cliente llega en el tiempo 0
            tiempo_llegada = 0

        cliente = Cliente(id, tiempo_llegada)
        self.clientes.append(cliente)
        return cliente

    def asignar_tecnico(self, cliente):
        r = random.random()
        acumulado = 0
        tecnico_seleccionado = None

        for tecnico in self.tecnicos:
            acumulado += tecnico.porcentaje
            if r <= acumulado:
                tecnico_seleccionado = tecnico
                break

        cliente.tecnico_asignado = tecnico_seleccionado

        if tecnico_seleccionado.esta_libre():
            tecnico_seleccionado.estado = 'ocupado'
            tecnico_seleccionado.cliente_actual = cliente
            cliente.estado = 'siendo_atendido'
            cliente.tiempo_inicio_servicio = self.tiempo_actual

            duracion = uniforme(tecnico_seleccionado.tiempo_min, tecnico_seleccionado.tiempo_max)
            self.calcular_evento_futuro(cliente, duracion)
        else:
            cliente.estado = 'esperando'
            tecnico_seleccionado.cola.append(cliente)  # Cola propia del técnico
            print(f"[{self.tiempo_actual:.2f}] {cliente} queda en espera en cola de {tecnico_seleccionado.nombre} (técnico ocupado)")

    def registrar_evento(self, tiempo_evento, tecnico, tipo_evento):
        self.eventos_futuros.append((tiempo_evento, tecnico, tipo_evento))

    def evaluar_espera(self, cliente):
        tiempo_espera = self.tiempo_actual - cliente.tiempo_llegada
        if tiempo_espera > 30:
            cliente.tiene_descuento = True
            self.costo_total_cupones += 1500
            print(f"[{self.tiempo_actual:.2f}] Cliente {cliente.id} esperó {tiempo_espera:.2f} min. Se le asigna CUPÓN.")
        else:
            print(f"[{self.tiempo_actual:.2f}] Cliente {cliente.id} esperó {tiempo_espera:.2f} min. No se asigna cupón.")

    def procesar_eventos(self):
        self.eventos_futuros.sort()
        while self.eventos_futuros:
            tiempo_evento, tecnico, tipo_evento = self.eventos_futuros.pop(0)
            self.tiempo_actual = tiempo_evento

            if tipo_evento == "liberar_tecnico":
                cliente = tecnico.cliente_actual
                cliente.estado = 'completado'
                self.evaluar_espera(cliente)
                tecnico.estado = 'libre'
                tecnico.cliente_actual = None
                print(f"[{self.tiempo_actual:.2f}] {tecnico.nombre} queda libre")

    def calcular_evento_futuro(self, cliente, duracion_diagnostico):
        tiempo_fin = self.tiempo_actual + duracion_diagnostico
        tecnico = cliente.tecnico_asignado

        # Actualizar estados
        cliente.estado = "completado"
        cliente.tiempo_fin_servicio = tiempo_fin
        tecnico.estado = "ocupado"
        tecnico.tiempo_fin_servicio = tiempo_fin

        # Registrar evento futuro
        self.eventos_futuros.append((tiempo_fin, tecnico, "liberar_tecnico"))

        print(f"[{self.tiempo_actual:.2f}] Evento registrado: {cliente} terminará diagnóstico con {tecnico.nombre} en {duracion_diagnostico:.2f} min")
    
    def ejecutar_siguiente_evento(self):
        if not self.eventos_futuros:
            return

        self.eventos_futuros.sort(key=lambda e: e[0])
        tiempo_evento, tecnico, tipo = self.eventos_futuros.pop(0)
        self.avanzar_tiempo(tiempo_evento)

        if tipo == "liberar_tecnico":
            tecnico.estado = 'libre'
            tecnico.cliente_actual = None
            tecnico.tiempo_fin_servicio = None
            print(f"[{self.tiempo_actual:.2f}] {tecnico.nombre} quedó LIBRE")

        # Atender siguiente cliente de la cola propia del técnico
        if tecnico.cola:
            siguiente_cliente = tecnico.cola.pop(0)
            siguiente_cliente.tecnico_asignado = tecnico
            tecnico.estado = 'ocupado'
            tecnico.cliente_actual = siguiente_cliente
            siguiente_cliente.estado = 'siendo_atendido'
            siguiente_cliente.tiempo_inicio_servicio = self.tiempo_actual

            duracion = uniforme(tecnico.tiempo_min, tecnico.tiempo_max)
            self.calcular_evento_futuro(siguiente_cliente, duracion)


if __name__ == "__main__":
    sim = Simulacion()

    # Agregar técnicos
    sim.agregar_tecnico("Carlos", "experimentado", 0.5, 20, 40, 3000)
    sim.agregar_tecnico("Lucía", "aprendiz", 0.5, 30, 50, 2000)

    tiempos_llegada = []

    # Agregar 100 clientes con tiempos automáticos y asignar técnico
    for i in range(1, 101):
        cliente = sim.agregar_cliente(i)
        tiempos_llegada.append(cliente.tiempo_llegada)
        sim.tiempo_actual = cliente.tiempo_llegada
        sim.asignar_tecnico(cliente)

    print("\n--- Procesando eventos futuros ---\n")
    sim.procesar_eventos()

    print(f"\nCosto total por cupones: ${sim.costo_total_cupones}")
