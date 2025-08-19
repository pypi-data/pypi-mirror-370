py-encase
=========

py-encase: Tool for encased python script environment.

Requirement
-----------

- Python >= 3.9
- pip3

Usage
-----

1. Initialization of working environment under certain directory
   (“${prefix}”) with creating new python script ‘newscript.py’ from
   template and installing specified python modules specified in CLI.

::

   # Create environment
   % py_encase --manage init -r -g -v --prefix=${prefix} -m pytz -m tzlocal newscript.py
   .....
   # Check file produced
   % ( cd ${prefix} ls -ltrd {bin,lib/python,lib/python/site-packages/*}/* )
   .... bin/py_encase.py
   .... bin/mng_encase -> py_encase.py
   .... bin/newscript -> py_encase.py
   .... lib/python/site-packages
   .... lib/python/newscript.py
   .... lib/python/site-packages/3.13.4/pytz
   .... lib/python/site-packages/3.13.4/pytz-2025.2.dist-info
   .... lib/python/site-packages/3.13.4/tzlocal
   .... lib/python/site-packages/3.13.4/tzlocal-5.3.1.dist-info

The entity of this tool will be copied to ``${prefix}/py_encase.py`` New
script is created as ``lib/python/newscript.py``.

The symbolic link under ``bin/`` (=\ ``bin/newscript``) is run
``lib/python/newscript.py`` by dealing with environmental variable
``PYTHONPATH`` to use python modules that are locally installed by pip
under ``lib/python/site-packages``.

::

   % ${prefix}/bin/newscript -d
   Hello, World! It is "Wed Jul  2 16:26:06 2025."
   Python : 3.13.4 ({somewhere}/bin/python3.13)
   1  : ${prefix}/lib/python
   2  : ${prefix}/lib/python/site-packages/3.13.4
   3  : ....

Another symbolic link ``bin/mng_encase`` can be used to make another
python script and symbolic link for execution from template.

::

   % ${prefix}/bin/mng_encase add another_script_can_be_run.py

another python script for library/module from template also can be
created.

::

   % ${prefix}bin/mng_encase addlib another_script_can_be_run.py

It is also possible to install module by ``pip`` locally under
‘${prefix}/lib/python/site-packages’.

::

   % ${prefix}bin/mng_encase install modulename1 modulename2 ....

The moduled installed locally by this tool can be deleted by
sub-commands ``clean`` or ``distclean``

::

   # Removing module installed locally by currently used python/pip version
   % ${prefix}bin/mng_encase clean
   # Removing all module installed locally by pip
   % ${prefix}bin/mng_encase distclean

Please refer the help messages for further usage.

::

   % ${prefix}/bin/mng_encase --help

   usage: mng_encase [-P PYTHON] [-I PIP] [-p PREFIX] [-G GIT_COMMAND] [-v] [-n] [-h]
                     {info,init,add,addlib,newmodule,clean,distclean,selfupdate,install,download,freeze,inspect,list,cache,piphelp} ...

   positional arguments:
     {info,init,add,addlib,newmodule,clean,distclean,selfupdate,install,download,freeze,inspect,list,cache,piphelp}
       info                Show information
       init                Initialise Environment
       add                 add new script files
       addlib              add new script files
       newmodule           add new module source
       clean               clean-up
       distclean           Entire clean-up
       selfupdate          Self update of py_encase.py
       install             PIP command : install
       download            PIP command : download
       freeze              PIP command : freeze
       inspect             PIP command : inspect
       list                PIP command : list
       cache               PIP command : cache
       piphelp             PIP command : help

   optional arguments:
     -P PYTHON, --python PYTHON
                           Python path / command
     -I PIP, --pip PIP     PIP path / command
     -p PREFIX, --prefix PREFIX
                           prefix of the directory tree. (Default:
                           Grandparent directory if the name of parent
                           directory of mng_encase is bin, otherwise
                           current working directory.
     -G GIT_COMMAND, --git-command GIT_COMMAND
                           git path / command
     -v, --verbose         Verbose output
     -n, --dry-run         Dry Run Mode
     -h, --help

Author
------

::

   Nanigashi Uji (53845049+nanigashi-uji@users.noreply.github.com)
   Nanigashi Uji (4423013-nanigashi_uji@users.noreply.gitlab.com)
