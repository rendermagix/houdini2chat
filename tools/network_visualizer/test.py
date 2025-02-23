import networkx as nx
from pyvis.network import Network


def visualize(identity_id,html_name):
    # Generate synthetic data
    G = nx.complete_bipartite_graph(3, 4)
    nx.set_node_attributes(G, 3, 'modularity')
    nx.set_node_attributes(G, 'cust', 'category')
    nx.set_node_attributes(G, 'ACITVE', 'status')

    #create subgraph using the provided identity_id    
    classx = [n for n in G.nodes() if G.nodes[n]['modularity'] == 
              G.nodes[identity_id]['modularity']]
    SG = G.subgraph(classx)

    #instantiate the Network object
    N = Network(height='800px', width='100%', bgcolor='#ffffff', # Changed height
                font_color='black',notebook = True, directed=False)

    #this line effects the physics of the html File
    N.barnes_hut(spring_strength=0.006)

    #Change colors of nodes and edges
    for n in SG:
        if (SG.nodes[n]['category']=='cust') and (SG.nodes[n]['status']=='ACTIVE'):  # assign color to nodes based on cust status
            color = 'green'
            shape = 'square'
        if (SG.nodes[n]['category']=='cust') and (SG.nodes[n]['status']=='CLOSED'):  # assign color to nodes based on cust status
            color = 'red'
            shape = 'square'   
        elif SG.nodes[n]['category']=='app':# assign shape to nodes based on cust versus app
            color = 'blue'
            shape = 'triangle'
        else:
            color = 'blue'
            shape = 'triangle'
        N.add_node(n, label=n, color=color,shape = shape)

    for e in SG.edges:
        if e in SG.edges:  # add the edges to the graph
            color = 'black'
            width = 2
        N.add_edge(e[0],e[1],color=color, width=width)

    N.show_buttons(filter_=True)
    #generate html file
    N.show(f'subgraph_{html_name}.html')

visualize(3, 'test_name')