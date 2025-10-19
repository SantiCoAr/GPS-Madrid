# Madrid Graph-based GPS

Graph-based mini-GPS for Madrid built from scratch: it loads the official street gazetteer, parses addresses into coordinates, builds and simplifies the road network from OpenStreetMap, and computes optimal routes using a custom **Dijkstra** algorithm with three cost models (distance, travel time, and expected time with traffic lights). It also generates turn-by-turn instructions and plots the route efficiently using OSMnx.

---

## 🚀 Features

- **Address lookup:** parses street names and numbers, converts DMS → decimal degrees, and returns accurate coordinates.
- **Road graph from OSM:** downloads and simplifies a directed MultiDiGraph for realistic routing.
- **Custom graph algorithms:** implementation of `Dijkstra`, `Prim`, and `Kruskal` in `grafo_pesado.py`.
- **Three cost modes:**
  1. **Shortest distance** (meters)
  2. **Fastest route** (using `maxspeed` by road type)
  3. **Expected time** (adds a probability-based traffic light delay)
- **Turn-by-turn instructions:** detects street changes and calculates left/straight/right turns.
- **Fast plotting:** uses OSMnx `plot_graph_route` with a subgraph around the path for smooth visualization.

---

## 📂 Project Structure

gps.py # CLI & integration: weights, nearest node, instructions, plotting
callejero.py # Street gazetteer loader and preprocessing (DMS→decimal)
grafo_pesado.py # Graph algorithms (Dijkstra, Prim, Kruskal)
test_grafo.py # Toy tests for correctness
requirements_gps.txt
README.md

---

## ⚙️ Installation

### Option A — Conda (recommended on Windows)

```bash
conda create -n gps-madrid -c conda-forge python=3.11 osmnx=1.9.3 networkx=3.3 matplotlib=3.8.2
conda activate gps-madrid

### Option B — pip (Linux/Mac)
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements_gps.txt
Note: The code assumes a directed MultiDiGraph (multiple parallel edges per node pair). Keep networkx==3.3 and osmnx==1.9.3 for compatibility.

### ▶️ How to Run
Run the GPS in your terminal:

bash
Copiar código
python gps.py
Then:

Enter origin and destination in the format Street Name, number (e.g. Gran Vía, 25).

Choose one of the three modes:

(1) Shortest distance

(2) Fastest time (maxspeed)

(3) Expected time (adds traffic light delay)

The console will show turn-by-turn directions and open a map highlighting your route.

### 🧠 How It Works
Street Gazetteer (callejero.py)
Reads the official Madrid CSV, converts DMS → decimal, and constructs normalized “Street, number” entries.

Graph Creation
Loads/simplifies the road network from OpenStreetMap via OSMnx and stores it locally as madrid.graphml.

Routing
Uses your own Dijkstra implementation (from grafo_pesado.py) to compute the optimal path under the chosen weight function.

Visualization
Only plots a subgraph around the route for faster rendering, hiding nodes and drawing thin edges.

### 🧪 Testing
You can test your graph algorithms independently:
python test_grafo.py
This verifies Dijkstra path reconstruction and MST algorithms on small random graphs.

⚡ Performance Tips
Reduce the map margin (default 250 m) in resalta_ruta to make plotting even faster.

Keep node_size=0 and edge_linewidth≤0.4 for large city graphs.

Use networkx.MultiDiGraph to prevent “keys” errors in OSMnx plotting.

### 🧰 Dependencies
Python 3.11

OSMnx 1.9.3

NetworkX 3.3

Matplotlib 3.8.2

### ❗ Troubleshooting
Problem	Solution
nx-loopback / dataclass error on import	Downgrade to networkx==3.3
Slow map rendering	Use the optimized resalta_ruta (subgraph + thin lines)
Address not found	Check accent/case normalization in the gazetteer CSV

### 🙌 Acknowledgments
OpenStreetMap contributors and the OSMnx project

Ayuntamiento de Madrid — official street gazetteer

ICAI course “Matemática Discreta — Práctica 3
