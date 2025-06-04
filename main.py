# ============================================================================
# SIMULADOR TECNIPLUS - ESTRUCTURAS BÁSICAS
# ============================================================================

import random

# Generar número aleatorio de distribución uniforme U(a,b)
def uniforme(min_val, max_val):
    """Genera un número aleatorio con distribución uniforme entre min_val y max_val"""
    r = random.random()
    return min_val + (max_val - min_val) * r

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
        self.tiempo_min = tiempo_min
        self.tiempo_max = tiempo_max
        self.precio = precio
        self.estado = 'libre'  # 'libre', 'ocupado'
        self.cliente_actual = None
        self.tiempo_fin_servicio = None
    
    def esta_libre(self):
        return self.estado == 'libre'
    
    def __str__(self):
        if self.cliente_actual:
            return f"{self.nombre} - {self.estado} (con Cliente {self.cliente_actual.id})"
        else:
            return f"{self.nombre} - {self.estado}"
# ============================================================================
# CLASE SIMULACION la cual contendra todos los metodos de mi simulacion
# ============================================================================
class Simulacion:
    def __init__(self):
        self.tecnicos = []
        self.clientes = []
        self.eventos_futuros = []
        self.costo_total_cupones = 0
        self.tiempo_actual = 0

    def agregar_tecnico(self, nombre, tipo, porcentaje, tiempo_min, tiempo_max, precio):
        tecnico = Tecnico(nombre, tipo, porcentaje, tiempo_min, tiempo_max, precio)
        self.tecnicos.append(tecnico)

    def agregar_cliente(self, id, tiempo_llegada):
        cliente = Cliente(id, tiempo_llegada)
        self.clientes.append(cliente)
        return cliente

# 1er metodo
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
            cliente.tiempo_fin_servicio = self.tiempo_actual + duracion
            tecnico_seleccionado.tiempo_fin_servicio = cliente.tiempo_fin_servicio

            self.registrar_evento(cliente.tiempo_fin_servicio, tecnico_seleccionado, "liberar_tecnico")

            print(f"[{self.tiempo_actual:.2f}] {cliente} asignado a {tecnico_seleccionado.nombre} durante {duracion:.2f} min")
        else:
            cliente.estado = 'esperando'
            print(f"[{self.tiempo_actual:.2f}] {cliente} queda en espera (técnico ocupado)")

# 2do metodo 
    def registrar_evento(self, tiempo_evento, tecnico, tipo_evento):
        self.eventos_futuros.append((tiempo_evento, tecnico, tipo_evento))

# 3er metodo
    def evaluar_espera(self, cliente):
        tiempo_espera = self.tiempo_actual - cliente.tiempo_llegada
        if tiempo_espera > 30:
            cliente.tiene_descuento = True
            self.costo_total_cupones += 1500
            print(f"[{self.tiempo_actual:.2f}] Cliente {cliente.id} esperó {tiempo_espera:.2f} min. Se le asigna CUPÓN.")
        else:
            print(f"[{self.tiempo_actual:.2f}] Cliente {cliente.id} esperó {tiempo_espera:.2f} min. No se asigna cupón.")

# 4to metodo
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

# PRUEBA
sim = Simulacion()

cliente = Cliente(1, tiempo_llegada=5)
tecnico = Tecnico("Técnico A", "experimentado", 1.0, 11, 13, 3500)
cliente.tecnico_asignado = tecnico

# Asignamos el técnico como si estuviera siendo atendido ahora
tecnico.estado = "ocupado"
tecnico.cliente_actual = cliente

# Simulamos duración aleatoria
duracion = uniforme(tecnico.tiempo_min, tecnico.tiempo_max)

# Calculamos el evento (automáticamente usa tiempo_actual = 0)
sim.calcular_evento_futuro(cliente, duracion)

