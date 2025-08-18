class Order:
    """Represents a customer order with destination and requested items."""

    def __init__(self, order_id, destination_node):
        """
        Initialize an Order.

        Args:
            order_id: Unique identifier for the order
            destination_node: Node object representing the delivery destination
        """
        self.id = order_id
        self.destination = destination_node
        self.requested_items = {}

    def __repr__(self):
        return f"Order({self.id} to {self.destination.id})"