import array_api_extra as xpx
import pytest
from array_api._2024_12 import Array, ArrayNamespaceFull
from array_api_compat import array_namespace
from array_api_compat import numpy as np

from gumerov_expansion_coefficients._main import (
    R_all,
    idx,
    idx_all,
    idx_i,
    minus_1_power,
    ndim_harm,
    translational_coefficients,
    translational_coefficients_sectorial_init,
    translational_coefficients_sectorial_n_m,
    translational_coefficients_sectorial_nd_md,
)


def euclidean_to_spherical(x: Array, y: Array, z: Array) -> tuple[Array, Array, Array]:
    xp = array_namespace(x)
    r = (x**2 + y**2 + z**2) ** 0.5
    theta = xp.atan2(xp.sqrt(x**2 + y**2), z)
    phi = xp.atan2(y, x)
    return r, theta, phi


def test_idx(xp: ArrayNamespaceFull) -> None:
    n = xp.asarray([0, 1, 1, 1])
    m = xp.asarray([0, -1, 0, 1])
    assert xp.all(idx(n, m) == xp.asarray([0, 1, 2, 3]))


def test_idx_i() -> None:
    assert idx_i(0, 0) == 0
    assert idx_i(1, -1) == 1
    assert idx_i(1, 0) == 2
    assert idx_i(1, 1) == 3


def test_idx_all(xp: ArrayNamespaceFull) -> None:
    n, m = idx_all(3, xp=xp, dtype=xp.int32, device=None)
    assert xp.all(n == xp.asarray([0, 1, 1, 1, 2, 2, 2, 2, 2]))
    assert xp.all(m == xp.asarray([0, -1, 0, 1, -2, -1, 0, 1, 2]))


def test_ndim_harm() -> None:
    assert ndim_harm(2) == 4


def test_minus_1_power() -> None:
    assert minus_1_power(0) == 1
    assert minus_1_power(1) == -1
    assert minus_1_power(2) == 1
    assert minus_1_power(3) == -1
    assert minus_1_power(4) == 1


def test_init(xp: ArrayNamespaceFull) -> None:
    # Gumerov (2, -7, 1)
    k = xp.asarray(1.0)
    r = xp.asarray(7.3484693)
    theta = xp.asarray(1.43429)
    phi = xp.asarray(-1.2924967)
    n_end = 4
    init = translational_coefficients_sectorial_init(k * r, theta, phi, True, n_end)
    assert init[idx_i(2, 1)] == pytest.approx(-0.01413437 - 0.04947031j)
    assert init[idx_i(3, 2)] == pytest.approx(-0.01853696 + 0.01153411j)


def test_sectorial_n_m(xp: ArrayNamespaceFull) -> None:
    # Gumerov (2, -7, 1)
    k = xp.asarray(1.0)
    r = xp.asarray(7.3484693)
    theta = xp.asarray(1.43429)
    phi = xp.asarray(-1.2924967)
    n_end = 3
    init = translational_coefficients_sectorial_init(k * r, theta, phi, True, n_end)
    sectorial = translational_coefficients_sectorial_n_m(
        n_end=n_end,
        translational_coefficients_sectorial_init=init,
    )
    # assert sectorial[idx_i(1, 1), 0] == pytest.approx(0.01656551+0.05797928j)
    assert sectorial[idx_i(0, 0), 1] == pytest.approx(0.01656551 - 0.05797928j)
    assert sectorial[idx_i(0, 0), 2] == pytest.approx(0.15901178 + 0.09894066j)
    assert sectorial[idx_i(0, 0), 3] == pytest.approx(-0.04809683 + 0.04355622j)
    assert sectorial[idx_i(0, 0), -2] == pytest.approx(0.15901178 - 0.09894066j)
    assert sectorial[idx_i(1, 0), 1] == pytest.approx(-0.01094844 + 0.03831954j)
    assert sectorial[idx_i(1, -1), 1] == pytest.approx(-0.17418868 - 0.10838406j)
    assert sectorial[idx_i(1, 1), 1] == pytest.approx(0.18486702 + 0.0j)

    # assert sectorial[idx_i(2, 1), 0] == pytest.approx(-0.01413437 - 0.04947031j)
    assert sectorial[idx_i(2, 1), 1] == pytest.approx(-0.00290188 + 0.0j, abs=1e-7)
    assert sectorial[idx_i(2, 1), -1] == pytest.approx((0.01716189 - 0.01067851j), abs=1e-7)


