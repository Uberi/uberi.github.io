#!/usr/bin/env python3

from collections import defaultdict

def minimize_owings_approximate(owings): # O(n)
    net_balances = defaultdict(int) # net dollar amount each person is owed
    for entry in owings:
        net_balances[entry[0]] += entry[2]
        net_balances[entry[1]] -= entry[2]
    nonzero_owings = [entry for entry in owings if net_balances[entry[0]] != 0 and net_balances[entry[1]] != 0]
    vertices = {vertex for vertex, net_value in net_balances.items() if net_value != 0}

    connections = defaultdict(set) # mapping from each person to the set of people that owe or are owed by this person
    for entry in nonzero_owings:
        connections[entry[0]].add(entry[1])
        connections[entry[1]].add(entry[0])

    result = [] # list of transactions
    unvisited_vertices = set(vertices) # duplicate the set of vertices, since we will be mutating both separately later
    while unvisited_vertices: # there are still vertices to visit
        # find all connected vertices and group them together into a component
        component, vertices_to_visit = set(), {unvisited_vertices.pop()}
        while vertices_to_visit:
            vertex = vertices_to_visit.pop() # visit the next vertex
            component.add(vertex)
            vertices_to_visit.update(v for v in connections[vertex] if v not in component) # add all the vertices that are connected that we haven't visited yet
        unvisited_vertices -= component
        
        vertex_hub = component.pop() # pick arbitrary hub, and remove it from the set of vertices
        result += [
            (
                (vertex_hub, vertex, net_balances[vertex]) # hub owes the person
                if net_balances[vertex] > 0 else
                (vertex, vertex_hub, -net_balances[vertex]) # person owes the hub
            )
            for vertex in component if net_balances[vertex] != 0
        ]
    return result

from pprint import pprint
pprint(minimize_owings_approximate([
    ("Avi",      "Randall",   25), # Avi owes Randall 25 dollars
    ("Charlene", "Andrew",    65),
    ("Avi",      "Andrew",    73),
    ("Beryl",    "Randall",    8),
    ("Beryl",    "Charlene",  65),
    ("Hubert",   "Amy",       12),
    ("Amy",      "Hubert",    46),
    ("Avi",      "Andrew",    17),
    ("Avi",      "Randall",    4),
    ("Beryl",    "John",      25),
]))
