#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-

import sys
import os
import datetime
import pathlib
import argparse
import shutil
import subprocess
import inspect
import filecmp
import textwrap
import re
import typing
import io
import itertools
import getpass
import socket
import collections
import urllib.parse
import json
import glob
import importlib.metadata
import keyword

class PyEncase(object):

    VERSION          = '0.0.8'
    PIP_MODULE_NAME  = 'py-encase'
    ENTYTY_FILE_NAME = pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name
    #    ENTYTY_FILE_NAME = pathlib.Path(__file__).resolve().name

    MNG_SCRIPT = 'mng_encase'
    MNG_OPT    = '--manage'

    PIP_SBCMDS_ACCEPT = {'install':   None,
                         'download':  None,
#                         'uninstall': None,
                         'freeze':    None,
                         'inspect':   None,
                         'list':      None,
#                         'show':      None,
#                         'check':     None,
#                         'search':    None,
                         'cache':     None,
#                         'index':     None,
#                         'wheel':     None,
#                         'hash':      None,
                         'help':      'piphelp'}

    SCRIPT_STD_LIB = {}

    FILENAME_DEFAULT = { '____GIT_DUMMYFILE____': '.gitkeep',
                         '____README_NAME____':   'README.md',
                        }

    NON_ASCII_PATTERN       = re.compile('[^0-9A-Za-z]+')

    SHEBANG_DEFAULT = '#!/usr/bin/env python3'

    GIT_REMOTE_DEFAULT = { 'LOCATION'      : os.path.join('~', 'git_repositories'),
                           'REMOTE_GITCMD' : 'git',
                           'SSH_COMMAND'   : 'ssh',
                           'REMOTE_ALIAS'  : 'origin'}

    class StreamExtd(object):
        """
        Extended Stream Interface
        """
        class StreamIF(object):
            """
            Wrapper for stdout/stderr to show with full qualified function name
            """
            def __init__(self, stream=sys.stderr):
                self.stream      = stream
                
            def write(self, text='', *args, clsname=None, more_upper=False):
                refname,lineno = self.ana_caller_fqn(clsname=clsname, more_upper=more_upper)
                tmplt = "[%%s:%%d] %s\n" % (text, )
                return self.stream.write(tmplt % ((refname, lineno)
                                                  + (args if isinstance(args, tuple) else (args,) )))
        
            def ana_caller_fqn(self, clsname=None, more_upper=False):
                try:
                    if more_upper:
                        frm = inspect.currentframe().f_back.f_back.f_back
                    else:
                        frm = inspect.currentframe().f_back.f_back
        
                    mod_name = frm.f_globals.get('__name__', '')
                    code = frm.f_code
        
                    if sys.version_info >= (3, 11):
                        qualname = code.co_qualname
                    else:
                        if clsname:
                            qualname = clsname + '.' + code.co_name
                        else:
                            prntobj = frm.f_locals.get('self') or frm.f_locals.get('cls')
                            if prntobj:
                                qualname = type(prntobj).__name__ + '.' + code.co_name
                            else:
                                qualname = code.co_name
        
                    fqn_name = (mod_name+'.'+qualname) if ( mod_name and mod_name != '__main__' ) else qualname
                    return (fqn_name, frm.f_lineno)
        
                finally:
                    del frm
    
    
        def __init__(self,
                     stdin=sys.stdin,
                     stderr=sys.stdout,
                     stdout=sys.stderr):
    
            self.streams = collections.namedtuple('streams',
                                                  ['stdin',
                                                   'stdout',
                                                   'stderr'])(stdin=self.__class__.StreamIF(sys.stdin),
                                                              stderr=self.__class__.StreamIF(sys.stdout),
                                                              stdout=self.__class__.StreamIF(sys.stderr))
        @property
        def stdin(self):
            return self.streams.stdin
    
        @property
        def stdout(self):
            return self.streams.stdout
    
        @property
        def stderr(self):
            return self.streams.stderr
    
    def __init__(self, argv:list=sys.argv, 
                 python_cmd:str=None, pip_cmd:str=None, 
                 prefix_cmd:str=None, git_cmd:str=None, 
                 verbose:bool=False, dry_run:bool=False, encoding='utf-8'):

        self.streams = self.__class__.StreamExtd(stdin=sys.stdin,
                                                 stderr=sys.stdout,
                                                 stdout=sys.stderr)

        self.argv         = argv
        self.path_invoked = pathlib.Path(self.argv[0])
        self.flg_symlink  = self.path_invoked.is_symlink()
        self.encoding     = encoding
        self.set_python_path(python_cmd=python_cmd,
                             pip_cmd=pip_cmd, prefix_cmd=prefix_cmd)
        self.set_git_path(git_cmd=git_cmd)
        self.verbose      = verbose
        self.dry_run      = dry_run

        self.__class__.SCRIPT_STD_LIB['pkg_cache'] = {'creator'     : self.python_pkg_cache_template_save,
                                                      'description' : 'Module for cache file under package directory',
                                                      'depends'     : ['intrinsic_format'],
                                                      'pip_module'  : ['PyYAML', 'pkgstruct']}

        self.__class__.SCRIPT_STD_LIB['intrinsic_format'] = {'creator'     : self.python_intrinsic_format_template_save,
                                                             'description' : 'Module for intrinsic data formater',
                                                             'depends'     : [],
                                                             'pip_module'  : ['PyYAML']}

    @property
    def stdin(self):
        return self.streams.stdin

    @property
    def stdout(self):
        return self.streams.stdout
    
    @property
    def stderr(self):
        return self.streams.stderr


    def set_python_path(self, python_cmd=None, pip_cmd=None, prefix_cmd=None):
        self.python_select = (python_cmd if isinstance(python_cmd,str) and python_cmd
                              else os.environ.get('PYTHON', os.environ.get('PYTHON3', 'python3')))

        self.python_shebang = (("#!"+self.python_select) if self.python_select.startswith('/') 
                               else ("#!"+shutil.which('env')+' '+self.python_select) )

        self.python_use = pathlib.Path(shutil.which(python_cmd) if isinstance(python_cmd,str) and python_cmd 
                                       else shutil.which(os.environ.get('PYTHON',
                                                                        os.environ.get('PYTHON3',
                                                                                       shutil.which('python3') or shutil.which('python')))))

        self.pip_use = pathlib.Path(shutil.which(pip_cmd) if isinstance(pip_cmd,str) and pip_cmd 
                                    else shutil.which(os.environ.get('PIP',
                                                                     os.environ.get('PIP3',
                                                                                    shutil.which('pip3') or shutil.which('pip')))))
        
        if sys.executable == self.python_use.absolute():
            self.python_vertion_str = '.'.join(sys.version_info[:2])
        else:
            py_version_fetch = subprocess.run([str(self.python_use), '--version'], encoding=self.encoding, stdout=subprocess.PIPE)
            self.python_vertion_str = py_version_fetch.stdout.split()[1]

        pip_version_fetch = subprocess.run([str(self.pip_use), '--version'], encoding=self.encoding, stdout=subprocess.PIPE)
        self.pip_vertion_str = pip_version_fetch.stdout.split()[1]

        if isinstance(prefix_cmd,str) and prefix_cmd:
            self.prefix = os.path.expandvars(os.path.expanduser(prefix_cmd))
            flg_substructure = not ( os.path.exists(os.path.join(self.prefix, self.path_invoked.name)) or 
                                     os.path.exists(os.path.join(self.prefix, self.path_invoked.name)+'.py') )
        else:
            path_abs     = self.path_invoked.absolute()
            flg_substructure = (path_abs.parent.name=='bin')
            self.prefix  = str(path_abs.parent.parent) if flg_substructure else str(path_abs.parent)

        self.bindir  = os.path.join(self.prefix, 'bin') if flg_substructure else self.prefix
        self.libdir  = os.path.join(self.prefix, 'lib') if flg_substructure else self.prefix
        self.vardir  = os.path.join(self.prefix, 'var') if flg_substructure else self.prefix
        self.srcdir  = os.path.join(self.prefix, 'src') if flg_substructure else self.prefix

        self.tmpdir            = os.path.join(self.vardir, 'tmp', 'python', 'packages', self.python_vertion_str)
        self.logdir            = os.path.join(self.vardir, 'log')

        self.python_path         = os.path.join(self.libdir, 'python')
        self.python_pip_path     = os.path.join(self.libdir, 'python', 'site-packages', self.python_vertion_str)
        self.python_pip_cache    = os.path.join(self.vardir, 'cache', 'python', 'packages', self.python_vertion_str)
        self.python_pip_src      = os.path.join(self.srcdir, 'python', 'packages', self.python_vertion_str)
        self.python_pip_logdir   = os.path.join(self.logdir, 'pip', self.pip_vertion_str)
        self.python_pip_log_path = os.path.join(self.python_pip_logdir, 'pip-log.txt')
        self.git_keepdirs = [os.path.dirname(self.python_pip_path),
                             os.path.dirname(self.python_pip_cache),
                             os.path.dirname(self.python_pip_src),
                             os.path.dirname(self.python_pip_logdir), 
                             os.path.dirname(self.tmpdir)]


    def set_git_path(self, git_cmd:str=None):
        self.git_path = shutil.which(git_cmd if isinstance(git_cmd,str) and git_cmd else os.environ.get('GIT', 'git'))

    def main(self):
        argprsr = argparse.ArgumentParser(add_help=False)
        if self.flg_symlink:
            argprsr.set_defaults(manage=(self.path_invoked.name
                                         in (self.MNG_SCRIPT, self.MNG_SCRIPT+'.py')))
        else:
            argprsr.add_argument(self.MNG_OPT, action='store_true') 

        args, rest = argprsr.parse_known_args()

        if not args.manage:

            if self.flg_symlink:
                scriptname = self.path_invoked.name
                scriptargs = rest
            else:
                argprsr.add_argument('script', nargs='?', default=None, const=None, help='script name/path')
                narg,rest = argprsr.parse_known_args()
                scriptname = narg.script
                scriptargs = rest

            self.run_script(script=scriptname, args=rest)
        else:
            argprsrm = argparse.ArgumentParser(add_help=False, exit_on_error=False)
            argprsrm.add_argument('-P', '--python', default=None, help='Python path / command')
            argprsrm.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            argprsrm.add_argument('-p', '--prefix',  default=None, help=('prefix of the directory tree. ' +
                                                                         '(Default: Grandparent directory' +
                                                                         ' if the name of parent directory of %s is bin,'
                                                                         ' otherwise current working directory.' 
                                                                         % (self.path_invoked.name, )))
            argprsrm.add_argument('-G', '--git-command', default=None, help='git path / command')
            argprsrm.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
            argprsrm.add_argument('-n', '--dry-run', action='store_true', help='Dry Run Mode')

            argpre,restpre = argprsrm.parse_known_args(rest) 
            self.verbose = argpre.verbose
            self.dry_run = argpre.dry_run

            self.set_python_path(python_cmd=argpre.python, pip_cmd=argpre.pip, 
                                 prefix_cmd=(argpre.prefix if hasattr(argpre, 'prefix') else None))
            self.set_git_path(git_cmd=argpre.git_command)

            argprsrm.add_argument('-h', '--help', action='help') 

            sbprsrs = argprsrm.add_subparsers(dest='subcommand')
            
            parser_add_info = sbprsrs.add_parser('info', help='Show information')
            parser_add_info.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Show all path information')
            parser_add_info.add_argument('-l', '--long',    action='store_true', help='Show long description')
            parser_add_info.add_argument('-s', '--short',   action='store_true', help='Show minimum description')
            parser_add_info.add_argument('-V', '--version', action='store_true', help='Show version information')
            parser_add_info.add_argument('-m', '--pip-module-name',    action='store_true', help='Show PyPI module name')
            parser_add_info.add_argument('-M', '--manage-script-name', action='store_true', help='Show manage script name')
            parser_add_info.add_argument('-O', '--manage-option',      action='store_true', help='Show CLI option for manage-mode')
            parser_add_info.set_defaults(handler=self.show_info)


            parser_add_contents = sbprsrs.add_parser('contents', help='Show file list')
            parser_add_contents.add_argument('-v', '--verbose',     action='store_true', default=self.verbose, help='Show all path information')
            parser_add_contents.add_argument('-a', '--all',         action='store_true', help='Show all list')
            parser_add_contents.add_argument('-b', '--bin-script',  action='store_true', help='Show bin scripts')
            parser_add_contents.add_argument('-l', '--lib-script',  action='store_true', help='Show lib scripts')
            parser_add_contents.add_argument('-m', '--modules-src', action='store_true', help='Show module sources')
            parser_add_contents.set_defaults(handler=self.show_contents)

            parser_add_init = sbprsrs.add_parser('init', help='Initialise Environment')
            parser_add_init.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_init.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_init.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                       '(Default: Grandparent directory' +
                                                                                       ' if the name of parent directory of %s is bin,'
                                                                                       ' otherwise current working directory.' 
                                                                                       % (self.path_invoked.name, )))
            parser_add_init.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_init.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_init.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')


            parser_add_init.add_argument('-M', '--move', action='store_true', help='moving this script body into instead of copying')
            parser_add_init.add_argument('-g', '--git',  action='store_true', help='setup files for git')

            self.__class__.GitIF.add_remoteif_arguments(arg_parser=parser_add_init)
            #self.__class__.GitIF.add_invokeoptions_arguments(arg_parser=parser_add_init)
            
            parser_add_init.add_argument('-r', '--readme', action='store_true', help='setup/update README.md')
            parser_add_init.add_argument('-t', '--title',  help='Project title')
            parser_add_init.add_argument('-m', '--module', default=[], action='append', help='install module by pip')
            parser_add_init.add_argument('-s', '--script-lib', default=[], action='append', help='install library script from template.')
            parser_add_init.add_argument('-S', '--std-script-lib', action='store_true', help=('install standard library scripts. (equivalent to "' +
                                                                                         ' '.join(['-s %s' % (m, ) for m 
                                                                                                   in self.__class__.SCRIPT_STD_LIB.keys() ])
                                                                                         +')"'))
            parser_add_init.add_argument('scriptnames', nargs='*', help='script file name to be created')
            parser_add_init.set_defaults(handler=self.manage_env)
          
            parser_add_add = sbprsrs.add_parser('add', help='add new script files')
            parser_add_add.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_add.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_add.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                      '(Default: Grandparent directory' +
                                                                                      ' if the name of parent directory of %s is bin,'
                                                                                      ' otherwise current working directory.' 
                                                                                      % (self.path_invoked.name, )))
            parser_add_add.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_add.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_add.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')

            parser_add_add.add_argument('-r', '--readme', action='store_true', help='setup/update README.md')
            parser_add_add.add_argument('-m', '--module', default=[], action='append', help='install module by pip')
            parser_add_add.add_argument('-s', '--script-lib', default=[], action='append', help='install library script from template.')
            parser_add_add.add_argument('-S', '--std-script-lib', action='store_true', help=('install standard library scripts. (equivalent to "' +
                                                                                             ' '.join(['-s %s' % (m, ) for m 
                                                                                                       in self.__class__.SCRIPT_STD_LIB.keys() ])
                                                                                             +'"'))
            parser_add_add.add_argument('scriptnames', nargs='+', help='all files')
            parser_add_add.set_defaults(handler=self.manage_env)

            parser_add_addlib = sbprsrs.add_parser('addlib', help='add new script files')
            parser_add_addlib.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_addlib.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_addlib.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                         '(Default: Grandparent directory' +
                                                                                         ' if the name of parent directory of %s is bin,'
                                                                                         ' otherwise current working directory.' 
                                                                                        % (self.path_invoked.name, )))
            parser_add_addlib.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_addlib.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_addlib.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_addlib.add_argument('-r', '--readme', action='store_true', help='setup/update README.md')
            parser_add_addlib.add_argument('-m', '--module', default=[], action='append', help='install module by pip')
            parser_add_addlib.add_argument('-S', '--std-script-lib', action='store_true', help=('install standard library scripts. (equivalent to "' +
                                                                                                ' '.join(['-s %s' % (m, ) for m 
                                                                                                          in self.__class__.SCRIPT_STD_LIB.keys() ])
                                                                                                +'"'))
            parser_add_addlib.add_argument('script_lib', nargs='+', help='all files')
            parser_add_addlib.set_defaults(handler=self.manage_env)

            parser_add_newmodule = sbprsrs.add_parser('newmodule', help='add new module source')
            parser_add_newmodule.add_argument('-P', '--python', default=None, help='Python path / command')
            parser_add_newmodule.add_argument('-I', '--pip',  default=None, help='PIP path / command')
            parser_add_newmodule.add_argument('-p', '--prefix',  default=self.prefix, help=('prefix of the directory tree. ' +
                                                                                         '(Default: Grandparent directory' +
                                                                                         ' if the name of parent directory of %s is bin,'
                                                                                         ' otherwise current working directory.' 
                                                                                        % (self.path_invoked.name, )))
            parser_add_newmodule.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_newmodule.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_newmodule.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')

            parser_add_newmodule.add_argument('-S', '--set-shebang', action='store_true', help='Set shebang based on the local environment')

            parser_add_newmodule.add_argument('-Q', '--no-readme', action='store_false', dest='readme',
                                              default='True', help='NO README.md created')
            parser_add_newmodule.add_argument('-b', '--no-git-file', action='store_false', dest='git',
                                              default='True', help='NO README.md created')
            
            self.__class__.GitIF.add_remoteif_arguments(arg_parser=parser_add_newmodule)
            #self.__class__.GitIF.add_invokeoptions_arguments(arg_parser=parser_add_newmodule)

            parser_add_newmodule.add_argument('-W', '--module-website', default=[], action='append', help='New module URL')
            parser_add_newmodule.add_argument('-d', '--description',  help='Project description')
            parser_add_newmodule.add_argument('-t', '--title',        help='Project title')
            parser_add_newmodule.add_argument('-C', '--class-name', default=[], action='append', help='Module class name')
            parser_add_newmodule.add_argument('-m', '--module', default=[], action='append', help='required (external) modules used by new modules')
            parser_add_newmodule.add_argument('-k', '--keywords', default=[], action='append', help='keywords related to new modules')
            parser_add_newmodule.add_argument('-c', '--classifiers', default=[], action='append', help='keywords related to new modules')
            parser_add_newmodule.add_argument('-A', '--author-name',   default=[], action='append', help='author name of new modules')
            parser_add_newmodule.add_argument('-E', '--author-email',  default=[], action='append', help='author email of new modules')
            parser_add_newmodule.add_argument('-M', '--maintainer-name',  default=[], action='append', help='maintainer name of new modules')
            parser_add_newmodule.add_argument('-N', '--maintainer-email',  default=[], action='append', help='maintainer email of new modules')
            parser_add_newmodule.add_argument('-Y', '--create-year', default=[], action='append', help='Year in LICENSE')
            parser_add_newmodule.add_argument('module_name', nargs='+', help='new module names')
            parser_add_newmodule.set_defaults(handler=self.setup_newmodule)
            
            parser_add_updatereadme = sbprsrs.add_parser('update_readme', help='update readme file')
            parser_add_updatereadme.set_defaults(handler=self.manage_readme)
            parser_add_updatereadme.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_updatereadme.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_updatereadme.add_argument('-b', '--backup',  action='store_true', help='Keep backup file')
            parser_add_updatereadme.add_argument('-t', '--title',   help='Title text')

            parser_add_managegit = sbprsrs.add_parser('init_git', help='Initialise git repository')
            parser_add_managegit.add_argument('-G', '--git-command', default=self.git_path, help='git path / command')
            parser_add_managegit.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_managegit.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            self.__class__.GitIF.add_remoteif_arguments(arg_parser=parser_add_managegit)
            parser_add_managegit.add_argument('-m', '--module-src', help='Setup git for specified module source')
            parser_add_managegit.set_defaults(handler=self.manage_git)

            parser_add_clean = sbprsrs.add_parser('clean', help='clean-up')

            parser_add_clean.set_defaults(handler=self.clean_env)
            parser_add_clean.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_clean.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')

            parser_add_distclean = sbprsrs.add_parser('distclean', help='Entire clean-up')
            parser_add_distclean.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_distclean.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_distclean.set_defaults(handler=self.clean_env)

            #parser_add_selfupdate = sbprsrs.add_parser('selfupdate', help='Self update of '+os.path.basename(__file__))
            parser_add_selfupdate = sbprsrs.add_parser('selfupdate', 
                                                       help='Self update of '
                                                       +pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name)

            parser_add_selfupdate.add_argument('-v', '--verbose', action='store_true', default=self.verbose, help='Verbose output')
            parser_add_selfupdate.add_argument('-n', '--dry-run', action='store_true', default=self.dry_run, help='Dry Run Mode')
            parser_add_selfupdate.add_argument('-f', '--force-install', action='store_true', help='Force install')

            parser_add_selfupdate.set_defaults(handler=self.self_update)

            for c,cc in self.__class__.PIP_SBCMDS_ACCEPT.items():
                _scmd = c if cc is None else cc
                _prsr_add = sbprsrs.add_parser(_scmd, 
                                               help=('PIP command : %s' % (c,)))
                _prsr_add.add_argument('pip_subcommand_args', nargs='*', help='Arguments for pip subcommands')
                _prsr_add.set_defaults(handler=self.invoke_pip)

            #argps= argprsrm.parse_args()

            argps,restps = argprsrm.parse_known_args(rest) 

            #self.set_python_path(python_cmd=argps.python, pip_cmd=argps.pip, 
            #                     prefix_cmd=(argps.prefix if hasattr(argps, 'prefix') else None))
            
            if hasattr(argps, 'handler'):
                argps.handler(argps, restps)
            else:
                argprsrm.print_help()
            
    def invoke_pip(self, args:argparse.Namespace, rest:list=[]):
        flg_verbose = args.verbose if hasattr(args, 'verbose') else False
        flg_dry_run  = args.dry_run  if hasattr(args, 'dry_run') else False
        return self.run_pip(subcmd=args.subcommand,
                            args=args.pip_subcommand_args+rest,
                            verbose=flg_verbose, dry_run=flg_dry_run)
    @classmethod
    def version_compare(cls, v1:str, v2:str):
        """
        v1 < v2: -1, v1 == v2 :0, v1 > v2: 1
        """
        ibuf1  = [int(x) for x in v1.split('.')]
        ibuf2  = [int(x) for x in v2.split('.')]
        l_ibuf = max(len(ibuf1), len(ibuf2))
        ibuf1 += [0] * (l_ibuf- len(ibuf1))
        ibuf2 += [0] * (l_ibuf- len(ibuf2))
        for i1, i2 in zip(ibuf1, ibuf2):
            if i1 < i2:
                return -1
            elif i1 > i2:
                return 1
        return 0

    def self_update(self, args:argparse.Namespace, rest:list=[]):
        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'
        self.set_python_path(python_cmd=(args.python if (hasattr(args, 'python') and
                                                         args.python is not None) else self.python_select),
                             pip_cmd=(args.pip if (hasattr(args, 'pip') and
                                                   args.pip is not None) else str(self.pip_use)),
                             prefix_cmd=( args.prefix if (hasattr(args, 'prefix') and
                                                          args.prefix  is not None) else self.prefix))
        flg_verbose   = args.verbose       if hasattr(args, 'verbose')       else self.verbose
        flg_dry_run   = args.dry_run       if hasattr(args, 'dry_run')       else False
        force_install = args.force_install if hasattr(args, 'force_install') else False

        pip_install_out = self.run_pip(subcmd='install', 
                                       args=['--upgrade', '--force-reinstall', 
                                             self.__class__.PIP_MODULE_NAME],
                                       verbose=flg_verbose, dry_run=False)

        pip_list_out = self.run_pip(subcmd='list', args=['--format', 'json'],
                                    verbose=flg_verbose, dry_run=False, capture_output=True)
        pip_installed = json.loads(pip_list_out.stdout)
        latest_version="0.0.0"
        for minfo in pip_installed:
            if ( (not isinstance(minfo, dict)) or 
                 minfo.get('name', "") != self.__class__.PIP_MODULE_NAME):
                continue
            latest_version=minfo.get('version', "0.0.0")

        if self.__class__.version_compare(self.__class__.VERSION, latest_version)<0 or force_install:
            orig_path = self.path_invoked.resolve()
            if orig_path.name != self.__class__.ENTYTY_FILE_NAME:
                self.stderr.write("selfupdate: Current version=='%s', Latest version=='%s', Force install?: %s" %
                                  (self.__class__.VERSION, latest_version, str(force_install)))
                raise ValueError("Filename is not proper: '"+orig_path.name+"' != '"+self.__class__.ENTYTY_FILE_NAME+"'")

            if flg_verbose or dry_run:
                self.stderr.write("selfupdate: Current version=='%s', Latest version=='%s', Force install?: %s" %
                                 (self.__class__.VERSION, latest_version, str(force_install)))

            new_version_path = os.path.join(self.python_pip_path,
                                            self.__class__.PIP_MODULE_NAME.replace('-', '_'),
                                            self.__class__.ENTYTY_FILE_NAME)
            
            if not os.path.isfile(new_version_path):
                self.stderr.write("selfupdate: Internal error: file not found: '%s'" %
                                  (self.__class__.VERSION, latest_version, str(force_install)))
                raise FileNotFoundError("Is not file: "+new_version_path)

            bkup_path = self.__class__.rename_with_mtime_suffix(orig_path,
                                                                add_sufix=("-"+self.__class__.VERSION),
                                                                dest_dir=self.tmpdir,
                                                                verbose=flg_verbose,
                                                                dry_run=flg_dry_run)
            if flg_verbose or flg_dry_run:
                self.stderr.write("selfupdate: Backup current file: '%s' --> '%s'" % (orig_path, bkup_path))
                                 
            if flg_verbose or flg_dry_run:
                self.stderr.write("selfupdate: Copy file: '%s' --> '%s'" % (new_version_path, orig_path, ))
            if not flg_dry_run:
                shutil.copy2(new_version_path, orig_path, follow_symlinks=True)
                os.chmod(orig_path, mode=0o755, follow_symlinks=True)
        else:
            if flg_verbose:
                self.stderr.write("selfupdate: skip (up-to-date) : Current version=='%s', Latest version=='%s', Force install?: %s" %
                                  (self.__class__.VERSION, latest_version, str(force_install)))

    def run_pip(self, subcmd:str, args=[], verbose=False, dry_run=False, **popen_kwargs):
        
        argprsrx = argparse.ArgumentParser(add_help=False, exit_on_error=False)
        argprsrx.add_argument('--isolated',  action='store_true')
        argprsrx.add_argument('--python',    default=str(self.python_use.absolute()))
        argprsrx.add_argument('--cache-dir', default=self.python_pip_cache)
        argprsrx.add_argument('--log',       default=self.python_pip_log_path)

        if subcmd == 'install':
            argprsrx.add_argument('-t', '--target', default=self.python_pip_path)
            argprsrx.add_argument('-s', '--src',    default=self.python_pip_src)
        elif subcmd == 'download':
            argprsrx.add_argument('-d', '--dest',   default=self.python_pip_path)
            argprsrx.add_argument('-s', '--src',    default=self.python_pip_src)
        elif subcmd in ('freeze', 'inspect', 'list'):
            argprsrx.add_argument('--path', default=self.python_pip_path)

        argsx, restx = argprsrx.parse_known_args(args)

        cmdargs = [ str(self.pip_use.absolute()) ]
        if argsx.isolated:
            cmdargs.append('--isolated')

        if self.__class__.version_compare(self.pip_vertion_str, "23.1")>=0:
            # python option is available for pip >= 23.1
            for opt in ['python']:
                if not hasattr(argsx, opt.replace('-', '_')):
                    continue
                cmdargs.extend(['--'+opt.replace('_', '-'), getattr(argsx,opt.replace('-', '_')) ] )

        cmdargs.append(subcmd)

        for opt in ['cache-dir', 'log', 'target', 'src', 'dest', 'path']:
            if not hasattr(argsx, opt.replace('-', '_')):
                continue
            cmdargs.extend(['--'+opt.replace('_', '-'), getattr(argsx,opt.replace('-', '_')) ] )

        cmdargs.extend(restx)

        if verbose or dry_run:
            self.stderr.write("Exec: '%s'" % (" ".join(cmdargs),))
        if not dry_run:
            return subprocess.run(cmdargs, shell=False,
                                  encoding=self.encoding, **popen_kwargs)

    def run_script(self, script:str, args:list=[]):
        os.environ['PYTHONPATH'] = "%s:%s:%s" % (self.python_path,
                                                 self.python_pip_path,
                                                 os.environ.get('PYTHONPATH',''))

        if script is None:
            cmd_args = [self.python_use ] + args
        elif isinstance(script, str) and script and os.path.isfile(script):
            cmd_args = [self.python_use, script ] + args
        else:
            script_path = os.path.join(self.python_path, script if script.endswith('.py') else script+'.py')
            
            if os.path.isdir(script_path):
                self.stderr.write("Error: '%s' is directory" % (script_path, ))
                raise IsADirectoryError()
            elif not os.path.isfile(script_path):

                pip_bin_path = os.path.join(self.python_pip_path, 'bin', script.removesuffix('.py') if script.endswith('.py') else script)
                if not os.path.isfile(pip_bin_path):
                    self.stderr.write("Error: File not found: '%s', '%s'" % (script_path, pip_bin_path))
                    raise FileNotFoundError()
                else:
                    script_path = pip_bin_path

            cmd_args = [self.python_use, script_path ] + args

        if self.verbose:
            self.stderr.write("Exec: '%s' with PYTHONPATH='%s'" %
                              ("".join(cmd_args), os.environ['PYTHONPATH']))
        sys.stdout.flush()
        sys.stderr.flush()
        os.execvpe(cmd_args[0], cmd_args, os.environ)


    def description(self):
        return "%s (Version: %s : %s)" % (self.__class__.PIP_MODULE_NAME, 
                                          self.__class__.VERSION, 
                                          pathlib.Path(__file__).resolve())

    def show_info(self, args:argparse.Namespace, rest:list=[]):

        flg_verbose            = args.verbose            if hasattr(args, 'verbose')            else self.verbose
        flg_long               = args.long               if hasattr(args, 'long')               else False
        flg_short              = args.short              if hasattr(args, 'short')              else False
        flg_version            = args.version            if hasattr(args, 'version')            else False
        flg_manage_script_name = args.manage_script_name if hasattr(args, 'manage_script_name') else False
        flg_manage_option      = args.manage_option      if hasattr(args, 'manage_option')      else False
        flg_pip_module_name    = args.pip_module_name    if hasattr(args, 'pip_module_name')    else False


        if not(flg_verbose or flg_long):
            if flg_version:
                sys.stdout.write("%s%s\n" % ('' if flg_short else 'PIP module version: ', self.__class__.VERSION ))
            if flg_pip_module_name:
                sys.stdout.write("%s%s\n" % ('' if flg_short else 'PIP module name:    ', self.__class__.PIP_MODULE_NAME ))
            if flg_manage_script_name:
                sys.stdout.write("%s%s\n" % ('' if flg_short else 'Manage script name: ', self.__class__.MNG_SCRIPT))
            if flg_manage_option:
                sys.stdout.write("%s%s\n" % ('' if flg_short else 'Manage mode option: ', self.__class__.MNG_OPT))
            if ( flg_version or flg_pip_module_name
                 or flg_manage_script_name  or flg_manage_option):
                return 

            print(self.description())
            return

        if flg_long:
            print(self.description())
            print('PIP module name:    ', self.__class__.PIP_MODULE_NAME )
            print('PIP module version: ', self.__class__.VERSION )
            print('Manage script name: ', self.__class__.MNG_SCRIPT)
            print('Manage mode option: ', self.__class__.MNG_OPT)
            return

        print("Description            : ", self.description())
        print("Python command         : ", str(self.python_use))
        print("Python select          : ", self.python_select)
        print("Python full path       : ", self.python_use.absolute())
        print("Command invoked        : ", self.path_invoked, "(LINK? : ", self.flg_symlink, ")")
        print("This file              : ", __file__)
        print("(source)               : ", pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve())
        print("Top of work directory  : ", self.prefix)
        print("bin directory          : ", self.bindir)
        print("var directory          : ", self.vardir)
        print("src directory          : ", self.srcdir)
        print("tmp directory          : ", self.tmpdir)
        print("log directory          : ", self.logdir)
        print("script directory       : ", self.python_path)
        print("python module directory: ", self.python_pip_path)
        print("PIP command            : ", str(self.pip_use))
        print("PIP full path          : ", self.pip_use.absolute())
        print("PIP cache directory    : ", self.python_pip_cache)
        print("PIP src directory      : ", self.python_pip_src)
        print("PIP log directory      : ", self.python_pip_logdir)
        print("PIP log path           : ", self.python_pip_log_path)
        print("Python shebang         : ", self.python_shebang)

    def show_contents(self, args:argparse.Namespace, rest:list=[]):
        flg_verbose = args.verbose       if hasattr(args, 'verbose')       else self.verbose
        flg_all     = args.all           if hasattr(args, 'all')           else False
        flg_bin     = args.bin_script    if hasattr(args, 'bin_script')    else False
        flg_lib     = args.lib_script    if hasattr(args, 'lib_script')    else False
        flg_mod     = args.module_src    if hasattr(args, 'module_src')    else False
        flg_pip     = args.pip_installed if hasattr(args, 'pip_installed') else False
        
        if flg_bin or flg_lib or flg_all:
            bin_scr, lib_scr = self.list_categorized_pkg_scripts()
            if flg_bin or flg_all:
                if flg_verbose:
                    print('Bin Scripts: ----------------------------------------')
                for scr in bin_scr:
                    print(scr)
            if flg_lib or flg_all:
                if flg_verbose:
                    print('Lib Scripts: ----------------------------------------')
                for scr in lib_scr:
                    print(scr)
        if flg_mod or flg_all:
            mod_src = self.list_module_source()
            if flg_verbose:
                print('Module source: ----------------------------------------')
            for src in mod_src:
                print(src)
        if flg_pip or flg_all:
            pip_mod = self.list_pip_modules()
            l_name    = max([len(n) for n,v,p in pip_mod])
            l_version = max([len(v) for n,v,p in pip_mod])
            if flg_verbose:
                print('Module installed: ----------------------------------------')
            for name, version, path in pip_mod:
                print("%-*s : %-*s (%s)" % (l_name, name, l_version, version, path))

    def list_all_pkg_scripts(self):
        return [os.path.basename(x) for x in 
                glob.glob(os.path.join(self.python_path, '*.py'))]

    def list_categorized_pkg_scripts(self):
        buf_bin = []
        buf_lib = []
        for x in self.list_all_pkg_scripts():
            b_path = os.path.join(self.bindir, x.removesuffix('.py'))
            if ( os.path.exists(b_path) 
                 and os.path.islink(b_path) ) : 
                buf_bin.append(x)
            else:
                buf_lib.append(x)
        return (buf_bin, buf_lib)

    def list_pip_modules(self):
        location = pathlib.Path(self.python_pip_path)
        buf = []
        for pttrn in ("*.dist-info", "*.egg-info"):
            for info_dir in (location.glob(pttrn)):
                try:
                    dist = importlib.metadata.PathDistribution(info_dir)
                    buf.append((dist.metadata.get("Name"), dist.version, dist.locate_file("")))
                except Exception as e:
                    print(e)
                    pass
        return sorted(buf, key=lambda x: x[0].lower())

    def list_module_source(self):
        buf = []
        for x in glob.glob(os.path.join(self.srcdir, '*', 'pyproject.toml')):
            buf.append(os.path.dirname(x))
        return buf

    def pkg_dir_list(self):
        return [self.prefix, self.bindir, self.vardir, 
                self.srcdir, self.tmpdir, self.logdir, self.python_path]

    def pip_dir_list(self):
        return [self.python_pip_path, self.python_pip_cache,
                self.python_pip_src, self.python_pip_logdir]

    def all_dir_list(self):
        return self.pkg_dir_list() + self.pip_dir_list()

    def make_directory_structure(self, dry_run=False, verbose=False):
        # Make directory structure 
        for dd in self.all_dir_list():
            if verbose or dry_run:
                self.stderr.write("mkdir -p : '%s'" % (dd, ))
            if not dry_run:
                os.makedirs(dd, mode=0o755, exist_ok=True)
        return

    def put_this_into_structure(self, flg_move=False, dry_run=False, verbose=False):

        #orig_path   = pathlib.Path(__file__).resolve() # self.path_invoked.absolute().name
        orig_path   = pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve()
        script_dest = os.path.join(self.bindir, orig_path.name)
        
        if os.path.exists(script_dest):
            if filecmp.cmp(orig_path, script_dest, shallow=False):
                if verbose:
                    self.stderr.write("Warning : same file already exists: '%s'" % (script_dest, ))
            else:
                self.stderr.write("Error : (different) file already exists: '%s'" % (script_dest, ))
                # raise FileExistsError
            return
        else:
            # Copy script into bindir 
            if verbose or dry_run:
                self.stderr.write("%s '%s' '%s' " %
                                  ('mv -i' if flg_move else 'cp -ai', orig_path, script_dest))
            if not dry_run:
                if flg_move:
                    try:
                        os.rename(orig_path, script_dest)
                    except OSError:
                        shutil.move(orig_path, script_dest)
                    except Exception as e:
                        self.stderr.write("Error: Can not meve : '%s' --> '%s'" % (orig_path, script_dest))
                        raise(e)
                else:
                    shutil.copy2(orig_path, script_dest, follow_symlinks=True)
                    os.chmod(script_dest, mode=0o755, follow_symlinks=True)
        return

    def mksymlink_this_in_structure(self, link_name, strip_py=True,
                                    dry_run=False, verbose=False):
        #entiry_name = self.path_invoked.resolve().name
        #entiry_name = pathlib.Path(__file__).resolve().name
        entiry_name = pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name
        link_dest   = os.path.join(self.bindir, 
                                   link_name.removesuffix('.py')
                                   if strip_py and link_name.endswith('.py') else link_name)

        if os.path.exists(link_dest):
            if pathlib.Path(link_dest).resolve() == self.path_invoked.absolute():
                self.stderr.write("Symbolic link already exists: '%s' --> '%s'" % (link_dest, entiry_name))
            else:
                self.stderr.write("(different) Symbolic link already exists: '%s'" % (link_dest, ))
                #raise FileExistsError
            return

        if verbose or dry_run:
            self.stderr.write("make symbolic link : '%s' --> '%s'" % (link_dest, entiry_name))
        if not dry_run:
            os.symlink(entiry_name, link_dest)

    @classmethod
    def rename_with_mtime_suffix(cls, file_path, add_sufix=None, dest_dir=None, verbose=False, dry_run=False):
        if not os.path.exists(file_path):
            if verbose or dry_run:
                self.stderr.write("File not found : '%s'" % (file_path, ))
            return None

        mtime  = os.path.getmtime(file_path)
        tmstmp = datetime.datetime.fromtimestamp(mtime).strftime("%Y%m%d_%H%M%S")

        bn, ext = os.path.splitext(os.path.basename(file_path))
        dest = os.path.dirname(file_path) if dest_dir is None else dest_dir
        
        if isinstance(add_sufix,str) and add_sufix:
            new_path = os.path.join(dest, ("%s%s.%s%s" % (bn, add_sufix, tmstmp, ext)))
        else:
            new_path = os.path.join(dest, ("%s.%s%s" % (bn, tmstmp, ext)))

        if not os.path.isdir(dest):
            if verbose or dry_run:
                cls.StreamExtd().stderr.write("Make directory: '%s'" % (dest, ))
            if not dry_run:
                os.makedirs(dest, exist_ok=True)

        if verbose or dry_run:
            cls.StreamExtd().stderr.write("Move file: '%s' --> '%s'" % (file_path, new_path))
        if not dry_run:
            try:
                os.rename(file_path, new_path)
            except OSError:
                shutil.move(file_path, new_path)
            except Exception as e:
                cls.StreamExtd().stderr.write("Error: Can not rename file '%s' --> '%s': %s" %
                                  (file_path, new_path, str(e)))
                return None

        return new_path

    @classmethod
    def remove_dircontents(cls, path_dir:str, 
                           dir_itself:bool=False,
                           verbose:bool=False, dry_run:bool=False):
        pdir = pathlib.Path(path_dir)

        if ((pdir.is_file() or pdir.is_symlink() )
            and ( not pdir.name.startswith('.'))):
            if verbose or dry_run:
                cls.StreamExtd().stderr.write("Remove file or symblic-link: '%s'" % (str(pdir), ))
            if not dry_run:
                try:
                    pdir.unlink()
                except Exception as e:
                    cls.StreamExtd().stderr.write("Error: removin file or symblic-link: '%s' : %s" %
                                      (str(pdir), str(e)))
                    # raise(e)
        elif (pdir.is_dir() and (not pdir.name.startswith('.'))):

            if dir_itself:

                if verbose or dry_run:
                    cls.StreamExtd().stderr.write("Remove directory: '%s'" % (str(pdir), ))
                if not dry_run:
                    shutil.rmtree(pdir)

            else:
                for ifp in pdir.iterdir():
                    if ifp.name.startswith('.'):
                        continue
                    if verbose or dry_run:
                        cls.StreamExtd().stderr.write("Remove file or symblic-link: '%s'" % (str(ifp), ))

                    if not dry_run:
                        try:
                            if ifp.is_file() or ifp.is_symlink():
                                ifp.unlink()
                            elif ifp.is_dir():
                                shutil.rmtree(ifp)
                        except Exception as e:
                            cls.StreamExtd().stderr.write("Error: removing file or symblic-link: '%s' : %s" % (str(ifp), str(e)))
                            # raise(e)
        else:
            cls.StreamExtd().stderr.write("Error: Unknown file type: '%s'" % (pdir.name, ))
            # raise(NotADirectoryError)

    def clean_env(self, args:argparse.Namespace, rest:list=[]):
        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'
        
        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False

        rmlist = []
        if subcmd == 'distclean':
            rmlist.extend(self.git_keepdirs)
        else:
            rmlist.extend(self.pip_dir_list())
            rmlist.append(self.tmpdir)
            
        if flg_verbose or flg_dry_run:
            self.stderr.write("s : '%s'" % (subcmd, ", ".join(rmlist)))
        for pdir in rmlist:
            self.__class__.remove_dircontents(path_dir=pdir, 
                                              dir_itself=False,
                                              verbose=flg_verbose, dry_run=flg_dry_run)

    class ExtCmdIF(StreamExtd):
    
        def __init__(self, verbose=False, dry_run=False, encoding='utf-8', **args):
            super().__init__(**args)
            self.verbose  = verbose
            self.dry_run  = dry_run
            self.encoding = encoding
    
        def invoke(self, cmdargs:list, verbose:bool=None, dry_run:bool=None,
                   check:bool=True, text:bool=True, hook=None,
                   more_upper:bool=False, encoding=None, **args):
            
            f_verbose = self.verbose if verbose is None else bool(verbose)
            f_dry_run = self.dry_run if dry_run is None else bool(dry_run)
            o_encoding = encoding if encoding else self.encoding
                
            if isinstance(cmdargs[0], (list, tuple)):
                buf = [self.invoke(cmdargs=list(cmdarg), verbose=f_verbose,
                                   dry_run=f_dry_run, check=check, text=text,
                                   hook=hook, more_upper=more_upper,
                                   encoding=o_encoding, **args) for cmdarg in cmdargs ]
                return tuple(buf) if isinstance(cmdargs, tuple) else buf
    
            if f_verbose or f_dry_run:
                self.stderr.write("Exec : '%s'" % (' '.join(cmdargs),))
    
            ret = subprocess.CompletedProcess(cmdargs, returncode=0, stdout='', stderr='')
            if not f_dry_run:
                try:
                    ret = subprocess.run(list(cmdargs), encoding=o_encoding, check=check, 
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=text)
                    if f_verbose:
                        self.stderr.write("Return code(%s): %d" % (cmdargs[0], ret.returncode, ), more_upper=more_upper)
                        if ret.stdout:
                            self.stdout.write("STDOUT(%s)     : '%s'" % (cmdargs[0], ret.stdout, ), more_upper=more_upper)
                    if ret.stderr:
                        self.stderr.write("STDERR(%s)     : '%s'" % (cmdargs[0], ret.stderr, ), more_upper=more_upper) 
                except Exception as e:
                    self.stderr.write(f"Exec ERROR ({e})", more_upper=more_upper) 

            if callable(hook):
                hook(cmdargs, ret, **args)
            return int(ret.returncode)
        
    class GitHubIF(StreamExtd):
        DEFAULT = {'gh_cmd':  'gh'}
    
        def __init__(self, opts:argparse.Namespace=None, gh_cmd=None, **kwds):
            super().__init__(**{k: v for k in kwds.items()
                                if k in ('stdin', 'stderr', 'stdout')})
            self.gh_cmd = (opts.gh_cmd if (hasattr(opts, 'gh_cmd') and opts.gh_cmd) else
                           (gh_cmd if gh_cmd else
                            os.environ.get('GITHUB_CLI', self.__class__.DEFAULT['gh_cmd'])))
            
            self.gh_path   = shutil.which(self.gh_cmd)
            self.gh_username   = None
            self.gh_user_id    = None
            self.gh_user_email = None
            self.gh_available  = False
            self.gh_repos      = None
            self.gh_licences   = []
            self.gh_gitignore  = []
            if self.gh_path:
                try:
                    gh_ret = subprocess.run([self.gh_path, 'api', 'user'],
                                            check=True, capture_output=True, text=True)
                    gh_userinfo = json.loads(gh_ret.stdout)
                    self.gh_username   = gh_userinfo['login']
                    self.gh_user_id    = gh_userinfo['id']
                    self.gh_user_email = f"{self.gh_user_id}+{self.gh_username}@users.noreply.github.com"
                    self.gh_available  = True
                    gh_ret = subprocess.run([self.gh_path, 'api', '/licenses', '--paginate'],
                                            check=True, capture_output=True, text=True)
                    self.gh_licences  = [ x.get('key') for x in  json.loads(gh_ret.stdout) ]
                    gh_ret = subprocess.run([self.gh_path, 'api', '/gitignore/templates', '--paginate'],
                                            check=True, capture_output=True, text=True)
                    self.gh_gitignore = json.loads(gh_ret.stdout)
                except Exception as e:
                    self.stderr.write(f'{self.__class__.__name__}.__init__() Error: {e}')
                    pass


        def __bool__(self):
            return bool(self.gh_available)
                
        def get_repos(self):
            if self.gh_available:
                try:
                    result = subprocess.run([self.gh_path, 'api', 'user/repos', '--paginate'],
                                            check=True, capture_output=True, text=True)
                    repos = json.loads(result.stdout)
                    return { r['name']: (r['full_name'],
                                         r['html_url'],
                                         r['clone_url'],
                                         r['ssh_url']) for r in repos }
                except Exception as e:
                    self.stderr.write(f'{self.__class__.__name__}.get_repos() Error: {e}')
            return {}
    
        def chk_repos(self, module, subdir=''):
            if not self.gh_available:
                return None
            if self.gh_repos is None:
                self.gh_repos = self.get_repos()
    
            mod_path = '_'.join([subdir.replace(os.sep, '_', module)]) if subdir else module
    
            return not (self.gh_repos.get(mod_path) is None)
    

        @property
        def userinfo(self):
            return (self.gh_username, self.gh_user_email)

        def guess_user(self, opts:argparse.Namespace=None, account=None):
            github_account = ( opts.git_remote_account if (hasattr(opts, 'git_remote_account')
                                                           and opts.git_remote_account) else
                               (account if account else 
                                (self.gh_username if self.gh_username else
                                 os.environ.get('GITHUB_USER',
                                                getpass.getuser()))))
            return github_account
    
        def guess_repo_url_base(self, opts:argparse.Namespace=None,
                                protocol=None, account=None):
            github_account = self.guess_user(opts=opts, account=account)
            github_protocol = ( opts.git_protocol
                                if (hasattr(opts, 'git_protocol')
                                    and opts.git_protocol) else protocol )
    
            return ( '%s://github.com/%s/' % (github_protocol, github_account)
                     if github_protocol in ('http', 'https') else
                     ( '%s://git@github.com/%s/' % (github_protocol, github_account)
                       if github_protocol == 'ssh' else
                       'git@github.com:%s/' % (github_account)))
    
        def guess_repo_url(self, module, subdir='',
                           opts:argparse.Namespace=None,
                           protocol=None, account=None, rmtext='.git'):
            url_base = self.guess_repo_url_base(opts=opts, protocol=protocol, account=account)
            mod_path = '_'.join([subdir.replace(os.sep, '_', module)]) if subdir else module
            return url_base.removesuffix('/')+f'/{module}{rmtext}'
    
        def create_repo_cmdargs(self, module, subdir='',
                                opts:argparse.Namespace=None, description=None,
                                push=False, proj_name=None, share=None, permit=None,
                                team_name=None, remote_name=None, source=None,
                                add_readme=False, add_license=None, add_gitignore=None):
            
            if not self.gh_available:
                return None
    
            if self.chk_repos(module=module, subdir=subdir):
                self.stderr.write(f'{self.__class__.__name__}.setup_repo(): Repository already exists on GitHub: {module}\n')
                return False
    
            mod_path = '_'.join([subdir.replace(os.sep, '_', module)]) if subdir else module
            cmd_args = [self.gh_path, 'repo',  'create', mod_path]
            if description:
                cmd_args.extend(['--description', description])
    
            if permit=='internal' and team_name:
                cmd_args.extend(['--internal', '--team', team_name])
            elif permit=='public':
                cmd_args.append('--public')
            elif permit=='private':
                cmd_args.append('--private')
    
            if push:
                cmd_args.append(['--push'])
    
            if source:
                cmd_args.extend(['--source', source])
    
            if remote_name:
                cmd_args.extend(['--remote', remote_name])
    
            if add_readme:
                cmd_args.append('--add-readme')
    
            if hasattr(opts, 'verbose') and opts.verbose:
                if proj_name:
                    self.stderr('WARNING: option "proj_name" is not supported by gh: ignored')
    
                if share:
                    self.stderr('WARNING: option "share" is not supported by gh: ignored')
                
            if add_license:
                if add_license in self.gh_licences:
                    cmd_args.extend(['--license', add_license])
                else:
                    self.stderr.write(f'{self.__class__.__name__}.setup_repo(): Invalid license name : {add_license}\n')
    
            if add_gitignore:
                if add_gitignore in self.gh_gitignore:
                    cmd_args.extend(['--gitignore', add_gitignore])
                else:
                    self.stderr.write(f'{self.__class__.__name__}.setup_repo(): Invalid gitignore template name : {add_gitignore}\n')
    
            return cmd_args
    
    class GitLabIF(StreamExtd):
        DEFAULT = {'glab_cmd':  'glab'}
    
        def __init__(self, opts:argparse.Namespace=None, glab_cmd=None, **kwds):
            super().__init__(**{k: v for k in kwds.items()
                                if k in ('stdin', 'stderr', 'stdout')})
            self.glab_cmd = (opts.glab_cmd if (hasattr(opts, 'glab_cmd') and opts.glab_cmd) else
                             (glab_cmd if glab_cmd else
                              os.environ.get('GITLAB_CLI', self.__class__.DEFAULT['glab_cmd'])))
            self.glab_path = shutil.which(self.glab_cmd)
            self.glab_username   = None
            self.glab_user_id    = None
            self.glab_user_email = None
            self.glab_available  = False
            self.glab_repos      = None
            if self.glab_path:
                try:
                    glab_ret = subprocess.run([self.glab_path, 'api', 'user'],
                                            check=True, capture_output=True, text=True)
                    glab_userinfo = json.loads(glab_ret.stdout)
                    self.glab_username   = glab_userinfo['username']
                    self.glab_user_id    = glab_userinfo['id']
                    self.glab_user_email = f"{self.glab_user_id}-{self.glab_username}@users.noreply.gitlab.com"
                    self.glab_available  = True
                except Exception as e:
                    self.stderr.write(f'{self.__class__.__name__}.__init__() Error: {e}')
    
        def __bool__(self):
            return bool(self.glab_available)

        def get_repos(self):
            if self.glab_available:
                try:
                    result = subprocess.run([self.glab_path, 'api',
                                             #'projects?membership=true&pagination=keyset&per_page=100'
                                             'projects?membership=true&per_page=100'],
                                            check=True, capture_output=True, text=True)
                    repos = json.loads(result.stdout)
                    return { r['path']: (r['path_with_namespace'],
                                         r['web_url'],
                                         r['http_url_to_repo'],
                                         r['ssh_url_to_repo']) for r in repos }
                except Exception as e:
                    self.stderr.write(f'{self.__class__.__name__}.get_repos() Error: {e}')
    
            return {}
    
        def chk_repos(self, module, subdir=''):
            if not self.glab_available:
                return None
            if self.glab_repos is None:
                self.glab_repos = self.get_repos()
    
            mod_path = '_'.join([subdir.replace(os.sep, '_', module)]) if subdir else module
    
            return not (self.glab_repos.get(mod_path) is None)
    
        @property
        def userinfo(self):
            return (self.glab_username, self.glab_user_email)

        def guess_user(self, opts:argparse.Namespace=None, account=None):
            gitlab_account = ( opts.git_remote_account if (hasattr(opts, 'git_remote_account')
                                                           and opts.git_remote_account) else
                               (account if account else 
                                (self.glab_username if self.glab_username else
                                os.environ.get('GITLAB_USER',
                                               getpass.getuser()))))
            return gitlab_account
    
        def guess_repo_url_base(self, opts:argparse.Namespace=None,
                                protocol=None, account=None):
            gitlab_account = self.guess_user(opts=opts, account=account)
            gitlab_protocol = ( opts.git_protocol
                                if (hasattr(opts, 'git_protocol')
                                    and opts.git_protocol) else protocol )
    
            return ( '%s://gitlab.com/%s/' % (gitlab_protocol, gitlab_account)
                     if gitlab_protocol in ('http', 'https') else
                     ( '%s://git@gitlab.com/%s/' % (gitlab_protocol, gitlab_account)
                       if gitlab_protocol == 'ssh' else
                       'git@gitlab.com:%s/'     % (gitlab_account, )))
    
        def guess_repo_url(self, module, subdir='',
                           opts:argparse.Namespace=None,
                           protocol=None, account=None, rmtext='.git'):
            url_base = self.guess_repo_url_base(opts=opts, protocol=protocol, account=account)
            mod_path = '_'.join([subdir.replace(os.sep, '_', module)]) if subdir else module
            return url_base.removesuffix('/')+f'/{module}{rmtext}'
        
        def create_repo_cmdargs(self, module, subdir='',
                                opts:argparse.Namespace=None, description=None,
                                push=False, proj_name=None, share=None, permit=None,
                                team_name=None, remote_name=None, source=None,
                                add_readme=False, add_license=None, add_gitignore=None):
    
            if not self.glab_available:
                return None
            if self.chk_repos(module=module, subdir=subdir):
                self.stderr.write(f'{self.__class__.__name__}.setup_repo(): Repository already exists on Gitlab: {module}\n')
                return False
    
            mod_path = '_'.join([subdir.replace(os.sep, '_', module)]) if subdir else module
            cmd_args = [self.glab_path, 'repo',  'create', mod_path]
    
            if description:
                cmd_args.extend(['--description', description])
    
            if permit=='internal' and team_name:
                cmd_args.extend(['--internal', '--group', team_name])
            elif permit=='public':
                cmd_args.append('--public')
            elif permit=='private':
                cmd_args.append('--private')
    
            if proj_name:
                cmd_args.extend(['--name', proj_name])
    
            if remote_name:
                cmd_args.extend(['--remoteName', remote_name])
    
            if add_readme:
                cmd_args.extend(['--readme'])

            if hasattr(opts, 'verbose') and opts.verbose:
                if push:
                    self.stderr('WARNING: option "push" is not supported by glab: ignored')
    
                if source:
                    self.stderr('WARNING: option "source" is not supported by glab: ignored')
    
                if share:
                    self.stderr('WARNING: option "share" is not supported by glab: ignored')
                
                if add_license:
                    self.stderr('WARNING: option "add_license" is not supported by glab: ignored')
    
                if add_gitignore:
                    self.stderr('WARNING: option "add_gitignore" is not supported by glab: ignored')
                
            return cmd_args
    
    class GitSSHIF(StreamExtd):
        DEFAULT = {'ssh_cmd': 'ssh',
                   'git_cmd': 'git'}
    
        reg_top_pttrn   = re.compile(r'^\s*top=\s*')
        reg_share_pttrn = re.compile(f'^(?P<shareopt>false|true|umask|group|all|world|everybody|\d{3,4})$', re.A)
        
        def __init__(self, 
                     opts:argparse.Namespace=None,
                     remote_host=None,
                     ssh_account=None,
                     repository_dir=None,
                     ssh_cmd=None,
                     git_cmd=None,
                     remote_git_cmd=None,
                     ssh_port=None, ssh_opts=[], **kwds):
            super().__init__(**{k: v for k in kwds.items()
                                if k in ('stdin', 'stderr', 'stdout')})
    
            self.ssh_cmd = (opts.ssh_cmd if (hasattr(opts, 'ssh_cmd') and opts.ssh_cmd) else
                            (ssh_cmd if ssh_cmd else 
                             os.environ.get('SSH', self.__class__.DEFAULT['ssh_cmd'])))
            self.git_cmd = (opts.git_cmd if (hasattr(opts, 'git_cmd') and opts.git_cmd) else
                            (git_cmd if git_cmd else 
                             os.environ.get('GIT', self.__class__.DEFAULT['git_cmd'])))
            self.ssh_path = shutil.which(self.ssh_cmd)
            self.git_path = shutil.which(self.git_cmd)
            self.ssh_port = (opts.git_remote_port if (hasattr(opts, 'git_remote_port')
                                                      and opts.git_remote_port) else ssh_port)
            
            self.remote_git_cmd = (opts.git_remote_cmd if (hasattr(opts, 'git_remote_cmd')
                                                           and opts.git_remote_cmd) else
                                   (remote_git_cmd if remote_git_cmd else 
                                    os.environ.get('REMOTE_GIT', 
                                                os.environ.get('GIT', 
                                                               self.__class__.DEFAULT['git_cmd']))))
    
            self.remote_host     = (opts.git_remote_host if (hasattr(opts, 'git_remote_host')
                                                            and opts.git_remote_host) else
                                    (remote_host if remote_host else
                                     os.environ.get('GIT_REMOTE_HOST')))
            self.remote_dir      = (opts.git_remote_path if (hasattr(opts, 'git_remote_path')
                                                             and opts.git_remote_path) else
                                    (repository_dir if repository_dir else
                                     os.environ.get('GIT_REMOTE_DIR', 
                                                    os.path.join('~', 'git_repositories'))))
            self.ssh_account     = (opts.git_remote_account if (hasattr(opts, 'git_remote_account')
                                                             and opts.git_remote_account) else
                                    (ssh_account if ssh_account else 
                                     os.environ.get('GIT_REMOTE_USER', getpass.getuser())))
            self.gitrmt_available = ( isinstance(self.remote_host, str) and self.remote_host )
            self.gitrmt_repos_buf = None
            self.ssh_cmd_common   = [self.ssh_path]
            if self.ssh_port is not None:
                self.ssh_cmd_common.expand(['-P', self.ssh_port])
            if self.ssh_account != getpass.getuser():
                self.ssh_cmd_common.expand(['-l', self.ssh_account])
    
            ssh_cmmd_opts = ([( x.removeprefix('\\')
                                if x.startswith('\\-') else x )
                              for x in opts.git_remote_sshopts ]
                             if (hasattr(opts, 'git_remote_sshopts')
                                 and isinstance(opts.git_remote_sshopts, list)) else
                             (list(ssh_opts) if isinstance(ssh_opts, (list,tuple)) else []))
            
            self.ssh_cmd_common.extend(ssh_cmmd_opts)
            self.ssh_cmd_common.append(self.remote_host)
    
            self.remote_dir_expnd = self.expand_remote_path(self.remote_dir)
    
        def __bool__(self):
            return bool(self.gitrmt_available)

        def get_repos_buf(self, rmtext='.git'):
            if self.gitrmt_available:
                self.gitrmt_repos_buf = {}
                try:
                    ret = subprocess.run(self.ssh_cmd_common
                                         +['(', 'echo', 'top=', self.remote_dir, ';',
                                           'find', self.remote_dir, 
                                           '-follow', '\(',  '-name',  '.git',  '-o',  '-name',  'HEAD', '\)'
                                           ')'],
                                         check=True, capture_output=True, text=True)
                    if ret.returncode==0:
                        rmt_repos_dir = self.remote_dir
                        for line in ret.stdout.splitlines():
                            if line.startswith('top='):
                                rmt_repos_dir = self.__class__.reg_top_pttrn.sub('', line)
                                continue
                            pl = pathlib.Path(os.path.dirname(line))
                            if pl.name == '.git':
                                pl = pl.parent
                            rel_pl = pl.relative_to(rmt_repos_dir)
    
                            rpath  = str(rel_pl.name) # .removesuffix(rmtext)
                            subdir = str(rel_pl.parent) if len(rel_pl.parents)>1 else ''
                            repnm = rel_pl.name.removesuffix(rmtext)
                            
                            if self.gitrmt_repos_buf.get(repnm) is None:
                                self.gitrmt_repos_buf.update({repnm: {}})
    
                            self.gitrmt_repos_buf.get(repnm).update({subdir: (rpath, rmt_repos_dir)})
                except Exception as e:
                    self.stderr.write(f'{self.__class__.__name__}.get_repos_buf() Error: {e}')
    
            return self.gitrmt_repos_buf
    
        def get_repos(self):
            if not self.gitrmt_available:
                return None
    
            if self.gitrmt_repos_buf is None:
                self.get_repos_buf()
            return { os.path.join(s,k) : (k, #os.path.join(s, r[0].removesuffix('.git')),
                          f'ssh://{self.ssh_account}@{self.remote_host}/{r[1].removeprefix("/")}/'+os.path.join(s, r[0]),
                          f'ssh://{self.ssh_account}@{self.remote_host}/{r[1].removeprefix("/")}/'+os.path.join(s, r[0]),
                          f'{self.ssh_account}@{self.remote_host}:{self.remote_dir}/'+os.path.join(s, r[0]))
                     for k,v in self.gitrmt_repos_buf.items() for s,r in v.items() }
    
        def chk_repos(self, module, subdir=''):
            if not self.gitrmt_available:
                return None
            if self.gitrmt_repos_buf is None:
                self.get_repos_buf()
            return not (self.gitrmt_repos_buf.get(os.path.join(subdir, module)) is None)
    
        @property
        def userinfo(self):
            return (self.ssh_account, self.ssh_account+'@'+self.remote_host)

        def guess_user(self, opts:argparse.Namespace=None, account=None):
            return ( opts.git_remote_account if (hasattr(opts, 'git_remote_account')
                                                           and opts.git_remote_account) else
                     (account if account else self.ssh_account))
    
        def expand_remote_path(self, path):
            if not self.gitrmt_available:
                return path
            rmt_path = path
            try:
                ret = subprocess.run(self.ssh_cmd_common+['(', 'echo', 'top=', path, ')'],
                                     check=True, capture_output=True, text=True)
                if ret.returncode==0:
                    for line in ret.stdout.splitlines():
                        if line.startswith('top='):
                            return self.__class__.reg_top_pttrn.sub('', line)
                return rmt_path
            except Exception as e:
                self.stderr.write(f'{self.__class__.__name__}.expand_remote_path({path}) Error: {e}')
            return rmt_path
    
        def guess_repo_url_base(self, opts:argparse.Namespace=None,
                                protocol=None, account=None, port=None):
            if not self.gitrmt_available:
                return None
    
            gitrmt_account = self.guess_user(opts=opts, account=account)
            gitrmt_protocol = ( opts.git_protocol
                                if (hasattr(opts, 'git_protocol')
                                    and opts.git_protocol) else protocol )

            gitrmt_port = (opts.git_remote_port if (hasattr(opts, 'git_remote_port')
                                                    and opts.git_remote_port) else
                           (port if port else
                            self.ssh_port if gitrmt_protocol=='ssh' else None))
            
            return ( '%s://%s@%s%s/%s/' % (gitrmt_protocol, gitrmt_account,
                                           self.remote_host,
                                           ':'+self.ssh_port if self.ssh_port else '',
                                           self.remote_dir_expnd)
                     if gitrmt_protocol in ('http', 'https') else
                     ( '%s://%s@%s%s/%s/' % (gitrmt_protocol, gitrmt_account,
                                             self.remote_host,
                                             (':'+gitrmt_port) if gitrmt_port else '',
                                             self.remote_dir_expnd)
                       if gitrmt_protocol=='ssh' else
                       ('%s@%s:%s/' % (gitrmt_account, self.remote_host, self.remote_dir)
                        if not self.ssh_port else
                        '%s://%s@%s%s/%s/' % (gitrmt_protocol, gitrmt_account,
                                              self.remote_host,
                                              (':'+gitrmt_port) if gitrmt_port else '',
                                              self.remote_dir_expnd))))
        
        def guess_repo_url(self, module, subdir='',
                           opts:argparse.Namespace=None,
                           protocol=None, account=None, port=None, rmtext='.git'):
            if not self.gitrmt_available:
                return None

            url_base = self.guess_repo_url_base(opts=opts, protocol=protocol,
                                                account=account, port=port)
            return url_base.removesuffix('/')+f'/{os.path.join(subdir, module)}{rmtext}'
        
    
        def create_repo_cmdargs(self, module, subdir='',
                                opts:argparse.Namespace=None, description=None,
                                push=False, proj_name=None, share=None, permit=None,
                                team_name=None, remote_name=None, source=None,
                                add_readme=False, add_license=None, add_gitignore=None,
                                rmtext='.git'):
    
            if not self.gitrmt_available:
                return None
    
            if self.chk_repos(module=module, subdir=subdir):
                self.stderr.write(f'{self.__class__.__name__}.setup_repo(): '
                                 f'Repository already exists on {self.remote_host} '
                                 f': {os.path.join(subdir,module)}\n')
                return False

            if hasattr(opts, 'verbose') and opts.verbose:
                if description:
                    self.stderr.write("Warning: 'description' is not supported")
                if push:
                    self.stderr.write("Warning: 'push' is not supported")
                if proj_name:
                    self.stderr.write("Warning: 'proj_name' is not supported")
                if permit:
                    self.stderr.write("Warning: 'permit' is not supported")
                if team_name:
                    self.stderr.write("Warning: 'team_name' is not supported")
                if remote_name:
                    self.stderr.write("Warning: 'remote_name' is not supported")
                if source:
                    self.stderr.write("Warning: 'source' is not supported")
                if add_readme:
                    self.stderr.write("Warning: 'add_readme' is not supported")
                if add_license:
                    self.stderr.write("Warning: 'add_license' is not supported")
                if add_gitignore:
                    self.stderr.write("Warning: 'add_gitignore' is not supported")
            
            cmd_args = []
            cmd_args.extend(self.ssh_cmd_common)
            rmt_repo_path = os.path.join(self.remote_dir, subdir, module.removesuffix(rmtext)+rmtext)
    
            cmd_args.extend(['(', 'test', '-d', rmt_repo_path, '||'])
            cmd_args.extend([self.remote_git_cmd, 'init', '--bare'])
            
            if isinstance(share,str):
                m = self.__class__.reg_share_pttrn.match(share)
                if m:
                    cmd_args.append(f'--share={m.group("shareopt")}')
                elif share:
                    cmd_args.append('--share')
            elif share:
                cmd_args.append('--share')
            cmd_args.extend([rmt_repo_path, ')'])
    
            return cmd_args
    
    class GitIF(ExtCmdIF):
    
        PTTRN_OPTARG = re.compile(r'^-*(?P<long>(?P<short>[^-\s]{1})(?P<rest>[^\s]*))')
    
        DEFAULT = {
            'git_remote_host' : None,
            'git_local_path'  : '~/git_repositories', #None,
            'git_remote_path' : '~/git_repositories', #None,
            'git_cmd'         : 'git',
            'git_remote_name' : 'origin',
        }
        
        def __init__(self,
#                     repo_name,
                     opts:argparse.Namespace=None,
                     local_path=None,
                     url=None,
                     hosting=None,
                     host=None, port=None, remote_path=None,
                     protocol=None, remote_account=None,
                     user_name=None, user_email=None,
                     subdir=None, gh_cmd=None, glab_cmd=None, ssh_cmd=None,
                     git_cmd=None, remote_git_cmd=None,
                     verbose=False, dry_run=False, encoding='utf-8', **kwds):
            
            super().__init__(**{k: v for k in kwds.items()
                                if k in ('verbose', 'dry_run', 'encoding',
                                         'stdin', 'stderr', 'stdout')})
    
            self.git_path = shutil.which(opts.git_cmd if (hasattr(opts, 'git_cmd')
                                                          and opts.git_cmd) else
                                         (git_cmd if git_cmd else
                                          self.__class__.DEFAULT.get('git_cmd', 'git')))
            
            urlprsd = urllib.parse.urlparse((opts.git_remote_url
                                             if (hasattr(opts, 'git_remote_url')
                                                 and opts.git_remote_url) else
                                             (url if url else '')), scheme='ssh')
            
            self.remote_host = ( opts.git_remote_host if (hasattr(opts, 'git_remote_host')
                                                 and opts.git_remote_host) else
                                 (urlprsd.hostname if urlprsd.hostname else
                                  ( host if host else
                                    os.environ.get('GIT_REMOTE_HOST',
                                                   self.__class__.DEFAULT.get('git_remote_host')))))
    
            self.remote_account = (opts.git_remote_account
                                   if (hasattr(opts, 'git_remote_account')
                                       and opts.git_remote_account) else
                                   (urlprsd.username if urlprsd.username else
                                    (remote_account if remote_account else
                                     os.environ.get('GIT_REMOTE_USER',
                                                    getpass.getuser()))))

            self.remote_port = (opts.git_remote_port if (hasattr(opts, 'git_remote_port')
                                                and opts.git_remote_port) else
                       (urlprsd.port if urlprsd.port else
                        (port if port else
                         os.environ.get('GIT_REMOTE_PORT', None))))
    
            self.local_path = (opts.git_local_path if (hasattr(opts, 'git_local_path')
                                                       and opts.git_local_path) else
                               (urlprsd.path.removeprefix('/') if urlprsd.path.startswith('/~') else
                                (urlprsd.path if urlprsd.path else
                                 ( local_path if local_path else
                                   os.environ.get('GIT_LOCAL_PATH',
                                                  self.__class__.DEFAULT['git_local_path'])))))
            
            self.remote_path = (opts.git_remote_path if (hasattr(opts, 'git_remote_path')
                                                             and opts.git_remote_path) else
                       (urlprsd.path.removeprefix('/') if urlprsd.path.startswith('/~') else
                        (urlprsd.path if urlprsd.path else
                         ( remote_path if remote_path else
                           os.environ.get('GIT_REMOTE_PATH',
                                          self.__class__.DEFAULT['git_remote_path'])))))
    
            # if not repo_name:
            #     self.stderr.write(f'Remote repository name is not specified: {str(repo_name)}')
            #     # status += 1
            #     # return status 
            #     raise ValueError(f'{self.__class__.__name__}.__init__() Error: Remote repository name is not specified')
    
            self.gitrmt_if = None
            __outer__ = globals().get(self.__class__.__qualname__.split('.')[0])


            _hosting = ( opts.git_hosting if (hasattr(opts, 'git_hosting') and
                                              opts.git_hosting is not None ) else hosting )
            
            if isinstance(_hosting, str) and _hosting.lower()=='github':
                self.gitrmt_if = __outer__.GitHubIF(opts=opts, gh_cmd=gh_cmd)
                if not self.gitrmt_if.gh_available:
                    self.gitrmt_if = None
                ####################
                # To be implimented
                ####################
            elif isinstance(_hosting, str) and _hosting.lower()=='gitlab':
                self.gitrmt_if = __outer__.GitLabIF(opts=opts, glab_cmd=glab_cmd)
                if not self.gitrmt_if.glab_available:
                    self.gitrmt_if = None
                ####################
                # To be implimented
                ####################
            elif (not urlprsd.scheme) or (urlprsd.scheme == 'ssh'):
                self.gitrmt_if = __outer__.GitSSHIF(opts=opts,
                                                    remote_host=host,
                                                    ssh_account=self.remote_account,
                                                    repository_dir=self.remote_path,
                                                    ssh_cmd=ssh_cmd,
                                                    git_cmd=git_cmd,
                                                    remote_git_cmd=remote_git_cmd,
                                                    ssh_port=self.remote_port)
                
            if self.gitrmt_if is not None:
                self.rmt_url_base = self.gitrmt_if.guess_repo_url_base(opts=opts,
                                                                       protocol=protocol,
                                                                       account=self.remote_account)
            else:
                schm  = (urlprsd.scheme
                         if urlprsd.scheme in ('https', 'http', 'ssh') else 'ssh')
    
                rmthst, rmtaccnt, rmtpth = (('github.com', 'git', self.remote_account)
                                            if isinstance(_hosting, str) and _hosting.lower()=='github'
                                            else (('gitlab.com', 'git', self.remote_account)
                                                  if isinstance(_hosting, str) and _hosting.lower()=='gitlab'
                                                  else (self.remote_host, self.remote_account, self.remote_path)))
    
                portsuffix = '' if self.remote_port is None else ':'+str(self.remote_port)
                self.rmt_url_base = f'{schm}://{rmtaccnt+"@" if rmtaccnt else ""}{portsuffix}/{rmtpth.removeprefix("/")}'


        @property
        def userinfo(self):
            return (self.gitrmt_if.userinfo 
                    if self.gitrmt_if else 
                    (self.remote_account, 
                     self.remote_account+'@'+(self.remote_host
                                              if self.remote_host
                                              else socket.gethostname())))
    
        @classmethod
        def add_argument(cls, arg_parser:argparse.ArgumentParser,
                         opt_s:str=None, opt_l:str=None, **opt_args):
            optarg_defined = arg_parser._option_string_actions.keys()
            argstr = []
            
            if opt_s:
                m = cls.PTTRN_OPTARG.match(opt_s)
                if m and m.group('short'):
                    s_opt = '-'+m.group('short')
                    if not s_opt in optarg_defined:
                        argstr.append(s_opt)
    
            if opt_l:
                m = cls.PTTRN_OPTARG.match(opt_l)
                if m and m.group('long'):
                    l_opt = '--'+m.group('long')
                    if not l_opt in optarg_defined:
                        argstr.append(l_opt)
    
            if len(argstr)<1:
                # raise ValueError(r"There is no un-used valid option arguments {str(opt_s)},{str(opt_l)}")
                StreamExtd().stderr.write(r"Warning: There is no un-used valid option arguments {str(opt_s)},{str(opt_l)}")
                return None
            return arg_parser.add_argument(*argstr, **opt_args)


        class UseGitHostingUserInfoAction(argparse.Action):

            def __call__(self, parser, namespace, values, option_string=None):

                __outer__ = globals().get(self.__class__.__qualname__.split('.')[0])

                
                if option_string == '--github-userinfo':
                    gitxxb_if = __outer__.GitHubIF(opts=namespace)
                    if not gitxxb_if:
                        __outer__.StreamExtd().write(f'GitHub CLI("gh") is unavailable (skipped) : {option_string}')
                        return
                        
                elif option_string == '--gitlab-userinfo':
                    gitxxb_if = __outer__.GitLabIF(opts=namespace)
                    if not gitxxb_if:
                        __outer__.StreamExtd().stderr.write(f'GitLab CLI("glab") is unavailable (skipped) : {option_string}')
                        return
                else:
                    __outer__.StreamExtd().write(f'Internal Error: unsupported option (skipped) : {option_string}')
                    return

                for dest,val in zip(('git_user_name', 'git_user_email'), gitxxb_if.userinfo):
                    if not val:
                        continue
                    setattr(namespace, dest, val)

                return
        
        @classmethod
        def add_remoteif_arguments(cls, arg_parser:argparse.ArgumentParser):
            # Flags
            cls.add_argument(arg_parser, opt_s='-y', opt_l='--git-set-upstream', action='store_true', default=None, help='git set upstream')
            cls.add_argument(arg_parser, opt_s='-R', opt_l='--git-remote-setup', action='store_true', default=None, help='Setup git remote bare repository')
            # Options
            cls.add_argument(arg_parser, opt_s='-u', opt_l='--git-user-name',  help='Specify git user name')
            cls.add_argument(arg_parser, opt_s='-e', opt_l='--git-user-email', help='Specify git user email')
            #
            cls.add_argument(arg_parser, opt_s=None, opt_l='--github-userinfo',
                             action=cls.UseGitHostingUserInfoAction, nargs=0,
                             help='Guess git user name/email by github CLI("gh")')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--gitlab-userinfo',
                             action=cls.UseGitHostingUserInfoAction, nargs=0,
                             help='Guess git user name/email by gitlab CLI("glab")')
            #
            cls.add_argument(arg_parser, opt_s='-T', opt_l='--git-repository-name', help='Git remote repository name')
            cls.add_argument(arg_parser, opt_s='-H', opt_l='--git-hosting',  choices=('github', 'gitlab'), default=None, help='git hosting service')
            cls.add_argument(arg_parser, opt_s='-z', opt_l='--git-protocol', choices=('http', 'https', 'ssh'), default=None, help='git protocol')
            cls.add_argument(arg_parser, opt_s='-U', opt_l='--git-remote-url', help='git remote URL')
            cls.add_argument(arg_parser, opt_s='-l', opt_l='--git-remote-account', help='github/gitlab/remote_host account-name')
            # cls.add_argument(arg_parser, opt_s='-W', opt_l='--git-remote-password', help='github/gitlab/remote_host account password')
            cls.add_argument(arg_parser, opt_s='-L', opt_l='--git-remote-host', help='git remote host')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--git-remote-port', help='port id for git remote access')
            cls.add_argument(arg_parser, opt_s='-w', opt_l='--git-remote-path', help='git remote repository path')
            cls.add_argument(arg_parser, opt_s='-X', opt_l='--git-remote-sshopts', action='append', default=[], help='ssh options to connect git-remote (Escape first - by "\\")')
            cls.add_argument(arg_parser, opt_s='-Z', opt_l='--git-remote-cmd',     help='git command @ git remote host')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--git-remote-share', default=None, help='Argument of git init --share option for remote host')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--git-remote-name', default=None, help=f'Git remote name (default:{cls.DEFAULT["git_remote_name"]})')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--ssh-command', help='ssh command')
            #cls.add_argument(arg_parser, opt_s='-g', opt_l='--git-command', help='git command')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--gh-command', help='gh command')
            cls.add_argument(arg_parser, opt_s=None, opt_l='--glab-command', help='glab command')
    
            return

        @classmethod
        def add_invokeoptions_arguments(cls, arg_parser:argparse.ArgumentParser):
            # Flags
            cls.add_argument(arg_parser, opt_s='-v', opt_l='--verbose', default=None, action='store_true', help='Show verbose infomation')
            cls.add_argument(arg_parser, opt_s='-n', opt_l='--dry-run', default=None, action='store_true', help='Dry-run mode')
            return

            
        def remote_repo_url_base(self):
            return self.rmt_url_base
        
        def remote_repo_url(self, module, subdir='',
                            opts:argparse.Namespace=None,
                            protocol=None, account=None, rmtext='.git'):
            if self.gitrmt_if is not None:
                return self.gitrmt_if.guess_repo_url(module=module, subdir=subdir, opts=opts,
                                                     protocol=protocol, account=account, rmtext=rmtext)
    
            return self.rmt_url_base.removesuffix('/')+f'/{os.path.join(subdir, module)}{rmtext}'


        def guess_module_name(self, opts:argparse.Namespace=None, module=None):
            return ( opts.git_repository_name
                     if (hasattr(opts, 'git_repository_name')
                         and opts.git_repository_name) else
                     ( module if module else
                       os.path.basename(self.local_path.removesuffix('/'))))
        
        def git_config_value_cmdargs(self, module=None, subdir='',
                                     key='user.email', mode='--global',
                                     local_workdir=None, local_git_dir=None,
                                     opts:argparse.Namespace=None, git_cmd_args=[]):

            o_module = self.guess_module_name(opts=opts, module=module)

            workdir = ( local_workdir if local_workdir else 
                        os.path.join(self.local_path, subdir, o_module))
            
            dot_git_dir = (local_git_dir if local_git_dir else
                           os.path.join(workdir, '.git'))
                        
            cmdarg = [ self.git_path ]

            if dot_git_dir:
                # '--git-dir',  dot_git_dir, '--work-tree', local_workdir, 
                cmdarg.extend(['--file', os.path.join(dot_git_dir, 'config')])
            
            cmdarg.extend(['config', mode, '--get', key])
                
            git_cmd_args.append(cmdarg)

            return git_cmd_args

        def get_git_config_value(self, module=None, subdir='',
                                 key='user.email', mode='--global',
                                 local_workdir=None, local_git_dir=None,
                                 opts:argparse.Namespace=None):
            try:
                cmdargs = self.git_config_value_cmdargs(module=module, subdir=subdir,
                                                        key=key, mode=mode,
                                                        local_workdir=local_workdir,
                                                        local_git_dir=local_git_dir,
                                                        opts=opts, git_cmd_args=[])
                ret = subprocess.run(cmdargs[0], check=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True)
                value = ret.stdout.strip()
            except subprocess.CalledProcessError:
                return None

        def chk_git_config_value(self, module='', subdir='',
                                 key='user.email', mode='--global',
                                 local_workdir=None, local_git_dir=None,
                                 opts:argparse.Namespace=None):
            return bool(self.get_git_config_value(module=module, subdir=subdir,
                                                  key=key, mode=mode,
                                                  local_workdir=local_workdir,
                                                  local_git_dir=local_git_dir, opts=opts))

        def init_local_cmdargs(self, module=None, subdir='',
                               local_workdir=None,
                               opts:argparse.Namespace=None,
                               share=None, git_cmd_args=[]):

            o_module = self.guess_module_name(opts=opts, module=module)

            workdir = ( local_workdir if local_workdir else 
                        os.path.join(self.local_path, subdir, o_module))
            
            if os.path.exists(os.path.join(workdir, '.git')):
                self.stderr.write(f'Warning: Repository already exists (skillped): {workdir}\n')
                return git_cmd_args

            cmd_args = [self.git_path, 'init']
            if isinstance(share,str):
                m = self.__class__.reg_share_pttrn.match(share)
                if m:
                    cmd_args.append(f'--share={m.group("shareopt")}')
                elif share:
                    cmd_args.append('--share')
            elif share:
                cmd_args.append('--share')
            cmd_args.extend([workdir])
            git_cmd_args.append(cmd_args)

            return git_cmd_args


        def config_minimum_cmdargs(self, module=None, subdir='',
                                   local_workdir=None,
                                   opts:argparse.Namespace=None,
                                   user_name=None, user_email=None,
                                   dot_git_dir=None, git_cmd_args=[]):

            o_module = self.guess_module_name(opts=opts, module=module)
            
            workdir = ( local_workdir if local_workdir else 
                        os.path.join(self.local_path, subdir, o_module))
            
            dtgit_dir = (dot_git_dir if dot_git_dir else
                         os.path.join(workdir, '.git'))

            config_path = os.path.join(dtgit_dir, 'config')        

            git_user_name = ( opts.git_user_name
                              if (hasattr(opts, 'git_user_name')
                                  and opts.git_user_name) else user_name )

            git_user_email = ( opts.git_user_email
                               if (hasattr(opts, 'git_user_email')
                                   and opts.git_user_email) else user_email )
            
            if isinstance(git_user_name, str) and git_user_name:
                git_cmd_args.append([self.git_path,
                                     'config', '--file', config_path,
                                     'user.name', git_user_name])

            elif not self.chk_git_config_value(module=module, subdir=subdir,
                                               key='user.name', mode='--global',
                                               local_workdir=workdir,
                                               local_git_dir=dtgit_dir, opts=opts):
                git_cmd_args.append([self.git_path,
                                     'config', '--file', config_path,
                                     'user.name', getpass.getuser()])

                
            if isinstance(git_user_email, str) and git_user_email:
                git_cmd_args.append([self.git_path,
                                     'config', '--file', config_path,
                                     'user.email', git_user_email])

            elif not self.chk_git_config_value(key='user.email', mode='--global',
                                               local_workdir=workdir,
                                               local_git_dir=dtgit_dir, opts=opts):
                git_cmd_args.append([self.git_path,
                                     'config', '--file', config_path,
                                     'user.email', getpass.getuser()+'@'+socket.gethostname()])
                
            return git_cmd_args


        def create_remote_repo_cmdargs(self, module=None, subdir='',
                                       opts:argparse.Namespace=None, description=None,
                                       push=False, proj_name=None,
                                       share=None, permit=None, team_name=None,
                                       remote_name=None, source=None,
                                       add_readme=False, add_license=None,
                                       add_gitignore=None, git_cmd_args=[]):

            o_module = self.guess_module_name(opts=opts, module=module)
            
            if self.gitrmt_if is None:
                self.stderr.write('GitHubIF/GitLabIF/GitSSHIF object is unavailable: (skip) Please create manually.')
            else:
                cmdarg = self.gitrmt_if.create_repo_cmdargs(module=o_module,
                                                            subdir=subdir,
                                                            opts=opts,
                                                            description=description,
                                                            push=push,
                                                            proj_name=proj_name,
                                                            share=share, permit=permit,
                                                            team_name=team_name,
                                                            remote_name=remote_name,
                                                            source=source,
                                                            add_readme=add_readme,
                                                            add_license=add_license,
                                                            add_gitignore=add_gitignore)
                if isinstance(cmdarg, (list, tuple)):
                    git_cmd_args.append(list(cmdarg))
            return git_cmd_args
        
        def set_upstream_cmdargs(self, module=None, subdir='',
                                 local_workdir=None,
                                 opts:argparse.Namespace=None,
                                 remote_url=None, local_git_dir=None, remote_name=None,                                
                                 protocol=None, account=None, rmtext='.git', git_cmd_args=[]):

            o_module = self.guess_module_name(opts=opts, module=module)

            workdir = ( local_workdir if local_workdir else 
                        os.path.join(self.local_path, subdir, o_module))
            
            remote_url = (opts.git_remote_url if (hasattr(opts, 'git_remote_url')
                                                  and opts.git_remote_url) else
                          (remote_url if remote_url else 
                           self.remote_repo_url(opts=opts, module=o_module, subdir=subdir,
                                                protocol=protocol, account=account, rmtext=rmtext)))
            
            rmt_name = (opts.git_remote_name if (hasattr(opts, 'git_remote_name')
                                                  and opts.git_remote_name) else
                        ( remote_name if remote_name else
                          self.__class__.DEFAULT['git_remote_name'] ))
    
            dot_git_dir = (local_git_dir if local_git_dir
                           else os.path.join(workdir, '.git'))

            if remote_url:

                git_cmd_args.append([self.git_path, 
                                     '--git-dir',  dot_git_dir, '--work-tree', workdir,
                                     'remote', 'add', rmt_name, remote_url] )
    
                git_cmd_args.append([self.git_path, 
                                     '--git-dir',  dot_git_dir, '--work-tree', workdir,
                                     'commit', '--allow-empty', '-m', 'Initialize Repository'] )
    

                git_cmd_args.append([self.git_path, 
                                     '--git-dir',  dot_git_dir, '--work-tree', workdir,
                                     'push', '-u', f'{rmt_name}', 'main'] )

                # git_cmd_args.append([self.git_path, 
                #                      '--git-dir',  dot_git_dir, '--work-tree', local_workdir,
                #                      'branch', f'--set-upstream-to={rmt_name}/main', 'main'])
    
            # git_cmd_args.append([self.git_path, 
            #                      # '--git-dir',  dot_git_dir, '--work-tree', local_workdir, 
            #                      '--file', os.path.join(dot_git_dir, 'config'),
            #                      '--local', 'push.default', 'current'])

            return git_cmd_args

        def setup_cmdargs(self, module=None, subdir='',
                          remote_setup=False,
                          set_upstream=False,
                          local_workdir=None,
                          opts:argparse.Namespace=None,
                          share=None, user_name=None, user_email=None,
                          dot_git_dir=None,
                          description=None,
                          push=False, proj_name=None,
                          permit=None, team_name=None,
                          remote_name=None, source=None,
                          add_readme=False, add_license=None,
                          add_gitignore=None,
                          remote_url=None,
                          local_git_dir=None,
                          protocol=None, account=None, rmtext='.git',
                          git_cmd_args=[]):

            buf = self.init_local_cmdargs(module=module,
                                          subdir=subdir,
                                          local_workdir=local_workdir,
                                          opts=opts, share=share,
                                          git_cmd_args=git_cmd_args)

            buf = self.config_minimum_cmdargs(module=module,
                                              subdir=subdir,
                                              local_workdir=local_workdir,
                                              opts=opts,
                                              user_name=user_name,
                                              user_email=user_email,
                                              dot_git_dir=dot_git_dir,
                                              git_cmd_args=git_cmd_args)

            f_remote_setup = (opts.git_remote_setup
                              if (hasattr(opts, 'git_remote_setup')
                                  and opts.git_remote_setup is not None) else remote_setup)

            f_set_upstream = (opts.git_set_upstream
                              if (hasattr(opts, 'git_set_upstream')
                                  and opts.git_set_upstream is not None) else set_upstream)
            if f_remote_setup:
                buf = self.create_remote_repo_cmdargs(module=module, subdir=subdir,
                                                      opts=opts, description=description,
                                                      push=push, proj_name=proj_name,
                                                      share=share, permit=permit,
                                                      team_name=team_name,
                                                      remote_name=remote_name, source=source,
                                                      add_readme=add_readme, add_license=add_license,
                                                      add_gitignore=add_gitignore,
                                                      git_cmd_args=git_cmd_args)

            if f_set_upstream:
                buf = self.set_upstream_cmdargs(module=module, subdir=subdir,
                                                local_workdir=local_workdir,
                                                opts=opts, remote_url=remote_url,
                                                local_git_dir=local_git_dir,
                                                remote_name=remote_name,
                                                protocol=protocol, account=account,
                                                rmtext=rmtext, git_cmd_args=git_cmd_args)
            
            return buf
        

        def setup(self, module=None, subdir='',
                  remote_setup=False,
                  set_upstream=False,
                  local_workdir=None,
                  opts:argparse.Namespace=None,
                  share=None, user_name=None, user_email=None,
                  dot_git_dir=None,
                  description=None,
                  push=False, proj_name=None,
                  permit=None, team_name=None,
                  remote_name=None, source=None,
                  add_readme=False, add_license=None,
                  add_gitignore=None,
                  remote_url=None,
                  local_git_dir=None,
                  protocol=None, account=None, rmtext='.git',
                  verbose:bool=None, dry_run:bool=None,
                  check:bool=True, text:bool=True, hook=None,
                  more_upper:bool=False, encoding=None, **args):

            cmdargs = self.setup_cmdargs(module=module,
                                         subdir=subdir,
                                         remote_setup=remote_setup,
                                         set_upstream=set_upstream,
                                         local_workdir=local_workdir,
                                         opts=opts, share=share,
                                         user_name=user_name, user_email=user_email,
                                         dot_git_dir=dot_git_dir,
                                         description=description,
                                         push=push, proj_name=proj_name,
                                         permit=permit, team_name=team_name,
                                         remote_name=remote_name, source=source,
                                         add_readme=add_readme, add_license=add_license,
                                         add_gitignore=add_gitignore,
                                         remote_url=remote_url,
                                         local_git_dir=local_git_dir,
                                         protocol=protocol, account=account, rmtext=rmtext,
                                         git_cmd_args=[])

            f_verbose = (opts.verbose if (hasattr(opts, 'verbose')
                                          and opts.verbose is not None) else verbose)

            f_dry_run = (opts.dry_run if (hasattr(opts, 'dry_run')
                                          and opts.dry_run is not None) else
                         (opts.dryrun if (hasattr(opts, 'dryrun')
                                          and opts.dryrun is not None) else dry_run))

            self.invoke(cmdargs=cmdargs, verbose=f_verbose, dry_run=f_dry_run,
                        check=check, text=text, hook=hook,
                        more_upper=more_upper, encoding=encoding, **args)

    
    def manage_env(self, args:argparse.Namespace, rest:list=[]):

        subcmd      = args.subcommand if hasattr(args, 'subcommand') else 'unknown'

        self.set_python_path(python_cmd=(args.python if (hasattr(args, 'python') and
                                                         args.python is not None) else self.python_select),
                             pip_cmd=(args.pip if (hasattr(args, 'pip') and
                                                   args.pip is not None) else str(self.pip_use)),
                             prefix_cmd=( args.prefix if (hasattr(args, 'prefix') and
                                                          args.prefix  is not None) else self.prefix))

        if hasattr(args, 'git_command') and (args.git_command is not None):
            self.set_git_path(git_cmd=args.git_command)

        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False

        flg_move   = args.move   if hasattr(args, 'move')   else False
        flg_git    = args.git    if hasattr(args, 'git')    else False
        flg_readme = args.readme if hasattr(args, 'readme') else False
        title      = args.title  if hasattr(args, 'title')  else str(pathlib.Path(self.prefix).name)
        
        modules   = args.module      if hasattr(args, 'module')     else []
        scrptlibs = args.script_lib  if hasattr(args, 'script_lib') else []
        scripts   = args.scriptnames if hasattr(args, 'scriptnames') else []

        if hasattr(args, 'std_script_lib') and args.std_script_lib:
            for _scrlib in self.__class__.SCRIPT_STD_LIB.keys():
                if _scrlib in scrptlibs or (_scrlib+'.py') in scrptlibs:
                    continue
                scrptlibs.append(_scrlib)

        for _scrlib in scrptlibs:
            _scrlib_info = self.__class__.SCRIPT_STD_LIB.get(_scrlib)
            if _scrlib_info is None:
                continue
            for _dep in _scrlib_info.get('depends', []):
                if _dep in scrptlibs:
                    continue
                scrptlibs.append(_dep)

        for _scrlib in scrptlibs:
            _scrlib_info = self.__class__.SCRIPT_STD_LIB.get(_scrlib)
            if _scrlib_info is None:
                continue
            for _m in _scrlib_info.get('pip_module', []):
                if _m in modules:
                    continue
                modules.append(_m)

        keyword_buf = {}
        keyword_buf.update(self.__class__.FILENAME_DEFAULT)
        keyword_buf.update({
            '____TITLE____':              title,
            '____MNGSCRIPT_NAME____':     self.__class__.MNG_SCRIPT,
            '____AUTHOR_NAME____':        self.__class__.guess_git_username(),
            '____AUTHOR_EMAIL____':       self.__class__.guess_git_useremail(),
            '____py_shebang_pattern____': self.python_shebang,
        })

        if subcmd == 'init':

            self.make_directory_structure(dry_run=flg_dry_run, verbose=flg_verbose)

            self.put_this_into_structure(flg_move=flg_move, dry_run=flg_dry_run, verbose=flg_verbose)

            self.mksymlink_this_in_structure(self.__class__.MNG_SCRIPT, strip_py=True,
                                             dry_run=flg_dry_run, verbose=flg_verbose)

            if flg_git:

                self.make_gitignore_contents(os.path.join(self.prefix, '.gitignore'),
                                             encoding=self.encoding, dry_run=flg_dry_run, verbose=flg_verbose)
            
                self.put_gitkeep(dry_run=flg_dry_run, verbose=flg_verbose)
                # self.setup_git(git_user=git_user, git_email=git_email, git_url=git_url,
                #                verbose=flg_verbose, dry_run=flg_dry_run, remote_name=git_origin)

                gitif = self.__class__.GitIF(opts=args,
                                             local_path=self.prefix,
                                             verbose=flg_verbose, dry_run=flg_dry_run,
                                             encoding=self.encoding)
                ret = gitif.setup(module=None, subdir='',
                                  local_workdir=self.prefix,
                                  verbose=flg_verbose, dry_run=flg_dry_run, opts=args)

        if flg_readme:

            readme_path = self.update_readme(keywords=keyword_buf,
                                             bin_basenames=[x.removesuffix('.py') for x in scripts],
                                             lib_basenames=[x.removesuffix('.py') for x in scrptlibs],
                                             flg_git=flg_git, backup=False,
                                             verbose=flg_verbose, dry_run=flg_dry_run)

        self.add_pyscr(basename=[x.removesuffix('.py') for x in scripts],
                       keywords=keyword_buf, verbose=flg_verbose, dry_run=flg_dry_run)
                
        self.add_pylib(basename=[x.removesuffix('.py') for x in scrptlibs],
                       keywords=keyword_buf, verbose=flg_verbose, dry_run=flg_dry_run)

        if len(modules)>0:
            self.run_pip(subcmd='install', args=modules, verbose=flg_verbose, dry_run=flg_dry_run)

    def manage_readme(self, args:argparse.Namespace, rest:list=[]):
        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'

        bin_scr, lib_scr = self.list_categorized_pkg_scripts()

        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False
        flg_backup  = args.backup  if hasattr(args, 'backup')  else False

        flg_git = os.path.exists(os.path.join(self.prefix, '.gitignore'))

        title      = ( args.title if (hasattr(args, 'title') and args.title )
                       else str(pathlib.Path(self.prefix).name))

        keyword_buf = {}
        keyword_buf.update(self.__class__.FILENAME_DEFAULT)
        keyword_buf.update({
            '____TITLE____':              title,
            '____MNGSCRIPT_NAME____':     self.__class__.MNG_SCRIPT,
            '____AUTHOR_NAME____':        self.__class__.guess_git_username(),
            '____AUTHOR_EMAIL____':       self.__class__.guess_git_useremail(),
            '____py_shebang_pattern____': self.python_shebang,
        })

        readme_path = self.update_readme(keywords=keyword_buf,
                                         bin_basenames=[x.removesuffix('.py') for x in bin_scr],
                                         lib_basenames=[x.removesuffix('.py') for x in lib_scr],
                                         flg_git=flg_git, backup=flg_backup,
                                         verbose=flg_verbose, dry_run=flg_dry_run)
        
    def manage_git(self, args:argparse.Namespace, rest:list=[]):
        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'
        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False
        if hasattr(args, 'git_command') and (args.git_command is not None):
            self.set_git_path(git_cmd=args.git_command)

        flg_module_source = ( hasattr(args, 'module_src') and args.module_src )

        work_top = os.path.join(self.srcdir, args.module_src) if flg_module_source else self.prefix 

        if (not os.path.exists(work_top)) or (not os.path.isdir(work_top)):
            self.stderr.write("ERROR: Directory not found : ", work_top)
            return 

        if not flg_module_source:
            self.make_gitignore_contents(os.path.join(self.prefix, '.gitignore'),
                                         encoding=self.encoding, dry_run=flg_dry_run, verbose=flg_verbose)
                
            self.put_gitkeep(dry_run=flg_dry_run, verbose=flg_verbose)
            gitif = self.__class__.GitIF(opts=args,
                                         local_path=self.prefix,
                                         verbose=flg_verbose, dry_run=flg_dry_run,
                                         encoding=self.encoding)
            ret = gitif.setup(module=None, subdir='',
                              local_workdir=self.prefix,
                              verbose=flg_verbose, dry_run=flg_dry_run, opts=args)
            return

        module_name     = args.module_src
        module_dir      = os.path.join(self.srcdir, module_name)
        module_test_dir = os.path.join(module_dir, 'test')
        module_gitif = self.__class__.GitIF(opts=args,
                                            local_path=self.srcdir,
                                            verbose=flg_verbose, dry_run=flg_dry_run,
                                            encoding=self.encoding)

        self.put_gitkeep(dest_dirs=[module_test_dir], dry_run=flg_dry_run, verbose=flg_verbose)

        module_gitignore = os.path.join(module_dir, '.gitignore')
        str_format = {}
        str_format.update(self.__class__.FILENAME_DEFAULT)

        # text_filter = self.__class__.EmbeddedText.FormatFilter(format_variables=str_format)
        self.make_gitignore_contents(output_path=module_gitignore,
                                     git_keepdirs=[],
                                     template_s_marker=r'\s*#{5,}\s*____MODULE_DOT_GITIGNORE_TEMPLATE_START____\s*#{5,}',
                                     templete_e_marker=r'\s*#{5,}\s*____MODULE_DOT_GITIGNORE_TEMPLATE_END____\s*#{5,}',
                                     dry_run=flg_dry_run, verbose=flg_verbose, format_alist=str_format)

        ret = module_gitif.setup(module=module_name, subdir='',
                                 verbose=flg_verbose, dry_run=flg_dry_run, opts=args)
        return

    def setup_newmodule(self, args:argparse.Namespace, rest:list=[]):

        subcmd = args.subcommand if hasattr(args, 'subcommand') else 'unknown'

        self.set_python_path(python_cmd=(args.python if (hasattr(args, 'python') and
                                                         args.python is not None) else self.python_select),
                             pip_cmd=(args.pip if (hasattr(args, 'pip') and
                                                   args.pip is not None) else str(self.pip_use)),
                             prefix_cmd=( args.prefix if (hasattr(args, 'prefix') and
                                                          args.prefix  is not None) else self.prefix))


        module_src_top = self.srcdir

        if hasattr(args, 'git_command') and (args.git_command is not None):
            self.set_git_path(git_cmd=args.git_command)

        flg_verbose = args.verbose if hasattr(args, 'verbose') else self.verbose
        flg_dry_run = args.dry_run if hasattr(args, 'dry_run') else False

        flg_readme = args.readme if hasattr(args, 'readme') else True
        flg_git    = args.git    if hasattr(args, 'git')    else True

        flg_set_shebang = args.set_shebang if hasattr(args, 'set_shebang') else False

        newmodule_shebang = self.python_shebang if flg_set_shebang else self.__class__.SHEBANG_DEFAULT

        newmodule_gitif = self.__class__.GitIF(opts=args,
                                               local_path=self.srcdir,
                                               verbose=flg_verbose, dry_run=flg_dry_run,
                                               encoding=self.encoding)

        git_user, git_email = newmodule_gitif.userinfo

        module_website = args.module_website      if hasattr(args, 'module_website')   else []

        title       = args.title       if hasattr(args, 'title')       else ""
        description = args.title       if hasattr(args, 'description') else ""

        clsnames     = args.class_name  if hasattr(args, 'class_name')  else []
        req_modules  = args.module      if hasattr(args, 'module')      else []

        module_keywords  = args.keywords     if hasattr(args, 'keywords')     else []
        classifiers      = args.classifiers  if hasattr(args, 'classifiers')  else []
        author_name      = args.author_name  if hasattr(args, 'author_name')  else []
        author_email     = args.author_email if hasattr(args, 'author_email') else []
        maintainer_name  = args.maintainer_name  if hasattr(args, 'maintainer_name')  else []
        maintainer_email = args.maintainer_email if hasattr(args, 'maintainer_email') else []
        create_year      = args.create_year  if hasattr(args, 'create_year')  else [ datetime.date.today().year ]
        
        # if len(author_name)==0:
        #     author_name.append(git_user if isinstance(git_user,str) and git_user else self.__class__.guess_git_username())
        # if len(author_email)==0:
        #     author_email.append(git_email if isinstance(git_email,str) and git_email else self.__class__.guess_git_useremail())
            
        if len(author_name)==0:
            author_name.append(git_user)
        if len(author_email)==0:
            author_email.append(git_email)

        author_text_readme    = []
        author_text_pyproject = []
        for athr,eml in itertools.zip_longest(author_name, author_email):
            if athr is None or (not athr):
                break
            author_text_readme.append("  %s" % (athr, )
                                      if eml is None or (not eml) 
                                      else "  %s(%s)\n" % (athr, eml))
            author_text_pyproject.append("{name = %s, email= %s}\n" 
                                         % (repr(athr), repr(eml) if eml is not None else repr("")))

        maintainer_text_pyproject = []
        for athr,eml in itertools.zip_longest(maintainer_name, maintainer_email):
            if athr is None or (not athr):
                break
            maintainer_text_readme.append("  %s" % (athr, )
                                          if eml is None or (not eml) 
                                          else "  %s(%s)\n" % (athr, eml))
            maintainer_text_pyproject.append("{name = %s, email= %s}\n" 
                                             % (repr(athr), repr(eml) if eml is not None else repr("")))

        author_text_readme    = "\n".join(author_text_readme)
        author_text_pyproject = ", ".join(author_text_pyproject)
        author_text_pyproject.rstrip(os.linesep)

        maintainer_text_pyproject = []
        if len(maintainer_text_pyproject)>0:
            maintainer_text_pyproject = ", ".join(maintainer_text_pyproject)
        else:
            maintainer_text_pyproject = author_text_pyproject

        maintainer_text_pyproject.rstrip(os.linesep)

        if git_user is None or (not git_user):
            git_user  = author_name[0]
        if git_email is None or (not git_email):
            git_email = author_email[0]

        for nmidx,new_module_name in enumerate(args.module_name):
            bare_name = pathlib.Path(new_module_name).name.removesuffix('.py')
            module_name       = bare_name.replace('_','-')
            module_short_path = bare_name.replace('-','_')

            desc_text = "%s : %s" % (title if title else module_name, 
                                     description if description else '')

            git_url_nm = newmodule_gitif.remote_repo_url(module=module_name, subdir='', opts=args,
                                                         protocol=None, account=None, rmtext='.git')


            if len(args.module_name)==1 and len(module_website)>0:
                url = ",".join(module_website)
            else:
                # url = ( module_website[nmidx] if nmidx<len(module_website)
                #         else (git_url_nm if git_url_nm else 'https://gitxxx.com/%s/%s'
                #               % ( git_account if git_account
                #                   else "-".join([str(s).lower() 
                #                                  for s in author_name[0].split(" ")]), module_name)))
                url = ( module_website[nmidx] if nmidx<len(module_website)
                        else (git_url_nm if git_url_nm else 'https://gitxxx.com/%s/%s'
                              % ( git_user if git_user
                                  else "-".join([str(s).lower() 
                                                 for s in author_name[0].split(" ")]), module_name)))
                
            # clsnm = clsnames[nmidx] if nmidx<len(clsnames) else ("".join([ i.capitalize() for i in module_name.split("-")]))
            clsnm = clsnames[nmidx] if nmidx<len(clsnames) else (self.__class__.to_py_identifier_capitalized(module_name,
                                                                                                             use_underscore=False))

            str_format = {}
            str_format.update(self.__class__.FILENAME_DEFAULT)
            str_format.update({
                '____AUTHOR_EMAIL____' : ", ".join(author_email),
                '____AUTHOR_NAME____' : ", ".join(author_name),
                '____GIT_DUMMYFILE____' : self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'],
                '____MODULE_AUTHOR_LIST____' : author_text_pyproject,
                '____MODULE_AUTHOR_LIST_TEXT____' : author_text_readme,
                '____MODULE_CLASSIFIER_LIST____' : ",".join([str(c) for c in classifiers]),
                '____MODULE_CLS_NAME____' : clsnm,
                '____MODULE_CREATE_YEAR____' : ", ".join([str(y) for y in create_year]),
                '____MODULE_DESC____' : desc_text,
                '____MODULE_DESC_QUOTE____' : repr(desc_text),
                '____MODULE_HOMEPAGE_URL_QUOTE____' : repr(url),
                '____MODULE_KEYWORDS____' : ",".join([repr(c) for c in module_keywords]),
                '____MODULE_MAINTAINERS_LIST____' : maintainer_text_pyproject,
                '____MODULE_NAME____' : module_name,
                '____MODULE_REQUIREMENTS____' : ", ".join([repr(c) for c in req_modules]),
                '____MODULE_SHORT_PATH____' : module_short_path,
                '____py_shebang_pattern____' : newmodule_shebang,
                '____README_NAME____' : self.__class__.FILENAME_DEFAULT.get('____README_NAME____', 'README.md'),
                '____TITLE____':              title,
                '____PIP_MODULE_NAME____': self.__class__.ENTYTY_FILE_NAME,
            })

            new_module_top = os.path.join(module_src_top, module_name)
            new_module_test_dir = os.path.join(new_module_top, 'test')

            for dd in [new_module_top, new_module_test_dir,
                       os.path.join(new_module_top, 'src'),
                       os.path.join(new_module_top, 'src', module_short_path)]:
                if flg_verbose or flg_dry_run:
                    self.stderr.write("mkdir -p : '%s'" % (dd, ))
                if not flg_dry_run:
                    os.makedirs(dd, mode=0o755, exist_ok=True)

            text_filter = self.__class__.EmbeddedText.FormatFilter(format_variables=str_format)
            code_filter = self.__class__.PyCodeFilter(newmodule_shebang, keyword_table=str_format)

            if flg_git:
                self.put_gitkeep(dest_dirs=[new_module_test_dir, ], dry_run=flg_dry_run, verbose=flg_verbose)

                new_module_gitignore = os.path.join(new_module_top, '.gitignore')
                self.make_gitignore_contents(output_path=new_module_gitignore,
                                             git_keepdirs=[],
                                             template_s_marker=r'\s*#{5,}\s*____MODULE_DOT_GITIGNORE_TEMPLATE_START____\s*#{5,}',
                                             templete_e_marker=r'\s*#{5,}\s*____MODULE_DOT_GITIGNORE_TEMPLATE_END____\s*#{5,}',
                                             dry_run=flg_dry_run, verbose=flg_verbose, format_alist=str_format)

                ret = newmodule_gitif.setup(module=module_name, subdir='',
                                            verbose=flg_verbose, dry_run=flg_dry_run, opts=args)

            if flg_readme:
                new_module_readme = os.path.join(new_module_top, str_format.get('____README_NAME____', 'README.md'))
                self.extract_template_with_check(output_path=new_module_readme,
                                                 template_s_marker=r'\s*#{5,}\s*____MODULE_README_MD_TEMPLATE_START____\s*#{5,}',
                                                 template_e_marker=r'\s*#{5,}\s*____MODULE_README_MD_TEMPLATE_END____\s*#{5,}',
                                                 filter_obj=text_filter, dequote=True,
                                                 short_name='README', verbose=flg_verbose, dry_run=flg_dry_run)
                
            text_path_templates = [('LICENSE',        'BSD_3_CLAUSE_LICENSE'), 
                                   ('Makefile',       'MODULE_DIR_MAKEFILE'), 
                                   ('pyproject.toml', 'MODULE_PYPROJECT_TOML')]
            for fname, markerid in text_path_templates:
                lpath = os.path.join(new_module_top, fname)
                self.extract_template_with_check(output_path=lpath,
                                                 template_s_marker=r'\s*#{5,}\s*____'+markerid+'_TEMPLATE_START____\s*#{5,}',
                                                 template_e_marker=r'\s*#{5,}\s*____'+markerid+'_TEMPLATE_END____\s*#{5,}',
                                                 filter_obj=text_filter, dequote=True,
                                                 short_name=fname, verbose=flg_verbose, dry_run=flg_dry_run)

            code_path_template = [('__init__.py',           'MODULE_SRC_INIT_PY'),
                                  (module_short_path+'.py' ,'MODULE_SRC_MODULE_NAME_PY')]

            for fname, markerid in code_path_template:
                lpath = os.path.join(new_module_top, 'src', module_short_path, fname)
                self.extract_template_with_check(output_path=lpath,
                                                 template_s_marker=r'\s*#{5,}\s*____'+markerid+'_TEMPLATE_START____\s*#{5,}',
                                                 template_e_marker=r'\s*#{5,}\s*____'+markerid+'_TEMPLATE_END____\s*#{5,}',
                                                 filter_obj=code_filter, dequote=False,
                                                 short_name=fname, verbose=flg_verbose, dry_run=flg_dry_run)


    def extract_template_with_check(self, output_path,
                                    template_s_marker,
                                    template_e_marker,
                                    filter_obj, dequote,
                                    short_name=None, verbose=False, dry_run=False):
        fname = short_name if short_name else os.path.basename(output_path)
        if os.path.exists(output_path):
            if verbose:
                self.stderr.write("Warning: File already exists (Skipped) : '%s'" % (output_path, ))
            return

        if verbose or dry_run:
            self.stderr.write("Preparing %s from template : '%s'" % (fname, output_path))
                
        if not dry_run:
            self.__class__.EmbeddedText.extract_to_file(outfile=output_path, infile=None,
                                                        s_marker=template_s_marker,
                                                        e_marker=template_e_marker,
                                                        include_markers=False, multi_match=False, dedent=True, 
                                                        skip_head_emptyline=True, skip_tail_emptyline=True,
                                                        dequote=dequote, format_filter=filter_obj, 
                                                        open_mode='w', encoding=self.encoding)
            os.chmod(output_path, mode=0o644)

    def update_readme(self, keywords={}, bin_basenames=[], lib_basenames=[],
                      flg_git=False, backup=False, verbose=False, dry_run=False):

        readme_path = os.path.join(self.prefix,
                                   self.__class__.FILENAME_DEFAULT.get('____README_NAME____', 'README.md'))

        readme_updater = self.ReadMeUpdater(ref_pycan=self,
                                            keywords=keywords, 
                                            bin_basenames=bin_basenames, 
                                            lib_basenames=lib_basenames,
                                            flg_git=flg_git)
        if os.path.exists(readme_path):
            readme_bkup = self.__class__.rename_with_mtime_suffix(readme_path,
                                                                  dest_dir=self.tmpdir,
                                                                  verbose=verbose,
                                                                  dry_run=dry_run)
            if readme_bkup is None:
                if verbose or dry_run:
                    self.stderr.write("Save Readme file : '%s'" % (readme_path, ))
                if not dry_run:
                    readme_updater.save_readme_contents(output=readme_path, format_alist=keywords)
            else:
                buf = readme_updater.proc_file(in_file=readme_bkup, 
                                               out_file=readme_path, encoding=self.encoding,
                                               verbose=verbose, dry_run=dry_run)
        else:
            if verbose or dry_run:
                self.stderr.write("Save Readme file : '%s'" % (readme_path, ))
            if not dry_run:
                readme_updater.save_readme_contents(output=readme_path, format_alist=keywords)

    @classmethod
    def to_py_identifier_capitalized(cls, s:str, use_underscore:bool=True)->str:
        chanks   = cls.NON_ASCII_PATTERN.split(s)
        catchank = ('_' if use_underscore else '').join(word.capitalize() for word in chanks if word)
        if not catchank:
            catchank = "___"
        if catchank[0].isdigit():
            catchank = "___" + catchank
        if keyword.iskeyword(catchank):
            catchank += "___"
        return catchank
    
    @classmethod
    def to_py_identifier(cls, s:str, lowercase:bool=True) -> str:
        chanks = cls.NON_ASCII_PATTERN.sub('_', s)
        if lowercase:
            chanks = chanks.lower()
        if not chanks:
            chanks = "___"
        if chanks[0].isdigit():
            chanks = "___" + chanks
        if keyword.iskeyword(chanks):
            chanks += "___"
        return chanks

    def add_pyscr(self, basename, keywords={}, verbose=False, dry_run=False):
        if isinstance(basename, list):
            for bn in basename:
                self.add_pyscr(bn, keywords=keywords, verbose=verbose, dry_run=dry_run)
            return

        scr_path = os.path.join(self.python_path, basename+'.py')
        if os.path.exists(scr_path):
            self.stderr.write("Warning: File already exists (Skipped) : '%s'" % (scr_path, ))
        else:
            if verbose or dry_run:
                self.stderr.write("Preparing python library file from template : '%s'" % (scr_path, ))
                
            if not dry_run:
                str_format = {
                    '____SCRIPT_NAME____':                basename if basename.endswith('.py') else basename+'.py',
                    '____SCRIPT_SYMBOLIZED____' :         self.__class__.to_py_identifier(basename.removesuffix('.py'),
                                                                                          lowercase=True),
                    '____SCRIPT_CAPITAL_SYMBOLIZED____' : self.__class__.to_py_identifier_capitalized(basename.removesuffix('.py'),
                                                                                                      use_underscore=False),
                }
                str_format.update(keywords)

                code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=str_format)

                self.__class__.EmbeddedText.extract_to_file(outfile=scr_path,infile=None,
                                                            s_marker=r'\s*#{5,}\s*____PY_MAIN_TEMPLATE_START____\s*#{5,}',
                                                            e_marker=r'\s*#{5,}\s*____PY_MAIN_TEMPLATE_END____\s*#{5,}',
                                                            include_markers=False, multi_match=False,dedent=True, 
                                                            skip_head_emptyline=True, skip_tail_emptyline=True,
                                                            dequote=False, format_filter=code_filter, 
                                                            open_mode='w', encoding=self.encoding)
                os.chmod(scr_path, mode=0o755)


        bin_path = os.path.join(self.bindir, basename)
        if os.path.exists(bin_path):
            self.stderr.write("Warning: File already exists (Skipped) : '%s'" % (bin_path, ))
        else:
            self.mksymlink_this_in_structure(basename, strip_py=True,
                                             dry_run=dry_run, verbose=verbose)


    def add_pylib(self, basename, keywords={}, verbose=False, dry_run=False):
        if isinstance(basename, list):
            for bn in basename:
                self.add_pylib(bn, keywords=keywords, verbose=verbose, dry_run=dry_run)
            return

        scr_path = os.path.join(self.python_path, basename+'.py')
        if os.path.exists(scr_path):
            self.stderr.write("Warning: File already exists (Skipped) : '%s'" % (scr_path, ))
        else:
            if verbose or dry_run:
                self.stderr.write("Preparing python library file from template : '%s'" % (scr_path, ))
                
            gen_fuction = self.__class__.SCRIPT_STD_LIB.get(basename,{}).get('creator')

            
            if not dry_run:
                if callable(gen_fuction):
                    gen_fuction(scr_path, keywords=keywords, shebang=self.python_shebang)
                else:
                    str_format = {'____NEW_CLS_NAME____': basename}
                    str_format.update(keywords)
                    code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=str_format)

                    self.__class__.EmbeddedText.extract_to_file(outfile=scr_path, infile=None,
                                                                s_marker=r'\s*#{5,}\s*____PY_LIB_SCRIPT_TEMPLATE_START____\s*#{5,}',
                                                                e_marker=r'\s*#{5,}\s*____PY_LIB_SCRIPT_TEMPLATE_END____\s*#{5,}',
                                                                include_markers=False, multi_match=False,dedent=True, 
                                                                skip_head_emptyline=True, skip_tail_emptyline=True,
                                                                dequote=False, format_filter=code_filter, 
                                                                open_mode='w', encoding=self.encoding)

    def make_gitignore_contents(self, output_path,
                                git_keepdirs=None,
                                template_s_marker=None,
                                templete_e_marker=None,
                                dry_run=False, verbose=False, format_alist={}, **format_args):

        if os.path.exists(output_path):
            if verbose:
                self.stderr.write("Warning File exists : skip : '%s'" % (output_path, ))
            return

        if verbose or dry_run:
            self.stderr.write("gitignore : '%s'" % (output_path, ))
        if not dry_run:
            str_format={'____GIT_DUMMYFILE____': 
                        self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'] }

            str_format['____GIT_INGORE_DIRS____'] = ""

            keepdirs = git_keepdirs if isinstance(git_keepdirs, (list,tuple)) else self.git_keepdirs

            for _gitkpdir in keepdirs:
                str_format['____GIT_INGORE_DIRS____'] += ("%s/*\n" % (_gitkpdir, ))
            str_format['____GIT_INGORE_DIRS____'].rstrip()
            str_format.update(format_alist)
            str_format.update(**format_args)
            
            text_filter = self.__class__.EmbeddedText.FormatFilter(format_variables=str_format)

            tmplt_s_mrkr = template_s_marker if template_s_marker else r'\s*#{5,}\s*____GITIGNORE_TEMPLATE_START____\s*#{5,}'
            tmplt_e_mrkr = templete_e_marker if template_s_marker else r'\s*#{5,}\s*____GITIGNORE_TEMPLATE_END____\s*#{5,}'

            self.__class__.EmbeddedText.extract_to_file(outfile=output_path, infile=None,
                                                        s_marker=tmplt_s_mrkr,
                                                        e_marker=tmplt_e_mrkr,
                                                        include_markers=False, multi_match=False,dedent=True, 
                                                        skip_head_emptyline=True, skip_tail_emptyline=True,
                                                        dequote=True, format_filter=text_filter, 
                                                        open_mode='w', encoding=self.encoding)
            os.chmod(output_path, mode=0o644)


    def put_gitkeep(self, dest_dirs=None, dry_run=False, verbose=False):
        dests = dest_dirs if isinstance(dest_dirs, (list, tuple)) else self.git_keepdirs
        for d in dests: # not self.pip_dir_list():
            dp = os.path.join(d, self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'])
            
            if os.path.exists(dp):
                if verbose:
                    self.stderr.write("Warning File exists : skip : '%s'" % (dp, ))
                continue
            if verbose or dry_run:
                self.stderr.write("put %s in '%s'" %
                                  (self.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'], d))
            if not dry_run:
                pathlib.Path(dp).touch(mode=0o644, exist_ok=True)

    @classmethod
    def guess_git_username(cls):
        gitcmd = os.environ.get('GIT', 'git')
        
        gitcmdio = subprocess.run([gitcmd, 'config', '--local', '--get', 'user.name'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        gitcmdio = subprocess.run([gitcmd, 'config', '--global', '--get', 'user.name'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        return getpass.getuser().rstrip(os.linesep)

    @classmethod
    def guess_git_useremail(cls):
        gitcmd = os.environ.get('GIT', 'git')
        
        gitcmdio = subprocess.run([gitcmd, 'config', '--local', '--get', 'user.email'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        gitcmdio = subprocess.run([gitcmd, 'config', '--global', '--get', 'user.email'],
                                  encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gitcmdio.returncode==0:
            return gitcmdio.stdout.rstrip(os.linesep)

        return (getpass.getuser()+'@'+socket.gethostname()).rstrip(os.linesep)


    class ReadMeUpdater(object):
        CNTNTS_HD_MRKR  = re.compile(r"^ *- *Contents:")
        CNTNTS_TL_MRKR  = re.compile(r"^ *- *Usage.*:")
        CNTNTS_IDX_MRKR = re.compile(r"^ +(?P<index>[0-9]+)\. +(?P<file_path>[^\b][^:]+) *: *(?P<desc>\S.*)$")
        GITIGNORE_RE    = re.compile(r"\.gitignore")
        USAGE_RE        = CNTNTS_TL_MRKR
        
        def __init__(self, ref_pycan, keywords={}, bin_basenames=[], lib_basenames=[], flg_git:bool=False):
            self.ref_pycan = ref_pycan
            self.keywords=keywords
            self.bin_basenames=bin_basenames
            self.lib_basenames=lib_basenames

            self.bin_subdir       = self.ref_pycan.bindir.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.python_subdir    = self.ref_pycan.python_path.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_subdir       = self.ref_pycan.python_pip_path.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_cache_subdir = self.ref_pycan.python_pip_cache.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_src_subdir   = self.ref_pycan.python_pip_src.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.pip_log_subdir   = self.ref_pycan.python_pip_logdir.removeprefix(self.ref_pycan.prefix).removeprefix('/')
            self.gitkeep_subdirs  = [ x.removeprefix(self.ref_pycan.prefix).removeprefix('/') for x in self.ref_pycan.git_keepdirs ]

            self.flg_git=flg_git

        def update_keywords(self, text):
            for k,v in self.keywords.items():
                text = text.replace(k, v)
            return text

        def proc_file(self, in_file=None, in_text='', out_file=None, encoding="utf-8", verbose=False, dry_run=False):
            if verbose or dry_run:
                if in_file is None:
                    msg = "Read from text: '%s%s'" % (in_text[:20], "..." if len(in_text)>20 else '')
                else:
                    msg = "Read from file: '%s'"   % (in_file)

                self.ref_pycan.stderr.write("Read from text: '%s'" % (msg, ))

            fin = (io.StringIO(initial_value=in_text, encoding=encoding) 
                   if in_file is None else open(in_file, encoding=encoding) )
            fout = (io.StringIO(encoding=encoding)
                    if (dry_run or out_file is None)
                    else open(out_file, "w", encoding=encoding))

            for line in self.process_lines(fin):
                if (dry_run) and (out_file is not None):
                    continue
                fout.write(line)
            fin.close()
            if out_file is None:
                return fout.getvalue()
            else:
                fout.close()
                        
        def process_lines(self, lines: typing.Iterator[str]) -> typing.Iterator[str]:
            fidx, flg_added, flg_in_range = (0, False, False)
            file_listed = {}

            for raw in lines:
                line = self.update_keywords(raw.rstrip("\n"))

                if self.__class__.CNTNTS_HD_MRKR.match(line):
                    flg_in_range = True
                if self.__class__.CNTNTS_TL_MRKR.match(line):
                    if ( (not flg_added) and (self.__class__.USAGE_RE.match(line))):
                        block, fidx = self.make_additional_block(fidx, file_listed)
                        for b in block:
                            yield b
                        yield "\n"
                        added = True
        
                    flg_in_range = False
        
                if flg_in_range:
                    f_match=self.__class__.CNTNTS_IDX_MRKR.match(line)
                    if f_match:
                        fidx += 1
                        line = "  %-3s %-42s %s" % ( ("%d." % (fidx,)),
                                                     f_match.group('file_path')+":",
                                                     f_match.group('desc'))
                        file_listed[f_match.group('file_path')] = f_match.group('index')
        
                if flg_in_range and self.__class__.CNTNTS_TL_MRKR.match(line):
                    in_range = False
        
                yield line + "\n"

        def make_additional_block(self, start_idx:int, file_listed:dict) -> tuple[list[str], int]:
            buf = []
            f = start_idx

            for bn in self.bin_basenames:
                scr_subpath = os.path.join(self.python_subdir,bn+'.py')
                if not scr_subpath in file_listed.keys():
                    f += 1
                    buf.append("  %-3s %-42s Example Python script that use modules\n" % ("%d." % (f,), scr_subpath+':'))

                bin_subpath = os.path.join(self.bin_subdir, bn)
                if not bin_subpath in file_listed.keys():
                    f += 1
                    # buf.append("  %-3s %-42s Symbolic link to %s to invoke %s.py.\n" % ("%d." % (f,), bin_subpath+':', 
                    #                                                                     os.path.basename(__file__), bn))
                    buf.append("  %-3s %-42s Symbolic link to %s to invoke %s.py.\n"
                               % ("%d." % (f,), bin_subpath+':', 
                                  pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name, bn))

            for bn in self.lib_basenames:
                scr_subpath = os.path.join(self.python_subdir, bn+'.py')
                if scr_subpath in file_listed.keys():
                    continue
                f += 1
                buf.append("  %-3s %-42s Python Library script used in this package\n" % ("%d." % (f,), scr_subpath+':'))

            return buf, f

        def save_readme_contents(self, output, bin_basenames=None, lib_basenames=None, gitkeepdirs=None, format_alist={}, **format_args):

            str_format={'____GIT_DUMMYFILE____':        self.ref_pycan.__class__.FILENAME_DEFAULT['____GIT_DUMMYFILE____'],
                        '____TITLE____' :               'Project Title',
                        '____README_NAME____':          self.ref_pycan.__class__.FILENAME_DEFAULT.get('____README_NAME____', 'README.md'),
                        '____MNGSCRIPT_NAME____':       self.ref_pycan.__class__.FILENAME_DEFAULT.get('MNG_SCRIPT',          'pycan_mng'),
                        '____BIN_PATH____':             str(self.bin_subdir),
                        '____PYLIB_PATH____':           str(self.python_subdir),
                        '____PIP_PATH____':             str(self.pip_subdir),
                        '____PIP_CACHE____':            str(self.pip_cache_subdir),
                        '____PIP_SRC____':              str(self.pip_src_subdir),
                        '____PIP_LOG____':              str(self.pip_log_subdir),
                        '____SHSCRIPT_ENTITY_NAME____':
                        pathlib.Path(inspect.getsourcefile(inspect.currentframe())).resolve().name, # os.path.basename(__file__),
                        '____AUTHOR_NAME____':          'Auther Name',
                        '____AUTHOR_EMAIL____':         'Auther-email-address',
                        '____GIT_DUMMY_LISTS____':      "\n",
                        '____SCRIPT_DESC____':          "\n",
                        '____LIBFILE_DESC____':         "\n"
                        }
            str_format.update(format_alist)
            str_format.update(**format_args)

            bin_bns = bin_basenames if isinstance(bin_basenames, list) else self.bin_basenames
            lib_bns = lib_basenames if isinstance(lib_basenames, list) else self.lib_basenames
            git_kds = gitkeepdirs   if isinstance(gitkeepdirs, list)   else self.gitkeep_subdirs

            dummy_desc   = str_format.get('____GIT_DUMMY_LISTS____', "\n")
            script_desc  = str_format.get('____SCRIPT_DESC____', "\n")
            libfile_desc = str_format.get('____LIBFILE_DESC____', "\n")

            contents_list = []
            contents_list.append([str_format['____README_NAME____'],
                                  "This file"])
            contents_list.append([os.path.join(str_format['____BIN_PATH____'],
                                               str_format['____MNGSCRIPT_NAME____']),
                                  "Symblic link to '"
                                  +str_format['____SHSCRIPT_ENTITY_NAME____']
                                  +" for installing Python modules by pip locally."])
            contents_list.append([os.path.join(str_format['____BIN_PATH____'],
                                               str_format['____SHSCRIPT_ENTITY_NAME____']),
                                  "Wrapper python script to invoke Python script. (Entity)"])
            contents_list.append([str_format['____PIP_PATH____'],  "Directory where python modules are stored"])
            contents_list.append([str_format['____PIP_CACHE____'], "Cache directory for module installation by pip"])
            contents_list.append([str_format['____PIP_SRC____'],   "Source directory for module installation for pip"])
            contents_list.append([str_format['____PIP_LOG____'],   "Log directory for module installation for pip"])
            contents_list.append("\n")

            if self.flg_git:
                contents_list.append([".gitignore", "Git-related file"])
                git_keepdir_desc = "Git-related file to keep modules directory in repository."
                for _gitkd in git_kds:
                    contents_list.append([os.path.join(_gitkd, str_format['____GIT_DUMMYFILE____']),
                                          git_keepdir_desc])
                    git_keepdir_desc = 'a ditto'
                contents_list.append("\n")

            for _scr in bin_bns:
                _scr_bn = _scr.removesuffix('.py')
                contents_list.append([os.path.join(self.python_subdir, _scr_bn+'.py'),
                                      "Example Python script that use modules"])
                contents_list.append([os.path.join(self.bin_subdir, _scr_bn),
                                      ( "Symbolic link to '%s' to invoke %s.py." 
                                        % (str_format['____SHSCRIPT_ENTITY_NAME____'], _scr_bn))])
                #contents_list.append("\n")

            lib_desc_default = 'Example Python module file by template'
            for _lib in lib_bns:
                _lib_bn   = _lib.removesuffix('.py')
                _lib_desc = ( self.ref_pycan.__class__.SCRIPT_STD_LIB.get(_lib_bn,{'description': lib_desc_default}).get('description') 
                              if _lib_bn in self.ref_pycan.__class__.SCRIPT_STD_LIB.keys() else None)
                if _lib_desc is None:
                    _lib_desc = lib_desc_default
                contents_list.append([("%s.py" % (os.path.join(self.python_subdir,_lib_bn),)),
                                      _lib_desc])

            contents_lines = ""
            desc_idx=0
            for descinfo in contents_list:
                if (isinstance(descinfo,(list, tuple)) and 
                    isinstance(descinfo[0], str) and descinfo[0]):
                    contents_lines += "  %-3s %-42s %s\n" % (("%d." % (desc_idx+1,)),
                                                             ("%s:" % (descinfo[0],)),
                                                             (str(descinfo[1]) if len(descinfo)>1 else '' ))
                    desc_idx += 1
                else:
                    contents_lines += (descinfo if isinstance(descinfo,str) else "")

            str_format.update({'____contents_lines____': contents_lines.rstrip(os.linesep)})

            text_filter = self.ref_pycan.__class__.EmbeddedText.FormatFilter(format_variables=str_format)

            self.ref_pycan.__class__.EmbeddedText.extract_to_file(outfile=output, infile=None,
                                                                  s_marker=r'\s*#{5,}\s*____README_TEMPLATE_START____\s*#{5,}',
                                                                  e_marker=r'\s*#{5,}\s*____README_TEMPLATE_END____\s*#{5,}',
                                                                  include_markers=False, multi_match=False,dedent=True, 
                                                                  skip_head_emptyline=True, skip_tail_emptyline=True,
                                                                  dequote=True, format_filter=text_filter, 
                                                                  open_mode='w', encoding=self.ref_pycan.encoding)
            os.chmod(output, mode=0o644)

    class PyCodeFilter(object):

        SHEBANG_PATTERN = re.compile(r'^\s*#+ *____py_shebang_pattern____ *#+ *(?=[\n\r]+)')
            
        def __init__(self, 
                     shebang,
                     keyword_table:dict=None, 
                     **cmd_args):
            self.shebang=shebang
            self.keyword_table  = keyword_table
            self.valid_keywords = (keyword_table is not None)
            if self.valid_keywords:
                self.keyword_table.update(cmd_args)
    
        def __call__(self, line:str)->str:
            if isinstance(self.shebang, str) and self.shebang:
                line = self.__class__.SHEBANG_PATTERN.sub(self.shebang, line, 1)
            if self.valid_keywords:
                for k,v in self.keyword_table.items():
                    line = line.replace(str(k), str(v))
            return line

    def python_pkg_cache_template_save(self, outputfile, keywords:dict={}, shebang:str=None):

        code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=keywords)

        self.__class__.EmbeddedText.extract_to_file(outfile=outputfile, infile=None,
                                                    s_marker=r'\s*#{5,}\s*____PKG_CACHE_TEMPLATE_START____\s*#{5,}',
                                                    e_marker=r'\s*#{5,}\s*____PKG_CACHE_TEMPLATE_END____\s*#{5,}',
                                                    include_markers=False, multi_match=False,dedent=True, 
                                                    skip_head_emptyline=True, skip_tail_emptyline=True,
                                                    dequote=False, format_filter=code_filter, 
                                                    open_mode='w', encoding=self.encoding)
        os.chmod(outputfile, mode=0o644)

    def python_intrinsic_format_template_save(self, outputfile, keywords:dict={}, shebang:str=None):

        code_filter = self.__class__.PyCodeFilter(self.python_shebang, keyword_table=keywords)

        self.__class__.EmbeddedText.extract_to_file(outfile=outputfile, infile=None,
                                                    s_marker=r'\s*#{5,}\s*____INTRINSIC_FORMATTER_TEMPLATE_START____\s*#{5,}',
                                                    e_marker=r'\s*#{5,}\s*____INTRINSIC_FORMATTER_TEMPLATE_END____\s*#{5,}',
                                                    include_markers=False, multi_match=False,dedent=True, 
                                                    skip_head_emptyline=True, skip_tail_emptyline=True,
                                                    dequote=False, format_filter=code_filter, 
                                                    open_mode='w', encoding=self.encoding)
        os.chmod(outputfile, mode=0o644)

    class EmbeddedText(object):
    
        HEADSPACE   = re.compile(r'^(?P<indent>\s*).*')
        EMPTYLINE   = re.compile(r'^\s*$')
        TRIPLEQUATE = re.compile(r"^\s*(?P<triplequote>'{3}|\"{3})(?P<rest>.*)$")
    
        class FormatFilter(object):
            
            def __init__(self, 
                         keyword_table:dict=None, 
                         format_variables:dict=None,
                         **cmd_args):
                self.keyword_table    = keyword_table
                self.format_variables = format_variables
                self.flg_filters      = (isinstance(self.keyword_table,dict),
                                         isinstance(self.format_variables,dict))
                if self.flg_filters[0]:
                    self.keyword_table.update(cmd_args)
                if self.flg_filters[1]:
                    self.format_variables.update(cmd_args)
    
            def __call__(self, line:str)->str:
                if self.flg_filters[1]:
                    line = line.format(**self.format_variables)
                if self.flg_filters[0]:
                    for k,v in self.keyword_table.items():
                        line = line.replace(k, v)
                return line
    
        @classmethod
        def extract_raw(cls, lines: typing.Iterable[str],
                        s_marker:str=None, e_marker:str=None,
                        include_markers:bool=True, multi_match:bool=False,
                        dedent:bool=False, format_filter=None) -> typing.Iterator[str]:
    
            s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                        else ( re.compile(s_marker) 
                               if isinstance(s_marker, str) and s_marker else None))
            e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
    
            indent     = ''
            in_range = True if s_pttrn is None else False

            for line in lines:
                if not in_range:
                    if s_pttrn is None or s_pttrn.match(line):
                        if dedent:
                            m_indent = cls.HEADSPACE.match(line)
                            if m_indent:
                                indent = m_indent.group('indent')
                                line = line.removeprefix(indent)
                        in_range = True
                        if include_markers:
                            yield format_filter(line) if callable(format_filter) else line
                else:
                    line = line.removeprefix(indent)
                    if e_pttrn is None:
                        yield format_filter(line) if callable(format_filter) else line
                    elif e_pttrn.match(line):
                        if include_markers:
                            yield format_filter(line) if callable(format_filter) else line
                        if multi_match and s_pttrn is not None:
                            in_range   = False
                            indent     = ''
                        else:
                            return
                    else:
                        yield format_filter(line) if callable(format_filter) else line
    
        @classmethod
        def extract_dequote(cls, lines: typing.Iterable[str],
                            s_marker:str=None, e_marker:str=None,
                            include_markers:bool=True, multi_match:bool=False,
                            dedent:bool=False, dequote:bool=True, 
                            format_filter=None) -> typing.Iterator[str]:
    
            s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                        else ( re.compile(s_marker) 
                               if isinstance(s_marker, str) and s_marker else None))
            e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
    
            quote_mrkr = ''
            for line in cls.extract_raw(lines=lines,
                                        s_marker=s_pttrn,
                                        e_marker=e_pttrn,
                                        include_markers=include_markers,
                                        multi_match=multi_match,
                                        dedent=dedent,
                                        format_filter=format_filter):
                if dequote:
                    if quote_mrkr:
                        pos = line.find(quote_mrkr)
                        if pos>=0:
                            line = line[0:pos] + line[pos+len(quote_mrkr):]
                            quote_mrkr = ''
    
                    m_triquote = cls.TRIPLEQUATE.match(line)
                    while m_triquote:
                        quote_mrkr = m_triquote.group('triplequote')
                        line = m_triquote.group('rest')+os.linesep
                        
                        pos = line.find(quote_mrkr)
                        if pos>=0:
                            line = line[0:pos]+line[pos+len(quote_mrkr):]
                            quote_mrkr = ''
                        else:
                            break
                        m_triquote = cls.TRIPLEQUATE.match(line)
                        
                yield line
    
        @classmethod
        def extract(cls,lines: typing.Iterable[str],
                    s_marker:str=None,
                    e_marker:str=None,
                    include_markers:bool=True,
                    multi_match:bool=False,
                    dedent:bool=False,
                    dequote:bool=False,
                    skip_head_emptyline:bool=False,
                    skip_tail_emptyline:bool=False, 
                    format_filter=None) -> typing.Iterator[str]:
    
            s_pttrn = ( s_marker if isinstance(s_marker, re.Pattern) 
                        else ( re.compile(s_marker) 
                               if isinstance(s_marker, str) and s_marker else None))
            e_pttrn = ( e_marker if isinstance(e_marker, re.Pattern) 
                         else ( re.compile(e_marker) 
                                if isinstance(e_marker, str) and e_marker else None))
            el_buf     = []
            el_bfr_hdr = True
            in_range = True if s_pttrn is None else False
            for line in cls.extract_dequote(lines=lines,
                                            s_marker=s_pttrn, e_marker=e_pttrn,
                                            include_markers=True,
                                            multi_match=multi_match,
                                            dedent=dedent, dequote=dequote,
                                            format_filter=format_filter):
                if not in_range:
                    if s_pttrn is None or s_pttrn.match(line):
                        in_range = True
                        if include_markers:
                            yield line
                else:
                    m_el = cls.EMPTYLINE.match(line)
                    if m_el:
                        el_buf.append(line)
                    else:
                        if el_bfr_hdr and skip_head_emptyline:
                            el_bfr_hdr = False
                            el_buf=[]
    
                    if e_pttrn is not None and e_pttrn.match(line):
                        if not skip_tail_emptyline:
                            yield from el_buf
                            el_buf = []
                        if include_markers:
                            yield line
                        if multi_match or (s_pttrn is not None):
                            el_buf     = []
                            el_bfr_hdr = True
                            in_range   = False
                        else:
                            return
                    elif not m_el:
                        yield from el_buf
                        el_buf = []
                        yield line
    
            if e_pttrn is None and (not skip_tail_emptyline):
                yield from el_buf
                el_buf = []
    
        @classmethod
        def extract_from_file(cls, infile:str=None, s_marker:str=None, e_marker:str=None,
                              include_markers:bool=True, multi_match:bool=False,
                              dedent:bool=False, skip_head_emptyline:bool=False,
                              skip_tail_emptyline:bool=False, dequote:bool=False,
                              format_filter=None, encoding:str='utf-8') -> typing.Iterator[str]:
    
            input_path = pathlib.Path( infile if isinstance(infile,str) and infile
                                       else inspect.getsourcefile(inspect.currentframe())).resolve()
            with open(input_path, encoding=encoding) as fin:
                for line in cls.extract(fin, 
                                        s_marker=s_marker,
                                        e_marker=e_marker,
                                        include_markers=include_markers,
                                        multi_match=multi_match,
                                        dedent=dedent, dequote=dequote,
                                        format_filter=format_filter,
                                        skip_head_emptyline=skip_head_emptyline,
                                        skip_tail_emptyline=skip_tail_emptyline):
                    yield line
    
        @classmethod
        def extract_to_file(cls, outfile, infile:str=None, s_marker:str=None, e_marker:str=None,
                            include_markers:bool=True, multi_match:bool=False,
                            dedent:bool=False, skip_head_emptyline:bool=False,
                            skip_tail_emptyline:bool=False, dequote:bool=False,
                            format_filter=None, open_mode='w', encoding:str='utf-8'):
            
            fout = sys.stdout if outfile is None else open(outfile, mode=open_mode, encoding=encoding)
            for line in cls.extract_from_file(infile=infile, 
                                              s_marker=s_marker, e_marker=e_marker,
                                              include_markers=include_markers,
                                              multi_match=multi_match, dedent=dedent, 
                                              skip_head_emptyline=skip_head_emptyline,
                                              skip_tail_emptyline=skip_tail_emptyline,
                                              dequote=dequote, format_filter=format_filter, encoding=encoding):
                fout.write(line)
            if outfile is not None:
                fout.close()

def main():
    import sys
    return PyEncase(sys.argv).main()

if __name__=='__main__':
    main()

    if False:

        ############# ____GITIGNORE_TEMPLATE_START____ #######################

        """
        # .gitignore
        *.py[cod]
        *$py.class
        # For emacs backup file
        *~
        {____GIT_INGORE_DIRS____}
        !{____GIT_DUMMYFILE____}
        """

        ############# ____GITIGNORE_TEMPLATE_END____ #######################

        ############# ____README_TEMPLATE_START____ #######################
    
        """
        #
        # {____TITLE____}
        #
        
        Skeleton for small portable tools by python script
        
        - Contents:

        {____contents_lines____}
         
        - Usage (Procedure for adding new script):
        
          1. Put new script under '{____PYLIB_PATH____}'.
        
             Example: '{____PYLIB_PATH____}/{{newscriptname}}.py'
        
          2. Make symbolic link to '{____BIN_PATH____}/{____SHSCRIPT_ENTITY_NAME____}' with same basename as the
             basename of new script.
        
              Example: '{____BIN_PATH____}/{{newscriptname}}' --> {____SHSCRIPT_ENTITY_NAME____}
        
          3. Download external python module by './{____BIN_PATH____}/{____MNGSCRIPT_NAME____}'
        
              Example: '{____PYLIB_PATH____}/{{newscriptname}}.py' uses modules, pytz and tzlocal.
        
              % ./{____BIN_PATH____}/{____MNGSCRIPT_NAME____} install pytz tzlocal
        
          4. Invoke the symbolic link made in step.2 for execute the script.
        
              % ./{____BIN_PATH____}/{{newscriptname}}
        
        - Caution:
        
          - Do not put python scripts/modules that are not managed by pip
            under '{____PIP_PATH____}'.
        
            Otherwise those scripts/modules will be removed by
            `./{____BIN_PATH____}/{____MNGSCRIPT_NAME____} distclean`
        
        - Note:
        
          - Python executable is seeked by the following order.
        
            1. Environmental variable: PYTHON
            2. Shebang in called python script
            3. python3 in PATH
            4. python  in PATH
        
          - pip command is seeked by the following order.
        
            1. Environmental variable: PIP
            2. pip3 in PATH for "{____MNGSCRIPT_NAME____}"
            3. pip3 in PATH
        
        - Requirements (Tools used in "{____SHSCRIPT_ENTITY_NAME____}")
        
          - Python, PIP
        
        - Author
        
          - {____AUTHOR_NAME____} ({____AUTHOR_EMAIL____})
    
        --
        """

        ############# ____README_TEMPLATE_END____ #######################


        ############# ____PY_MAIN_TEMPLATE_START____ #######################
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
            
        import argparse
        import datetime
        import sys
            
        import pytz
        import tzlocal
        
        #import pkgstruct

        class ____SCRIPT_CAPITAL_SYMBOLIZED____(object):

            def __init__(self):
                pass
        
            def main(self, args=sys.argv):
                """
                ____SCRIPT_NAME____
                Example code skeleton: Just greeting
                """
                argpsr = argparse.ArgumentParser(description='Example: showing greeting words')
                argpsr.add_argument('name', nargs='*', type=str, default=['World'],  help='your name')
                argpsr.add_argument('-d', '--date', action='store_true', help='Show current date & time')
                args = argpsr.parse_args(args)
                if args.date:
                    tz_local = tzlocal.get_localzone()
                    datestr  = datetime.datetime.now(tz=tz_local).strftime(" It is \"%c.\"")
                else:
                    datestr = ''
        
                print("Hello, %s!%s" % (' '.join(args.name), datestr))
                print("Python : %d.%d.%d " % sys.version_info[0:3]+ "(%s)" % sys.executable)
                hdr_str = "Python path: "
                for i,p in enumerate(sys.path):
                    print("%-2d : %s" % (i+1, p))
                    hdr_str = ""
            
                #pkg_info   = pkgstruct.PkgStructure(script_path=sys.argv[0])
                #pkg_info.dump(relpath=False, with_seperator=True)
        
        if __name__ == '__main__':
            ____SCRIPT_CAPITAL_SYMBOLIZED____().main()

        ########## ____PY_MAIN_TEMPLATE_END____ ##########

        
        ########## ____PY_LIB_SCRIPT_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        
        import json
        
        class ____NEW_CLS_NAME____(object):
            """
            ____NEW_CLS_NAME____
            Example class code skeleton: 
            """
            def __init__(self):
                self.contents = {}  
        
            def __repr__(self):
                return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
        
            def __str__(self):
                return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
        
        if __name__ == '__main__':
            help(____NEW_CLS_NAME____)

        ########## ____PY_LIB_SCRIPT_TEMPLATE_END____ ##########

        ########## ____PKG_CACHE_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        import gzip
        import bz2
        import re
        import os
        import sys
        import json
        import filecmp
        
        import yaml
        
        import intrinsic_format
        import pkgstruct
        
        class PkgCache(pkgstruct.PkgStruct):
            """
            Class for Data cache for packaged directory
            """
            def __init__(self, subdirkey='pkg_cachedir', subdir=None, 
                         dir_perm=0o755, perm=0o644, keep_oldfile=False, backup_ext='.bak',
                         timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True,
                         script_path=None, env_input=None, prefix=None, pkg_name=None,
                         flg_realpath=False, remove_tail_digits=True, remove_head_dots=True, 
                         basename=None, tzinfo=None, unnecessary_exts=['.sh', '.py', '.tar.gz'],
                         namespece=globals(), yaml_register=True, **args):
        
                super().__init__(script_path=script_path, env_input=env_input, prefix=prefix, pkg_name=pkg_name,
                                 flg_realpath=flg_realpath, remove_tail_digits=remove_tail_digits, remove_head_dots=remove_head_dots, 
                                 unnecessary_exts=unnecessary_exts, **args)
        
                self.config = { 'dir_perm':                 dir_perm,
                                'perm':                     perm,
                                'keep_oldfile':             keep_oldfile,
                                'backup_ext':               backup_ext,
                                'timestampformat':          timestampformat,
                                'avoid_duplicate':          avoid_duplicate,
                                'json:skipkeys':            False,
                                'json:ensure_ascii':        False, # True,
                                'json:check_circular':      True, 
                                'json:allow_nan':           True,
                                'json:indent':              4, # None,
                                'json:separators':          None,
                                'json:default':             None,
                                'json:sort_keys':           True, # False,
                                'json:parse_float':         None,
                                'json:parse_int':           None,
                                'json:parse_constant':      None,
                                'json:object_pairs_hook':   None,
                                'yaml:stream':              None,
                                'yaml:default_style':       None,
                                'yaml:default_flow_style':  None,
                                'yaml:encoding':            None,
                                'yaml:explicit_start':      True, # None,
                                'yaml:explicit_end':        True, # None,
                                'yaml:version':             None,
                                'yaml:tags':                None,
                                'yaml:canonical':           True, # None,
                                'yaml:indent':              4, # None,
                                'yaml:width':               None,
                                'yaml:allow_unicode':       None,
                                'yaml:line_break':          None
                               }
        
                if isinstance(subdir,list) or isinstance(subdir,tuple):
                    _subdir = [ str(sd) for sd in subdir]
                    self.cache_dir = self.concat_path(skey, *_subdir)
                elif subdir is not None:
                    self.cache_dir = self.concat_path(skey, str(subdir))
                else:
                    self.cache_dir = self.concat_path(skey)
        
                self.intrinsic_formatter = intrinsic_format.intrinsic_formatter(namespace=namespace,
                                                                                register=yaml_register)
        
            def read(self, fname, default=''):
                return self.read_cache(fname, default='', directory=self.cache_dir)
        
            def save(self, fname, data):
                return self.save_cache(fname, data, directory=self.cache_dir, **self.config)
        
            @classmethod
            def save_cache(cls, fname, data, directory='./cache', dir_perm=0o755,
                           keep_oldfile=False, backup_ext='.bak', 
                           timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
                """ function to save data to cache file
                fname     : filename
                data      : Data to be stored
                directory : directory where the cache is stored. (default: './cache')
            
                Return value : file path of cache file
                               None when fail to make cache file
                """
                data_empty = True if (((isinstance(data, str) or isinstance(data, bytes) or
                                        isinstance(data, dict) or isinstance(data, list) or
                                        isinstance(data, tuple) ) and len(data)==0)
                                      or isinstance(data, NoneType) ) else False
                if data_empty:
                    return None
                if not os.path.isdir(directory):
                    os.makedirs(directory, mode=dir_perm, exist_ok=True)
                o_path = os.path.join(directory, fname)
                ext1, ext2, fobj = cls.open_autoassess(o_path, 'w',
                                                       keep_oldfile=keep_oldfile,
                                                       backup_ext=backup_ext, 
                                                       timestampformat=timestampformat,
                                                       avoid_duplicate=avoid_duplicate)
                if fobj is None:
                    return None
        
                if ext2 == 'yaml':
                    #f.write(yaml.dump(data))
                    f.write(self.intrinsic_formatter.dump_json(data, 
                                                               skipkeys=self.config['json:skipkeys'],
                                                               ensure_ascii=self.config['json:ensure_ascii'],
                                                               check_circular=self.config['json:check_circular'],
                                                               allow_nan=self.config['json:allow_nan'],
                                                               indent=self.config['json:indent'],
                                                               separators=self.config['json:separators'],
                                                               default=self.config['json:default'],
                                                               sort_keys=self.config['json:sort_keys']))
                elif ext2 == 'json':
                    #f.write(json.dumps(data, ensure_ascii=False))
                    f.write(self.intrinsic_formatter.dump_yaml(data,
                                                               stream=self.config['yaml:stream'],
                                                               default_style=self.config['yaml:default_style'],
                                                               default_flow_style=self.config['yaml:default_flow_style'],
                                                               encoding=self.config['yaml:encoding'],
                                                               explicit_start=self.config['yaml:explicit_start'],
                                                               explicit_end=self.config['yaml:explicit_end'],
                                                               version=self.config['yaml:version'],
                                                               tags=self.config['yaml:tags'],
                                                               canonical=self.config['yaml:canonical'],
                                                               indent=self.config['yaml:indent'],
                                                               width=self.config['yaml:width'],
                                                               allow_unicode=self.config['yaml:allow_unicode'],
                                                               line_break=self.config['yaml:line_break']))
                else:
                    f.write(data)
                f.close()
        
                os.path.chmod(o_path, mode=perm)
                return o_path
        
            @classmethod
            def backup_by_rename(cls, orig_path, backup_ext='.bak',
                                 timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
                if not os.path.lexists(orig_path):
                    return
                path_base, path_ext2 = os.path.splitext(orig_path)
                if path_ext2 in ['.bz2', '.gz']:
                    path_base, path_ext = os.path.splitext(path_base)
                else:
                    path_ext2, path_ext = ('', path_ext2)
                if path_ext == backup_ext and len(path_base)>0:
                    path_base, path_ext = os.path.splitext(path_base)
                if isinstance(timestampformat, str) and len(timestampformat)>0:
                    mtime_txt = '.' + datetime.datetime.fromtimestamp(os.lstat(orig_path).st_mtime).strftime(timestampformat)
                else:
                    mtime_txt = ''
        
                i=0
                while(True):
                    idx_txt = ( ".%d" % (i) ) if i>0 else ''
                    bak_path = path_base + mtime_txt + idx_txt + path_ext  + backup_ext + path_ext2
                    if os.path.lexists(bak_path):
                        if avoid_duplicate and filecmp.cmp(orig_path, bak_path, shallow=False):
                            os.unlink(bak_path)
                        else:
                            continue
                    os.rename(orig_path, bak_path)
                    break
        
                    
            @classmethod
            def open_autoassess(cls, path, mode, 
                                keep_oldfile=False, backup_ext='.bak', 
                                timestampformat="%Y%m%d_%H%M%S", avoid_duplicate=True):
        
                """ function to open normal file or file compressed by gzip/bzip2
                    path : file path
                    mode : file open mode 'r' or 'w'
            
                    Return value: (1st_extension: bz2/gz/None,
                                   2nd_extension: yaml/json/...,
                                   opend file-io object or None)
                """
                if 'w' in mode or 'W' in mode:
                    modestr = 'w'
                    if keep_oldfile:
                        cls.backup_by_rename(path, backup_ext=backup_ext,
                                             timestampformat=timestampformat,
                                             avoid_duplicate=avoid_duplicate)
                elif 'r' in mode  or 'R' in mode:
                    modestr = 'r'
                    if not os.path.isfile(path):
                        return (None, None, None)
                else:
                    raise ValueError("mode should be 'r' or 'w'")
        
                base, ext2 = os.path.splitext(path)
                if ext2 in ['.bz2', '.gz']:
                    base, ext1 = os.path.splitext(path_base)
                else:
                    ext1, ext2 = (ext2, '')
        
                if ext2 == 'bz2':
                    return (ext2, ext1, bz2.BZ2File(path, modestr+'b'))
                elif ext2 == 'gz':
                    return (ext2, ext1, gzip.open(path, modestr+'b'))
                return (ext2, ext1, open(path, mode))
        
            @classmethod
            def read_cache(cls, fname, default='', directory='./cache'):
                """ function to read data from cache file
                fname      : filename
                default   : Data when file is empty (default: empty string)
                directory : directory where the cache is stored. (default: ./cache)
            
                Return value : data    when cache file is exist and not empty,
                               default otherwise
                """
                if not os.path.isdir(directory):
                    return default
                in_path = os.path.join(directory, fname)
                ext1, ext2, fobj = cls.open_autoassess(in_path, 'r')
                if fobj is None:
                    return default
                f_size = os.path.getsize(in_path)
        
                data = default
                if ((ext1 == 'bz2' and f_size > 14) or
                    (ext1 == 'gz'  and f_size > 14) or
                    (ext1 != 'bz2' and ext1 != 'gz' and f_size > 0)):
                    if ext2 == 'yaml' or ext2 == 'YAML':
                        #data = yaml.load(fobj)
                        data = self.intrinsic_formatter.load_json(fobj,
                                                                  parse_float=self.config['json:parse_float'],
                                                                  parse_int=self.config['json:parse_int'],
                                                                  parse_constant=self.config['json:parse_constant'],
                                                                  object_pairs_hook=self.config['json:object_pairs_hook'])
                    elif ext2 == 'json'or ext2 == 'JSON':
                        # data = json.load(fobj)
                        data = self.intrinsic_formatter.load_yaml(fobj)
                    else:
                        data = fobj.read()
                f.close()
                return data
            
        
        if __name__ == '__main__':
            help(PkgCache)

        ########## ____PKG_CACHE_TEMPLATE_END____ ##########

        ########## ____INTRINSIC_FORMATTER_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        import os
        import sys
        import io
        
        import datetime
        import copy
        import inspect
        
        import json
        import yaml
        
        class intrinsic_formatter(object):
            """
            Utility for intrinsic format to store/restore class instanse data.
                    w/  interface for PyYAML and json
            """
            def __init__(self, namespace=globals(), register=True, proc=None):
                self.pyyaml_dumper  = yaml.SafeDumper
                self.pyyaml_loader  = yaml.SafeLoader
                self.namespace      = namespace
                self.proc           = proc
                if register:
                    self.pyyaml_register(namespace=self.namespace)
        
            @classmethod
            def decode(cls, data, proc=None, namespace=globals()):
                """
                Restore object from intrinsic data expression as much as possible
                """
                untouch_type  = (int, float, complex, bool, str, bytes, bytearray)
                sequence_type = (list, tuple, set, frozenset)
            
                if isinstance(data, dict):
                    meta_data_tag = ('____class____', '____name____', '____tag____')
                    _cls_, _clsname, _clstag = ( data.get(k) for k in meta_data_tag )
                    if _cls_ == 'datetime.datetime':
                        # return datetime.datetime.fromisoformat(data.get('timestamp'))
                        return datetime.datetime.strptime(data.get('timestamp'), '%Y-%m-%dT%H:%M:%S.%f%z')
            
                    if _cls_ is not None and _clsname is not None and _clstag is not None:
                        if isinstance(namespace, dict):
                            cls_ref = namespace.get(_cls_)
                            if cls_ref is None:
                                cls_ref = namespace.get(_clsname)
                        if cls_ref is None:
                            cls_ref = locals().get(_cls_)
                        if cls_ref is None:
                            cls_ref = locals().get(_clsname)
                        if cls_ref is None:
                            cls_ref = globals().get(_cls_)
                        if cls_ref is None:
                            cls_ref = globals().get(_clsname)
                        if cls_ref is not None and inspect.isclass(cls_ref):
                            if hasattr(cls_ref, 'from_intrinsic') and callable(cls_ref.from_intrinsic):
                                return proc(cls_ref.from_intrinsic(data)) if callable(proc) else cls_ref.from_intrinsic(data)
                            if hasattr(cls_ref, 'from_dict') and callable(cls_ref.from_dict):
                                return proc(cls_ref.from_dict(data)) if callable(proc) else cls_ref.from_dict(data)
            
                            cnstrctr_args={k: cls.decode(d, proc=proc, namespace=namespace) for k, d in data.items() if k not in meta_data_tag }
                            try:
                                new_obj=cls_ref()
                                for k,d in cnstrctr_args.items():
                                    new_obj.__dict__[k] = copy.deepcopy(d)
                                return new_obj
                            except:
                                pass
                    return {k: cls.decode(d, proc=proc, namespace=namespace) for k, d in data.items() }
            
                for _seqtype in sequence_type:
                    if isinstance(data, _seqtype):
                        return _seqtype( cls.decode(d, proc=proc) for d in data )
            
                if isinstance(data, untouch_type):
                    return proc(data) if callable(proc) else data
            
                #if data is None:
                #    return None
            
                return proc(data) if callable(proc) else data
            
            @classmethod
            def encode(cls, data, proc=None):
                """
                Convert object to intrinsic data expression as much as possible
                """
            
                untouch_type  = (int, float, complex, bool, str, bytes, bytearray)
                sequence_type = (list, tuple, set, frozenset)
                undump_keys   = ('__init__', '__doc__' )
                # undump_keys   = ('__module__', '__init__', '__doc__' )
            
                if data is None:
                    return None
            
                if isinstance(data, untouch_type):
                    return proc(data) if callable(proc) else data
            
                if isinstance(data, datetime.datetime):
                    return {'____class____': data.__class__.__module__+'.'+data.__class__.__name__,
                            '____name____':  data.__class__.__name__,
                            '____tag____':  '!!'+data.__class__.__name__,
                            #'timestamp': data.isoformat(timespec='microseconds'),
                            'timestamp': data.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),  }
            
                if isinstance(data, dict):
                    return {k: cls.encode(d, proc=proc) for k,d in data.items() }
            
                for _seqtype in sequence_type:
                    if isinstance(data, _seqtype):
                        return _seqtype( cls.encode(d, proc=proc) for d in data )
            
                if ( isinstance(data,object) and
                     ( not inspect.ismethod(data) ) and 
                     ( not inspect.isfunction(data) ) ):
                    try:
                        meta_data = {'____class____': data.__class__.__module__+'.'+data.__class__.__name__,
                                     '____name____':  data.__class__.__name__,
                                     '____tag____':  '!!'+data.__class__.__name__}
                        if hasattr(data, 'intrinsic_form') and callable(data.intrinsic_form):
                            return { **meta_data, **(data.intrinsic_form()) }
                        elif hasattr(data, 'to_dict') and callable(data.to_dict):
                            return { **meta_data, **(data.to_dict()) }
                        elif hasattr(data, 'asdict') and callable(data.asdict):
                            return { **meta_data, **(data.asdict()) }
            
                        _data_dict_=data.__dict__
                        return { **meta_data,
                                 **{ k: cls.encode(d, proc=proc) 
                                     for k, d in _data_dict_.items()
                                     if ( ( k not in undump_keys ) and
                                          ( isinstance(d,object) and
                                            ( not inspect.ismethod(d) ) and 
                                            ( not inspect.isfunction(d) ) ) ) } }
                    except:
                        return proc(data) if callable(proc) else data
            
                return None
        
            @classmethod
            def pyyaml_extended_representer(cls, dumper, obj):
                cnved = cls.encode(obj)
                node = dumper.represent_mapping(cnved.get('____tag____'), cnved)
                return node
        
            def pyyaml_register_presenter(self, namespace=globals()):
                apathic_keys = ('__name__', '__doc__', '__package__', '__loader__', '__spec__',
                                '__annotations__', '__builtins__', '__module__', '__init__')
                if isinstance(namespace, dict):
                    glbs = {clskey: cls for clskey, cls in namespace.items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ str(cls.__name__) for key,cls in glbs.items() ]
                    for i_tag in tag_tbd:
                        self.pyyaml_dumper.add_representer(namespace.get(i_tag), intrinsic_formatter.pyyaml_extended_representer)
                else:            
                    glbs = {clskey: cls for clskey, cls in globals().items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ str(cls.__name__) for key,cls in glbs.items() ]
                    for i_tag in tag_tbd:
                        self.pyyaml_dumper.add_representer(globals()[i_tag], intrinsic_formatter.pyyaml_extended_representer)
        
            @classmethod
            def pyyaml_node_to_dict(cls, loader, node):
                if isinstance(node, yaml.nodes.SequenceNode):
                    ret = loader.construct_sequence(node)
                    for idx, sub_node in enumerate(node.value):
                        if isinstance(sub_node, yaml.nodes.CollectionNode):
                            ret[idx] = cls.pyyaml_node_to_dict(loader, sub_node)
                elif isinstance(node, yaml.nodes.MappingNode):
                    ret = loader.construct_mapping(node)
                    for sub_key, sub_node in node.value:
                        if isinstance(sub_node, yaml.nodes.CollectionNode):
                            ret[sub_key.value] = cls.pyyaml_node_to_dict(loader, sub_node)
                else:
                    ret = loader.construct_scalar(node)
                return ret
        
            @classmethod
            def pyyaml_extended_constructor(cls, loader, node, proc=None, namespace=globals()):
                deced = cls.pyyaml_node_to_dict(loader, node)
                obj = cls.decode(deced, proc=proc, namespace=namespace)
                return obj
        
            def pyyaml_register_constructor(self, namespace=globals()):
                apathic_keys = ('__name__', '__doc__', '__package__', '__loader__', '__spec__',
                                '__annotations__', '__builtins__', '__module__', '__init__')
                if namespace is None:
                    glbs = {clskey: cls for clskey, cls in globals().items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ '!!'+str(cls.__name__) for key,cls in glbs.items() ]
                elif isinstance(namespace, (list, tuple, set, frozenset)):
                    tag_tbd = namespace
                elif isinstance(namespace, dict):
                    glbs = {clskey: cls for clskey, cls in namespace.items()
                            if inspect.isclass(cls) and clskey not in apathic_keys }
                    tag_tbd = [ '!!'+str(cls.__name__) for key,cls in glbs.items() ]
                else:
                    tag_tbd = [ namespace ]
        
                for i_tag in tag_tbd:
                    self.pyyaml_loader.add_constructor(i_tag,
                                                       lambda l, n : intrinsic_formatter.pyyaml_extended_constructor(l, n,
                                                                                                                     proc=self.proc,
                                                                                                                     namespace=self.namespace))
        
            def pyyaml_register(self, namespace=globals()):
                self.pyyaml_register_constructor(namespace=namespace)
                self.pyyaml_register_presenter(namespace=namespace)
        
            class json_encoder(json.JSONEncoder):
                def default(self, obj):
                    ret = intrinsic_formatter.encode(obj)
                    if type(obj)!=type(ret):
                        return ret
                    return super().default(obj)
        
            @classmethod
            def dump_json_bulk(cls, obj, fp=None, skipkeys=False, ensure_ascii=True, check_circular=True, 
                               allow_nan=True, indent=None, separators=None, default=None, sort_keys=False, **kw):
        
                if fp is not None:
                    return json.dump(obj, fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                     allow_nan=allow_nan, cls=cls.json_encoder, indent=indent, separators=separators,
                                     default=default, sort_keys=sort_keys, **kw)
                else:
                    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                      allow_nan=allow_nan, cls=cls.json_encoder, indent=indent, separators=separators,
                                      default=default, sort_keys=sort_keys, **kw)
        
        
            def dump_json(self, obj, fp=None, skipkeys=False, ensure_ascii=False, check_circular=True, 
                          allow_nan=True, indent=4, separators=None, default=None, sort_keys=False, **kw):
                return self.dump_json_bulk(obj, fp=fp, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, 
                                           allow_nan=allow_nan, indent=indent, separators=separators, default=default, sort_keys=sort_keys, **kw)
        
            @classmethod
            def load_json_bulk(cls, obj, parse_float=None, parse_int=None,
                               parse_constant=None, object_pairs_hook=None, namespace=globals(), **kw):
                if isinstance(obj, io.IOBase):
                    return json.load(obj, object_hook=lambda x : cls.decode(x, namespace=namespace),
                                     parse_float=parse_float, parse_int=parse_int, 
                                     parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
                return json.loads(obj, object_hook=lambda x : cls.decode(x, namespace=namespace),
                                  parse_float=parse_float, parse_int=parse_int,
                                  parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, **kw)
        
            def load_json(self, obj, parse_float=None, parse_int=None,
                          parse_constant=None, object_pairs_hook=None, namespace=globals(), **kw):
                return self.load_json_bulk(obj=obj, parse_float=parse_float, parse_int=parse_int,
                                           parse_constant=parse_constant, object_pairs_hook=object_pairs_hook,
                                           namespace=self.namespace, **kw)
        
            def dump_yaml(self, obj, stream=None, default_style=None, default_flow_style=None, encoding=None,
                          #indent=None, explicit_start=None, explicit_end=None, canonical=None,
                          indent=4, explicit_start=True, explicit_end=True, canonical=True,
                          version=None, tags=None, width=None, allow_unicode=None, line_break=None):
                return yaml.dump(obj, stream=stream, Dumper=self.pyyaml_dumper, default_style=default_style,
                                 default_flow_style=default_flow_style, encoding=encoding, explicit_end=explicit_end,
                                 version=version, tags=tags, canonical=canonical, indent=indent, width=width,
                                 allow_unicode=allow_unicode, line_break=line_break)
        
            def load_yaml(self, obj):
                return yaml.load(obj, Loader=self.pyyaml_loader)
        
        if __name__ == '__main__':
            help(intrinsic_formatter)
                    
        ########## ____INTRINSIC_FORMATTER_TEMPLATE_END____ ##########

        #
        # Template data for module 
        #

        ########## ____BSD_3_CLAUSE_LICENSE_TEMPLATE_START____ ##########
        """
        BSD 3-Clause License
        
        Copyright (c) 2025, {____AUTHOR_NAME____}
        All rights reserved.
        
        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are met:
        
        1. Redistributions of source code must retain the above copyright notice, this
           list of conditions and the following disclaimer.
        
        2. Redistributions in binary form must reproduce the above copyright notice,
           this list of conditions and the following disclaimer in the documentation
           and/or other materials provided with the distribution.
        
        3. Neither the name of the copyright holder nor the names of its
           contributors may be used to endorse or promote products derived from
           this software without specific prior written permission.
        
        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
        AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
        IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
        FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
        DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
        SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
        CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
        OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """
        ########## ____BSD_3_CLAUSE_LICENSE_TEMPLATE_END____ ##########


        ########## ____MODULE_DIR_MAKEFILE_TEMPLATE_START____ ##########
        """
        PYTHON ?= python3
        PIP    ?= pip3
        
        MAKEFILE_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

        MODULE_NAME  ?= {____MODULE_NAME____}
        MODULE_SPATH ?= $(subst -,_,$(MODULE_NAME))
        
        PYTMPDIR ?= $(MAKEFILE_DIR)/var/lib/python
        
        REQUIERD_MODULES = build twine
        
        TWINE ?= $(PYTMPDIR)/bin/twine
        BUILD ?= $(PYTMPDIR)/build
        TOML ?= $(PYTMPDIR)/toml
        
        MOD_TEST_DIR_SRC  ?= $(MAKEFILE_DIR)/var/tmp/test_src
        MOD_TEST_DIR_DIST ?= $(MAKEFILE_DIR)/var/tmp/test_dist
        
        MOD_DEPENDENCIES := $(shell env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PYTHON) -c "import sys,toml;[sys.stdout.write(i) for i in toml.load('pyproject.toml').get('project')['dependencies']]")
        
        MOD_VERSION := $(shell env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PYTHON) -c "import sys,toml;sys.stdout.write(toml.load('pyproject.toml').get('project')['version'])")
        
        MOD_TEST_OPT = -h

        PYVERSTR       ?= $(shell $(PYTHON) -c 'import sys; sys.stdout.write(".".join([str(i) for i in sys.version_info[0:3]]))')
        LOCAL_DESTDIR  ?= $(MAKEFILE_DIR)/../../lib/python/site-packages/$(PYVERSTR)
        LOCAL_BINDIR   ?= $(MAKEFILE_DIR)/../../bin/
        PYENCASE       ?= {____PIP_MODULE_NAME____}
        
        .PHONY: info clean sdist test_src test_dist test_upload upload clean distclean install_local
        
        info:
        	@echo 'Module name         : '$(MODULE_NAME)
        	@echo 'Module short path   : '$(MODULE_SPATH)
        	@echo 'Module VERSION      : '$(MOD_VERSION)
        	@echo 'Module dependencies : '$(MOD_DEPENDENCIES)
        
        $(TWINE): 
        	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PIP) install --target $(PYTMPDIR) $(notdir $@)
        
        $(BUILD): 
        	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PIP) install --target $(PYTMPDIR) $(notdir $@)
        
        $(TOML):
        	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PIP) install --target $(PYTMPDIR) $(notdir $@)
        
        sdist:
        	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(PYTHON) -m build 
        
        test_src: $(MOD_TEST_DIR_SRC)
        	-env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_SRC) $(notdir $(MOD_DEPENDENCIES))
        	env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_SRC) $(MAKEFILE_DIR)
        	env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(MOD_TEST_DIR_SRC)/bin/$(MODULE_NAME) $(MOD_TEST_OPT)
        
        test_dist: $(MOD_TEST_DIR_DIST) $(MAKEFILE_DIR)/dist/$(MODULE_SPATH)-$(MOD_VERSION).tar.gz
        	-env PYTHONPATH=$(MOD_TEST_DIR_DIST):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_DIST) $(notdir $(MOD_DEPENDENCIES))
        	env PYTHONPATH=$(MOD_TEST_DIR_DIST):$(PYTHONPATH) $(PIP) install --target $(MOD_TEST_DIR_DIST) $(MAKEFILE_DIR)/dist/$(MODULE_SPATH)-$(MOD_VERSION).tar.gz
        	env PYTHONPATH=$(MOD_TEST_DIR_DIST):$(PYTHONPATH) $(MOD_TEST_DIR_DIST)/bin/$(MODULE_NAME) $(MOD_TEST_OPT)
        
        install_local: 
        	-mkdir -p $(LOCAL_DESTDIR)
        	-env PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(LOCAL_DESTDIR) $(notdir $(MOD_DEPENDENCIES))
        	env  PYTHONPATH=$(MOD_TEST_DIR_SRC):$(PYTHONPATH) $(PIP) install --target $(LOCAL_DESTDIR) $(MAKEFILE_DIR)
        	if [ -f $(LOCAL_BINDIR)/$(PYENCASE) ] ; then (cd $(LOCAL_BINDIR); ln -s $(PYENCASE) $(MODULE_NAME) ) ; fi

        $(MAKEFILE_DIR)/dist/$(MODULE_SPATH)-$(MOD_VERSION).tar.gz: sdist
        
        $(MOD_TEST_DIR_SRC):
        	mkdir -p $(MOD_TEST_DIR_SRC)
        
        $(MOD_TEST_DIR_DIST):
        	mkdir -p $(MOD_TEST_DIR_DIST)
        
        test_upload: $(TWINE) sdist
        	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(TWINE) upload --verbose --repository pypitest $(MAKEFILE_DIR)/dist/*
        
        upload: $(TWINE) sdist
        	env PYTHONPATH=$(PYTMPDIR):$(PYTHONPATH) $(TWINE) upload --verbose $(MAKEFILE_DIR)/dist/*
        
        clean: 
        	rm -rf $(MAKEFILE_DIR)/src/$(MODULE_SPATH)/*~ \
                       $(MAKEFILE_DIR)/src/$(MODULE_SPATH)/__pycache__ \
                       $(MAKEFILE_DIR)/src/$(MODULE_SPATH)/share/data/*~ \
                       $(MAKEFILE_DIR)/dist/* \
                       $(MAKEFILE_DIR)/build/* \
                       $(MAKEFILE_DIR)/var/lib/python/* \
                       $(MAKEFILE_DIR)/*~  \
                       $(MAKEFILE_DIR)/test/*~ 
        
        distclean: clean
        	rm -rf $(MAKEFILE_DIR)/$(MODULE_SPATH).egg-info \
                       $(MAKEFILE_DIR)/dist \
                       $(MAKEFILE_DIR)/build \
                       $(MAKEFILE_DIR)/lib \
                       $(MAKEFILE_DIR)/var
        """
        ########## ____MODULE_DIR_MAKEFILE_TEMPLATE_END____ ##########

        ########## ____MODULE_PYPROJECT_TOML_TEMPLATE_START____ ##########
        '''
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"
        
        [project]
        name = "{____MODULE_NAME____}"
        version = "0.0.1"
        description = {____MODULE_DESC_QUOTE____}
        dependencies = [{____MODULE_REQUIREMENTS____}]
        readme = "{____README_NAME____}"
        #requires-python = ">=3.9"
        
        license = {{ file = "LICENSE" }}
        #license-files = ["LICEN[CS]E*", "vendored/licenses/*.txt", "AUTHORS.md"]
        
        keywords = [{____MODULE_KEYWORDS____}]
        
        authors = [{____MODULE_AUTHOR_LIST____}]
                   
        maintainers = [{____MODULE_MAINTAINERS_LIST____}]
                   
        
        classifiers = [{____MODULE_CLASSIFIER_LIST____}]
        
        [project.urls]
        Homepage = {____MODULE_HOMEPAGE_URL_QUOTE____}
        
        [project.scripts]
        {____MODULE_NAME____} = "{____MODULE_SHORT_PATH____}.{____MODULE_SHORT_PATH____}:main"
        
        '''
        ########## ____MODULE_PYPROJECT_TOML_TEMPLATE_END____ ##########

        ########## ____MODULE_README_MD_TEMPLATE_START____ ##########
        """
        # {____MODULE_NAME____}
        
        {____MODULE_DESC____}
        
        ## Requirement
        
        - Python: tested with version 3.X
        
        ## Usage
        
        - To be written
        
        ## Author
         {____MODULE_AUTHOR_LIST_TEXT____}
        """
        ########## ____MODULE_README_MD_TEMPLATE_END____ ##########

        ########## ____MODULE_DOT_GITIGNORE_TEMPLATE_START____ ##########
        '''
        # Byte-compiled / optimized / DLL files
        __pycache__/
        *.py[codz]
        *$py.class
        
        # C extensions
        *.so
        
        # Distribution / packaging
        .Python
        build/
        develop-eggs/
        dist/
        downloads/
        eggs/
        .eggs/
        lib/
        lib64/
        parts/
        sdist/
        var/
        wheels/
        share/python-wheels/
        *.egg-info/
        .installed.cfg
        *.egg
        MANIFEST
        
        # Flask stuff:
        instance/
        .webassets-cache
        
        # Scrapy stuff:
        .scrapy
        
        # PyBuilder
        .pybuilder/
        target/
        
        # IPython
        profile_default/
        ipython_config.py
        
        # PyPI configuration file
        .pypirc
        
        # This module build
        !{____GIT_DUMMYFILE____}
        '''
        ########## ____MODULE_DOT_GITIGNORE_TEMPLATE_END____ ##########

        ########## ____MODULE_SRC_INIT_PY_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8 -*-
        
        from .____MODULE_SHORT_PATH____ import ____MODULE_CLS_NAME____
        
        __copyright__    = 'Copyright (c) ____MODULE_CREATE_YEAR____, ____AUTHOR_NAME____'
        __version__      = ____MODULE_CLS_NAME____.VERSION
        __license__      = 'BSD-3-Clause'
        __author__       = '____AUTHOR_NAME____'
        __author_email__ = '____AUTHOR_EMAIL____'
        __url__          = ____MODULE_HOMEPAGE_URL_QUOTE____
        
        __all__ = ['____MODULE_CLS_NAME____', ]
        ########## ____MODULE_SRC_INIT_PY_TEMPLATE_END____ ##########

        ########## ____MODULE_SRC_MODULE_NAME_PY_TEMPLATE_START____ ##########
        #### ____py_shebang_pattern____ ####
        # -*- coding: utf-8; mode: python; -*-
        """
        ____MODULE_DESC____
        """
        import json
                
        class ____MODULE_CLS_NAME____(object):
            """
            ____MODULE_CLS_NAME____
            ____MODULE_DESC____
            """

            VERSION = "0.0.1"

            def __init__(self):
                self.contents = {}  
                
            def __repr__(self):
                return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
                
            def __str__(self):
                return json.dumps(self.contents, ensure_ascii=False, indent=4, sort_keys=True)
        
        def main():
            help(____MODULE_CLS_NAME____)
                
        if __name__ == '__main__':
            main()
        ########## ____MODULE_SRC_MODULE_NAME_PY_TEMPLATE_END____ ##########
