import pytest

from scm.plams.tools.periodic_table import PT
from scm.plams.core.errors import PTError


@pytest.mark.parametrize(
    "atomic_number,symbol,mass,radius,connectors,is_metallic,is_electronegative",
    [
        [11, "Na", 22.98977, 1.86, 8, 1, 0],
        [0, "Xx", 0, 0, 0, 0, 0],
        [None, "Foo", 0, 0, 0, 0, 0],
    ],
)
def test_get_property(atomic_number, symbol, mass, radius, connectors, is_metallic, is_electronegative):
    if atomic_number is not None:
        assert PT.get_atomic_number(symbol) == atomic_number
        assert PT.get_symbol(atomic_number) == symbol
        assert PT.get_mass(symbol) == mass
        assert PT.get_radius(atomic_number) == radius
        assert PT.get_connectors(symbol) == connectors
        assert PT.get_metallic(atomic_number) == is_metallic
        assert PT.get_electronegative(symbol) == is_electronegative
    else:
        with pytest.raises(PTError):
            PT.get_atomic_number(symbol)
