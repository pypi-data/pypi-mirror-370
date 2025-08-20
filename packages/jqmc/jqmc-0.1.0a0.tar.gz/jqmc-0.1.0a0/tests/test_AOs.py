"""collections of unit tests."""

# Copyright (C) 2024- Kosuke Nakano
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
# * Neither the name of the jqmc project nor the names of its
#   contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import itertools

import jax
import numpy as np
import pytest
from numpy import linalg as LA
from numpy.testing import assert_almost_equal

from ..jqmc.atomic_orbital import (
    AOs_cart_data,
    AOs_sphe_data,
    _compute_S_l_m_debug,
    _compute_S_l_m_jax,
    compute_AOs_cart_debug,
    compute_AOs_cart_jax,
    compute_AOs_grad_debug,
    compute_AOs_grad_jax,
    compute_AOs_laplacian_debug,
    compute_AOs_laplacian_jax,
    compute_AOs_shpe_debug,
    compute_AOs_sphe_jax,
)
from ..jqmc.structure import Structure_data

# JAX float64
jax.config.update("jax_enable_x64", True)
jax.config.update("jax_traceback_filtering", "off")


@pytest.mark.parametrize(
    ["l", "m"],
    list(itertools.chain.from_iterable([[pytest.param(l, m, id=f"l={l}, m={m}") for m in range(-l, l + 1)] for l in range(7)])),
)
def test_spherical_harmonics_hard_coded_vs_analytic_expressions(l, m):
    """Test the spherical harmonics."""

    def Y_l_m_ref(l=0, m=0, r_cart_rel=None):
        if r_cart_rel is None:
            r_cart_rel = [0.0, 0.0, 0.0]
        """See https://en.wikipedia.org/wiki/Table_of_spherical_harmonics#Real_spherical_harmonics"""
        x, y, z = r_cart_rel[..., 0], r_cart_rel[..., 1], r_cart_rel[..., 2]
        r = np.sqrt(x**2 + y**2 + z**2)
        # s orbital
        if (l, m) == (0, 0):
            return 1.0 / 2.0 * np.sqrt(1.0 / np.pi) * r**0.0
        # p orbitals
        elif (l, m) == (1, -1):
            return np.sqrt(3.0 / (4 * np.pi)) * y / r
        elif (l, m) == (1, 0):
            return np.sqrt(3.0 / (4 * np.pi)) * z / r
        elif (l, m) == (1, 1):
            return np.sqrt(3.0 / (4 * np.pi)) * x / r
        # d orbitals
        elif (l, m) == (2, -2):
            return 1.0 / 2.0 * np.sqrt(15.0 / (np.pi)) * x * y / r**2
        elif (l, m) == (2, -1):
            return 1.0 / 2.0 * np.sqrt(15.0 / (np.pi)) * y * z / r**2
        elif (l, m) == (2, 0):
            return 1.0 / 4.0 * np.sqrt(5.0 / (np.pi)) * (3 * z**2 - r**2) / r**2
        elif (l, m) == (2, 1):
            return 1.0 / 2.0 * np.sqrt(15.0 / (np.pi)) * x * z / r**2
        elif (l, m) == (2, 2):
            return 1.0 / 4.0 * np.sqrt(15.0 / (np.pi)) * (x**2 - y**2) / r**2
        # f orbitals
        elif (l, m) == (3, -3):
            return 1.0 / 4.0 * np.sqrt(35.0 / (2 * np.pi)) * y * (3 * x**2 - y**2) / r**3
        elif (l, m) == (3, -2):
            return 1.0 / 2.0 * np.sqrt(105.0 / (np.pi)) * x * y * z / r**3
        elif (l, m) == (3, -1):
            return 1.0 / 4.0 * np.sqrt(21.0 / (2 * np.pi)) * y * (5 * z**2 - r**2) / r**3
        elif (l, m) == (3, 0):
            return 1.0 / 4.0 * np.sqrt(7.0 / (np.pi)) * (5 * z**3 - 3 * z * r**2) / r**3
        elif (l, m) == (3, 1):
            return 1.0 / 4.0 * np.sqrt(21.0 / (2 * np.pi)) * x * (5 * z**2 - r**2) / r**3
        elif (l, m) == (3, 2):
            return 1.0 / 4.0 * np.sqrt(105.0 / (np.pi)) * (x**2 - y**2) * z / r**3
        elif (l, m) == (3, 3):
            return 1.0 / 4.0 * np.sqrt(35.0 / (2 * np.pi)) * x * (x**2 - 3 * y**2) / r**3
        # g orbitals
        elif (l, m) == (4, -4):
            return 3.0 / 4.0 * np.sqrt(35.0 / (np.pi)) * x * y * (x**2 - y**2) / r**4
        elif (l, m) == (4, -3):
            return 3.0 / 4.0 * np.sqrt(35.0 / (2 * np.pi)) * y * z * (3 * x**2 - y**2) / r**4
        elif (l, m) == (4, -2):
            return 3.0 / 4.0 * np.sqrt(5.0 / (np.pi)) * x * y * (7 * z**2 - r**2) / r**4
        elif (l, m) == (4, -1):
            return 3.0 / 4.0 * np.sqrt(5.0 / (2 * np.pi)) * y * (7 * z**3 - 3 * z * r**2) / r**4
        elif (l, m) == (4, 0):
            return 3.0 / 16.0 * np.sqrt(1.0 / (np.pi)) * (35 * z**4 - 30 * z**2 * r**2 + 3 * r**4) / r**4
        elif (l, m) == (4, 1):
            return 3.0 / 4.0 * np.sqrt(5.0 / (2 * np.pi)) * x * (7 * z**3 - 3 * z * r**2) / r**4
        elif (l, m) == (4, 2):
            return 3.0 / 8.0 * np.sqrt(5.0 / (np.pi)) * (x**2 - y**2) * (7 * z**2 - r**2) / r**4
        elif (l, m) == (4, 3):
            return 3.0 / 4.0 * np.sqrt(35.0 / (2 * np.pi)) * x * z * (x**2 - 3 * y**2) / r**4
        elif (l, m) == (4, 4):
            return 3.0 / 16.0 * np.sqrt(35.0 / (np.pi)) * (x**2 * (x**2 - 3 * y**2) - y**2 * (3 * x**2 - y**2)) / r**4
        elif (l, m) == (5, -5):
            return 3.0 / 16.0 * np.sqrt(77.0 / (2 * np.pi)) * (5 * x**4 * y - 10 * x**2 * y**3 + y**5) / r**5
        elif (l, m) == (5, -4):
            return 3.0 / 16.0 * np.sqrt(385.0 / np.pi) * 4 * x * y * z * (x**2 - y**2) / r**5
        elif (l, m) == (5, -3):
            return 1.0 / 16.0 * np.sqrt(385.0 / (2 * np.pi)) * -1 * (y**3 - 3 * x**2 * y) * (9 * z**2 - r**2) / r**5
        elif (l, m) == (5, -2):
            return 1.0 / 8.0 * np.sqrt(1155 / np.pi) * 2 * x * y * (3 * z**3 - z * r**2) / r**5
        elif (l, m) == (5, -1):
            return 1.0 / 16.0 * np.sqrt(165 / np.pi) * y * (21 * z**4 - 14 * z**2 * r**2 + r**4) / r**5
        elif (l, m) == (5, 0):
            return 1.0 / 16.0 * np.sqrt(11 / np.pi) * (63 * z**5 - 70 * z**3 * r**2 + 15 * z * r**4) / r**5
        elif (l, m) == (5, 1):
            return 1.0 / 16.0 * np.sqrt(165 / np.pi) * x * (21 * z**4 - 14 * z**2 * r**2 + r**4) / r**5
        elif (l, m) == (5, 2):
            return 1.0 / 8.0 * np.sqrt(1155 / np.pi) * (x**2 - y**2) * (3 * z**3 - z * r**2) / r**5
        elif (l, m) == (5, 3):
            return 1.0 / 16.0 * np.sqrt(385.0 / (2 * np.pi)) * (x**3 - 3 * x * y**2) * (9 * z**2 - r**2) / r**5
        elif (l, m) == (5, 4):
            return 3.0 / 16.0 * np.sqrt(385.0 / np.pi) * (x**2 * z * (x**2 - 3 * y**2) - y**2 * z * (3 * x**2 - y**2)) / r**5
        elif (l, m) == (5, 5):
            return 3.0 / 16.0 * np.sqrt(77.0 / (2 * np.pi)) * (x**5 - 10 * x**3 * y**2 + 5 * x * y**4) / r**5
        elif (l, m) == (6, -6):
            return 1.0 / 64.0 * np.sqrt(6006.0 / np.pi) * (6 * x**5 * y - 20 * x**3 * y**3 + 6 * x * y**5) / r**6
        elif (l, m) == (6, -5):
            return 3.0 / 32.0 * np.sqrt(2002.0 / np.pi) * z * (5 * x**4 * y - 10 * x**2 * y**3 + y**5) / r**6
        elif (l, m) == (6, -4):
            return 3.0 / 32.0 * np.sqrt(91.0 / np.pi) * 4 * x * y * (11 * z**2 - r**2) * (x**2 - y**2) / r**6
        elif (l, m) == (6, -3):
            return 1.0 / 32.0 * np.sqrt(2730.0 / np.pi) * -1 * (11 * z**3 - 3 * z * r**2) * (y**3 - 3 * x**2 * y) / r**6
        elif (l, m) == (6, -2):
            return 1.0 / 64.0 * np.sqrt(2730.0 / np.pi) * 2 * x * y * (33 * z**4 - 18 * z**2 * r**2 + r**4) / r**6
        elif (l, m) == (6, -1):
            return 1.0 / 16.0 * np.sqrt(273.0 / np.pi) * y * (33 * z**5 - 30 * z**3 * r**2 + 5 * z * r**4) / r**6
        elif (l, m) == (6, 0):
            return 1.0 / 32.0 * np.sqrt(13.0 / np.pi) * (231 * z**6 - 315 * z**4 * r**2 + 105 * z**2 * r**4 - 5 * r**6) / r**6
        elif (l, m) == (6, 1):
            return 1.0 / 16.0 * np.sqrt(273.0 / np.pi) * x * (33 * z**5 - 30 * z**3 * r**2 + 5 * z * r**4) / r**6
        elif (l, m) == (6, 2):
            return 1.0 / 64.0 * np.sqrt(2730.0 / np.pi) * (x**2 - y**2) * (33 * z**4 - 18 * z**2 * r**2 + r**4) / r**6
        elif (l, m) == (6, 3):
            return 1.0 / 32.0 * np.sqrt(2730.0 / np.pi) * (11 * z**3 - 3 * z * r**2) * (x**3 - 3 * x * y**2) / r**6
        elif (l, m) == (6, 4):
            return (
                3.0
                / 32.0
                * np.sqrt(91.0 / np.pi)
                * (11 * z**2 - r**2)
                * (x**2 * (x**2 - 3 * y**2) + y**2 * (y**2 - 3 * x**2))
                / r**6
            )
        elif (l, m) == (6, 5):
            return 3.0 / 32.0 * np.sqrt(2002.0 / np.pi) * z * (x**5 - 10 * x**3 * y**2 + 5 * x * y**4) / r**6
        elif (l, m) == (6, 6):
            return 1.0 / 64.0 * np.sqrt(6006.0 / np.pi) * (x**6 - 15 * x**4 * y**2 + 15 * x**2 * y**4 - y**6) / r**6
        else:
            raise NotImplementedError

    num_samples = 1
    R_cart = [0.0, 0.0, 1.0]
    r_cart_min, r_cart_max = -10.0, 10.0
    r_x_rand = (r_cart_max - r_cart_min) * np.random.rand(num_samples) + r_cart_min
    r_y_rand = (r_cart_max - r_cart_min) * np.random.rand(num_samples) + r_cart_min
    r_z_rand = (r_cart_max - r_cart_min) * np.random.rand(num_samples) + r_cart_min

    for r_cart in zip(r_x_rand, r_y_rand, r_z_rand):
        r_norm = LA.norm(np.array(R_cart) - np.array(r_cart))
        r_cart_rel = np.array(r_cart) - np.array(R_cart)
        test_S_lm = _compute_S_l_m_debug(
            atomic_center_cart=R_cart,
            angular_momentum=l,
            magnetic_quantum_number=m,
            r_cart=r_cart,
        )
        ref_S_lm = np.sqrt((4 * np.pi) / (2 * l + 1)) * r_norm**l * Y_l_m_ref(l=l, m=m, r_cart_rel=r_cart_rel)
        assert_almost_equal(test_S_lm, ref_S_lm, decimal=8)

    jax.clear_caches()


