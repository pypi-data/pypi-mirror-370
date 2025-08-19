######
ut_com
######

********
Overview
********

.. start short_desc

**Communication and CLI Utilities**

.. end short_desc

************
Installation
************

.. start installation

The package ``ut_com`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_com

.. end installation

***************
Package logging 
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Package ``ut_com`` consist of the following file types (c.f.: **Appendix**: `Python Glossary`):

#. **Special files:**

   a. *py.typed*

#. **Special modules:**

   a. *__init__.py*
   #. *__version__.py*

#. **Modules**

   #. **Decorator Module**

      a. *dec.py*

   #. **Communication Module**

      a. *com.py*

   #. **Timer Module**

      #. *timer.py*

   #. **Base Modules**

      a. *app.py*
      #. *cfg.py*
      #. *exit.py*

****************
Decorator Module
****************

Overview
========

  .. Decorator Module-label:
  .. table:: *Decorator Module*

   +------+----------------+
   |Name  |Decription      |
   +======+================+
   |dec.py|Decorator module|
   +------+----------------+

Decorator module: dec.py
========================

Decorator functions of modul: dec
---------------------------------

The Decorator Module ``dec.py`` contains the follwing decorator functions.

  .. Decorator-functions-of-module-dec-label:
  .. table:: *Decorator functions of module dec*

   +------------+-----------------+
   |Name        |Description      |
   +============+=================+
   |timer       |Timer            |
   +------------+-----------------+
   |handle_error|Handle exceptions|
   +------------+-----------------+

Decorator functions: timer of modul: dec
----------------------------------------
        
Parameter
^^^^^^^^^

  .. Parameter-of-decorator-function-timer-label:
  .. table:: *Parameter of decorator function timer*

   +----+----------+-----------+
   |Name|Type      |Description|
   +====+==========+===========+
   |fnc |TyCallable|function   |
   +----+----------+-----------+

********************
Communication Module
********************

Overview
========

  .. Communication Module-label:
  .. table:: *Communication Module*

   +------+-----------------------------+
   |Name  |Decription                   |
   +======+=============================+
   |com.py|Communication handling module|
   +------+-----------------------------+

Communication module: com.py
============================

The Communication Module ``com.py`` contains the single static class ``Com``.

com.py Class: Com
-----------------

The static Class ``Com`` contains the subsequent variables and methods.

Com: Variables
^^^^^^^^^^^^^^

  .. Com-Variables-label:
  .. table:: *Com: Variables*

   +------------+-----------+-------+---------------------------------------+
   |Name        |Type       |Default|Description                            |
   +============+===========+=======+=======================================+
   |cmd         |TyStr      |None   |Command                                |
   +------------+-----------+-------+---------------------------------------+
   |d_com_pacmod|TyDic      |{}     |Communication package module dictionary|
   +------------+-----------+-------+---------------------------------------+
   |d_app_pacmod|TyDic      |{}     |Application package module dictionary  |
   +------------+-----------+-------+---------------------------------------+
   |sw_init     |TyBool     |None   |Initialisation switch                  |
   +------------+-----------+-------+---------------------------------------+
   |tenant      |TyStr      |None   |Tenant name                            |
   +------------+-----------+-------+---------------------------------------+
   |**Timestamp fields**                                                    |
   +------------+-----------+-------+---------------------------------------+
   |ts          |TnTimeStamp|None   |Timestamp                              |
   +------------+-----------+-------+---------------------------------------+
   |d_timer     |TyDic      |False  |Timer dictionary                       |
   +------------+-----------+-------+---------------------------------------+
   |**Links to other Classes**                                              |
   +------------+-----------+-------+---------------------------------------+
   |App         |TyAny      |None   |Application class                      |
   +------------+-----------+-------+---------------------------------------+
   |cfg         |TyDic      |None   |Configuration dictionary               |
   +------------+-----------+-------+---------------------------------------+
   |Log         |TyLogger   |None   |Log class                              |
   +------------+-----------+-------+---------------------------------------+
   |Exit        |TyAny      |None   |Exit class                             |
   +------------+-----------+-------+---------------------------------------+

Methods of class: Com
^^^^^^^^^^^^^^^^^^^^^

  .. Com-Methods-label:
  .. table:: *Com Methods*

   +---------+-------------------------------------------------------+
   |Name     |Description                                            |
   +=========+=======================================================+
   |init     |Initialise static variables if they are not initialized|
   +---------+-------------------------------------------------------+
   |sh_kwargs|Show keyword arguments                                 |
   +---------+-------------------------------------------------------+

Com Method: init
^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  ..Com-Method-init-Parameter-label:
  .. table:: *Com Method init: Parameter*

   +---------+-----+-----------------+
   |Name     |Type |Description      |
   +=========+=====+=================+
   |cls      |class|current class    |
   +---------+-----+-----------------+
   |\**kwargs|TyAny|keyword arguments|
   +---------+-----+-----------------+

Com Method: sh_kwargs
^^^^^^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Com-Method-sh_kwargs-Parameter-label:
  .. table:: *Com Method sh_kwargs: Parameter*

   +--------+-----+--------------------+
   |Name    |Type |Description         |
   +========+=====+====================+
   |cls     |class|current class       |
   +--------+-----+--------------------+
   |root_cls|class|root lass           |
   +--------+-----+--------------------+
   |d_parms |TyDic|parameter dictionary|
   +--------+-----+--------------------+
   |\*args  |list |arguments array     |
   +--------+-----+--------------------+

************
Timer Module
************

Overview
========

  .. Timer Modules-label:
  .. table:: *Timer Modules*

   +--------+-----------------------------+
   |Name    |Decription                   |
   +========+=============================+
   |timer.py|Timer management module      |
   +--------+-----------------------------+

Timer module: timer.py
======================

timer.py: Classes
-----------------

The Module ``timer.py`` contains the following classes


  .. timer.py-Classes-label:
  .. table:: *timer.py classes*

   +---------+------+---------------+
   |Name     |Type  |Description    |
   +=========+======+===============+
   |Timestamp|static|Timestamp class|
   +---------+------+---------------+
   |Timer    |static|Timer class    |
   +---------+------+---------------+

timer.py Class: Timer
---------------------

Timer: Methods
^^^^^^^^^^^^^^

  .. Timer-Methods-label:
  .. table:: *Timer Methods*

   +----------+------------------------------------+
   |Name      |Description                         |
   +==========+====================================+
   |sh_task_id|Show task id                        |
   +----------+------------------------------------+
   |start     |Start Timer                         |
   +----------+------------------------------------+
   |end       |End Timer and Log Timer info message|
   +----------+------------------------------------+

Timer Method: sh_task_id
^^^^^^^^^^^^^^^^^^^^^^^^
        
Show task id, which is created by the concatination of the following items if they are defined:
#. package,
#. module,
#. class_name,
#. parms
The items package and module are get from the package-module directory;
The item class_name is the class_id if its a string, otherwise the attribute
__qualname__ is used.
        
Parameter
"""""""""

  .. Parameter-of-Timer-Method-sh_task_id-label:
  .. table:: *Parameter of: Timer Method sh_task_id*

   +--------+-----+-----------------+
   |Name    |Type |Description      |
   +========+=====+=================+
   |d_pacmod|TyDic|pacmod dictionary|
   +--------+-----+-----------------+
   |class_id|TyAny|Class Id         |
   +--------+-----+-----------------+
   |parms   |TnAny|Parameters       |
   +--------+-----+-----------------+
   |sep     |TyStr|Separator        |
   +--------+-----+-----------------+

Return Value
""""""""""""

  .. Timer-Method-sh_task_id-Return-Value-label:
  .. table:: *Timer Method sh_task_id: Return Value*

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |    |TyStr|Task Id    |
   +----+-----+-----------+

Timer Method: start
^^^^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Parameter-of-Timer-Method-start-Parameter-label:
  .. table:: *Timer Method start: Parameter*

   +--------+-----+-------------+
   |Name    |Type |Description  |
   +========+=====+=============+
   |cls     |class|current class|
   +--------+-----+-------------+
   |class_id|TyAny|Class Id     |
   +--------+-----+-------------+
   |parms   |TnAny|Parameter    |
   +--------+-----+-------------+
   |sep     |TyStr|Separator    |
   +--------+-----+-------------+

Timer Method: end
^^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Parameter-of-Timer-Method-end-label:
  .. table:: *Parameter of: Timer Method end*

   +--------+-----+-------------+
   |Name    |Type |Description  |
   +========+=====+=============+
   |cls     |class|current class|
   +--------+-----+-------------+
   |class_id|TyAny|Class Id     |
   +--------+-----+-------------+
   |parms   |TnAny|Parameter    |
   +--------+-----+-------------+
   |sep     |TyStr|Separator    |
   +--------+-----+-------------+

************
Base Modules
************

Overview
========

  .. Base Modules-label:
  .. table:: *Base Modules*

   +---------+----------------------------+
   |Name     |Decription                  |
   +=========+============================+
   |app\_.py |Application setup module    |
   +---------+----------------------------+
   |cfg\_.py |Configuration setup module  |
   +---------+----------------------------+
   |exit\_.py|Exit Manafement setup module|
   +---------+----------------------------+

Base module: app\_.py
=====================

The Module ``app\_.py`` contains a single static class ``App_``.

Class: App\_
------------

The static class ``App_`` contains the subsequent static variables and methods

App\_: Static Variables
^^^^^^^^^^^^^^^^^^^^^^^

  .. Appl\_ Static-Variables-label:
  .. table:: *Appl\_ tatic Variables*

   +---------------+-------+-------+---------------------+
   |Name           |Type   |Default|Description          |
   +===============+=======+=======+=====================+
   |sw_init        |TyBool |False  |initialisation switch|
   +---------------+-------+-------+---------------------+
   |httpmod        |TyDic  |None   |http modus           |
   +---------------+-------+-------+---------------------+
   |sw_replace_keys|TnBool |False  |replace keys switch  |
   +---------------+-------+-------+---------------------+
   |keys           |TnArr  |None   |Keys array           |
   +---------------+-------+-------+---------------------+
   |reqs           |TyDic  |None   |Requests dictionary  |
   +---------------+-------+-------+---------------------+
   |app            |TyDic  |None   |Appliction dictionary|
   +---------------+-------+-------+---------------------+

App\_: Methods
^^^^^^^^^^^^^^

  .. App\_-Methods-label:
  .. table:: *App\_ Methods*

   +----+------+------------------------------------+
   |Name|Type  |Description                         |
   +====+======+====================================+
   |init|class |initialise static variables of class|
   |    |      |if they are not allready initialized|
   +----+------+------------------------------------+
   |sh  |class |show (return) class                 |
   +----+------+------------------------------------+

App\_ Method: init
^^^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Parameter-of-App\_-Method-init-label:
  .. table:: *Parameter of: App\_ Method init*

   +---------+-----+-----------------+
   |Name     |Type |Description      |
   +=========+=====+=================+
   |cls      |class|Current class    |
   +---------+-----+-----------------+
   |\**kwargs|TyAny|Keyword arguments|
   +---------+-----+-----------------+

App\_ Method: sh
^^^^^^^^^^^^^^^^
        
  .. App\_-Method-sh-label:
  .. table:: *App\_ Method: sh*

   +---------+-----+-----------------+
   |Name     |Type |Description      |
   +=========+=====+=================+
   |cls      |class|Current class    |
   +---------+-----+-----------------+
   |\**kwargs|TyAny|Keyword arguments|
   +---------+-----+-----------------+

Return Value
""""""""""""

  .. App\_-Method-sh-Return-Value-label:
  .. table:: *App\_ Method sh: Return Value*

   +----+--------+-----------+
   |Name|Type    |Description|
   +====+========+===========+
   |log |TyLogger|Logger     |
   +----+--------+-----------+

Base module: cfg\_.py
=====================

The Base module cfg\_.py contains a single static class ``Cfg_``.

cfg\_.py Class Cfg\_
---------------------

The static class ``Cfg_`` contains the subsequent static variables and methods

Cfg\_Static Variables
^^^^^^^^^^^^^^^^^^^^^

  .. Cfg\_-Static-Variables-label:
  .. table:: *Cfg\_ Static Variables*

   +----+-----+-------+--------------------+
   |Name|Type |Default|Description         |
   +====+=====+=======+====================+
   |cfg |TyDic|None   |Configuration object|
   +----+-----+-------+--------------------+

Cfg\_ Methods
^^^^^^^^^^^^^

  .. Cfg\_-Methods-label:
  .. table:: *Cfg\_ Methods*

   +----+------+-----------------------------------+
   |Name|Type  |Description                        |
   +====+======+===================================+
   |sh  |class |read pacmod yaml file into class   |
   |    |      |variable cls.dic and return cls.cfg|
   +----+------+-----------------------------------+

Cfg\_ Method: sh
^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Cfg\_-Method-sh-Parameter-label:
  .. table:: *Cfg\_ Method sh: Parameter*

   +--------+--------+-----------------+
   |Name    |Type    |Description      |
   +========+========+=================+
   |cls     |class   |Current class    |
   +--------+--------+-----------------+
   |log     |TyLogger|Logger           |
   +--------+--------+-----------------+
   |d_pacmod|TyDic   |pacmod dictionary|
   +--------+--------+-----------------+

Return Value
""""""""""""

  .. Cfg\_-Method-sh-Return-Value-label:
  .. table:: *Cfg\_ Method sh: Return Value*

   +-------+-----+-----------+
   |Name   |Type |Description|
   +=======+=====+===========+
   |cls.cfg|TyDic|           |
   +-------+-----+-----------+

Base Modul: exit\_.py
=====================

The Base module exit\_.py contains a single static class ``Ext_``.

exit\_.py class: Exit\_
-----------------------

The static Class ``Exit_`` of Module exit\_.py contains the subsequent static variables and methods.

Exit\_: Variables
^^^^^^^^^^^^^^^^^

  .. Exit\_-Variables-label:
  .. table:: *Exit\_ Variables*

   +--------------+------+-------+---------------------+
   |Name          |Type  |Default|Description          |
   +==============+======+=======+=====================+
   |sw_init       |TyBool|False  |initialisation switch|
   +--------------+------+-------+---------------------+
   |sw_critical   |TyBool|False  |critical switch      |
   +--------------+------+-------+---------------------+
   |sw_stop       |TyBool|False  |stop switch          |
   +--------------+------+-------+---------------------+
   |sw_interactive|TyBool|False  |interactive switch   |
   +--------------+------+-------+---------------------+

Exit\_: Methods
^^^^^^^^^^^^^^^

  .. Exit\_-Methods-label:
  .. table:: *Exit\_ Methods*

   +----+------+------------------------------------+
   |Name|Method|Description                         |
   +====+======+====================================+
   |init|class |initialise static variables of class|
   |    |      |if they are not allready initialized|
   +----+------+------------------------------------+
   |sh  |class |show (return) class                 |
   +----+------+------------------------------------+

Exit\_: Method: init
^^^^^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Exit\_-Method-init-Parameter:
  .. table:: *Exit\_ Method init: Parameter*

   +---------+-----+-----------------+
   |Name     |Type |Description      |
   +=========+=====+=================+
   |cls      |class|Current class    |
   +---------+-----+-----------------+
   |\**kwargs|TyAny|Keyword arguments|
   +---------+-----+-----------------+

Exit\_: Method: sh
^^^^^^^^^^^^^^^^^^
        
Parameter
"""""""""

  .. Exit\_-Method-sh-Parameter:
  .. table:: *Exit\_ Method sh: Parameter*

   +---------+-----+-----------------+
   |Name     |Type |Description      |
   +=========+=====+=================+
   |cls      |class|Current class    |
   +---------+-----+-----------------+
   |\**kwargs|TyAny|Keyword arguments|
   +---------+-----+-----------------+

Return Value
""""""""""""

  .. Exit\_-Method-sh-Return-Value:
  .. table:: *Exit\_ Method sh: Return Value*

   +----+-----+-------------+
   |Name|Type |Description  |
   +====+=====+=============+
   |cls |class|Current class|
   +----+-----+-------------+

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

Python Modules
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
