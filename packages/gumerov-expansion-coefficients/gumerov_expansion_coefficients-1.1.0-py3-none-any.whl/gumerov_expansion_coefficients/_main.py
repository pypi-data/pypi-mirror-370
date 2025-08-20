# https://github.com/search?q=gumerov+translation+language%3APython&type=code&l=Python
from types import EllipsisType
from typing import Any, ParamSpec, TypeVar

from array_api._2024_12 import Array, ArrayNamespace
from array_api_compat import array_namespace, to_device
from array_api_compat import numpy as np
from array_api_jit import jit as jit_raw
from scipy.special import sph_harm_y_all, spherical_jn, spherical_yn

prange = range
P = ParamSpec("P")
T = TypeVar("T")

jit = jit_raw(fail_on_error=True)
# {"numpy": numba.jit(nopython=True, nogil=True)})  # {"torch": lambda x: x})
pjit = jit_raw(
    fail_on_error=True
    # {"numpy": numba.jit(parallel=True, nopython=True, nogil=True)}
)  # {"torch": lambda x: x})


jit = lambda x: x  # noqa
pjit = lambda x: x  # noqa


# (2.14)
def R_all(kr: Array, theta: Array, phi: Array, *, n_end: int) -> Array:
    """Regular elementary solution of 3D Helmholtz equation.

    Parameters
    ----------
    kr : Array
        k * r of shape (...,)
    theta : Array
        polar angle of shape (...,)
    phi : Array
        azimuthal angle of shape (...,)
    n_end : int
        Maximum degree of spherical harmonics.

    Returns
    -------
    Array
        Regular elementary solution of 3D Helmholtz equation of shape (..., ndim_harm(n_end),)
    """
    xp = array_namespace(kr, theta, phi)
    device = kr.device
    dtype = kr.dtype
    if dtype == xp.float32:
        dtype = xp.complex64
    elif dtype == xp.float64:
        dtype = xp.complex128
    n, m = idx_all(n_end, xp=xp, dtype=xp.int32, device="cpu")
    kr = to_device(kr, "cpu")
    theta = to_device(theta, "cpu")
    phi = to_device(phi, "cpu")
    return xp.asarray(
        spherical_jn(n, kr[..., None])
        * np.moveaxis(sph_harm_y_all(n_end - 1, n_end - 1, theta, phi)[n, m, ...], 0, -1),
        dtype=dtype,
        device=device,
    )


def S_all(kr: Array, theta: Array, phi: Array, *, n_end: int) -> Array:
    """Singular elementary solution of 3D Helmholtz equation.

    Parameters
    ----------
    kr : Array
        k * r of shape (...,)
    theta : Array
        polar angle of shape (...,)
    phi : Array
        azimuthal angle of shape (...,)
    n_end : int
        Maximum degree of spherical harmonics.

    Returns
    -------
    Array
        Singular elementary solution of 3D Helmholtz equation of shape (..., ndim_harm(n_end),)"""
    xp = array_namespace(kr, theta, phi)
    device = kr.device
    dtype = kr.dtype
    if dtype == xp.float32:
        dtype = xp.complex64
    elif dtype == xp.float64:
        dtype = xp.complex128
    n, m = idx_all(n_end, xp=xp, dtype=xp.int32, device="cpu")
    kr = to_device(kr, "cpu")
    theta = to_device(theta, "cpu")
    phi = to_device(phi, "cpu")
    return xp.asarray(
        (spherical_jn(n, kr[..., None]) + 1j * spherical_yn(n, kr[..., None]))
        * np.moveaxis(sph_harm_y_all(n_end - 1, n_end - 1, theta, phi)[n, m, ...], 0, -1),
        dtype=dtype,
        device=device,
    )


# Gumerov's notation
# E^m_n = sum_{m'n'} (E|F)^{m' m}_{n' n} F^{m'}_{n'}
# (E|F)^{m' m}_{n'} := (E|F)^{m' m}_{n' |m|}
# (E|F)^{m' m}_{,n} := (E|F)^{m' m}_{|m'| n}