def test_solid_harmonics_hard_coded_vs_analytic_expressions():
    """Test the solid harmonics with a batch."""
    seed = 34487
    np.random.seed(seed)

    num_R_cart_samples = 49  # fixed
    num_r_cart_samples = 10
    r_cart_min, r_cart_max = -1.0, 1.0
    R_cart_min, R_cart_max = 0.0, 0.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min
    r_R_diffs_uq = r_carts[None, :, :] - R_carts[:, None, :]

    ml_list = list(itertools.chain.from_iterable([[(l, m) for m in range(-l, l + 1)] for l in range(7)]))

    # S_l_m debug
    S_l_m_debug = np.array(
        [
            [
                [
                    _compute_S_l_m_debug(
                        angular_momentum=l, magnetic_quantum_number=m, atomic_center_cart=R_cart, r_cart=r_cart
                    )
                    for r_cart in r_carts
                ]
                for R_cart in R_carts
            ]
            for l, m in ml_list
        ]
    )

    # S_l_m jax
    _, S_l_m_jax = _compute_S_l_m_jax(r_R_diffs_uq)

    # print(f"batch_S_l_m.shape = {batch_S_l_m.shape}.")

    np.testing.assert_array_almost_equal(S_l_m_debug, S_l_m_jax, decimal=10)
    jax.clear_caches()


