"""
Get wavelength of light given its frequency

This is what Python users use to access the Fortran.
It is been written by hand here,
but will be auto-generated in future (including docstrings).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from example_fgen_basic.exceptions import CompiledExtensionNotFoundError

if TYPE_CHECKING:
    import pint

try:
    from example_fgen_basic._lib import m_get_wavelength_w  # type: ignore
except (ModuleNotFoundError, ImportError) as exc:  # pragma: no cover
    raise CompiledExtensionNotFoundError("example_fgen_basic._lib") from exc


def get_wavelength_plain(frequency: float) -> float:
    """
    Get wavelength of light using values without units (i.e. 'plain' values)

    Parameters
    ----------
    frequency
        Frequency for which to get the wavelength

    Returns
    -------
    :
        Wavelength of light for given `frequency`
    """
    res: float = m_get_wavelength_w.get_wavelength(frequency)

    return res


def get_wavelength(
    frequency: pint.registry.UnitRegistry.Quantity,
) -> pint.registry.UnitRegistry.Quantity:
    """
    Get wavelength of light

    Parameters
    ----------
    frequency
        Frequency for which to get the wavelength

    Returns
    -------
    :
        Wavelength of light for given `frequency`
    """
    frequency_m = frequency.to("Hz").m

    res_m = get_wavelength_plain(frequency_m)

    # Could use frequency._REGISTRY, but private, not sure how risky that would be
    # Have asked here https://github.com/hgrecco/pint/issues/2207#issuecomment-3178361201
    res = frequency.__class__(res_m, "m")

    return res