def idx_i(n: int, m: int, /) -> int:
    """Index for the coefficients."""
    # (0, 0) -> 0
    # (1, -1) -> 1
    # (1, 0) -> 2
    if abs(m) > n:
        return -1
    return n * (n + 1) + m


@jit
def idx(n: Array, m: Array, /) -> Array:
    """Index for the coefficients."""
    # (0, 0) -> 0
    # (1, -1) -> 1
    # (1, 0) -> 2
    xp = array_namespace(n, m)
    m_abs = xp.abs(m)
    return xp.where(m_abs > n, -1, n * (n + 1) + m)


@jit
def idx_all(n_end: int, /, xp: ArrayNamespace, dtype: Any, device: Any) -> tuple[Array, Array]:
    dtype = dtype or xp.int32
    n = xp.arange(n_end, dtype=dtype, device=device)[:, None]
    m = xp.arange(-n_end + 1, n_end, dtype=dtype, device=device)[None, :]
    n, m = xp.broadcast_arrays(n, m)
    mask = n >= xp.abs(m)
    return n[mask], m[mask]


@jit
def ndim_harm(n_end: int, /) -> int:
    """Number of spherical harmonics which degree is less than n_end."""
    return n_end**2


@jit
def minus_1_power(x: Array, /) -> Array:
    return 1 - 2 * (x % 2)


@jit
def a(n: Array, m: Array, /) -> Array:
    xp = array_namespace(n, m)
    m_abs = xp.abs(m)
    return xp.where(
        m_abs > n,
        0,
        xp.sqrt((n + m_abs + 1) * (n - m_abs + 1) / ((2 * n + 1) * (2 * n + 3))),
    )


@jit
def b(n: Array, m: Array, /) -> Array:
    xp = array_namespace(n, m)
    m_abs = xp.abs(m)
    return xp.where(
        m_abs > n,
        0,
        xp.sqrt((n - m - 1) * (n - m) / ((2 * n - 1) * (2 * n + 1))) * xp.where(m >= 0, 1, -1),
    )


@jit
def getitem_outer_zero(
    array: Array,
    indices: tuple[int | slice | EllipsisType | Array | None, ...],
    /,
    *,
    axis: int = 0,
) -> Array:
    len_axis = array.shape[axis]
    index_axis = indices[axis]
    array = array[indices]
    array[..., (index_axis < 0) | (index_axis >= len_axis)] = 0  # type: ignore
    return array


def translational_coefficients_sectorial_init(
    kr: Array, theta: Array, phi: Array, same: bool, n_end: int, /
) -> Array:
    """Initial values of sectorial translational coefficients (E|F)^{m',0}_{n', 0}

    Parameters
    ----------
    kr : Array
        k * r of shape (...,)
    theta : Array
        polar angle of shape (...,)
    phi : Array
        azimuthal angle of shape (...,)
    same : bool
        If True, return (R|R) = (S|S).
        If False, return (S|R).
    n_end : int
        Maximum degree of spherical harmonics.

    Returns
    -------
    Array
        Initial sectorial translational coefficients of shape (..., ndim_harm(n_end),)
    """
    xp = array_namespace(kr, theta, phi)
    n, m = idx_all(2 * n_end - 1, xp=xp, dtype=xp.int32, device=kr.device)
    # (E|F)^{m' 0}_{n' 0} = (E|F)^{m' 0}_{n'}
    if not same:
        # 4.43
        return (
            minus_1_power(n)
            * xp.sqrt(xp.asarray(4.0, dtype=kr.dtype, device=kr.device) * xp.pi)
            * S_all(kr, theta, phi, n_end=2 * n_end - 1)[..., idx(n, -m)]
        )
    else:
        # 4.58
        return (
            minus_1_power(n)
            * xp.sqrt(xp.asarray(4.0, dtype=kr.dtype, device=kr.device) * xp.pi)
            * R_all(kr, theta, phi, n_end=2 * n_end - 1)[..., idx(n, -m)]
        )


