=====
Usage
=====

Folder structure
----------------

A recommended folder structure in Equinor is (assuming the revision folder is 21.2.0
in this example):

.. code-block:: bash

   21.2.0/fmuconfig/input
                   /bin
                   /output

The ``input`` has a file ``global_master_config.yml`` a possibly a few include files,
and these are edited by users.

The ``bin`` has shell scripts that process the input to a set of YAML and/or IPL
which is stored at ``output``. The files in output shall never be edited by hand.


Run from script
---------------

The ``fmu.config`` module is accessed through a script, and assuming the file structure
above, is to be run like this:

.. code-block:: shell

   # go to fmuconfig/bin
   fmuconfig ../input/global_master_config.yml <options...>

Here is an example of a shell script that runs `fmuconfig` from the ``bin`` folder:

.. code-block:: bash

   #!/bin/bash

   MASTER="../../fmuconfig/input/global_master_config.yml"  # all updates here
   OUTFOLDER="../../fmuconfig/output"                       # location of result files
   ROOTNAME="global_variables"                              # root name of result files

   # clean up (be careful with syntax)
   rm -f ${OUTFOLDER}/ROOTNAME*

   # run command for creating YAML version (+ ert tmpl version; yml.tmpl)
   fmuconfig $MASTER --rootname $ROOTNAME --mode yml --destination $OUTFOLDER \
         --template $OUTFOLDER

   # optional!
   # run command for creating IPL version if needed (+ ert tmpl version; ipl.tmpl)
   fmuconfig $MASTER --rootname $ROOTNAME --mode ipl --destination $OUTFOLDER \
         --template $OUTFOLDER --tool rms


Run from python inside or outside RMS
-------------------------------------

In RMS there are two options to run global variables:

* Run shell script above using system command (recommended)
* Run from RMS python

For shell script for RMS, use a system command job as this:

.. code-block:: shell

   cd ../../fmuconfig/bin; run_external sh global_variables_update.sh

The config can also be run from a python script inside RMS. In that case you
need to initiate the Class instance and run a few methods. Here is an example:

.. code-block:: python

   """Run global config in RMS python."""
   from pathlib import Path
   import fmu.config


   MASTER = "../../fmuconfig/input/global_master_config.yml"
   OUTPUT = "../../fmuconfig/output"
   ROOT = "global_variables"

   def cleanup():
      for file in Path(OUTPUT).glob(ROOT + "*"):
         file.unlink()
         print(f"Removed old {file}")


   def main():
      cfg = fmu.config.ConfigParserFMU()
      cfg.parse(MASTER)

      # make IPL, optional!
      cfg.to_ipl(rootname=ROOT, destination=OUTPUT, template=OUTPUT, tool="rms")

      # YAML
      cfg.to_yaml(rootname=ROOT, destination=OUTPUT, template=OUTPUT)

      print("\n\nGlobal IPL and YML are updated")


   if __name__ == "__main__":
      cleanup()
      main()

Using the output YAML in RMS or scripts
---------------------------------------

.. code-block:: python

   from fmu.config import utilities as util

   CONFIG = "../../fmuconfig/output/global_variables.yml"

   CFG = util.yaml_load(CONFIG)


Loading the input YAML in RMS or scripts
----------------------------------------

In some cases we may need to load the 'input' version of the YAML files which in fmu.config has
a syntax (e.g. the ``!include`` keys) which makes it not compatible with the YAML standard.
The solution then is to use a ``loader="FMU"`` key-value:

.. code-block:: python

   from fmu.config import utilities as util

   CONFIG = "../../fmuconfig/input/global_master_variables.yml"

   CFG = util.yaml_load(CONFIG, loader="FMU")