def test_sectorial_nd_md(xp: ArrayNamespaceFull) -> None:
    # Gumerov (2, -7, 1)
    k = xp.asarray(1.0)
    r = xp.asarray(7.3484693)
    theta = xp.asarray(1.43429)
    phi = xp.asarray(-1.2924967)
    n_end = 2
    init = translational_coefficients_sectorial_init(k * r, theta, phi, True, n_end)
    sectorial_n_m = translational_coefficients_sectorial_n_m(
        n_end=n_end,
        translational_coefficients_sectorial_init=init,
    )
    sectorial_nd_md = translational_coefficients_sectorial_nd_md(
        n_end=n_end,
        translational_coefficients_sectorial_n_m=sectorial_n_m,
    )
    assert sectorial_nd_md[1, idx_i(1, 0)] == sectorial_n_m[idx_i(1, 0), -1]
    assert sectorial_nd_md[1, idx_i(1, 0)] == pytest.approx(0.01094844 + 0.03831954j)


def test_main(xp: ArrayNamespaceFull) -> None:
    # Gumerov (2, -7, 1)
    k = xp.asarray(1.0)
    r = xp.asarray(7.3484693)
    theta = xp.asarray(1.43429)
    phi = xp.asarray(-1.2924967)
    n_end = 5
    coefs = translational_coefficients(
        k * r,
        theta,
        phi,
        same=True,
        n_end=n_end,
    )
    assert coefs[idx_i(1, 0), idx_i(1, 0)] == pytest.approx(-0.01254681 + 0.0j)
    assert coefs[idx_i(2, 1), idx_i(4, 3)] == pytest.approx(0.10999471 + 0.06844115j)
    assert coefs[idx_i(2, 1), idx_i(4, -3)] == pytest.approx(-0.10065599 + 0.20439409j)
    assert coefs[idx_i(2, -1), idx_i(4, -3)] == pytest.approx(0.10999471 - 0.06844115j)