@jit
def translational_coefficients_sectorial_n_m(
    *,
    n_end: int,
    translational_coefficients_sectorial_init: Array,
) -> Array:
    """Sectorial translational coefficients (E|F)^{m',m}_{n',n=|m|}

    Parameters
    ----------
    n_end : int
        Maximum degree of spherical harmonics.
    translational_coefficients_sectorial_init : Array
        Initial sectorial translational coefficients of shape (..., ndim_harm(n_end),)

    Returns
    -------
    Array
        Sectorial translational coefficients [(m',n'),m]
        of shape (..., ndim_harm(n_end), 2*n_end-1).
        While the array shape is redundant, we give up further optimization
        because the batched axis in calculation (first) and used axis (last) are different.
    """
    xp = array_namespace(translational_coefficients_sectorial_init)
    shape = translational_coefficients_sectorial_init.shape[:-1]
    dtype = translational_coefficients_sectorial_init.dtype
    device = translational_coefficients_sectorial_init.device
    result = xp.zeros((*shape, ndim_harm(2 * n_end - 1), 4 * n_end - 1), dtype=dtype, device=device)
    result[..., :, 0] = translational_coefficients_sectorial_init
    if dtype == xp.complex64:
        dtype = xp.float32
    elif dtype == xp.complex128:
        dtype = xp.float64
    # 4.67
    for m in range(2 * n_end - 2):
        nd, md = idx_all(2 * n_end - abs(m) - 2, xp=xp, dtype=xp.int32, device=device)
        result[..., idx(nd, md), m + 1] = (
            1
            / b(
                xp.asarray(m + 1, dtype=dtype, device=device),
                xp.asarray(-m - 1, dtype=dtype, device=device),
            )
            * (
                b(nd, -md) * getitem_outer_zero(result, (..., idx(nd - 1, md - 1), m), axis=-2)
                - b(nd + 1, md - 1)
                * getitem_outer_zero(result, (..., idx(nd + 1, md - 1), m), axis=-2)
            )
        )
    # 4.68
    for m in range(2 * n_end - 2):
        nd, md = idx_all(2 * n_end - abs(m) - 2, xp=xp, dtype=xp.int32, device=device)
        result[..., idx(nd, md), -m - 1] = (
            1
            / b(
                xp.asarray(m + 1, dtype=dtype, device=device),
                xp.asarray(-m - 1, dtype=dtype, device=device),
            )
            * (
                b(nd, md) * getitem_outer_zero(result, (..., idx(nd - 1, md + 1), -m), axis=-2)
                - b(nd + 1, -md - 1)
                * getitem_outer_zero(result, (..., idx(nd + 1, md + 1), -m), axis=-2)
            )
        )
    return result


def flip_symmetric_array(input: Array, /, *, axis: int = 0) -> Array:
    """
    Flip a symmetric array.

    Parameters
    ----------
    input : Array
        The input array.
    axis : int, optional
        The axis to flip, by default 0
    include_zero_twice : bool, optional
        If True, the zeroth element is included twice, by default False

    Returns
    -------
    Array
        The flipped array.
        Forall a < input.shape[axis] result[-a-1] = result[a] = input[a] = input[-a-1]

    """
    xp = array_namespace(input)
    if axis < 0:
        zero = input[(..., slice(0, 1)) + (slice(None),) * (-axis - 1)]
        nonzero = input[(..., slice(1, None)) + (slice(None),) * (-axis - 1)]
    else:
        zero = input[
            (
                slice(
                    None,
                ),
            )
            * axis
            + (slice(0, 1), ...)
        ]
        nonzero = input[
            (
                slice(
                    None,
                ),
            )
            * axis
            + (slice(1, None), ...)
        ]
    return xp.concat([zero, xp.flip(nonzero, axis=axis)], axis=axis)