def test_AOs_w_spherical_angular_part_comparing_jax_and_debug_implemenetations():
    """Test the AOs computation, comparing the JAX and debug implementations."""
    ml_list = list(itertools.chain.from_iterable([[(l, m) for m in range(-l, l + 1)] for l in range(7)]))
    num_el = 100
    num_ao = len(ml_list)
    num_ao_prim = len(ml_list)
    orbital_indices = list(range(len(ml_list)))
    exponents = [5.0] * len(ml_list)
    coefficients = [1.0] * len(ml_list)
    angular_momentums = [l for l, _ in ml_list]
    magnetic_quantum_numbers = [m for _, m in ml_list]

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    magnetic_quantum_numbers = tuple(magnetic_quantum_numbers)

    num_r_cart_samples = num_el
    num_R_cart_samples = num_ao
    r_cart_min, r_cart_max = -1.0, 1.0
    R_cart_min, R_cart_max = 0.0, 0.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_sphe_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        magnetic_quantum_numbers=magnetic_quantum_numbers,
    )
    aos_data.sanity_check()

    aos_jax = compute_AOs_sphe_jax(aos_data=aos_data, r_carts=r_carts)
    aos_debug = compute_AOs_shpe_debug(aos_data=aos_data, r_carts=r_carts)

    assert np.allclose(aos_jax, aos_debug, rtol=1e-12, atol=1e-05)

    num_el = 150
    num_ao = len(ml_list)
    num_ao_prim = len(ml_list)
    orbital_indices = list(range(len(ml_list)))
    exponents = [3.4] * len(ml_list)
    coefficients = [1.0] * len(ml_list)
    angular_momentums = angular_momentums
    magnetic_quantum_numbers = magnetic_quantum_numbers

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    magnetic_quantum_numbers = tuple(magnetic_quantum_numbers)

    num_r_cart_samples = num_el
    num_R_cart_samples = num_ao
    r_cart_min, r_cart_max = -1.0, 1.0
    R_cart_min, R_cart_max = -1.0, 1.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_sphe_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        magnetic_quantum_numbers=magnetic_quantum_numbers,
    )
    aos_data.sanity_check()

    aos_jax = compute_AOs_sphe_jax(aos_data=aos_data, r_carts=r_carts)
    aos_debug = compute_AOs_shpe_debug(aos_data=aos_data, r_carts=r_carts)

    assert np.allclose(aos_jax, aos_debug, rtol=1e-12, atol=1e-05)

    jax.clear_caches()