@pytest.mark.parametrize("same", [True, False])
def test_main_all(xp: ArrayNamespaceFull, same: bool) -> None:
    k = xp.asarray(1.0)
    r = xp.asarray(7.3484693)
    theta = xp.asarray(1.43429)
    phi = xp.asarray(-1.2924967)
    n_end = 3
    coefs = translational_coefficients(
        k * r,
        theta,
        phi,
        same=same,
        n_end=n_end,
    )
    if same:
        expected = xp.asarray(
            [
                [
                    [
                        [0.11906241 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.01171358 + 0.0j,
                            0.01656551 + 0.05797928j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.01656551 + 0.05797928j,
                        ],
                        [
                            0.14714358 + 0.0j,
                            -0.01413437 - 0.04947031j,
                            0.15901178 - 0.09894066j,
                            0.15901178 + 0.09894066j,
                            0.01413437 - 0.04947031j,
                        ],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                ],
                [
                    [
                        [-0.01171358 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.01254681 + 0.0j,
                            0.01094844 + 0.03831954j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.01094844 + 0.03831954j,
                        ],
                        [
                            0.03121856 + 0.0j,
                            0.02340277 + 0.08190971j,
                            0.01213529 - 0.00755084j,
                            0.01213529 + 0.00755084j,
                            -0.02340277 + 0.08190971j,
                        ],
                    ],
                    [
                        [0.01656551 - 0.05797928j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.01094844 + 0.03831954j,
                            0.18486702 + 0.0j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.17418868 - 0.10838406j,
                        ],
                        [
                            -0.00174659 + 0.00611308j,
                            -0.00290188 + 0.0j,
                            0.01440913 + 0.05043195j,
                            -0.05453668 + 0.04938812j,
                            0.01716189 + 0.01067851j,
                        ],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [-0.01656551 - 0.05797928j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.01094844 + 0.03831954j,
                            -0.17418868 + 0.10838406j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.18486702 + 0.0j,
                        ],
                        [
                            0.00174659 + 0.00611308j,
                            0.01716189 - 0.01067851j,
                            0.05453668 + 0.04938812j,
                            -0.01440913 + 0.05043195j,
                            -0.00290188 + 0.0j,
                        ],
                    ],
                ],
                [
                    [
                        [0.14714358 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.03121856 + 0.0j,
                            -0.00174659 - 0.00611308j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.00174659 - 0.00611308j,
                        ],
                        [
                            0.10114752 + 0.0j,
                            -0.00892893 - 0.03125126j,
                            0.14745029 - 0.09174684j,
                            0.14745029 + 0.09174684j,
                            0.00892893 - 0.03125126j,
                        ],
                    ],
                    [
                        [0.01413437 - 0.04947031j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.02340277 - 0.08190971j,
                            0.00290188 + 0.0j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.01716189 - 0.01067851j,
                        ],
                        [
                            0.00892893 - 0.03125126j,
                            0.02133132 + 0.0j,
                            0.01654808 + 0.05791828j,
                            0.035445 - 0.0320988j,
                            -0.04952915 - 0.03081814j,
                        ],
                    ],
                    [
                        [0.15901178 + 0.09894066j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.01213529 - 0.00755084j,
                            0.01440913 - 0.05043195j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.05453668 - 0.04938812j,
                        ],
                        [
                            0.14745029 + 0.09174684j,
                            -0.01654808 + 0.05791828j,
                            0.22575094 + 0.0j,
                            0.07690081 + 0.15615634j,
                            0.035445 - 0.0320988j,
                        ],
                    ],
                    [
                        [0.15901178 - 0.09894066j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.01213529 + 0.00755084j,
                            -0.05453668 - 0.04938812j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.01440913 - 0.05043195j,
                        ],
                        [
                            0.14745029 - 0.09174684j,
                            -0.035445 - 0.0320988j,
                            0.07690081 - 0.15615634j,
                            0.22575094 + 0.0j,
                            0.01654808 + 0.05791828j,
                        ],
                    ],
                    [
                        [-0.01413437 - 0.04947031j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.02340277 - 0.08190971j,
                            -0.01716189 + 0.01067851j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.00290188 + 0.0j,
                        ],
                        [
                            -0.00892893 - 0.03125126j,
                            -0.04952915 + 0.03081814j,
                            -0.035445 - 0.0320988j,
                            -0.01654808 + 0.05791828j,
                            0.02133132 + 0.0j,
                        ],
                    ],
                ],
            ]
        )
    else:
        expected = xp.asarray(
            [
                [
                    [
                        [0.11906241 - 0.06589887j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.01171358 + 0.03017697j,
                            -0.13280296 + 0.10065598j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.16593398 + 0.01530258j,
                        ],
                        [
                            0.14714358 - 0.01439304j,
                            -0.01897338 - 0.04808774j,
                            0.14933377 - 0.1144946j,
                            0.16868979 + 0.08338671j,
                            0.00929537 - 0.05085288j,
                        ],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                ],
                [
                    [
                        [-0.01171358 - 0.03017697j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.01254681 - 0.05302534j,
                            0.01469671 + 0.0372486j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.00720016 + 0.03939047j,
                        ],
                        [
                            0.03121856 - 0.03612805j,
                            0.02029515 + 0.0827976j,
                            -0.01084281 - 0.04447992j,
                            0.03511338 - 0.02937824j,
                            -0.0265104 + 0.08102182j,
                        ],
                    ],
                    [
                        [0.16593398 - 0.01530258j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.00720016 + 0.03939047j,
                            0.18486702 - 0.07233563j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.1847904 - 0.09134557j,
                        ],
                        [
                            0.16256115 + 0.05305815j,
                            -0.00290188 + 0.05981684j,
                            -0.18902336 + 0.10855551j,
                            0.09575707 + 0.21534953j,
                            0.04965782 - 0.0415471j,
                        ],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                    ],
                    [
                        [0.13280296 - 0.10065598j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.01469671 + 0.0372486j,
                            -0.16358695 + 0.12542255j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.18486702 - 0.07233563j,
                        ],
                        [
                            0.16605434 - 0.04083198j,
                            -0.01533404 - 0.06290411j,
                            0.20483042 - 0.1165733j,
                            -0.21784161 - 0.00769162j,
                            -0.00290188 + 0.05981684j,
                        ],
                    ],
                ],
                [
                    [
                        [0.14714358 - 0.01439304j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.03121856 + 0.03612805j,
                            -0.16605434 + 0.04083198j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.16256115 - 0.05305815j,
                        ],
                        [
                            0.10114752 + 0.03580504j,
                            0.04982273 - 0.04803745j,
                            0.17595986 - 0.04592788j,
                            0.11894071 + 0.1375658j,
                            0.06768059 - 0.01446507j,
                        ],
                    ],
                    [
                        [0.00929537 - 0.05085288j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.0265104 - 0.08102182j,
                            0.00290188 - 0.05981684j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.04965782 + 0.0415471j,
                        ],
                        [
                            0.06768059 - 0.01446507j,
                            0.02133132 - 0.12297353j,
                            -0.0030198 + 0.0635091j,
                            0.07446914 + 0.01099348j,
                            -0.11375463 + 0.0724014j,
                        ],
                    ],
                    [
                        [0.16868979 + 0.08338671j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.03511338 + 0.02937824j,
                            0.21784161 + 0.00769162j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            -0.09575707 - 0.21534953j,
                        ],
                        [
                            0.11894071 + 0.1375658j,
                            -0.03611596 + 0.05232746j,
                            0.22575094 - 0.05967615j,
                            -0.11294635 + 0.24964855j,
                            0.07446914 + 0.01099348j,
                        ],
                    ],
                    [
                        [0.14933377 - 0.1144946j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            0.01084281 + 0.04447992j,
                            -0.20483042 + 0.1165733j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.18902336 - 0.10855551j,
                        ],
                        [
                            0.17595986 - 0.04592788j,
                            0.00357913 - 0.07519108j,
                            0.26674798 - 0.06266413j,
                            0.22575094 - 0.05967615j,
                            -0.0030198 + 0.0635091j,
                        ],
                    ],
                    [
                        [-0.01897338 - 0.04808774j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j],
                        [
                            -0.02029515 - 0.0827976j,
                            0.01533404 + 0.06290411j,
                            0.0 + 0.0j,
                            0.0 + 0.0j,
                            0.00290188 - 0.05981684j,
                        ],
                        [
                            0.04982273 - 0.04803745j,
                            0.01469634 + 0.13403767j,
                            0.00357913 - 0.07519108j,
                            -0.03611596 + 0.05232746j,
                            0.02133132 - 0.12297353j,
                        ],
                    ],
                ],
            ]
        )
    n, m = idx_all(n_end, xp=xp, dtype=xp.int32, device=None)
    expected = expected[n, m, ...][:, n, m]
    expected = xp.moveaxis(expected, 0, -1)
    print(coefs, expected)
    assert xp.all(xpx.isclose(coefs, expected, atol=1e-6, rtol=1e-6))


def test_gumerov_table(xp: ArrayNamespaceFull) -> None:
    k = 1.0

    x = xp.asarray([-1.0, 1.0, 0.0])
    t = xp.asarray([2.0, -7.0, 1.0])
    y = x + t
    print(y)

    # to spherical coordinates
    x_sp = euclidean_to_spherical(x[0], x[1], x[2])
    t_sp = euclidean_to_spherical(t[0], t[1], t[2])
    y_sp = euclidean_to_spherical(y[0], y[1], y[2])

    for n_end_add in [3, 5, 7, 9]:
        x_R = R_all(k * x_sp[0], x_sp[1], x_sp[2], n_end=n_end_add)
        t_coef = translational_coefficients(
            k * t_sp[0], t_sp[1], t_sp[2], same=True, n_end=n_end_add
        )
        y_S = R_all(k * y_sp[0], y_sp[1], y_sp[2], n_end=n_end_add)
        expected = y_S[idx_i(2, 0)]
        actual = xp.vecdot(t_coef, x_R[:, None], axis=0)[idx_i(2, 0)]
        print(np.round(complex(expected), decimals=6), np.round(complex(actual), decimals=6))
