import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import requests
from io import StringIO

dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
base_url = "https://rawcdn.githack.com/ManuUBA/Horarios-zero/main/data/"
labos = list(range(1103, 1113))

def hora_a_decimal(hora):
    h, m = map(int, hora.split(':'))
    return h + m/60

def decimal_a_hora(dec):
    h = int(dec)
    m = int((dec - h) * 60)
    return f"{h:02d}:{m:02d}"

def obtener_horarios(url_csv):
    respuesta = requests.get(url_csv)
    archivo_csv = StringIO(respuesta.text)
    filas = list(csv.reader(archivo_csv, delimiter=','))

    fila_header = None
    for i, fila in enumerate(filas):
        fila_str = [f.strip().lower() for f in fila]
        if any("aula" in celda for celda in fila_str):
            fila_header = i
            break

    if fila_header is None:
        raise ValueError(f"No se encontró encabezado válido en {url_csv}")

    header = [h.strip() for h in filas[fila_header]]
    datos = filas[fila_header + 1:]

    header_lower = [h.lower() for h in header]

    def col(nombre):
        for i, h in enumerate(header_lower):
            if nombre.lower() in h:
                return i
        raise ValueError(f"No se encontró la columna '{nombre}' en {header}")

    c_aula   = col("aula")
    c_desde  = col("inicio")
    c_hasta  = col("fin")
    c_pab    = col("pab")

    filas_labo = []
    for f in datos:
        if len(f) <= max(c_aula, c_desde, c_hasta, c_pab):
            continue
        try:
            if f[c_pab].strip() == "0" and int(f[c_aula]) in labos:
                filas_labo.append(f)
        except ValueError:
            continue

    horarios_labo = []
    for aula in labos:
        tandas = [[f[c_desde], f[c_hasta]] for f in filas_labo if int(f[c_aula]) == aula]
        horarios_labo.append(tandas)

    return horarios_labo

fig, axes = plt.subplots(3, 2, figsize=(18, 12))
axes = axes.flatten()

for idx, dia in enumerate(dias):
    ax = axes[idx]
    horarios_labo = obtener_horarios(f"{base_url}{dia}.csv")

    ax.set_xlim(8, 23)
    ax.set_ylim(0, len(labos))
    ax.set_yticks([i + 0.5 for i in range(len(labos))])
    ax.set_yticklabels([str(l) for l in labos])
    ax.set_xlabel("Hora")
    ax.set_ylabel("Laboratorio")

    # Líneas horizontales que delimitan cada laboratorio
    for j in range(len(labos) + 1):
        ax.axhline(j, color="black", linewidth=0.8)

    # Dibujar bloques
    for jdx, aula in enumerate(horarios_labo):
        ax.add_patch(patches.Rectangle((8, jdx), 15, 1, facecolor='green', alpha=0.3))
        for inicio_str, fin_str in aula:
            inicio, fin = hora_a_decimal(inicio_str), hora_a_decimal(fin_str)
            ax.add_patch(patches.Rectangle((inicio, jdx), fin-inicio, 1, facecolor='red'))

    if idx == 0:
        ax.legend([patches.Patch(color='red'),
                   patches.Patch(color='green', alpha=0.3)],
                  ['Ocupado', 'Libre'], loc='upper right')

    ax.set_title(dia)

marcas = [8 + 0.5*i for i in range((23-8)*2 + 1)]
for ax in axes:
    ax.set_xticks(marcas)
    ax.set_xticklabels([decimal_a_hora(m) for m in marcas], rotation=45)
    ax.grid(True, axis='x', alpha=1, color=(0, 0, 0))

plt.suptitle("Grilla de ocupación de laboratorios - Semana completa", fontsize=16)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("grafico.png")
plt.show()
plt.close()
