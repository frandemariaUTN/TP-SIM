import random
import csv
random.seed(3000)

# ------------------------------
# Función auxiliar para generar valores uniformes
#   los valores los vamos a ingresar por parametros
# ------------------------------
def uniforme(min_val, max_val):
    return min_val + (max_val - min_val) * random.random()

# ------------------------------
# Clase Cliente: representa a cada persona que llega al centro
# ------------------------------
class Cliente:
    def __init__(self, id_cliente, tiempo_llegada):
        self.id = id_cliente
        self.tiempo_llegada = tiempo_llegada  # Cuándo llega el cliente
        self.tiempo_inicio = None             # Cuándo empieza a ser atendido
        self.tiempo_fin = None                # Cuándo termina de ser atendido
        self.tecnico_asignado = None          # Técnico que lo atendió
        self.descuento = False
        self.estado = "esperando"             # 'esperando', 'siendo_atendido', 'completado'
        self.espera = 0              # Tiempo total acumulado en espera
        self.tiempo_atencion = None # Para marcar cuándo entra a la cola (y medir espera)

    def obtener_tiempo_espera(self): # para poder mostrar el tiempo que espera el cliente
        if self.tiempo_inicio is not None:
            return round (self.tiempo_inicio - self.tiempo_llegada, 2)
        return "-"

    def obtener_tiempo_atencion(self): # para poder obtener el tiempo que lo atienden
        if self.tiempo_inicio is not None and self.tiempo_fin is not None:
            return round (self.tiempo_fin - self.tiempo_inicio, 2)
        return "-"

# ------------------------------
# Clase Técnico: puede ser aprendiz o experimentado
# ------------------------------
class Tecnico:
    def __init__(self, nombre, tipo, tiempo_min, tiempo_max, probabilidad):
        self.nombre = nombre
        self.tipo = tipo  # 'aprendiz' o 'experimentado'
        self.tiempo_min = tiempo_min # tiempo minimo requerido para atender
        self.tiempo_max = tiempo_max # tiempo maximo requerido para atender
        self.probabilidad = probabilidad
        self.estado = "libre"
        self.cliente_actual = None
        self.cola = []

