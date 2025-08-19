======================
Examples to learn from
======================

.. Notice that YAML files included are also input to testing
   and this secures consistency!

Below is a presentation of Ogre config files

--------------------
Ogre example config
--------------------

Ogre has a large number of surfaces, and for convenience these lists
are places into separate files. Note that these data are fake data.


The main global config file
"""""""""""""""""""""""""""

.. literalinclude:: ../tests/data/yml/ogre/global_master_config.yml
   :language: yaml

The include files
"""""""""""""""""
Note that the include files starts on indent level "zero".

rms_horizons.yml

.. literalinclude:: ../tests/data/yml/ogre/rms_horizons.yml
   :language: yaml

rms_zones.yml

.. literalinclude:: ../tests/data/yml/ogre/rms_zones.yml
   :language: yaml


----------------------
Vinstre example config
----------------------
Note that these data are fake data. In this example, a simplified version of the
FREE IPL variables is used, which perhaps should be the preferred form.

.. literalinclude:: ../tests/data/yml/vinstre/global_master_config.yml
   :language: yaml

The included file:

.. literalinclude:: ../tests/data/yml/vinstre/fwl2.yml
   :language: yaml


----------------------------------------
Using the config in RMS, IPL and Python
----------------------------------------

IPL example
"""""""""""
.. code-block:: text

   Include("../../fmuconfig/output/global_variables.ipl")

   FOR i FROM 1 TO TOP_LOBES.length DO
       Print("Reading ", TOP_LOBE[i])


Python example (using yaml_load)
""""""""""""""""""""""""""""""""
.. code-block:: python

   import fmu.config.utilities as utils

   CFG = utils.yaml_load('../../fmuconfig/output/global_variables.yml')

   for toplobe in CFG["rms"]["horizons"]["TOP_LOBES"]:
       print('Working with {}'.format(toplobe))
