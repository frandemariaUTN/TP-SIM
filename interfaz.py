import tkinter as tk
from tkinter import ttk, messagebox
from simulador import Simulacion  # Importamos la clase desde el archivo final

# ------------------------------
# Función que ejecuta la simulación al presionar el botón
# ------------------------------
def correr_simulacion():
    try:
        # Leemos todos los valores ingresados en la interfaz
        tiempo_max = int(entry_tiempo_max.get())
        desde_iter = int(entry_desde_iter.get())
        cant_iter = int(entry_cant_iter.get())
        llegada_min = int(entry_llegada_min.get())
        llegada_max = int(entry_llegada_max.get())
        diagnostico_aprendiz_min = int(entry_fin_aprendiz_min.get())
        diagnostico_aprendiz_max = int(entry_fin_aprendiz_max.get())
        diagnostico_tecnico_a_min = int(entry_fin_tecnico_a_min.get())
        diagnostico_tecnico_a_max = int(entry_fin_tecnico_a_max.get())
        diagnostico_tecnico_b_min = int(entry_fin_tecnico_b_min.get())
        diagnostico_tecnico_b_max = int(entry_fin_tecnico_b_max.get())

        if cant_iter > 100000:
            raise ValueError("La cantidad máxima de iteraciones permitidas es 100000.")

        # Creamos la instancia de simulación
        sim = Simulacion(tiempo_max, desde_iter, cant_iter, llegada_min, llegada_max)
        sim.agregar_tecnico("Aprendiz", "aprendiz", diagnostico_aprendiz_min, diagnostico_aprendiz_max, 0.15)
        sim.agregar_tecnico("Técnico A", "experimentado", diagnostico_tecnico_a_min, diagnostico_tecnico_a_max, 0.45)
        sim.agregar_tecnico("Técnico B", "experimentado", diagnostico_tecnico_b_min, diagnostico_tecnico_b_max, 0.40)

        # Borramos resultados anteriores
        tree.delete(*tree.get_children())

        # Corremos la simulación (silenciamos print temporalmente si se desea)
        sim.correr()

        # Mostramos resultados en la tabla
        for fila in sim.resultados:
            if desde_iter <= fila['iteracion'] < desde_iter + cant_iter or fila['evento'] == 'Fin simulacion':
                tree.insert('', 'end', values=(
                    fila['iteracion'],
                    fila['reloj'],
                    fila['evento'],
                    fila.get('rnd_llegada', '-'),
                    fila.get('prox_llegada', '-'),
                    fila.get('rnd_asignacion', '-'),
                    fila.get('tecnico_asignado', '-'),
                    fila.get('rnd_diagnostico', '-'),
                    fila.get('tiempo_diagnostico', '-'),
                    fila.get('hora_fin_diagnostico', '-'),
                    fila.get('importe', '-'),
                    fila.get('espera', '-'),
                    fila['tecnicos'][0],
                    fila['tecnicos'][1],
                    fila['tecnicos'][2],
                    fila['cola'][0] if len(fila['cola']) > 0 else '-',
                    fila['cola'][1] if len(fila['cola']) > 1 else '-',
                    fila['cola'][2] if len(fila['cola']) > 2 else '-',
                    fila.get('id_cliente', '-'),
                    fila.get('estado_cliente', '-'),
                    fila.get('espera_acumulada', '-'),
                    fila['cupones'],
                ))

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ------------------------------
# INTERFAZ GRÁFICA
# ------------------------------
root = tk.Tk()
root.title("Simulador Servicio Técnico Exprés")
root.geometry("1300x600")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# TAB CONFIGURACIÓN
tab_config = ttk.Frame(notebook)
notebook.add(tab_config, text="Configuración")

frame_superior = ttk.Frame(tab_config)
frame_superior.pack(side="top", fill="x", padx=10, pady=10)

frame_izq = ttk.LabelFrame(frame_superior, text="Parámetros Generales", padding=10)
frame_izq.pack(side="left", padx=10, pady=10, fill="y")

ttk.Label(frame_izq, text="Tiempo Máximo:").grid(row=0, column=0, sticky="e", pady=2)
entry_tiempo_max = ttk.Entry(frame_izq, width=10)
entry_tiempo_max.grid(row=0, column=1, pady=2)
entry_tiempo_max.insert(0, "480")

ttk.Label(frame_izq, text="Desde Iteración:").grid(row=1, column=0, sticky="e", pady=2)
entry_desde_iter = ttk.Entry(frame_izq, width=10)
entry_desde_iter.grid(row=1, column=1, pady=2)
entry_desde_iter.insert(0, "0")

