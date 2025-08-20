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

import os

import jax
import numpy as np

from ..jqmc.hamiltonians import Hamiltonian_data
from ..jqmc.jastrow_factor import Jastrow_data, Jastrow_one_body_data, Jastrow_three_body_data, Jastrow_two_body_data
from ..jqmc.jqmc_gfmc import GFMC_fixed_num_projection
from ..jqmc.trexio_wrapper import read_trexio_file
from ..jqmc.wavefunction import Wavefunction_data

# JAX float64
jax.config.update("jax_enable_x64", True)
jax.config.update("jax_traceback_filtering", "off")

'''
@pytest.mark.activate_if_disable_jit
def test_lrdmc_force_with_SWCT_ecp(request):
    """Test LRDMC force with SWCT."""
    if not request.config.getoption("--disable-jit"):
        pytest.skip(reason="A limilation of flux.struct (pytree_node=False) with @jit. See #24204 in jax repo.")
'''


def test_lrdmc_force_with_SWCT_ecp():
    """Test LRDMC force with SWCT."""
    # H2 dimer cc-pV5Z with Mitas ccECP (2 electrons, feasible).
    (
        structure_data,
        aos_data,
        _,
        _,
        geminal_mo_data,
        coulomb_potential_data,
    ) = read_trexio_file(trexio_file=os.path.join(os.path.dirname(__file__), "trexio_example_files", "H2_ecp_ccpvtz_cart.h5"))
    # """

    jastrow_onebody_data = None
    jastrow_twobody_data = Jastrow_two_body_data.init_jastrow_two_body_data(jastrow_2b_param=0.5)
    jastrow_threebody_data = Jastrow_three_body_data.init_jastrow_three_body_data(orb_data=aos_data)

    # define data
    jastrow_data = Jastrow_data(
        jastrow_one_body_data=jastrow_onebody_data,
        jastrow_two_body_data=jastrow_twobody_data,
        jastrow_three_body_data=jastrow_threebody_data,
    )

    wavefunction_data = Wavefunction_data(jastrow_data=jastrow_data, geminal_data=geminal_mo_data)

    hamiltonian_data = Hamiltonian_data(
        structure_data=structure_data,
        coulomb_potential_data=coulomb_potential_data,
        wavefunction_data=wavefunction_data,
    )

    # VMC parameters
    num_mcmc_warmup_steps = 5
    num_mcmc_bin_blocks = 5
    mcmc_seed = 34356

    # run GFMC
    gfmc = GFMC_fixed_num_projection(
        hamiltonian_data=hamiltonian_data,
        num_walkers=2,
        num_mcmc_per_measurement=30,
        num_gfmc_collect_steps=5,
        mcmc_seed=mcmc_seed,
        E_scf=-1.00,
        alat=0.30,
        non_local_move="tmove",
        comput_position_deriv=True,
    )

    gfmc.run(num_mcmc_steps=50)
    gfmc.get_E(
        num_mcmc_warmup_steps=num_mcmc_warmup_steps,
        num_mcmc_bin_blocks=num_mcmc_bin_blocks,
    )
    force_mean, force_std = gfmc.get_aF(
        num_mcmc_warmup_steps=num_mcmc_warmup_steps,
        num_mcmc_bin_blocks=num_mcmc_bin_blocks,
    )
    # print(force_mean, force_std)

    # See [J. Chem. Phys. 156, 034101 (2022)]
    np.testing.assert_almost_equal(np.array(force_mean[0]), -1.0 * np.array(force_mean[1]), decimal=6)
    np.testing.assert_almost_equal(np.array(force_std[0]), np.array(force_std[1]), decimal=6)


'''
@pytest.mark.activate_if_disable_jit
def test_lrdmc_force_with_SWCT_ae(request):
    """Test LRDMC force with SWCT."""
    if not request.config.getoption("--disable-jit"):
        pytest.skip(reason="A limilation of flux.struct (pytree_node=False) with @jit. See #24204 in jax repo.")
'''


def test_lrdmc_force_with_SWCT_ae():
    """Test LRDMC force with SWCT."""
    # H2 dimer cc-pV5Z with Mitas ccECP (2 electrons, feasible).
    (
        structure_data,
        aos_data,
        _,
        _,
        geminal_mo_data,
        coulomb_potential_data,
    ) = read_trexio_file(
        trexio_file=os.path.join(os.path.dirname(__file__), "trexio_example_files", "H2_ae_ccpvtz_cart.h5"), store_tuple=True
    )
    # """

    jastrow_onebody_data = Jastrow_one_body_data.init_jastrow_one_body_data(
        jastrow_1b_param=1.0, structure_data=structure_data, core_electrons=tuple([0, 0])
    )
    jastrow_twobody_data = Jastrow_two_body_data.init_jastrow_two_body_data(jastrow_2b_param=0.5)
    jastrow_threebody_data = Jastrow_three_body_data.init_jastrow_three_body_data(orb_data=aos_data)

    # define data
    jastrow_data = Jastrow_data(
        jastrow_one_body_data=jastrow_onebody_data,
        jastrow_two_body_data=jastrow_twobody_data,
        jastrow_three_body_data=jastrow_threebody_data,
    )

    wavefunction_data = Wavefunction_data(jastrow_data=jastrow_data, geminal_data=geminal_mo_data)

    hamiltonian_data = Hamiltonian_data(
        structure_data=structure_data,
        coulomb_potential_data=coulomb_potential_data,
        wavefunction_data=wavefunction_data,
    )

    # VMC parameters
    num_mcmc_warmup_steps = 5
    num_mcmc_bin_blocks = 5
    mcmc_seed = 34356

    # run GFMC
    gfmc = GFMC_fixed_num_projection(
        hamiltonian_data=hamiltonian_data,
        num_walkers=2,
        num_mcmc_per_measurement=30,
        num_gfmc_collect_steps=5,
        mcmc_seed=mcmc_seed,
        E_scf=-1.00,
        alat=0.30,
        non_local_move="tmove",
        comput_position_deriv=True,
    )

    gfmc.run(num_mcmc_steps=50)
    gfmc.get_E(
        num_mcmc_warmup_steps=num_mcmc_warmup_steps,
        num_mcmc_bin_blocks=num_mcmc_bin_blocks,
    )
    force_mean, force_std = gfmc.get_aF(
        num_mcmc_warmup_steps=num_mcmc_warmup_steps,
        num_mcmc_bin_blocks=num_mcmc_bin_blocks,
    )

    # See [J. Chem. Phys. 156, 034101 (2022)]
    np.testing.assert_almost_equal(np.array(force_mean[0]), -1.0 * np.array(force_mean[1]), decimal=6)
    np.testing.assert_almost_equal(np.array(force_std[0]), np.array(force_std[1]), decimal=6)


if __name__ == "__main__":
    from logging import Formatter, StreamHandler, getLogger

    logger = getLogger("jqmc")
    logger.setLevel("INFO")
    stream_handler = StreamHandler()
    stream_handler.setLevel("INFO")
    handler_format = Formatter("%(name)s - %(levelname)s - %(lineno)d - %(message)s")
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)
