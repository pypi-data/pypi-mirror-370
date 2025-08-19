==================================
YAML file and folders conventions
==================================

To summarize:

* YAML file endings is .yml

* Within the YAML master config file, the *small letters* headings are *"reserved"* words, while
  *uppercase* letters mean some kind of freeform variable.


Folder structure
----------------

The folder structure is *under discussion* and might change.

Alternative 1, close to compatible with current
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make it compatible with current FMU setups:

* Place the global_master_config.yml under ``share/config``

* Place shell scripts which runs fmuconfig under tool/bin, e.g. ``rms/bin``

* Output result to current standards, e.g. global_variables.ipl to
  ``rms/input/global_variables/global_variables.ipl`` and
  the templated version to ``ert/input/templates/global_variables.tmpl``


Alternative 2, a proposal for change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The proposal is that all config files, both input and output,
are stored under ``share/config``

* ``share/config/input`` for user defined global_master_config.yml + include files if any
* ``share/config/bin`` for scripts, reading from input, results to output
* ``share/config/output`` for all outputs; to be machine read.

It would then be a good practice to delete all files on output everytime the
fmuconfig script is ran.

In practice it means that the link in the RMS IPL scripts must be changed to:

  ``include("../../share/config/output/global_variables.ipl")``

Alternative 3, a second proposal for change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The proposal is that all config files, both input and output,
are stored under ``config`` on tool level (same level as rms, ert, ...)

* ``config/input`` for user defined global_master_config.yml + include files if any
* ``config/bin`` for scripts, reading from input, results to output
* ``config/output`` for all outputs; to be machine read.

In practice it means that the link in the RMS IPL scripts must be changed to:

  ``include("../../config/output/global_variables.ipl")``


File format and nested files
----------------------------

The master config file itself is a YAML formatted file. It follows the standard
YAML specification, with *one major exception*, and that is that
*file nesting* is allowed. This allows for placing various parts of
the CONFIG into separate subfiles, which improves the overview.

The *derived* YAML files to e.g. be used by RMS Python will not allow nesting;
they will follow the YAML standard.

What will be a good practice regarding nesting of the master config remains to be
seen.

Some conventions
----------------

The examples section (next) should be studied in detail in order to
understand the format.

* The preferred name of the input global config is ``global_master_config.yml``.

* YAML is a indent based file type; which means changing the indentation
  may change the whole meaning of the file!

* The first level indentation is important. Important sections are:

  - ``global``: For general settings
  - ``rms``: For RMS IPL compatible related settings
  - ``eclipse``: For Eclipse decks related settings

* Notice the difference between small letters and uppercase letters

  - The small letters are YAML keywords with a special meaning.
  - Uppercase letters are "client" keywords (free form)

* The dates format shall be `ISO 8601`_ compliant, on the form ``YYYY-MM-DD``.
  For file naming and IPL that date will be usually be compressed to
  the ``YYYYMMDD`` form, which is still in accordance with the ISO standard.

* Uncertainties are placed within numbers as these examples show:
  ``1.0 ~ <KH_MULT_MTR>`` or ``1.0~<KH_MULT_MTR>``. Notice that

  - First entry is the number that shall be used when running tests outside ERT,
    i.e. the *work* mode.
  - A tilde ``~`` is used to separate this number with an uncertainty identifier,
    which will be on the form ``<XXX>``, also called the *template* mode.
  - The files generated from this global master config, will either have the
    *work* form (e.g. 1.0 in this example) or the templated form (``<KH_MULT_MTR>``
    in this example). The alternate form may be present as a comment.
  - Uncertainty keys shall be UPPERCASE

* Note the templated files will have extesion ``.tpml``, e.g. for ``global_variables.ipl``
  it will be ``global_variables.ipl.tmpl``

* For most cases, a simple ``<>`` will default the name to key (it will not work when dtype
  and value(s) is applied). For example

  .. code-block:: yaml

     FLWX: 3203.0 ~ <>

     # is the same as

     FLWX: 3203.0 ~ <FLWX>


Include files
-------------

In the input master YAML config, include files are allowed. Note that the include
statement must "belong" to a keyword, e.g.::

  kwlists: !include kwlists.yml

