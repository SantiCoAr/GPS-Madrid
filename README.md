# Madrid Graph-based GPS

Graph-based mini-GPS for Madrid built from scratch: it loads the official street gazetteer, parses addresses into coordinates, builds and simplifies the road network from OpenStreetMap, and computes optimal routes using a custom **Dijkstra** algorithm with three cost models (distance, travel time, and expected time with traffic lights). It also generates turn-by-turn instructions and plots the route efficiently using OSMnx.

---

## 🚀 Features

- **Address lookup:** parses street names and numbers, converts DMS → decimal degrees, and returns accurate coordinates.
- **Road graph from OSM:** downloads and simplifies a directed **MultiDiGraph** for realistic routing (multiple parallel edges, one-way streets).
- **Custom graph algorithms:** implementation of `Dijkstra`, `Prim`, and `Kruskal` in `grafo_pesado.py`.
- **Three cost modes:**
  1) **Shortest distance** (meters)  
  2) **Fastest route** (using `maxspeed` by road type)  
  3) **Expected time** (adds a probability-based traffic-light delay)
- **Turn-by-turn instructions:** detects street changes and calculates left/straight/right turns by segment angles.
- **Fast plotting:** uses OSMnx `plot_graph_route` with a bbox subgraph around the path for smooth visualization.

---

## 📂 Project Structure

~~~text
gps.py             # CLI & integration: weights, nearest node, instructions, plotting
callejero.py       # Street gazetteer loader and preprocessing (DMS→decimal)
grafo_pesado.py    # Graph algorithms (Dijkstra, Prim, Kruskal)
test_grafo.py      # Toy tests for correctness
requirements_gps.txt
README.md
<<<<<<< HEAD
~~~

Optional folders:

~~~text
docs/              # Assignment brief or report (PDF)
notebooks/         # Jupyter notebooks for exploration
data/              # Optional sample data (e.g., direcciones_sample.csv)
~~~
=======
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb

---

## ⚙️ Installation

### Option A — Conda (recommended on Windows)

~~~bash
conda create -n gps-madrid -c conda-forge python=3.11 osmnx=1.9.3 networkx=3.3 matplotlib=3.8.2
conda activate gps-madrid
<<<<<<< HEAD
~~~

### Option B — pip (Linux/Mac; on Windows prefer Conda)

~~~bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements_gps.txt
~~~

> **Note:** The code assumes a **directed MultiDiGraph** (multiple parallel edges per node pair). Keep `networkx==3.3` and `osmnx==1.9.3` for compatibility.

---

## ▶️ How to Run

=======

### Option B — pip (Linux/Mac)
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements_gps.txt
Note: The code assumes a directed MultiDiGraph (multiple parallel edges per node pair). Keep networkx==3.3 and osmnx==1.9.3 for compatibility.

### ▶️ How to Run
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb
Run the GPS in your terminal:

~~~bash
python gps.py
~~~

Then:

1. Enter **origin** and **destination** in the format `Street Name, number` (e.g., `Gran Vía, 25`).
2. Choose one of the three modes:
   - (1) Shortest distance  
   - (2) Fastest time (maxspeed)  
   - (3) Expected time (adds traffic-light delay)
3. The console will print turn-by-turn directions and open a map highlighting your route.

---

## 🧠 How It Works

1. **Street Gazetteer** (`callejero.py`)  
   Reads the official Madrid CSV, converts DMS → decimal, and constructs normalized “Street, number” entries.

2. **Graph Creation**  
   Loads/simplifies the road network from OpenStreetMap via OSMnx and stores it locally as `madrid.graphml` for caching.

3. **Routing**  
   Uses a custom **Dijkstra** (from `grafo_pesado.py`) to compute the optimal path under the chosen weight function (distance, time, or expected time including traffic signals).

<<<<<<< HEAD
4. **Visualization**  
   Plots only a **subgraph around the route** (bbox margin) with hidden nodes and thin edges for fast rendering using OSMnx.
=======
### 🧠 How It Works
Street Gazetteer (callejero.py)
Reads the official Madrid CSV, converts DMS → decimal, and constructs normalized “Street, number” entries.
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb

---

## 🧪 Testing

Validate the algorithms on toy graphs:

<<<<<<< HEAD
~~~bash
=======
### 🧪 Testing
You can test your graph algorithms independently:
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb
python test_grafo.py
~~~

This verifies Dijkstra path reconstruction and MST algorithms (Prim/Kruskal) on small random graphs.

---

## ⚡ Performance Tips

<<<<<<< HEAD
- Reduce the plotting margin (e.g., 150–250 m) in the `resalta_ruta` helper to make rendering faster.
- Keep `node_size=0` and small `edge_linewidth` (≤ 0.4) for large city graphs.
- Ensure the graph remains a **MultiDiGraph** to avoid “keys” errors in OSMnx plotting.
=======
### 🧰 Dependencies
Python 3.11
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb

---

## 🧰 Dependencies

- Python **3.11**  
- **OSMnx 1.9.3**  
- **NetworkX 3.3**  
- **Matplotlib 3.8.2**

<<<<<<< HEAD
(Exact pins are listed in `requirements_gps.txt`.)

---

## ❗ Troubleshooting
=======
### ❗ Troubleshooting
Problem	Solution
nx-loopback / dataclass error on import	Downgrade to networkx==3.3
Slow map rendering	Use the optimized resalta_ruta (subgraph + thin lines)
Address not found	Check accent/case normalization in the gazetteer CSV

### 🙌 Acknowledgments
OpenStreetMap contributors and the OSMnx project
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb

| Problem | Solution |
| --- | --- |
| `nx-loopback` / dataclass error on import | Pin to `networkx==3.3` (as in the requirements). |
| Slow map rendering | Use the optimized `resalta_ruta` (bbox subgraph + thin edges, no nodes). |
| Address not found | Check accent/case normalization and the gazetteer CSV format. |

<<<<<<< HEAD
---

## 📜 License

This project is licensed under the **MIT License** — see `LICENSE` for details.

---

## 🙌 Acknowledgments

- OpenStreetMap contributors and the **OSMnx** project  
- Ayuntamiento de Madrid — official street gazetteer  
- ICAI course “Matemática Discreta — Práctica 3”
=======
ICAI course “Matemática Discreta — Práctica 3
>>>>>>> b4d601a54eca85cec427963adf007d1613829ebb
