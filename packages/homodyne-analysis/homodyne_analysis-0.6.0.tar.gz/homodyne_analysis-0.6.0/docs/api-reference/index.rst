API Reference
=============

Complete API documentation for the homodyne analysis package.

.. toctree::
   :maxdepth: 2
   :caption: Core Modules

   core
   mcmc
   models
   utilities

Core Classes
------------

* :class:`~homodyne.core.HomodyneAnalysisCore` - Main analysis orchestrator
* :class:`~homodyne.config.ConfigManager` - Configuration management
* :class:`~homodyne.optimization.mcmc.MCMCSampler` - Bayesian analysis

Quick Reference
---------------

**Essential Imports**:

.. code-block:: python

   from homodyne import HomodyneAnalysisCore, ConfigManager
   from homodyne.optimization.mcmc import MCMCSampler
   from homodyne.models import static_isotropic_model, laminar_flow_model

**Basic Workflow**:

.. code-block:: python

   # 1. Configuration
   config = ConfigManager("config.json")
   
   # 2. Analysis setup
   analysis = HomodyneAnalysisCore(config)
   analysis.load_experimental_data()
   
   # 3. Classical optimization
   classical_result = analysis.optimize_classical()
   
   # 4. MCMC (optional)
   mcmc_result = analysis.run_mcmc_sampling()

Module Index
------------

.. autosummary::
   :toctree: _autosummary
   :template: module.rst

   homodyne.core
   homodyne.config
   homodyne.optimization.mcmc
   homodyne.models
   homodyne.utils