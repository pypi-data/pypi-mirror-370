class SKU:
    """Represents a Stock Keeping Unit with weight and volume specifications."""

    def __init__(self, sku_id, weight_kg, volume_m3):
        """
        Initialize a SKU.

        Args:
            sku_id: Unique identifier for the SKU
            weight_kg: Weight in kilograms
            volume_m3: Volume in cubic meters
        """
        self.id = sku_id
        self.weight = float(weight_kg)
        self.volume = float(volume_m3)

    def __repr__(self):
        return f"SKU({self.id})"