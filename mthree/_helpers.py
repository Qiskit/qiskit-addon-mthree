# This code is part of Mthree.
#
# (C) Copyright IBM 2023.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module
"""
Helper functions
"""


def system_info(backend):
    """Return backend information needed by M3.

    Parameters:
        backend (BackendV1 or BackendV2): A Qiskit backend

    Returns:
        dict: Backend information
    """
    info_dict = {}
    info_dict["inoperable_qubits"] = []
    config = backend.configuration()
    if backend.version == 1:
        name = backend.name()
    else:
        name = backend.name
    info_dict["name"] = name
    info_dict["num_qubits"] = config.num_qubits
    _max_shots = config.max_shots
    info_dict["max_shots"] = _max_shots if _max_shots else int(1e6)
    info_dict["simulator"] = config.simulator
    if "fake" in info_dict["name"]:
        info_dict["simulator"] = True
    # max_circuits can be set a couple of ways
    max_circuits = getattr(config, "max_experiments", 1)
    if max_circuits == 1:
        max_circuits = getattr(config, "max_circuits", 1)
    if max_circuits == 1 and config.simulator:
        max_circuits = 1024
    info_dict["max_circuits"] = max_circuits
    # Look for faulty qubits.  Renaming to 'inoperable' here
    if hasattr(backend, "properties"):
        if hasattr(backend.properties(), "faulty_qubits"):
            info_dict["inoperable_qubits"] = backend.properties().faulty_qubits()
    return info_dict