def translational_coefficients_sectorial_nd_md(
    *,
    n_end: int,
    translational_coefficients_sectorial_n_m: Array,
) -> Array:
    """Sectorial translational coefficients (E|F)^{m',m}_{n'=|m'|,n}

    Parameters
    ----------
    n_end : int
        Maximum degree of spherical harmonics.
    translational_coefficients_sectorial_n_m : Array
        Initial sectorial translational coefficients of shape (..., ndim_harm(n_end), 2*n_end-1)

    Returns
    -------
    Array
        Sectorial translational coefficients [m',(m,n)] of shape (..., 2*n_end-1, ndim_harm(n_end)).
        While the array shape is redundant, we give up further optimization
        because the batched axis in calculation (first) and used axis (last) are different.
    """
    xp = array_namespace(translational_coefficients_sectorial_n_m)
    device = translational_coefficients_sectorial_n_m.device
    m = xp.concat(
        (
            xp.arange(2 * n_end, dtype=xp.int32, device=device),
            xp.arange(-2 * n_end + 1, 0, dtype=xp.int32, device=device),
        ),
        axis=0,
    )
    n = xp.abs(m)
    nd, md = idx_all(2 * n_end - 1, xp=xp, dtype=xp.int32, device=device)
    # 4.61
    return (
        minus_1_power(n[:, None] + nd[None, :])
        * flip_symmetric_array(
            xp.moveaxis(translational_coefficients_sectorial_n_m, -1, -2), axis=-2
        )[..., idx(nd, -md)]
    )


@jit
def translational_coefficients_iter(
    *,
    m: int,
    md: int,
    n_end: int,
    translational_coefficients_sectorial_n_m: Array,
    translational_coefficients_sectorial_nd_md: Array,
    shape: tuple[int, ...],
) -> Array:
    xp = array_namespace(
        translational_coefficients_sectorial_n_m, translational_coefficients_sectorial_nd_md
    )
    dtype = translational_coefficients_sectorial_n_m.dtype
    device = translational_coefficients_sectorial_n_m.device
    mabs = abs(m)
    mdabs = abs(md)
    mlarger = max(mabs, mdabs)
    sized = 2 * n_end - mdabs - mlarger - 1
    size = 2 * n_end - mabs - mlarger - 1
    n_iter = n_end - mlarger - 1

    # [nd, n]
    md_m_fixed = xp.zeros((*shape, sized, size), dtype=dtype, device=device)
    md_m_fixed[..., :, 0] = translational_coefficients_sectorial_n_m
    md_m_fixed[..., 0, :] = translational_coefficients_sectorial_nd_md

    if dtype == xp.complex64:
        dtype = xp.float32
    elif dtype == xp.complex128:
        dtype = xp.float64
    # batch for nd, grow n
    ms = (
        (md, m),
        (m, md),
    )
    # del mabs, mdabs, m, md
    for m1, m2 in ms:
        m1abs = abs(m1)
        m2abs = abs(m2)
        # comments are for the first iteration
        for i in range(n_iter):
            # 4.26, 2nd term is the result
            n1 = slice(m1abs + i + 1, 2 * n_end - mlarger - i - 2)
            n1f = xp.arange(n1.start, n1.stop, dtype=xp.int32, device=device)
            n2f = xp.asarray(i + m2abs, dtype=dtype, device=device)
            m1f = xp.asarray(m1, dtype=dtype, device=device)
            m2f = xp.asarray(m2, dtype=dtype, device=device)
            md_m_n2_fixed = (
                -a(n1f, m1f) * md_m_fixed[..., i + 2 : (None if i == 0 else -i), i]  # 3rd
                + a(n1f - 1, m1f) * md_m_fixed[..., i : -i - 2, i]  # 4th
            )
            if i > 0:
                md_m_n2_fixed += a(n2f - 1, m2f) * md_m_fixed[..., i + 1 : -i - 1, i - 1]  # 1st
            md_m_fixed[..., i + 1 : -i - 1, i + 1] = md_m_n2_fixed / a(n2f, m2f)
        md_m_fixed = xp.moveaxis(md_m_fixed, -2, -1)
    return md_m_fixed[..., : n_end - abs(md), : n_end - abs(m)]


