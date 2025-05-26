from flask import Flask, render_template, request, url_for
import matplotlib
matplotlib.use('Agg')  # Evita errores de tkinter
import matplotlib.pyplot as plt
import networkx as nx
import os
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    ruta = []
    costo = None
    error = None
    img_filename = None

    if request.method == "POST":
        inicio = request.form["inicio"].upper()
        fin = request.form["fin"].upper()

        G = nx.Graph()
        G.add_weighted_edges_from([
            ('A', 'B', 2), ('A', 'C', 4), ('B', 'C', 1), ('B', 'D', 7),
            ('C', 'D', 3), ('C', 'E', 5), ('D', 'E', 2), ('D', 'Z', 6),
            ('E', 'Z', 1)
        ])

        if inicio not in G.nodes or fin not in G.nodes:
            error = "Nodo inválido. Usa A, B, C, D, E, Z."
        elif inicio == fin:
            error = "El nodo de inicio y destino no pueden ser iguales."
        else:
            pos = {'A': (0, 2), 'B': (1, 2), 'C': (0.5, 1),
                   'D': (2, 1.5), 'E': (1.2, 0), 'Z': (3, 1)}

            nodos = list(G.nodes)
            dist = {n: float('inf') for n in nodos}
            prev = {n: None for n in nodos}
            dist[inicio] = 0
            visitados = set()

            while len(visitados) < len(nodos):
                no_visitados = [n for n in nodos if n not in visitados]
                actual = min(no_visitados, key=lambda n: dist[n])
                visitados.add(actual)

                for vecino in G[actual]:
                    peso = G[actual][vecino]['weight']
                    nueva = dist[actual] + peso
                    if nueva < dist[vecino]:
                        dist[vecino] = nueva
                        prev[vecino] = actual

            n = fin
            while n:
                ruta.insert(0, n)
                n = prev[n]

            costo = dist[fin]

            colores = []
            for u, v in G.edges():
                if u in ruta and v in ruta and abs(ruta.index(u) - ruta.index(v)) == 1:
                    colores.append("red")
                else:
                    colores.append("gray")

            plt.figure(figsize=(6, 5))
            nx.draw(G, pos, with_labels=True, node_color='lightblue',
                    node_size=800, edge_color=colores, width=2, font_weight='bold')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
            plt.title(" → ".join(ruta) + f" | Costo: {costo}")
            plt.axis('off')
            plt.tight_layout()

            # Guardar imagen en carpeta static con ruta absoluta
            static_dir = os.path.join(app.root_path, "static")
            os.makedirs(static_dir, exist_ok=True)
            img_filename = f"grafo_{uuid.uuid4().hex}.png"
            img_path = os.path.join(static_dir, img_filename)

            try:
                plt.savefig(img_path)
                print(f"[✔] Imagen guardada: {img_path}")
            except Exception as e:
                print(f"[✘] Error al guardar la imagen: {e}")
            finally:
                plt.close()

    return render_template("index.html", ruta=ruta, costo=costo, error=error, img_filename=img_filename)

if __name__ == "__main__":
    app.run(debug=True)