def test_AOs_w_cartesian_angular_part_comparing_jax_and_debug_implemenetations():
    """Test the AOs computation, comparing the JAX and debug implementations."""
    l_max = 10
    angular_momentums = []
    polynominal_order_x = []
    polynominal_order_y = []
    polynominal_order_z = []
    for l in range(l_max):
        poly_orders = ["".join(p) for p in itertools.combinations_with_replacement("xyz", l)]
        poly_x = [poly_order.count("x") for poly_order in poly_orders]
        poly_y = [poly_order.count("y") for poly_order in poly_orders]
        poly_z = [poly_order.count("z") for poly_order in poly_orders]
        num_ao_mag_moms = len(poly_orders)
        angular_momentums += [l] * num_ao_mag_moms
        polynominal_order_x += poly_x
        polynominal_order_y += poly_y
        polynominal_order_z += poly_z

    num_el = 100
    num_ao = len(angular_momentums)
    num_ao_prim = num_ao
    orbital_indices = list(range(num_ao))
    exponents = [5.0] * num_ao
    coefficients = [1.0] * num_ao

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    polynominal_order_x = tuple(polynominal_order_x)
    polynominal_order_y = tuple(polynominal_order_y)
    polynominal_order_z = tuple(polynominal_order_z)

    num_r_cart_samples = num_el
    num_R_cart_samples = num_ao
    r_cart_min, r_cart_max = -1.0, 1.0
    R_cart_min, R_cart_max = 0.0, 0.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_cart_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        polynominal_order_x=polynominal_order_x,
        polynominal_order_y=polynominal_order_y,
        polynominal_order_z=polynominal_order_z,
    )
    aos_data.sanity_check()

    aos_jax = compute_AOs_cart_jax(aos_data=aos_data, r_carts=r_carts)
    aos_debug = compute_AOs_cart_debug(aos_data=aos_data, r_carts=r_carts)

    assert np.allclose(aos_jax, aos_debug, rtol=1e-12, atol=1e-05)

    jax.clear_caches()


