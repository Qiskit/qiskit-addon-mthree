.. _runtime:

#############################
Using Runtime execution modes
#############################

The Qiskit Runtime has two execution modes, `Batch` and `Session`, that allow for grouping
multiple jobs.  You can include M3 calibration jobs in these modes using the `runtime_mode` argument 
in `mthree.M3Mitigation.cals_from_system`.  For example:

.. jupyter-execute::

    from qiskit_ibm_runtime import Batch
    from qiskit_ibm_runtime.fake_provider import FakeCasablancaV2
    import mthree

    backend = FakeCasablancaV2()
    batch = Batch(backend=backend)

    mit = mthree.M3Mitigation(backend)
    mit.cals_from_system(runtime_mode=batch); # This is where the Batch or Session goes


Note that if no `runtime_mode` is set, and the passed system is an IBM backend, then jobs are submitted in `Batch` mode automatically.  This mode is NOT closed by default, allowing users to include additional jobs.  This mode can be accessed via `mode = mit.system.get_mode()`
