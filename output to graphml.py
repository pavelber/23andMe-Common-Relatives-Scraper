import networkx as nx
import csv

datafile = r"Common Relatives per Relative.csv"

# print('Please consider percentages as 0-100 for the following questions')
# print('This means, for 51.2%, you would enter \'51.2\' instead of 0.512')
# cutoff_for_self_relation = float((input('What % cutoff do you want to use for relations to YOU?: '))
# cutoff_for_common_relation = float((input('What % cutoff do you want to use for relations to YOUR COMMON RELATIVE? '))

include_you = input('Do you want to include yourself? It may result in messier graphs. (Y/n) ') == 'Y'

cutoff_for_self_to_rel = 0.75
cutoff_for_self_to_common = 0.0
cutoff_for_rel_to_common = 0.0

relative_nodes_dict = {}
relative_nodes = []
if include_you:
    relative_nodes.append(('000', {'label': 'You', 'weight': 100.0}))
relative_edges = []

try:
    with open(datafile) as f:
        link_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        for row in link_reader:
            if row and row[0] != 'Relative ID':                           # Make sure it's a row we care about
                your_rel_to_them = float(row[2][:-1])
                your_rel_to_common = float(row[5][:-1])
                their_rel_to_common = float(row[6][:-1])
                if (    their_rel_to_common >= cutoff_for_rel_to_common  # Compare their relation to our cutoff
                    and your_rel_to_them >= cutoff_for_self_to_rel       # Compare our relations to our cutoff
                    and your_rel_to_common >= cutoff_for_self_to_common
                   ):
                    if include_you:
                        your_edge_to_rel = ['000', row[0], {'weight': your_rel_to_them}]
                        your_edge_to_common = ['000', row[3], {'weight': your_rel_to_common}]
                        if your_edge_to_rel not in relative_edges: relative_edges.append(your_edge_to_rel)
                        if your_edge_to_common not in relative_edges: relative_edges.append(your_edge_to_common)
                    relative_edges.append([row[0], row[3], {'weight': their_rel_to_common}])
                    for rel in [[row[0], row[1], their_rel_to_common], [row[3], row[4], your_rel_to_common]]:
                        if rel[0] not in relative_nodes_dict:
                            relative_nodes_dict[rel[0]]: rel[1]
                            relative_nodes.append((rel[0], {'label': rel[1], 'weight': rel[2]}))

except FileNotFoundError as ex:
    print('Unable to open the common relatives CSV, please be sure it\'s in the folder and try again.')
    print('Error: {}'.format(str(ex)))
    exit()

# print(relative_nodes)
# for node in relative_nodes:
#     print(node)
# # print(relative_edges)
# for edge in sorted(relative_edges):
#     print(edge)

print('creating G')
G = nx.Graph()
G.add_nodes_from(relative_nodes)
print('Total nodes: {}'.format(len(G.nodes())))
G.add_edges_from(relative_edges)
print('Total edges: {}'.format(len(G.edges())))

# print(G.edges())

print('getting position')
pos = nx.spring_layout(G)

for key, (x, y) in pos.items():
    G.node[key]['x'] = float(x)
    G.node[key]['y'] = float(y)

nx.write_graphml(G, 'relations network.graphml')