@pytest.mark.obsolete(reasons="Gradients are now implemented by fully exploiting JAX modules.")
def test_AOs_comparing_auto_and_numerical_grads():
    """Test the grad AOs computation, comparing the JAX and debug implementations."""
    num_r_cart_samples = 10
    num_R_cart_samples = 4
    r_cart_min, r_cart_max = -5.0, +5.0
    R_cart_min, R_cart_max = -3.0, +3.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    num_ao = 4
    num_ao_prim = 5
    orbital_indices = [0, 1, 2, 2, 3]
    exponents = [3.0, 1.0, 0.5, 0.5, 0.5]
    coefficients = [1.0, 1.0, 0.5, 0.5, 0.5]
    angular_momentums = [0, 0, 0, 0]
    magnetic_quantum_numbers = [0, 0, 0, 0]

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    magnetic_quantum_numbers = tuple(magnetic_quantum_numbers)

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_sphe_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        magnetic_quantum_numbers=magnetic_quantum_numbers,
    )
    aos_data.sanity_check()

    ao_matrix_grad_x_auto, ao_matrix_grad_y_auto, ao_matrix_grad_z_auto = compute_AOs_grad_jax(
        aos_data=aos_data, r_carts=r_carts
    )

    (
        ao_matrix_grad_x_numerical,
        ao_matrix_grad_y_numerical,
        ao_matrix_grad_z_numerical,
    ) = compute_AOs_grad_debug(aos_data=aos_data, r_carts=r_carts)

    np.testing.assert_array_almost_equal(ao_matrix_grad_x_auto, ao_matrix_grad_x_numerical, decimal=7)
    np.testing.assert_array_almost_equal(ao_matrix_grad_y_auto, ao_matrix_grad_y_numerical, decimal=7)

    np.testing.assert_array_almost_equal(ao_matrix_grad_z_auto, ao_matrix_grad_z_numerical, decimal=7)

    num_r_cart_samples = 2
    num_R_cart_samples = 4
    r_cart_min, r_cart_max = -3.0, +3.0
    R_cart_min, R_cart_max = -3.0, +3.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    num_ao = 4
    num_ao_prim = 5
    orbital_indices = [0, 1, 2, 2, 3]
    exponents = [3.0, 1.0, 0.5, 0.5, 0.5]
    coefficients = [1.0, 1.0, 0.5, 0.5, 0.5]
    angular_momentums = [0, 0, 0, 0]
    magnetic_quantum_numbers = [0, 0, 0, 0]

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    magnetic_quantum_numbers = tuple(magnetic_quantum_numbers)

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_sphe_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        magnetic_quantum_numbers=magnetic_quantum_numbers,
    )
    aos_data.sanity_check()

    ao_matrix_grad_x_auto, ao_matrix_grad_y_auto, ao_matrix_grad_z_auto = compute_AOs_grad_jax(
        aos_data=aos_data, r_carts=r_carts
    )

    (
        ao_matrix_grad_x_numerical,
        ao_matrix_grad_y_numerical,
        ao_matrix_grad_z_numerical,
    ) = compute_AOs_grad_debug(aos_data=aos_data, r_carts=r_carts)

    np.testing.assert_array_almost_equal(ao_matrix_grad_x_auto, ao_matrix_grad_x_numerical, decimal=7)
    np.testing.assert_array_almost_equal(ao_matrix_grad_y_auto, ao_matrix_grad_y_numerical, decimal=7)

    np.testing.assert_array_almost_equal(ao_matrix_grad_z_auto, ao_matrix_grad_z_numerical, decimal=7)

    jax.clear_caches()


