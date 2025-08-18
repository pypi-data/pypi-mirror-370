class Node:
    """Represents a node in the road network with geographic coordinates."""

    def __init__(self, node_id, lat, lon):
        """
        Initialize a Node.

        Args:
            node_id: Unique identifier for the node
            lat: Latitude coordinate
            lon: Longitude coordinate
        """
        self.id = int(node_id)
        self.lat = float(lat)
        self.lon = float(lon)

    def __repr__(self):
        return f"Node({self.id})"