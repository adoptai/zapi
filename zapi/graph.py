"""Module for generating interactive session graphs from HAR files."""

import json
from pathlib import Path
from urllib.parse import urlparse

import networkx as nx
from pyvis.network import Network


def create_graph_from_har(har_path: str, output_path: str = "session_graph.html") -> str:
    """
    Create an interactive graph visualization from a HAR file.

    Args:
        har_path: Path to the input HAR file.
        output_path: Path to save the HTML graph.

    Returns:
        The absolute path to the generated HTML file.
    """
    har_file = Path(har_path)
    if not har_file.exists():
        raise FileNotFoundError(f"HAR file not found: {har_path}")

    with open(har_file, encoding="utf-8") as f:
        har_data = json.load(f)

    entries = har_data.get("log", {}).get("entries", [])

    # Create a directed graph
    graph = nx.DiGraph()

    # Track nodes to ensure we only add edges between existing nodes or add nodes as we go
    # We'll use the full URL as the node ID, but display a shorter label

    previous_url = None

    for entry in entries:
        request = entry.get("request", {})
        response = entry.get("response", {})
        resource_type = entry.get("_resourceType", "")

        # We primarily care about document navigations to visualize the flow
        # Some HARs might not have _resourceType set correctly, so we can also check mimeType
        mime_type = response.get("content", {}).get("mimeType", "")

        is_document = resource_type == "document" or "text/html" in mime_type

        if is_document:
            url = request.get("url")
            if not url:
                continue

            # Parse URL to get a cleaner label (path)
            parsed_url = urlparse(url)
            label = parsed_url.path
            if not label or label == "/":
                label = parsed_url.netloc

            # Add node if it doesn't exist
            if not graph.has_node(url):
                graph.add_node(url, label=label, title=url, group="page")

            # Add edge from previous page to current page
            if previous_url and previous_url != url:
                graph.add_edge(previous_url, url)

            # Check for redirects
            redirect_url = response.get("redirectURL")
            if redirect_url:
                # Handle relative redirects
                if not redirect_url.startswith("http"):
                    # This is a simplification; robust handling would join with base URL
                    pass
                else:
                    # Add redirect target node
                    parsed_redirect = urlparse(redirect_url)
                    redirect_label = parsed_redirect.path
                    if not redirect_label or redirect_label == "/":
                        redirect_label = parsed_redirect.netloc

                    if not graph.has_node(redirect_url):
                        graph.add_node(redirect_url, label=redirect_label, title=redirect_url, group="redirect")

                    graph.add_edge(url, redirect_url, label="redirects to", dashes=True)

                    # Update previous_url to be the redirect target for the next iteration
                    # because the browser would logically be at the redirect target
                    previous_url = redirect_url
            else:
                previous_url = url

    # Visualize with Pyvis
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.from_nx(graph)

    # Customize physics for better layout
    net.toggle_physics(True)
    net.set_options("""
    var options = {
      "nodes": {
        "borderWidth": 2,
        "borderWidthSelected": 4,
        "opacity": 1,
        "font": {
          "size": 14,
          "face": "tahoma"
        }
      },
      "edges": {
        "color": {
          "inherit": true
        },
        "smooth": {
          "type": "continuous",
          "forceDirection": "none"
        },
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1
          }
        }
      },
      "physics": {
        "forceAtlas2Based": {
          "springLength": 100,
          "springConstant": 0.08,
          "damping": 0.4,
          "avoidOverlap": 0.5
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)

    output_abs_path = Path(output_path).resolve()
    net.save_graph(str(output_abs_path))

    return str(output_abs_path)
