######
ut_obj
######

********
Overview
********

.. start short_desc

**Object 'Utilities'**

.. end short_desc

************
Installation
************

.. start installation

Package ``ut_obj`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_obj

.. end installation

This requires that the ``readme`` extra is installed:

.. code-block:: shell

	$ python -m pip install ut_obj[readme]

***************
Package logging
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Files of Package ``ut_obj`` could be classified into the follwing file types (c.f.: **Appendix**: `Python Terminology`):


#. **Special files**

   a. *py.typed*

#. **Special modules**

   a. *__init__.py*
   #. *__version__.py*

#. **Modules**

   #. **Base objects Modules**

      a. *byte.py*
      a. *date.py*
      a. *num.py*
      a. *str.py*

   #. **Complex objects Modules**

      a. *obj.py*
      a. *pos.py*
      a. *poa.py*
      a. *pokv.py*

   #. **I/O Modules**

      a. *io.py*

********************
Base objects Modules
********************

The Base objects Modules of Package ``ut_obj`` are used for the management
of base objects like byte-objects, , num-obj́ects or objects.
The Base objects modules type contains the following modules.

  .. Base-objects-modules-label:
  .. table:: *Base objects Modules*

   +-------+------+-----------------+
   |Name   |Type  |Description      |
   +=======+======+=================+
   |byte.py|TyByte|Byte Manipulation|
   +-------+------+-----------------+
   |num.py |TyNum |Number Management|
   +-------+------+-----------------+
   |obj.py |TyObj |Object Management|
   +-------+------+-----------------+

byte.py (Base objects Module)
=============================

Classes
-------

The Base object Module ``byte.py`` contains the single static class ``Byte``;

byte.py Class: Byte
-------------------

The static Class ``Byte`` contains the subsequent methods

Methods
^^^^^^^

  .. Methods-of-static-class-Byte-label:
  .. table:: *Methods of static class Byte*

   +--------------+-------------------------------------+
   |Name          |Description                          |
   +==============+=====================================+
   |replace_by_dic|replace dictionary-keys found in byte|
   |              |string with corresponding values     |
   +--------------+-------------------------------------+

Byte Method: replace_by_dic
"""""""""""""""""""""""""""

  .. Parameter-of-Byte-method-replace_by_dic-label:
  .. table:: *Parameter of Byte method replace_by_dic*

   +-----------+-------+-------------------------------------------+
   |Name       |Type   |Description                                |
   +===========+=======+===========================================+
   |byte_string|TyBytes|Byte string                                |
   +-----------+-------+-------------------------------------------+
   |dic_replace|TyDic  |Dictionary with replacement keys and values| 
   +-----------+-------+-------------------------------------------+

***********************
Complex objects modules
***********************

The Complex objects module type of Package ``ut_obj`` consist of the single module ``poa.py``.

poa.py
======

The Module ``poa.py`` is used to manage Pairs of arrays;

Classes
-------

The Module ``oia.py`` contains contains the single static class ``PoA``.

poa.py Class: PoA
-----------------

The static Class ``PoA`` contains the subsequent methods

PoA Methods
^^^^^^^^^^^ 

Overview
""""""""

  .. Methods-of-static-class-PoA-label:
  .. table:: *Methods of static class PoA*

   +-----------+---------------------------------------------------------+
   |Name       |Description                                              |
   +===========+=========================================================+
   |yield_items|yield items for the given pair of objects and the object.|
   |           |Every item consist of the following elements:            |
   |           +---------------------------------------------------------+
   |           |1. element of the first given array                      |  
   |           |2. element of the second given array                     |
   |           |3. the given object                                      |
   +-----------+---------------------------------------------------------+

PoA Method: yield_items
"""""""""""""""""""""""

  .. Parameter-of-PoA-method-yield_items-label:
  .. table:: *Parameter of PoA method yield_items*

   +----------+--------------+
   |Name|Type |Description   |
   +====+=====+==============+
   |poa |TyPoA|Pair of Arrays|
   +----+-----+--------------+
   |obj |TyAny|Object        | 
   +----+-----+--------------+

************
File modules
************

The ``File modules`` type of Package ``ut_obj`` consist of the single module ``file.py``.

file.py
=======

The File module ``file.py`` is used for the management of file objects;
it contains the single class ``File``.

file.py Class: File
-------------------

The static Class ``File`` contains the subsequent methods

File Methods
^^^^^^^^^^^^

Overview
""""""""

  .. Methods-of-static-class-File-label:
  .. table:: *Methods of static class File*

   +--------------------+----------------------------------------------------------+
   |Name                |Description                                               |
   +====================+==========================================================+
   |count               |count number of paths that match path_pattern.            |
   +--------------------+----------------------------------------------------------+
   |ex_get_aod_using_fnc|execute get array of dictionaries using the function.     |
   +--------------------+----------------------------------------------------------+
   |ex_get_aod          |execute get array of dictionaries.                        |
   +--------------------+----------------------------------------------------------+
   |ex_get_dod_using_fnc|execute get dictionary of dictionaries using the function.|
   +--------------------+----------------------------------------------------------+
   |ex_get_dod          |execute get dictionary of dictionaries.                   |
   +--------------------+----------------------------------------------------------+
   |get_aod             |get array of dictionaries.                                |
   +--------------------+----------------------------------------------------------+
   |get_dic             |get array of dictionaries and return the first element.   |
   +--------------------+----------------------------------------------------------+
   |get_dod             |get dictionary of dictionaries.                           |
   +--------------------+----------------------------------------------------------+
   |get_paths           |yield paths which match given path pattern.               |
   +--------------------+----------------------------------------------------------+
   |get_latest          |get latest file path that match given path pattern.       |
   +--------------------+----------------------------------------------------------+
   |io                  |apply io function to given path and object.               |
   +--------------------+----------------------------------------------------------+

File Method: count
""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-put_aod-label:
  .. table:: *Parameter of File method put_aod*

   +------------+------+------------+
   |Name        |Type  |Description |
   +============+======+============+
   |path_pattern|TyPath|path_pattern|
   +------------+------+------------+

Return Value
............

  .. Return-value-of-File-method-count-label:
  .. table:: *Return value of File method count*

   +----+-----+---------------+
   |Name|Type |Description    |
   +====+=====+===============+
   |    |TyInt|Number pf paths|
   +----+-----+---------------+

File Method: ex_get_aod_using_fnc
"""""""""""""""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-ex_get_aod_using_fnc-label:
  .. table:: *Parameter of File method ex_get_aod_using_fnc*

   +------+----------+-----------------+
   |Name  |Type      |Description      |
   +======+==========+=================+
   |path  |TyPath    |Path             |
   +------+----------+-----------------+
   |fnc   |TyCallable|Object function  |
   +------+----------+-----------------+
   |kwargs|TyDic     |keyword arguments|
   +------+----------+-----------------+

Return Value
............


  .. Return-value-of-File-method-ex_get_aod_using_fnc-label:
  .. table:: *Return value of File method ex_get_aod_using_fnc*

   +----+-----+----------------------+
   |Name|Type |Description           |
   +====+=====+======================+
   |    |TyAoD|Array of Dictionariesy|
   +----+-----+----------------------+

File Method: ex_get_aod
"""""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-ex_get_aod-label:
  .. table:: *Parameter of File method ex_get_aod*

   +------+------+-----------------+
   |Name  |Type  |Description      |
   +======+======+=================+
   |path  |TyPath|Path             |
   +------+------+-----------------+
   |kwargs|TyDic |keyword arguments|
   +------+------+-----------------+

Return Value
............


  .. Return-value-of-IocWPep-method-get-label:
  .. table:: *Return value of IocWbPe method get*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |    |TyAoD|Array of Dictionaries|
   +----+-----+---------------------+

File Method: ex_get_dod_using_fnc
"""""""""""""""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-ex_get_dod_using_fnc-label:
  .. table:: *Parameter of File method ex_get_dod_using_fnc*

   +------+----------+-----------------+
   |Name  |Type      |Description      |
   +======+==========+=================+
   |path  |TyPath    |Path             |
   +------+----------+-----------------+
   |fnc   |TyCallable|Object function  |
   +------+----------+-----------------+
   |key   |TyAny     |Keyword          |
   +------+----------+-----------------+
   |kwargs|TyDic     |Keyword arguments|
   +------+----------+-----------------+

Return Value
............

  .. Return-value-of-File-method-ex_get_dod_using_fnc-label:
  .. table:: *Return value of File method ex_get_dod_using_fnc*

   +----+-----+--------------------------+
   |Name|Type |Description               |
   +====+=====+==========================+
   |    |TyDoD|Dictionary of dictionaries|
   +----+-----+--------------------------+

File Method: ex_get_dod
"""""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-ex_get_dod-label:
  .. table:: *Parameter of File method ex_get_dod*

   +------+------+-----------------+
   |Name  |Type  |Description      |
   +======+======+=================+
   |path  |TyPath|Path             |
   +------+------+-----------------+
   |key   |TyAny |Keyword          |
   +------+------+-----------------+
   |kwargs|TyDic |Keyword arguments|
   +------+------+-----------------+

Return Values
.............

  .. Return-value-of-File-method-ex_get_dod-label:
  .. table:: *Return value of File method ex_get_dod*

   +----+-----+--------------------------+
   |Name|Type |Description               |
   +====+=====+==========================+
   |    |TyDoD|Dictionary of dictionaries|
   +----+-----+--------------------------+

File Method: get_aod
""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-get_aod-label:
  .. table:: *Parameter of File method get_aod*

   +------+----------+-----------------+
   |Name  |Type      |Description      |
   +======+==========+=================+
   |cls   |class     |current class    |
   +------+----------+-----------------+
   |path  |TyPath    |Path             |
   +------+----------+-----------------+
   |fnc   |TyCallable|Object function  |
   +------+----------+-----------------+
   |kwargs|TyDic     |keyword arguments|
   +------+----------+-----------------+

Return Value
............

  .. Return-value-of-File-method-get_aod-label:
  .. table:: *Return value of File method get_aod*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |    |TyDic|Array of Dictionaries|
   +----+-----+---------------------+

File Method: get_dic
""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-get_dic-label:
  .. table:: *Parameter of File method get_dic*

   +------+----------+-----------------+
   |Name  |Type      |Description      |
   +======+==========+=================+
   |cls   |class     |current class    |
   +------+----------+-----------------+
   |path  |TyPath    |Path             |
   +------+----------+-----------------+
   |fnc   |TnCallable|Object function  |
   +------+----------+-----------------+
   |key   |TyStr     |Keyword          |
   +------+----------+-----------------+
   |kwargs|TyDic     |keyword arguments|
   +------+----------+-----------------+

Return Value
............

  .. Return-value-of-File-method-get_dic-label:
  .. table:: *Return value of File method get_dic*

   +----+------+--------------------------+
   |Name|Type  |Description               |
   +====+======+==========================+
   |    |TyDoD |Dictionary of Dictionaries|
   +----+------+--------------------------+

File Method: get_dod
""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-get_dod-label:
  .. table:: *Parameter of Byte method get_dod*

   +------+----------+-----------------+
   |Name  |Type      |Description      |
   +======+==========+=================+
   |obj   |TyAny     |Object           |
   +------+----------+-----------------+
   |path  |TyPath    |Path             |
   +------+----------+-----------------+
   |fnc   |TnCallable|Object function  |
   +------+----------+-----------------+
   |key   |TyStr     |IO function      |
   +------+----------+-----------------+
   |kwargs|TyDic     |keyword arguments|
   +------+----------+-----------------+

Return Value
............

  .. Return-value-of-File-method-get_dod-label:
  .. table:: *Return value of File method get_dod*

   +----+------+--------------------------+
   |Name|Type  |Description               |
   +====+======+==========================+
   |    |TyDoD |Dictionary of Dictionaries|
   +----+------+--------------------------+

File Method: get_latest
"""""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-get_latest-label:
  .. table:: *Parameter of File method get_latest*

   +------------+-----+------------+
   |Name        |Type |Description |
   +============+=====+============+
   |path_pattern|TyStr|Path pattern|
   +------------+-----+------------+

Return Value
............

  .. Return-value-of-File-method-get_latest-label:
  .. table:: *Return value of File method get_latest*

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |    |TyPath|Path       |
   +----+------+-----------+

File Method: get_paths
""""""""""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-get_paths-label:
  .. table:: *Parameter of File method get_paths*

   +------------+------+-------+----------------+
   |Name        |Type  |Default|Description     |
   +============+======+=======+================+
   |path_pattern|TyPath|       |Path pattern    |
   +------------+------+-------+----------------+
   |sw_recursive|TyBool|None   |Recursive switch|
   +------------+------+-------+----------------+

Return Value
............

  .. Parameter-of-File-method-get_paths-label:
  .. table:: *Parameter of File method get_paths*

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |    |TyIoS|yield path |
   +----+-----+-----------+

File Method: io
"""""""""""""""

Parameter
.........

  .. Parameter-of-File-method-io-label:
  .. table:: *Parameter of File method io*

   +----+----------+---------------+
   |Name|Type      |Description    |
   +====+==========+===============+
   |obj |TyObj     |Object         |
   +----+----------+---------------+
   |path|TnPath    |Path           |
   +----+----------+---------------+
   |fnc |TnCallable|Object function|
   +----+----------+---------------+

************
Path modules
************

The ``Path modules`` type of Package ``ut_obj`` consist of the following modules.

  .. Path-Modules-label:
  .. table:: *Path Modules*

   +-------+------+---------------+
   |Name   |Type  |Description    |
   +=======+======+===============+
   |path.py|TyPath|Path management|
   +-------+------+---------------+

path.py
=======

The module ``path.py`` is used for the management of path objects.

path.py Classes
---------------

The module ``path.py`` contains the single class ``Path``.

path.py Class: Path
-------------------

The static Class ``Path`` contains the subsequent methods

Path Methods
^^^^^^^^^^^^

Overview
""""""""

  .. Methods-of-static-class-Path-label:
  .. table:: *Methods of static class Path*

   +-----------------------------+---------------------------------------------------+
   |Name                         |Description                                        |
   +=============================+===================================================+
   |verify                       |Verify path                                        |
   +-----------------------------+---------------------------------------------------+
   |edit_path                    |put array of _keys found in                        |
   +-----------------------------+---------------------------------------------------+
   |mkdir                        |make directory of directory path                   |
   +-----------------------------+---------------------------------------------------+
   |mkdir_from_path              |make directory of the path, if it's a directory    |
   +-----------------------------+---------------------------------------------------+
   |sh_basename                  |show basename of the path                          |
   +-----------------------------+---------------------------------------------------+
   |sh_components                |split the path into components and show the        |
   |                             |joined components between start- and end-index     |
   +-----------------------------+---------------------------------------------------+
   |sh_component_using_field_name|split the given path into components and show the  |
   |                             |component identified by an index; the index is get |
   |                             |from the given dictionary with the given field name|
   +-----------------------------+---------------------------------------------------+
   |sh_fnc_name_using_pathlib    |extract function name from path with pathlib       |
   +-----------------------------+---------------------------------------------------+
   |sh_fnc_name_using_os_path    |extract function name from path with os.path       |
   +-----------------------------+---------------------------------------------------+
   |sh_last_component            |show last component of path                        |
   +-----------------------------+---------------------------------------------------+
   |sh_path_using_pathnm         |show basename of the path                          |
   +-----------------------------+---------------------------------------------------+
   |sh_path_using_d_path         |replace keys in path by dictionary values          |
   +-----------------------------+---------------------------------------------------+
   |sh_path_using_d_datetype     |show path using path function selected by the given|
   |                             |date type dictionary                               |
   +-----------------------------+---------------------------------------------------+
   |sh_path                      |show path                                          |
   +-----------------------------+---------------------------------------------------+
   |sh_path_first                |show first component of the given path             |
   +-----------------------------+---------------------------------------------------+
   |sh_path_last                 |show last component of the given path              |
   +-----------------------------+---------------------------------------------------+
   |sh_path_now                  |replace now variable in the path by the now date   |
   +-----------------------------+---------------------------------------------------+
   |split_to_array               |split normalized path to array                     |
   +-----------------------------+---------------------------------------------------+

########
Appendix
########

***************
Package Logging
***************

Description
===========

Logging use the module **log.py** of the logging package **ut_log**.
The module supports two Logging types:

#. **Standard Logging** (std) or 
#. **User Logging** (usr).

The Logging type can be defined by one of the values 'std' or 'usr' of the parameter log_type; 'std' is the default.
The different Logging types are configured by one of the following configuration files:

#. **log.std.yml** or 
#. **log.usr.yml** 
  
The configuration files can be stored in different configuration directories (ordered by increased priority):

#. <package directory of the log package **ut_log**>/**cfg**,
#. <package directory of the application package **ui_eviq_srr**>/**cfg**,
#. <application directory of the application **eviq**>/**cfg**,

The active configuration file is the configuration file in the directory with the highest priority.

Examples
========
  
Site-packages-path = **/appl/eviq/.pyenv/versions/3.11.12/lib/python3.11/site-packages**
Log-package = **ut_log**
Application-package = **ui_eviq_srr**
Application-home-path = **/appl/eviq**
  
.. Examples-of-log-configuration-files-label:
.. table:: **Examples of log configuration-files**

   +-----------------------------------------------------------------------------------+
   |Log Configuration                                                                  |
   +----+-------------------+----------------------------------------------+-----------+
   |Type|Directory Type     |Directory                                     |File       |
   +====+===================+==============================================+===========+
   |std |Log package        |<Site-packages-path>/<Log-package>/cfg        |log.std.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<Site-packages-path>/<application-package>/cfg|           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-home-path>/cfg                   |           |
   +----+-------------------+----------------------------------------------+-----------+
   |usr |Log package        |<site-packages-path>/ut_log/cfg               |log.usr.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<site-packages-path>/ui_eviq_srr/cfg          |           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-path>/cfg                        |           |
   +----+-------------------+----------------------------------------------+-----------+

Log message types
=================

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Log types and Log directories
-----------------------------

Single or multiple Application log directories can be used for each message type:

.. Log-types-and-Log-directories-label:
.. table:: *Log types and directoriesg*

   +--------------+---------------+
   |Log type      |Log directory  |
   +--------+-----+--------+------+
   |long    |short|multiple|single|
   +========+=====+========+======+
   |debug   |dbqs |dbqs    |logs  |
   +--------+-----+--------+------+
   |info    |infs |infs    |logs  |
   +--------+-----+--------+------+
   |warning |wrns |wrns    |logs  |
   +--------+-----+--------+------+
   |error   |errs |errs    |logs  |
   +--------+-----+--------+------+
   |critical|crts |crts    |logs  |
   +--------+-----+--------+------+

Application parameter for logging
---------------------------------

.. Application-parameter-used-in-log-naming-label:
.. table:: *Application parameter used in log naming*

   +-----------------+--------------+-----+------------------+-------+-----------+
   |Name             |Decription    |Value|Description       |Default|Example    |
   +=================+==============+=====+==================+=======+===========+
   |appl_data        |data directory|     |                  |       |/data/eviq |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |tenant           |tenant name   |UMH  |                  |       |UMH        |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |package          |package name  |     |                  |       |ui_eviq_srr|
   +-----------------+--------------+-----+------------------+-------+-----------+
   |cmd              |command       |     |                  |       |evupreg    |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_type         |Logging Type  |std: |Standard logging  |std    |std        |
   |                 |              +-----+------------------+       |           |
   |                 |              |usr: |User Logging      |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_ts_type      |Logging       |ts:  |Sec since 1.1.1970|ts     |ts         |
   |                 |timestamp     +-----+------------------+       |           |
   |                 |type          |dt:  |Datetime          |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_sw_single_dir|Use single log|True |use single dir.   |True   |True       |
   |                 |directory     +-----+------------------+       |           |
   |                 |              |False|use muliple dir.  |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+

Log files naming
----------------

Naming Conventions (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+----------------------------------------------+-------------------+
   |Type    |Directory                                     |File               |
   +========+==============================================+===================+
   |debug   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/debs|debs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |critical|/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|crts_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |error   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|errs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |info    |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|infs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |warning |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|rnsg_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+

Naming Conventions (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

 <appl_data>   Application data folder
 │
 └── <tenant>  Application tenant folder
     │
     └── RUN  Applications RUN folder for Application log files
         │
         └── <package>  RUN folder of Application package: <package>
             │
             └── <cmd>  RUN folder of Application command <cmd>
                 │
                 ├── debs  Application command debug messages folder
                 │   │
                 │   └── debs_<ts>_<pid>.log  debug messages for
                 │                            run of command <cmd>
                 │                            with pid <pid> at <ts>
                 │
                 └── logs  Application command log messages folder
                     │
                     ├── crts_<ts>_<pid>.log  critical messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── errs_<ts>_<pid>.log  error messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── infs_<ts>_<pid>.log  info messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     └── wrns_<ts>_<pid>.log  warning messages for
                                              run of command <cmd>
                                              with pid <pid> at <ts>

Naming Examples (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+--------------------------------------------+--------------------------+
   |Type    |Directory                                   |File                      |
   +========+============================================+==========================+
   |debug   |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/debs/|debs_1750096540_354710.log|
   +--------+--------------------------------------------+--------------------------+
   |critical|/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|crts_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |error   |                                            |errs_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |info    |                                            |infs_1750096540_354710.log|
   +--------+                                            +--------------------------+
   |warning |                                            |wrns_1749971151_240257.log|
   +--------+--------------------------------------------+--------------------------+

Naming Examples (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

  /data/eviq/UMH/RUN/ui_eviq_srr/evdomap  Run folder of
  │                                       of function evdomap
  │                                       of package ui_eviq_srr
  │                                       for teanant UMH
  │                                       of application eviq
  │
  ├── debs  debug folder of Application function: evdomap
  │   │
  │   └── debs_1748609414_314062.log  debug messages for run 
  │                                   of function evdomap     
  │                                   using pid: 314062 at: 1748609414
  │
  └── logs  log folder of Application function: evdomap
      │
      ├── errs_1748609414_314062.log  error messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      ├── infs_1748609414_314062.log  info messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      └── wrns_1748609414_314062.log  warning messages for run
                                      of function evdomap     
                                      with pid: 314062 at: 1748609414

Configuration files
===================

log.std.yml (jinja2 yml file)
-----------------------------

Content
^^^^^^^

.. log.std.yml-label:
.. code-block:: jinja

 version: 1

 disable_existing_loggers: False

 loggers:

     # standard logger
     std:
         # level: NOTSET
         level: DEBUG
         handlers:
             - std_debug_console
             - std_debug_file
             - std_info_file
             - std_warning_file
             - std_error_file
             - std_critical_file

 handlers:
 
     std_debug_console:
         class: 'logging.StreamHandler'
         level: DEBUG
         formatter: std_debug
         stream: 'ext://sys.stderr'

     std_debug_file:
         class: 'logging.FileHandler'
         level: DEBUG
         formatter: std_debug
         filename: '{{dir_run_debs}}/debs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_info_file:
         class: 'logging.FileHandler'
         level: INFO
         formatter: std_info
         filename: '{{dir_run_infs}}/infs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_warning_file:
         class: 'logging.FileHandler'
         level: WARNING
         formatter: std_warning
         filename: '{{dir_run_wrns}}/wrns_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_error_file:
         class: 'logging.FileHandler'
         level: ERROR
         formatter: std_error
         filename: '{{dir_run_errs}}/errs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true
 
     std_critical_file:
         class: 'logging.FileHandler'
         level: CRITICAL
         formatter: std_critical
         filename: '{{dir_run_crts}}/crts_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_critical_mail:
         class: 'logging.handlers.SMTPHandler'
         level: CRITICAL
         formatter: std_critical_mail
         mailhost : localhost
         fromaddr: 'monitoring@domain.com'
         toaddrs:
             - 'dev@domain.com'
             - 'qa@domain.com'
         subject: 'Critical error with application name'
 
 formatters:

     std_debug:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_info:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_warning:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_error:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical_mail:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'

Jinja2-variables
^^^^^^^^^^^^^^^^

.. log.std.yml-Jinja2-variables-label:
.. table:: *log.std.yml Jinja2 variables*

   +------------+-----------------------------+-------------------------------------------+
   |Name        |Definition                   |Example                                    |
   +============+=============================+===========================================+
   |dir_run_debs|debug run directory          |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/debs|
   +------------+-----------------------------+-------------------------------------------+
   |dir_run_infs|info run directory           |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +------------+-----------------------------+                                           |
   |dir_run_wrns|warning run directory        |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_errs|error run directory          |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_crts|critical error run directory |                                           |
   +------------+-----------------------------+-------------------------------------------+
   |ts          |Timestamp since 1970 in [sec]|1749483509                                 |
   |            |if log_ts_type == 'ts'       |                                           |
   |            +-----------------------------+-------------------------------------------+
   |            |Datetime in timezone Europe/ |20250609 17:38:29 GMT+0200                 |
   |            |Berlin if log_ts_type == 'dt'|                                           |
   +------------+-----------------------------+-------------------------------------------+
   |pid         |Process ID                   |79133                                      |
   +------------+-----------------------------+-------------------------------------------+

***************
Python Glossary
***************

.. _python-modules:

Python Modules
==============

Overview
--------

  .. Python-Modules-label:
  .. table:: *Python Modules*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-functions:

Python Function
===============

Overview
--------

  .. Python-Function-label:
  .. table:: *Python Function*

   +---------------+---------------------------------------------------------+
   |Name           |Definition                                               |
   +===============+==========+==============================================+
   |Python function|Files with suffix ``.py``; they could be empty or contain|
   |               |python code; other modules can be imported into a module.|
   +---------------+---------------------------------------------------------+
   |special Python |Modules like ``__init__.py`` or ``main.py`` with special |
   |modules        |names and functionality.                                 |
   +---------------+---------------------------------------------------------+

.. _python-packages:

Python Packages
===============

Overview
--------

  .. Python Packages-Overview-label:
  .. table:: *Python Packages Overview*

   +---------------------+---------------------------------------------+
   |Name                 |Definition                                   |
   +=====================+=============================================+
   |Python package       |Python packages are directories that contains|
   |                     |the special module ``__init__.py`` and other |
   |                     |modules, sub packages, files or directories. |
   +---------------------+---------------------------------------------+
   |Python sub-package   |Python sub-packages are python packages which|
   |                     |are contained in another python package.     |
   +---------------------+---------------------------------------------+
   |Python package       |directory contained in a python package.     |
   |sub-directory        |                                             |
   +---------------------+---------------------------------------------+
   |Python package       |Python package sub-directories with a special|
   |special sub-directory|meaning like data or cfg                     |
   +---------------------+---------------------------------------------+

Special python package sub-directories
--------------------------------------

  .. Special-python-package-sub-directory-Examples-label:
  .. table:: *Special python package sub-directories*

   +-------+------------------------------------------+
   |Name   |Description                               |
   +=======+==========================================+
   |bin    |Directory for package scripts.            |
   +-------+------------------------------------------+
   |cfg    |Directory for package configuration files.|
   +-------+------------------------------------------+
   |data   |Directory for package data files.         |
   +-------+------------------------------------------+
   |service|Directory for systemd service scripts.    |
   +-------+------------------------------------------+

.. _python-files:

Python Files
============

Overview
--------

  .. Python-files-label:
  .. table:: *Python files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Python package|Files within a python package.                           |
   |files         |                                                         |
   +--------------+---------------------------------------------------------+
   |Python dunder |Python modules which are named with leading and trailing |
   |modules       |double underscores.                                      |
   +--------------+---------------------------------------------------------+
   |special       |Files which are not modules and used as python marker    |
   |Python files  |files like ``py.typed``.                                 |
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-special-files:

Python Special Files
--------------------

  .. Python-special-files-label:
  .. table:: *Python special files*

   +--------+--------+--------------------------------------------------------------+
   |Name    |Type    |Description                                                   |
   +========+========+==============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages|
   |        |checking|to indicate that the package supports type checking. This is a|
   |        |marker  |part of the PEP 561 standard, which provides a standardized   |
   |        |file    |way to package and distribute type information in Python.     |
   +--------+--------+--------------------------------------------------------------+

.. _python-special-modules:

Python Special Modules
----------------------

  .. Python-special-modules-label:
  .. table:: *Python special modules*

   +--------------+-----------+----------------------------------------------------------------+
   |Name          |Type       |Description                                                     |
   +==============+===========+================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to|
   |              |directory  |execute initialisation code or mark the directory it contains   |
   |              |marker     |as a package. The Module enforces explicit imports and thus     |
   |              |file       |clear namespace use and call them with the dot notation.        |
   +--------------+-----------+----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as package entry point |
   |              |for the    |point. The module is executed when the package is called by the |
   |              |package    |interpreter with the command **python -m <package name>**.      |
   +--------------+-----------+----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment      |
   |              |file       |statements used in Versioning.                                  |
   +--------------+-----------+----------------------------------------------------------------+

Python classes
==============

Overview
--------

  .. Python-classes-overview-label:
  .. table:: *Python classes overview*

   +-------------------+---------------------------------------------------+
   |Name               |Description                                        |
   +===================+===================================================+
   |Python class       |A class is a container to group related methods and|
   |                   |variables together, even if no objects are created.|
   |                   |This helps in organizing code logically.           |
   +-------------------+---------------------------------------------------+
   |Python static class|A class which contains only @staticmethod or       |
   |                   |@classmethod methods and no instance-specific      |
   |                   |attributes or methods.                             |
   +-------------------+---------------------------------------------------+

Python methods
==============

Overview
--------

  .. Python-methods-overview-label:
  .. table:: *Python methods overview*

   +--------------+-------------------------------------------+
   |Name          |Description                                |
   +==============+===========================================+
   |Python method |Python functions defined in python modules.|
   +--------------+-------------------------------------------+
   |Python class  |Python functions defined in python classes.|
   |method        |                                           |
   +--------------+-------------------------------------------+
   |Python special|Python class methods with special names and|
   |class method  |functionalities.                           |
   +--------------+-------------------------------------------+

Python class methods
--------------------

  .. Python-class-methods-label:
  .. table:: *Python class methods*

   +--------------+----------------------------------------------+
   |Name          |Description                                   |
   +==============+==============================================+
   |Python no     |Python function defined in python classes and |
   |instance      |decorated with @classmethod or @staticmethod. |
   |class method  |The first parameter conventionally called cls |
   |              |is a reference to the current class.          |
   +--------------+----------------------------------------------+
   |Python        |Python function defined in python classes; the|
   |instance      |first parameter conventionally called self is |
   |class method  |a reference to the current class object.      |
   +--------------+----------------------------------------------+
   |special Python|Python class functions with special names and |
   |class method  |functionalities.                              |
   +--------------+----------------------------------------------+

Python special class methods
----------------------------

  .. Python-methods-examples-label:
  .. table:: *Python methods examples*

   +--------+-----------+--------------------------------------------------------------+
   |Name    |Type       |Description                                                   |
   +========+===========+==============================================================+
   |__init__|class      |The special method ``__init__`` is called when an instance    |
   |        |object     |(object) of a class is created; instance attributes can be    |
   |        |constructor|defined and initalized in the method. The method us a single  |
   |        |method     |parameter conventionally called ``self`` to access the object.|
   +--------+-----------+--------------------------------------------------------------+

#################
Table of Contents
#################

.. contents:: **Table of Content**