@pjit
def translational_coefficients_all(
    *,
    n_end: int,
    translational_coefficients_sectorial_m_n: Array,
    translational_coefficients_sectorial_md_nd: Array,
) -> Array:
    """Translational coefficients (E|F)^{m',m}_{n',n'}

    Parameters
    ----------
    n_end : int
        Maximum degree of spherical harmonics.
    translational_coefficients_sectorial_m_n : Array
        Sectorial translational coefficients [(m',n'),m] of shape (ndim_harm(n_end), 2*n_end-1)
    translational_coefficients_sectorial_md_nd : Array
        Sectorial translational coefficients [m',(m,n)] of shape (2*n_end-1, ndim_harm(n_end))

    Returns
    -------
    Array
        Translational coefficients [(m',n'),(m,n)] of shape (ndim_harm(n_end), ndim_harm(n_end))
    """
    xp = array_namespace(
        translational_coefficients_sectorial_m_n, translational_coefficients_sectorial_md_nd
    )
    dtype = translational_coefficients_sectorial_m_n.dtype
    device = translational_coefficients_sectorial_m_n.device
    shape = translational_coefficients_sectorial_m_n.shape[:-2]
    result = xp.zeros((*shape, ndim_harm(n_end), ndim_harm(n_end)), dtype=dtype, device=device)
    for m in prange(-n_end + 1, n_end):
        for md in prange(-n_end + 1, n_end):
            n = xp.arange(abs(m), n_end, dtype=xp.int32, device=device)[None, :]
            nd = xp.arange(abs(md), n_end, dtype=xp.int32, device=device)[:, None]
            mabs, mdabs = abs(m), abs(md)
            mlarger = max(mabs, mdabs)
            result[
                ...,
                idx(nd, xp.asarray(md, dtype=xp.int32, device=device)),
                idx(n, xp.asarray(m, dtype=xp.int32, device=device)),
            ] = translational_coefficients_iter(
                m=m,
                md=md,
                n_end=n_end,
                translational_coefficients_sectorial_n_m=translational_coefficients_sectorial_m_n[
                    ...,
                    idx(
                        xp.arange(mdabs, 2 * n_end - mlarger - 1, device=device, dtype=xp.int32),
                        xp.asarray(md, dtype=xp.int32, device=device),
                    ),
                    m,
                ],
                translational_coefficients_sectorial_nd_md=translational_coefficients_sectorial_md_nd[
                    ...,
                    md,
                    idx(
                        xp.arange(mabs, 2 * n_end - mlarger - 1, device=device, dtype=xp.int32),
                        xp.asarray(m, dtype=xp.int32, device=device),
                    ),
                ],
                shape=shape,
            )
    return result


def translational_coefficients(
    kr: Array, theta: Array, phi: Array, *, same: bool, n_end: int
) -> Array:
    """Initial values of sectorial translational coefficients (E|F)^{m',m}_{0, 0}

    Parameters
    ----------
    kr : Array
        k * r of shape (...,)
    theta : Array
        polar angle of shape (...,)
    phi : Array
        azimuthal angle of shape (...,)
    same : bool
        If True, return (R|R) = (S|S).
        If False, return (S|R).
    n_end : int
        Maximum degree of spherical harmonics.

    Returns
    -------
    Array
        Initial sectorial translational coefficients of shape (ndim_harm(n_end),)
    """
    translational_coefficients_sectorial_init_ = translational_coefficients_sectorial_init(
        kr, theta, phi, same, n_end
    )
    translational_coefficients_sectorial_n_m_ = translational_coefficients_sectorial_n_m(
        n_end=n_end,
        translational_coefficients_sectorial_init=translational_coefficients_sectorial_init_,
    )
    translational_coefficients_sectorial_nd_md_ = translational_coefficients_sectorial_nd_md(
        n_end=n_end,
        translational_coefficients_sectorial_n_m=translational_coefficients_sectorial_n_m_,
    )
    return translational_coefficients_all(
        n_end=n_end,
        translational_coefficients_sectorial_m_n=translational_coefficients_sectorial_n_m_,
        translational_coefficients_sectorial_md_nd=translational_coefficients_sectorial_nd_md_,
    )
