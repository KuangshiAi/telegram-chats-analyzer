import networkx as nx
import matplotlib.pyplot as plt

def generate_social_graph(messages, output_path="static/social_graph.png", min_edge_weight=1, top_n_nodes=100):
    """
    Generate a social network graph based on user interactions.

    Parameters:
        messages (list of dict): A list of messages where each message contains at least 'sender'.
        output_path (str): Path to save the generated graph image.
        min_edge_weight (int): Minimum weight for edges to be included in the graph.
        top_n_nodes (int): Maximum number of nodes to include in the graph.

    Returns:
        str: Path to the saved graph image.
    """
    if not messages:
        raise ValueError("No messages provided for graph generation.")

    # Initialize a directed graph
    graph = nx.DiGraph()

    # Iterate through the messages to build edges based on sender adjacency
    for i in range(len(messages) - 1):
        sender_1 = messages[i]["sender"]
        sender_2 = messages[i + 1]["sender"]

        # Skip if either sender is None
        if not sender_1 or not sender_2:
            continue

        # Add or update the edge weight between consecutive senders
        if graph.has_edge(sender_1, sender_2):
            graph[sender_1][sender_2]["weight"] += 1
        else:
            graph.add_edge(sender_1, sender_2, weight=1)

    # Filter edges based on the minimum weight
    filtered_graph = nx.DiGraph()
    for u, v, data in graph.edges(data=True):
        if data["weight"] >= min_edge_weight:
            filtered_graph.add_edge(u, v, weight=data["weight"])

    # Rank nodes by degree and keep only the top N
    degrees = dict(filtered_graph.degree())
    top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:top_n_nodes]
    filtered_graph = filtered_graph.subgraph(top_nodes)

    # Truncate labels to only include the part before "#"
    truncated_labels = {node: node.split("#")[0] for node in filtered_graph.nodes()}

    # Draw the graph
    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(filtered_graph, seed=42)  # Use spring layout for better separation

    # Scale node sizes by their degree
    degrees = dict(filtered_graph.degree())
    node_sizes = [degrees[node] * 100 for node in filtered_graph.nodes()]

    # Scale edge thickness by weight
    edges = filtered_graph.edges(data=True)
    weights = [data["weight"] for _, _, data in edges]
    edge_widths = [weight * 0.5 for weight in weights]

    # Dynamically adjust font size based on the number of nodes
    font_size = max(5, min(20, 300 // len(filtered_graph.nodes())))

    # Draw nodes and edges
    nx.draw_networkx_nodes(filtered_graph, pos, node_size=node_sizes, node_color="lightblue", alpha=0.9)
    nx.draw_networkx_edges(filtered_graph, pos, width=edge_widths, alpha=0.7, edge_color="gray")
    nx.draw_networkx_labels(filtered_graph, pos, labels=truncated_labels, font_size=font_size, font_color="black")

    # Add a colorbar for edge weights
    sm = plt.cm.ScalarMappable(cmap="cool", norm=plt.Normalize(vmin=min(weights), vmax=max(weights)))
    sm.set_array(weights)  # Associate weights with the colorbar
    plt.colorbar(sm, ax=plt.gca(), label="Edge Weight (Frequency)")

    plt.title("Social Network Graph of User Interactions")
    plt.savefig(output_path)
    plt.close()

    return output_path
