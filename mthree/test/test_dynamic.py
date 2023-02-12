# This code is part of Mthree.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module

"""Test matrix elements"""
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import FakeKolkata

import mthree


def test_dynamic_bv():
    """Test that one can mitigate dynamic BV"""
    backend = FakeKolkata()

    N = 5
    shots = 1e4

    qc = dynamic_bv('1'*N)
    trans_qc = transpile(qc, backend, optimization_level=3,
                         seed_transpiler=12345)

    # Verify that mapping is returning the same qubit (1)
    # for all the classical bits
    mapping = mthree.utils.final_measurement_mapping(trans_qc)
    assert mapping == {0: 1, 1: 1, 2: 1, 3: 1, 4: 1}

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(mapping, method='independent')
    # Check that only the 1 qubit is populated in the cals
    for idx, mat in enumerate(mit.single_qubit_cals):
        if idx == 1:
            assert mat is not None
        else:
            assert mat is None

    counts = backend.run(trans_qc, shots=shots).result().get_counts()
    quasis = mit.apply_correction(counts, mapping)

    assert quasis['1'*N] > counts['1'*N]/shots
    assert quasis['1'*N] > 0.97


def dynamic_bv(bitstring):
    """Create a Bernstein-Vazirani circuit from a given bitstring.

    Parameters:
        bitstring (str): A bitstring.

    Returns:
        QuantumCircuit: Output circuit.
    """
    qc = QuantumCircuit(2, len(bitstring))

    # Prepare the |-x> state on target qubit
    qc.x(1)
    qc.h(1)

    # For each bit (0 or 1) build a simple circuit block
    for idx, bit in enumerate(bitstring[::-1]):

        # Initial H gate on control
        qc.h(0)
        # If bit=1, do a CNOT gate
        if int(bit):
            qc.cx(0, 1)
        # Final H gate to convert phase to computational-basis
        qc.h(0)
        # Measure
        qc.measure(0, idx)

        # If not at the final bit, recycle and reset qubits
        if idx != (len(bitstring)-1):
            # Reset control qubit for reuse
            qc.reset(0)
            # reset target qubit to minimize dephasing
            qc.reset(1)
            # Prepare the |-x> state on target qubit again
            qc.x(1)
            qc.h(1)

    return qc