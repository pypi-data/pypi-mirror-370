from iccore.data import units, measurement


def xtest_units():

    q = quantity.Quantity(name="vecolity", unit=units.Unit(name="metres_per_second"))

    assert q.unit.name == "metres_per_second"

    unit_collection = units.load_default_units()
    assert unit_collection