@pytest.mark.obsolete(reasons="Laplacians are now implemented by fully exploiting JAX modules.")
def test_AOs_comparing_auto_and_numerical_laplacians():
    """Test the laplacian AOs computation, comparing the JAX and debug implementations."""
    num_r_cart_samples = 10
    num_R_cart_samples = 3
    r_cart_min, r_cart_max = -5.0, +5.0
    R_cart_min, R_cart_max = -3.0, +3.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    num_ao = 3
    num_ao_prim = 4
    orbital_indices = [0, 1, 2, 2]
    exponents = [3.0, 1.0, 0.5, 0.5]
    coefficients = [1.0, 1.0, 0.5, 0.5]
    angular_momentums = [0, 0, 0]
    magnetic_quantum_numbers = [0, 0, 0]

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    magnetic_quantum_numbers = tuple(magnetic_quantum_numbers)

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_sphe_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        magnetic_quantum_numbers=magnetic_quantum_numbers,
    )
    aos_data.sanity_check()

    ao_matrix_laplacian_numerical = compute_AOs_laplacian_jax(aos_data=aos_data, r_carts=r_carts)

    ao_matrix_laplacian_auto = compute_AOs_laplacian_debug(aos_data=aos_data, r_carts=r_carts)

    np.testing.assert_array_almost_equal(ao_matrix_laplacian_auto, ao_matrix_laplacian_numerical, decimal=5)

    num_r_cart_samples = 2
    num_R_cart_samples = 3
    r_cart_min, r_cart_max = -3.0, +3.0
    R_cart_min, R_cart_max = -3.0, +3.0
    r_carts = (r_cart_max - r_cart_min) * np.random.rand(num_r_cart_samples, 3) + r_cart_min
    R_carts = (R_cart_max - R_cart_min) * np.random.rand(num_R_cart_samples, 3) + R_cart_min

    num_ao = 3
    num_ao_prim = 3
    orbital_indices = [0, 1, 2]
    exponents = [30.0, 10.0, 8.5]
    coefficients = [1.0, 1.0, 1.0]
    angular_momentums = [1, 1, 1]
    magnetic_quantum_numbers = [0, 1, -1]

    orbital_indices = tuple(orbital_indices)
    exponents = tuple(exponents)
    coefficients = tuple(coefficients)
    angular_momentums = tuple(angular_momentums)
    magnetic_quantum_numbers = tuple(magnetic_quantum_numbers)

    structure_data = Structure_data(
        pbc_flag=False,
        positions=R_carts,
        atomic_numbers=tuple([0] * num_R_cart_samples),
        element_symbols=tuple(["X"] * num_R_cart_samples),
        atomic_labels=tuple(["X"] * num_R_cart_samples),
    )
    structure_data.sanity_check()

    aos_data = AOs_sphe_data(
        structure_data=structure_data,
        nucleus_index=tuple(list(range(num_R_cart_samples))),
        num_ao=num_ao,
        num_ao_prim=num_ao_prim,
        orbital_indices=orbital_indices,
        exponents=exponents,
        coefficients=coefficients,
        angular_momentums=angular_momentums,
        magnetic_quantum_numbers=magnetic_quantum_numbers,
    )
    aos_data.sanity_check()

    ao_matrix_laplacian_numerical = compute_AOs_laplacian_jax(aos_data=aos_data, r_carts=r_carts)

    ao_matrix_laplacian_auto = compute_AOs_laplacian_debug(aos_data=aos_data, r_carts=r_carts)

    np.testing.assert_array_almost_equal(ao_matrix_laplacian_auto, ao_matrix_laplacian_numerical, decimal=5)

    jax.clear_caches()


if __name__ == "__main__":
    from logging import Formatter, StreamHandler, getLogger

    logger = getLogger("jqmc")
    logger.setLevel("INFO")
    stream_handler = StreamHandler()
    stream_handler.setLevel("INFO")
    handler_format = Formatter("%(name)s - %(levelname)s - %(lineno)d - %(message)s")
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)
