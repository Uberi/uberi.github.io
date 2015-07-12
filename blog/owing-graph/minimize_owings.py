#!/usr/bin/env python3

from collections import defaultdict

def all_partitions(elements, max_index = None): # return partitions from most subsets to least subsets
    if max_index == None: max_index = len(elements) - 1
    if max_index < 0: yield () # zero elements has no partitions in its one partitioning
    else:
        current_subset = (elements[max_index],) # obtain a single element subset of the available elements
        for partition in all_partitions(elements, max_index - 1): # compute the partitions of the set without the current subset
            yield partition + (current_subset,) # insert the current subset as its own subset in the partition
            for i, subset in enumerate(partition): # insert the current subset into each subset in the partition in turn
                yield partition[:i] + (subset + current_subset,) + partition[i + 1:]

def largest_partition(net_balances):
    vertices = list(net_balances.keys())
    for partition in all_partitions(vertices):
        for subset in partition:
            if sum(net_balances[vertex] for vertex in subset) != 0: break
        else: # all subsets sum to 0
            return tuple(set(subset) for subset in partition)
    return None

def minimize_owings(owings): # O(if you have to ask, you can't afford it)
    net_balances = defaultdict(int) # net dollar amount each person is owed
    for entry in owings:
        net_balances[entry[0]] += entry[2]
        net_balances[entry[1]] -= entry[2]

    new_owings = [] # list of transactions
    for subset in largest_partition(net_balances):
        vertex_hub = subset.pop() # pick arbitrary hub, and remove it from the set of vertices
        new_owings += [
            (
                (vertex_hub, vertex, net_balances[vertex]) # hub owes the person
                if net_balances[vertex] > 0 else
                (vertex, vertex_hub, -net_balances[vertex]) # person owes the hub
            )
            for vertex in subset if net_balances[vertex] != 0
        ]
    return new_owings

from pprint import pprint
pprint(minimize_owings([
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