This variant is not allowed::

  !include something.yml

However, one can use an anonymous keywords, which is any word that starts with to
underscores::

  __tmpword: !include something.yml


Note here that ``__tmpword`` will not be a part of the configuration. See later Vinstre
example where this technique is applied.



RMS related settings
--------------------

Horizons, zones and kwlists
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Within the ``rms`` section there may be 3 significant subheadings:

* horizons
* zones
* kwlists

These are reserved for Horizon, Zone or keyword listing, and will usually (always?)
never contain uncertainties; they are just lists to facilitate looping with RMS
Python or IPL.

Examples:

.. code-block:: yaml

   horizons:

     TOP_RES:
       - Top Ness
       - Top Middle Ness
       - Top Lower Ness
       - Top Etive

     Top_DCONV:
       - Lista Fm.
       - BCU

   zones:
     ZONE_RES:
       - Upper Ness
       - Middle Ness
       - Lower Ness
       - Etive

   kwlists:

     FACIES_NAMES:
       OFFSHORE_VI_C:         [1, "Offshore mudstones, Viking Gp."]
       MUDDY_SPIC_C:          [2, "Muddy spiculites"]
       BIOSTROME_REEF_C:      [7, "Biostrome reef"]
       SANDY_SPIC_C:          [8, "Sandy spiculites"]


Freeform, with dtype and value(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rest of ``rms`` will be on so-called *freeform* format, where one needs to

* Have an identifier or variable name in **UPPERCASE**.
* The config script will try to guess, based on the value(s), whether RMS IPL should
  use String, Int, Bool or Float. In addition it will interpret if it is a scalar or a list.
* Optionally, if the automatics fails, one can specify (one indent level more) the

  - ``dtype`` (what kind of datatype; int, float, date, datepair, etc.)
  - ``value`` or ``values``: The single form ``value`` for single numbers, and the
    plural ``values`` form for lists.

Examples of a freeform type with uncertainty alternative:

.. code-block:: yaml

  KH_MULT_MTR: 1.0 ~ <KH_MULT_MTR>  # the config script will assume dtype=Float,
                                    # since it is a number with decimals, and uncertainty <...>

  KH_MULT_MTX: 1    # the config script will assume dtype=Int, since punctuation is missing

  KH_MULT_MTY: myvalue    # the config script will here assume dtype=String (text)

  KH_MULT_MTZ: [1.0, 1.2, 1.3]    # the config script will here a list of dtype=Floats


Example of a freeform type with explicit dtype and value(s):

.. code-block:: yaml

  KH_MULT_MTR:
    dtype: float
    value: 1.0 ~ <KH_MULT_MTR>

  KH_MULT_MTX:
    dtype: int
    value: 1

  KH_MULT_MTY:
    dtype: int
    value: 1

  KH_MULT_MTZ:
    dtype: float
    values:
      - 1.0
      - 1.2
      - 1.3


Freeform, output is always simplified
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the output YAML or JSON format, ``dtype`` and ``value(s)`` will be stripped aways, and
output style will always be on the form:

.. code-block:: yaml

  KH_MULT_MTR: 1.0

IPL code stubs:
~~~~~~~~~~~~~~~

IPL pure declarations can be defined as ``_IPL_DECLARE_WHATEVER``:

.. code-block:: yaml

   _IPL_DECLARE_STUB1: |
     GridModel GM
     Surface MAIN1, MAIN2

Similarly, IPL code stubs can be inserted as ``_IPL_CODE_WHATEVER``:

.. code-block:: yaml

   _IPL_CODE_STUB1: |
      // code for something
      FOR i FROM 1 TO 100 DO
         Print("Hello")
      ENDFOR


Summary of Reserved words
--------------------------

Here is an overview of reserved words (small letters), and the data values are also described
for some cases.

.. code-block:: yaml

   authors: ['shortname1', 'shortname2']

   version: 1.0   # this is config file version

   global:
     name: Name of your field
     coordsys: SOME_OW_COORDSYS_ID

   rms:
     horizons:
     zones:
     kwlists:

     ANYVARIABLE:
       dtype:  ... float/int/string/date/datepair
       value: a_scalar
       values: [...list...]

   eclipse:

Changes may occur!

.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
