class Unit:
    def __init__(self, value: float, base_factor: float):
        self.value = value
        self.base_factor = base_factor  # Conversion factor to base unit

    def to(self, other_unit):
        """Convert to another unit (returns a new Unit object)."""
        base_value = self.value * self.base_factor
        new_value = base_value / other_unit.base_factor
        return Unit(new_value, other_unit.base_factor)

    def __repr__(self):
        return f"{self.value}"

    def __float__(self):
        return self.value * self.base_factor

    def __eq__(self, other):
        return float(self) == float(other)

class _UnitFactory:
    base_factor = 1.0
    def __rmul__(self, value):
        return Unit(value, self.base_factor)

# Length units
class mm(_UnitFactory):
    base_factor = 0.001  # 1 mm = 0.001 m

class cm(_UnitFactory):
    base_factor = 0.01   # 1 cm = 0.01 m

class m(_UnitFactory):
    base_factor = 1.0    # 1 m = 1 m

# Force units
class N(_UnitFactory):
    base_factor = 1.0    # 1 N = 1 N

class kN(_UnitFactory):
    base_factor = 1000.0 # 1 kN = 1000 N

class daN(_UnitFactory):
    base_factor = 10.0   # 1 daN = 10 N