ttk.Label(frame_izq, text="Cantidad Iteraciones:").grid(row=2, column=0, sticky="e", pady=2)
entry_cant_iter = ttk.Entry(frame_izq, width=10)
entry_cant_iter.grid(row=2, column=1, pady=2)
entry_cant_iter.insert(0, "50")

# Parámetros de eventos
frame_der = ttk.LabelFrame(frame_superior, text="Eventos", padding=10)
frame_der.pack(side="left", padx=10, pady=10, fill="both", expand=True)

# Llegada cliente
ttk.Label(frame_der, text="Llegada cliente").grid(row=0, column=0, padx=5, pady=5)
ttk.Label(frame_der, text="a:").grid(row=0, column=1)
entry_llegada_min = ttk.Entry(frame_der, width=5)
entry_llegada_min.grid(row=0, column=2)
entry_llegada_min.insert(0, "2")

ttk.Label(frame_der, text="b:").grid(row=0, column=3)
entry_llegada_max = ttk.Entry(frame_der, width=5)
entry_llegada_max.grid(row=0, column=4)
entry_llegada_max.insert(0, "12")

# Aprendiz
ttk.Label(frame_der, text="Fin At. Aprendiz").grid(row=1, column=0, padx=5, pady=5)
ttk.Label(frame_der, text="a:").grid(row=1, column=1)
entry_fin_aprendiz_min = ttk.Entry(frame_der, width=5)
entry_fin_aprendiz_min.grid(row=1, column=2)
entry_fin_aprendiz_min.insert(0, "20")

ttk.Label(frame_der, text="b:").grid(row=1, column=3)
entry_fin_aprendiz_max = ttk.Entry(frame_der, width=5)
entry_fin_aprendiz_max.grid(row=1, column=4)
entry_fin_aprendiz_max.insert(0, "30")

# Técnico A
ttk.Label(frame_der, text="Fin At. Técnico A").grid(row=2, column=0, padx=5, pady=5)
ttk.Label(frame_der, text="a:").grid(row=2, column=1)
entry_fin_tecnico_a_min = ttk.Entry(frame_der, width=5)
entry_fin_tecnico_a_min.grid(row=2, column=2)
entry_fin_tecnico_a_min.insert(0, "11")

ttk.Label(frame_der, text="b:").grid(row=2, column=3)
entry_fin_tecnico_a_max = ttk.Entry(frame_der, width=5)
entry_fin_tecnico_a_max.grid(row=2, column=4)
entry_fin_tecnico_a_max.insert(0, "13")

# Técnico B
ttk.Label(frame_der, text="Fin At. Técnico B").grid(row=3, column=0, padx=5, pady=5)
ttk.Label(frame_der, text="a:").grid(row=3, column=1)
entry_fin_tecnico_b_min = ttk.Entry(frame_der, width=5)
entry_fin_tecnico_b_min.grid(row=3, column=2)
entry_fin_tecnico_b_min.insert(0, "12")

ttk.Label(frame_der, text="b:").grid(row=3, column=3)
entry_fin_tecnico_b_max = ttk.Entry(frame_der, width=5)
entry_fin_tecnico_b_max.grid(row=3, column=4)
entry_fin_tecnico_b_max.insert(0, "18")

# Botón ejecutar
btn_simular = ttk.Button(tab_config, text="▶ Ejecutar Simulación", command=correr_simulacion)
btn_simular.pack(pady=10)

# TAB RESULTADOS
tab_resultados = ttk.Frame(notebook)
notebook.add(tab_resultados, text="Resultados")

frame_tabla = ttk.Frame(tab_resultados, padding=10)
frame_tabla.pack(fill="both", expand=True)

columnas = [
    "Iteración", "Reloj", "Evento",
    "RND Llegada", "Próxima Llegada",
    "RND Asignación", "Técnico Asignado", "RND Diagnóstico", "Tiempo Diagnóstico",
    "Hora Fin Diagnóstico", "Importe", "Espera",
    "Estado Téc. A", "Estado Téc. B", "Estado Aprendiz",
    "Cola A", "Cola B", "Cola Aprendiz",
    "ID Cliente", "Estado Cliente", "Espera Acum.",
    "Total Cupones"]


tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
for col in columnas:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=100)

scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

frame_tabla.columnconfigure(0, weight=1)
frame_tabla.rowconfigure(0, weight=1)

root.mainloop()
