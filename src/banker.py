#data: list[tuple[str, list[tuple[str, tuple[int, int]]]]]
#maxAvail: dict[str, int]
import matplotlib.pyplot as plt
import networkx as nx
import json

def rescAllocation(rescQueries, maxAvail) -> None:
    for rescName, (rescAlloc, rescNeed) in rescQueries:
        maxAvail[rescName] += rescAlloc

def safetySeq(data, maxAvail):
    maxAvailCopy = maxAvail.copy()
    seq = set()
    while len(seq) < len(data):
        for name, rescQueries in data:
            if name in seq: continue
            for rescName, (rescAlloc, rescNeed) in rescQueries:
                if (rescName not in maxAvailCopy) or maxAvailCopy[rescName] < rescNeed:
                    break
            else:
                rescAllocation(rescQueries, maxAvailCopy)
                seq.add(name)
                break
        else:
            return []
    maxAvail = maxAvailCopy
    return list(seq)

def orderResource(rescList): rescList.sort()

def present(data, maxAvail, seq):
    pnodes = []; rnodes = list(f'{name}[{cnt}]' for name, cnt in maxAvail.items())
    G = nx.MultiDiGraph()
    G.add_nodes_from(rnodes)
    for name, rescQueries in data:
        pnodes.append(name)
        G.add_node(name)
        for rescName, (rescAlloc, rescNeed) in rescQueries:
            if rescName in maxAvail:
                if rescAlloc > 0:
                    #G.add_edge(f'{rescName}[{maxAvail[rescName]}]', name)
                    G.add_edges_from([(f'{rescName}[{maxAvail[rescName]}]', name, k) for k in range(0, rescAlloc)])
                if rescNeed > 0:
                    #G.add_edge(name, f'{rescName}[{maxAvail[rescName]}]')
                    G.add_edges_from([(name, f'{rescName}[{maxAvail[rescName]}]', k) for k in range(0, rescNeed)])
                    
    plt.style.use('dark_background')
    fig, axd = plt.subplot_mosaic('AB')
    axd['A'].set_title('Resource Allocation Graph')
    fig.canvas.manager.set_window_title('BankersAlgorithm')
    pos1 = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos1, ax=axd['A'], nodelist=pnodes, node_shape='o', node_color='skyblue', node_size=500)
    nx.draw_networkx_nodes(G, pos1, ax=axd['A'], nodelist=rnodes, node_shape='s', node_color='green', node_size=500)
    nx.draw_networkx_labels(G, pos1, ax=axd['A'], font_size=8, font_color='white')
    nx.draw_networkx_edges(G, pos1, ax=axd['A'], edge_color='grey', width=1, arrows=True, arrowstyle='-|>', arrowsize=20, connectionstyle='arc3,rad=0.25')
    if len(seq) == 0:
        axd['b'].set_title('No Safe Sequence. Deadlock')
        plt.show()
        return
    axd['B'].set_title('Safe Sequence')
    _G = nx.DiGraph()
    _G.add_node(seq[0])
    i = 1
    while i < len(seq):
        _G.add_node(seq[i])
        _G.add_edge(seq[i - 1], seq[i])
        i += 1
    pos2 = nx.spring_layout(_G)
    nx.draw_networkx_nodes(_G, pos2, ax=axd['B'], node_shape='o', node_color='skyblue', node_size=500)
    nx.draw_networkx_labels(_G, pos2, ax=axd['B'], font_size=8, font_color='white')
    nx.draw_networkx_edges(_G, pos2, ax=axd['B'], width=1, arrows=True, edge_color='grey', arrowstyle='-|>', arrowsize=20, connectionstyle='arc3,rad=0.25')
    return fig

def banker(data, maxAvail):
    temp = maxAvail.copy()
    for name, rescQueries in data:
        for rescName, (rescAlloc, rescNeed) in rescQueries:
            if rescName in maxAvail:
                maxAvail[rescName] -= rescAlloc
    seq = safetySeq(data, maxAvail)
    return present(data, temp, seq)
    
if __name__ == '__main__':
    data = [
        ['P1', [['R1', [0, 1]], ['R2', [1, 1]]]],
        ['P2', [['R1', [2, 1]], ['R2', [0, 1]]]],
        ['P3', [['R1', [1, 1]], ['R2', [1, 0]]]],
    ]
    maxAvail = {'R1': 4, 'R2': 3}
    print(json.dumps([data, maxAvail]))
    # banker(data, maxAvail)

