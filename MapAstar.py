import osmnx as ox
import networkx as nx
import numpy as np
import folium
import tkinter as tk
from tkinter import Frame
from tkinter import messagebox

def heuristic(node1, node2, G):
    lat1, lon1 = G.nodes[node1]['y'], G.nodes[node1]['x']
    lat2, lon2 = G.nodes[node2]['y'], G.nodes[node2]['x']
    return np.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2)

def a_star(G, start_node, end_node):
    open_set = set([start_node])
    closed_set = set()
    
    g_costs = {node: float('inf') for node in G.nodes}
    g_costs[start_node] = 0

    f_costs = {node: float('inf') for node in G.nodes}
    f_costs[start_node] = heuristic(start_node, end_node, G)

    came_from = {}

    while open_set:
        current_node = min(open_set, key=lambda node: f_costs[node])
        
        if current_node == end_node:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            return path[::-1]  # Return reversed path

        open_set.remove(current_node)
        closed_set.add(current_node)

        for neighbor in G.neighbors(current_node):
            if neighbor in closed_set:
                continue

            tentative_g_cost = g_costs[current_node] + G[current_node][neighbor][0]['length']

            if neighbor not in open_set:
                open_set.add(neighbor)
            elif tentative_g_cost >= g_costs[neighbor]:
                continue

            came_from[neighbor] = current_node
            g_costs[neighbor] = tentative_g_cost
            f_costs[neighbor] = g_costs[neighbor] + heuristic(neighbor, end_node, G)

    return None  # Path not found

def get_route(start_city, end_city):
    start_point = ox.geocode(start_city + ', Pune, India')
    end_point = ox.geocode(end_city + ', Pune, India')
    
    if start_point is None or end_point is None:
        raise ValueError("Geocoding failed. Please check your input.")

    north = max(start_point[0], end_point[0]) + 0.01
    south = min(start_point[0], end_point[0]) - 0.01
    east = max(start_point[1], end_point[1]) + 0.01
    west = min(start_point[1], end_point[1]) - 0.01

    G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
    start_node = ox.distance.nearest_nodes(G, start_point[1], start_point[0])
    end_node = ox.distance.nearest_nodes(G, end_point[1], end_point[0])

    route = a_star(G, start_node, end_node)

    return G, route, start_point, end_point

def plot_route(G, route, start_point, end_point):
    # Set zoom_start to 16 for a closer view
    route_map = folium.Map(location=[(start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2], zoom_start=15, tiles='OpenStreetMap')
    
    # Plot the route
    folium.PolyLine(locations=[(G.nodes[node]['y'], G.nodes[node]['x']) for node in route], color='blue', weight=5, opacity=0.7).add_to(route_map)
    
    # Plot start and end points
    folium.Marker(location=start_point, icon=folium.Icon(color='green')).add_to(route_map)
    folium.Marker(location=end_point, icon=folium.Icon(color='red')).add_to(route_map)

    return route_map

def show_map():
    start_city = entry_start.get()
    end_city = entry_end.get()
    
    try:
        G, route, start_point, end_point = get_route(start_city, end_city)
        if route:
            route_map = plot_route(G, route, start_point, end_point)
            route_map.save('route_map.html')  # Save the map as HTML
            
            # Open the map in a web browser
            import webbrowser
            webbrowser.open('route_map.html')
        else:
            messagebox.showerror("Error", "No route found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Set up the GUI
root = tk.Tk()
root.title("Route Finder")

frame = Frame(root)
frame.pack(pady=10)

label_start = tk.Label(frame, text="Starting Point:")
label_start.grid(row=0, column=0)
entry_start = tk.Entry(frame)
entry_start.grid(row=0, column=1)

label_end = tk.Label(frame, text="Destination Point:")
label_end.grid(row=1, column=0)
entry_end = tk.Entry(frame)
entry_end.grid(row=1, column=1)

button_find = tk.Button(frame, text="Find Route", command=show_map)
button_find.grid(row=2, columnspan=2)

root.mainloop()