# ------------------------------
# Clase principal que gestiona la simulación completa
# ------------------------------
class Simulacion:
    def __init__(self, tiempo_max, desde_iteracion, cantidad_iteraciones, llegada_min, llegada_max):
        self.tiempo_actual = 0 # inicializa el tiempo y a partir de aca se va acumulando
        self.eventos = [] # vamos a almacenar todos los eventos (llegada_cliente, fin_diagnostico_tecnico_a, fin_diagnostico_tecnico_b, fin_diagnostico_aprendiz)
        self.tecnicos = [] # aqui se almacenan los 3 tecnicos
        self.clientes = [] # aqui se almacenan los clientes que llegan
        self.proximo_id_cliente = 1 # contador incremental de lo ids de los clientes, estos van incrementando en 1 a medida que se van creando
        self.costo_cupones = 0 # costo del cupon en base a el tiempo del cliente esperando 
        self.recaudacion_total = 0 # este acumulador responda a la 1er pregunta
        self.max_en_colas = 0 # este acumulador responde a la 2da pregunta, que es para luego determiar la cantidad minima de sillas que necesitamos

        self.tiempo_max = tiempo_max # el tiempo maximo permitido para atender clientes
        self.desde_iteracion = desde_iteracion # desde donde vamos a arrancar a iterar cuando probemos la simulacion
        self.cantidad_iteraciones = cantidad_iteraciones # cantidad de iteraciones con las que vamos a trabajar (cantidad de simulaciones)
        self.llegada_min = llegada_min # vendria a ser el tiempo de llegada minimo determinado para el evento donde llega un cliente
        self.llegada_max = llegada_max # vendria a ser el tiempo de llegada maximo determinado para el evento donde llega un cliente

        self.ultimo_cliente = None  # Mi ultimo cliente en evento
        
    def agregar_tecnico(self, nombre, tipo, tiempo_min, tiempo_max, probabilidad):
        self.tecnicos.append(Tecnico(nombre, tipo, tiempo_min, tiempo_max, probabilidad)) #agregamos cada tecnico al vector

    def generar_llegada_cliente(self):
        # Calcula el próximo tiempo de llegada en base a la última llegada
        ultimo_tiempo = self.clientes[-1].tiempo_llegada if self.clientes else 0
        tiempo_llegada = ultimo_tiempo + uniforme(self.llegada_min, self.llegada_max)

        if tiempo_llegada > self.tiempo_max:
            return

        cliente = Cliente(self.proximo_id_cliente, tiempo_llegada)
        self.cliente = cliente  # ← para que esté disponible en el registro de resultados
        self.proximo_id_cliente += 1
        self.clientes.append(cliente)
        self.eventos.append((tiempo_llegada, "llegada", cliente))

    def seleccionar_tecnico(self):
        # Asigna técnico basado en probabilidad
        r = random.random()
        acumulado = 0
        for tecnico in self.tecnicos:
            acumulado += tecnico.probabilidad 
            if r <= acumulado: # mientras el acumulado de la probabilidad del tecnico sea menor al random, sigo iterando hasta que lo supere
                return tecnico, r # me devuelve el tecnico con probabilidad mayor que el random
        return self.tecnicos[-1], r # me devuelve el ultimo tecnico

    def procesar_evento(self, evento):
        tiempo, tipo, obj = evento # evento es una tupla que contiene 3 elementos:
                                    # - tiempo → Representa el instante en que ocurre el evento dentro de la simulación.
                                    # - tipo → Es una cadena de texto que indica el tipo de evento ("llegada", "fin_atencion").
                                    # - obj → Es el objeto asociado al evento, que puede ser un Cliente o un Técnico.
        self.tiempo_actual = tiempo # se actualiza el RELOJ
        
        cliente = obj # el objeto del evento es el cliente en este caso
        acum_espera = 0

        fila = {
            'iteracion': len(self.resultados),
            'reloj': round(self.tiempo_actual, 2),
            'evento': tipo.capitalize(), # se pone el nombre comenzando en Mayuscula
            'rnd_llegada': '-',
            'prox_llegada': '-',
            'rnd_asignacion': '-',
            'tecnico_asignado': '-',
            'rnd_diagnostico': '-',
            'tiempo_diagnostico': '-',
            'hora_fin_diagnostico': '-',
            'importe': '-',
            'espera': '-',
            'tecnicos': [t.estado for t in self.tecnicos], # muestra los tecnicos con su estados (ocupado o libre)
            'cola': [len(t.cola) for t in self.tecnicos], # muestra la cantidad que tienen el tecnico en cola
            'id_cliente': cliente.id if cliente else '---',
            'estado_cliente': cliente.estado if cliente else '---',
            'espera_acumulada': cliente.obtener_tiempo_espera() if cliente else '---',
            'tiempo_atencion': acum_espera if cliente else '---',
            'cupones': self.costo_cupones
        }
        

        if tipo == "llegada":
            tecnico, rnd_asignacion = self.seleccionar_tecnico() # al llamar a la funcion nos devuelve el tecnico asignado
            cliente.tecnico_asignado = tecnico # aqui se lo asignamos a ese cliente

            if tecnico.estado == "libre":
                tecnico.estado = "ocupado" # actualizamos el estado del tecnico a ocupado
                tecnico.cliente_actual = cliente
                cliente.estado = "atendiendo" # actualizamos el estado del cliente
                cliente.tiempo_inicio = self.tiempo_actual # establecemos el tiempo de inicio del cliente en base al RELOJ
                duracion = uniforme(tecnico.tiempo_min, tecnico.tiempo_max) # creamos la variable que contiene la DURACION del diagnostico
                cliente.tiempo_fin = self.tiempo_actual + duracion # calculamos el tiempo final del cliente en base al RELOJ y a la DURACION
                self.eventos.append((cliente.tiempo_fin, "fin_atencion", cliente)) # registrando el momento en que finalizará el diagnóstico del cliente
                # se agrega un nuevo evento a la lista de eventos futuros.
                fila['rnd_diagnostico'] = round((duracion - tecnico.tiempo_min) / (tecnico.tiempo_max - tecnico.tiempo_min), 4) # creamos el random a traves de la duracion
                fila['tiempo_diagnostico'] = round(duracion, 2)
                fila['hora_fin_diagnostico'] = round(cliente.tiempo_fin, 2)
            else:
                tecnico.cola.append(cliente)

            fila['rnd_llegada'] = round(random.random(), 4)
            fila['rnd_asignacion'] = round(rnd_asignacion, 4)
            fila['tecnico_asignado'] = tecnico.nombre
            fila['importe'] = 1800 if tecnico.tipo == "aprendiz" else 3500 # el importe depende del tipo
            fila['espera'] = 0.0 # una vez que esta siendo atendido la espera es 0.0

            prox_llegadas = [e for e in self.eventos if e[1] == "llegada"]
            fila['prox_llegada'] = round(prox_llegadas[0][0], 2) if prox_llegadas else '-'

        elif tipo == "fin_atencion":
            cliente = obj # este vendria a ser el objeto del cliente que esta esperando
            cliente.estado = "finalizado"
            espera = cliente.tiempo_inicio - cliente.tiempo_llegada # aqui es donde calculamos el tiempo en que inicio el diagnostica para el cliente - el tiempo en el que fue su llegada
            # determinamos si hay que cobrarle o no descuento si ese tiempo es mayor a 30 minutos

            if espera > 30: # si es mayo a 30min
                cliente.descuento = True
                self.costo_cupones += 1500

            importe = 1800 if cliente.tecnico_asignado.tipo == "aprendiz" else 3500
            self.recaudacion_total += importe

            fila['tecnico_asignado'] = cliente.tecnico_asignado.nombre 
            fila['hora_fin_diagnostico'] = round(cliente.tiempo_fin, 2) # registramos la hora que finalizo el diagnostico
            fila['importe'] = importe # este es el importe que se le va a cobrar al cliente sin aplicar descuentos
            fila['espera'] = round(espera, 2) # se muestra el tiempo que calculamos que espero
            self.ultimo_cliente = cliente 
            acum_espera += cliente.obtener_tiempo_atencion() 

            tecnico = cliente.tecnico_asignado 
            if tecnico.cola: # nos fijamos si el tecnico tiene gente en cola
                siguiente = tecnico.cola.pop(0) # sacamos el siguiente cliente de la cola para atenderlo
                siguiente.estado = "atendiendo" # actualizamos el estado
                siguiente.tiempo_inicio = self.tiempo_actual # establecemos su tiempo de inicio de atencion a traves del RELOJ
                duracion = uniforme(tecnico.tiempo_min, tecnico.tiempo_max) # calculamos la duracion a partir de la distribucion
                siguiente.tiempo_fin = self.tiempo_actual + duracion # establecemos el tiempo final de la atencion para saber cuando se va a liberar el tecnico
                tecnico.cliente_actual = siguiente # actualizamos el nuevo cliente para el tecnico
                self.eventos.append((siguiente.tiempo_fin, "fin_atencion", siguiente)) # registrando el momento en que finalizará el diagnóstico del cliente
                # se agrega un nuevo evento a la lista de eventos futuros.

            else:
                tecnico.estado = "libre" # si no hay nadie en cola el tecnico vuelve a estar libre
                tecnico.cliente_actual = None # seteamos el cliente

        total_en_colas = sum(len(t.cola) for t in self.tecnicos) # obtenemos el total de clientes que tiene cada tecnico en la cola
        if total_en_colas > self.max_en_colas: # preguntamos si ese total es mayor al maximo que hemos tenido, esto lo vamos a usar para determinar si hay que agregar mas sillas
            self.max_en_colas = total_en_colas # establecemos el nuevo maximo

        cliente = self.ultimo_cliente
        self.resultados.append(fila)

        if tipo == "llegada": # volvemos a preguntar si es de tipo llegada el evento para seguir generando nuevas llegadas de clientes 
            self.generar_llegada_cliente()

    def correr(self):
        self.resultados = [] # se crea la lista vacia donde vamos a ir almacenando los resultados de cada simulacion, es decir todos los datos almacenados en la variable fila

        # Agregar fila de inicio
        cliente = self.ultimo_cliente
        self.resultados.append({
            'iteracion': 0,
            'reloj': 0,
            'evento': '',
            'rnd_llegada': '',
            'prox_llegada': '',
            'rnd_asignacion': '',
            'tecnico_asignado': '',
            'rnd_diagnostico': '',
            'tiempo_diagnostico': '',
            'hora_fin_diagnostico': '',
            'importe': '',
            'espera': '',
            'tecnicos': [''] * 3,
            'cola': [''] * 3,
            'id_cliente': cliente.id if cliente else '---',
            'estado_cliente': cliente.estado if cliente else '---',
            'espera_acumulada': cliente.obtener_tiempo_espera() if cliente else '---',
            'tiempo_atencion': cliente.obtener_tiempo_atencion() if cliente else '---',
            'cupones': self.costo_cupones
        })


        self.generar_llegada_cliente() # activamos la secuencia de llegadas de los clientes

        while self.eventos and self.tiempo_actual <= self.tiempo_max and len(self.resultados) < self.cantidad_iteraciones: 
            # mientras haya eventos, el tiempo actual sea menor al tiempo maximo y la cantidad de resultados siga siendo menor a la cantidad de iteraciones solicitadas, seguimos iterando
            self.eventos.sort() # ordenamos los eventos
            evento = self.eventos.pop(0) # limpiamos el evento que vamos a procesar de la lista
            self.procesar_evento(evento) # llamamos a la funcion para procesar dicho evento

        # Agregar fila de resumen final
        cliente = self.ultimo_cliente
        self.resultados.append({
            'iteracion': len(self.resultados),
            'reloj': round(self.tiempo_actual, 2),
            'evento': 'Fin simulacion',
            'rnd_llegada': '-',
            'prox_llegada': '-',
            'rnd_asignacion': '-',
            'tecnico_asignado': '-',
            'rnd_diagnostico': '-',
            'tiempo_diagnostico': '-',
            'hora_fin_diagnostico': '-',
            'importe': '-',
            'espera': '-',
            'tecnicos': [t.estado for t in self.tecnicos],
            'cola': [len(t.cola) for t in self.tecnicos],
            'id_cliente': cliente.id if cliente else '---',
            'estado_cliente': cliente.estado if cliente else '---',
            'espera_acumulada': cliente.obtener_tiempo_espera() if cliente else '---',
            'tiempo_atencion': cliente.obtener_tiempo_atencion() if cliente else '---',
            'cupones': self.costo_cupones
        })



        # Mostrar métricas finales
        dias_simulados = len(self.resultados)
        promedio_diario = round (self.recaudacion_total / dias_simulados, 2)
        # aca obtenemos la respuesta a la pregunta 1 sobre la recaudación promedio diaria del centro técnico

        print(f"\n--- RESULTADOS FINALES ---")
        print(f"Recaudación total: ${self.recaudacion_total}")
        print(f"Recaudación promedio diaria: ${promedio_diario}")
        print(f"Total de dinero en cupones entregados: ${self.costo_cupones}")
        print(f"Cantidad mínima de sillas necesarias: {self.max_en_colas}")

        # Guardar vector de estado en CSV para que los resultados queden almacenados
        with open("vector_estado.csv", "w", newline="", encoding="utf-8") as f:
            # - Abre (o crea) el archivo vector_estado.csv en modo escritura ("w").
            # - Usa newline="" para evitar líneas vacías innecesarias en el archivo.
            # - Establece utf-8 como codificación, asegurando compatibilidad con caracteres especiales
            writer = csv.DictWriter(f, fieldnames=self.resultados[0].keys()) # - Crea un escritor CSV que estructurará los datos en columnas, usando los nombres de campo (keys()) de los diccionarios en self.resultados.
            writer.writeheader() # - Escribe la primera línea del archivo con los nombres de las columnas (como "evento", "reloj", "espera", etc.).
            writer.writerows(self.resultados) # - Escribe todas las filas de la lista self.resultados, cada una representando un estado del sistema en algún instante de la simulación.

# Realizamos una prueba manual
if __name__ == "__main__":
    sim = Simulacion(tiempo_max=480, desde_iteracion=0, cantidad_iteraciones=200, llegada_min=2, llegada_max=12)
    sim.agregar_tecnico("Aprendiz", "aprendiz", 20, 30, 0.15)
    sim.agregar_tecnico("Técnico A", "experimentado", 11, 13, 0.45)
    sim.agregar_tecnico("Técnico B", "experimentado", 12, 18, 0.40)
    sim.correr()
