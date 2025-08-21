# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %            Build wrapper module - Classes and functions      %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Build configuration and management assistance wrapper.
 
@note: 
Created on 03.02.2024

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

import os, sys, re
import subprocess
import signal
import site
import glob
import packaging.tags

from distutils import log, util
from setuptools import find_packages #@UnresolvedImport

def build(*args, **kwargs):
    """
    Shim interface for python wheel setup
    """
    # All local imports
    from setuptools.command.build_py import build_py as _build_py #@UnresolvedImport
    from setuptools.command.egg_info import egg_info as _egg_info
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class build_py(_build_py):
        """
        Compatibility shim for build_py
        """
        def initialize_options(self):
            """
            Shim interface for all options
            """
            # Execute original class method
            _build_py.initialize_options(self)
            
            # Update class attributes with user settings
            try: 
                wc = self.get_finalized_command("bdist_wheel", 0)
                self.exclude_source_files = wc and wc.exclude_source_files
                self.bdist_wheel = True
            except: 
                self.bdist_wheel = False
                self.exclude_source_files = False

        def finalize_options(self):
            """
            Shim interface to finalize all inputs
            """
            # User requests to remove all source files (and create a meta package)
            if self.exclude_source_files:
                self.force = 1
                self.compile = 1
            # Execute original class method
            _build_py.finalize_options(self)

        def byte_compile(self, files):
            """
            Shim interface for class attribute byte_compile
            """
            # User requests to remove all source files (and create a meta package)
            if self.exclude_source_files:
                for file in files:
                    if os.path.isfile(file):
                        try: 
                            os.unlink(file)
                            log.info('removing source file %s', file)
                        except: pass
            # Execute original class method. Only if required and source files are included
            else: _build_py.byte_compile(self, files)
                        
        def run(self):
            """
            Shim interface to execute the process
            """
            if not self.bdist_wheel and not self.exclude_source_files:
                command = [sys.executable,"setup.py","bdist_wheel"]
                if kwargs.get("platform_tag",False): command.append("--platform-tag")
                if kwargs.get("exclude_source_files",False): command.append("--exclude-source-files")
                # Execute a new subprocess
                subprocess.check_call(command)
                return
            # Execute original class method. 
            _build_py.run(self)
            
    class bdist_wheel(_bdist_wheel):
        """
        Compatibility shim for bdist_wheel
        """
        # Update default user settings
        _bdist_wheel.user_options.append(('exclude-source-files', None, "Remove all .py files from the generated wheel")) #@UndefinedVariable
        _bdist_wheel.user_options.append(('abi-tag', None, "Add a non-default abi-tag")) #@UndefinedVariable
        _bdist_wheel.user_options.append(('platform-tag', None, "Enforce the creation of a platform-tag")) #@UndefinedVariable

        def initialize_options(self):
            """
            Shim interface for all options
            """
            # Execute original class method
            _bdist_wheel.initialize_options(self) #@UndefinedVariable
            # Update default settings
            self.abi_tag = None
            self.python_tag = None
            self.platform_tag = False
            self.exclude_source_files = False

        def finalize_options(self):
            """
            Shim interface to finalize all inputs
            """
            # Execute original class method
            _bdist_wheel.finalize_options(self) #@UndefinedVariable
            # Read python tag from user input
            self.python_tag = kwargs.get("python_tag", "py2.py3")
            # If no python tag is given - create a pure wheel
            if str(self.python_tag).lower() in [None,"py2.py3"]: self.root_is_pure = True
            # All other cases
            else: self.root_is_pure = False
            
        def run(self):
            """
            Shim interface to execute the process
            """
            # Execute original class method
            _bdist_wheel.run(self) #@UndefinedVariable
            
            # Update wheel tags
            if any([not self.root_is_pure,self.platform_tag]):
                # Gather system and platform information
                sys_tags = next(packaging.tags.sys_tags()) #@UndefinedVariable
                python_tag = sys_tags.interpreter if not str(self.python_tag).lower().startswith("p") else self.python_tag
                # Only add abi tag when a non pure python wheel is created
                abi_tag = sys_tags.abi if not self.root_is_pure and not python_tag.startswith("p") else "none"
                # Use the current platform to update the wheel
                platform_tag = re.sub(r'[^0-9a-zA-Z]+','_', util.get_platform()) if self.platform_tag else "any"
                build_wheel = [os.path.join(os.getcwd(),"dist",x) for x in os.listdir(os.path.join(os.getcwd(),"dist")) if x.endswith(".whl")][-1]
                subprocess.check_call([sys.executable,"-m","wheel","tags","--abi-tag",abi_tag,"--python-tag",python_tag,"--platform-tag", platform_tag, build_wheel])
                # Remove the outdated wheel. Only when changes were made
                if len(os.listdir(os.path.join(os.getcwd(),"dist"))) > 1: 
                    os.remove(os.path.join(os.getcwd(),"dist",build_wheel))
                
            # We created a wheel using user-defined settings. Kill the main process
            if os.getenv("pyx_poetry_main_pid",""):
                try: 
                    os.remove(os.path.join(os.getcwd(),"setup.py"))
                    # Delete all temporary path files before shutting down the process
                    for pthpath in glob.iglob(os.path.join(site.getusersitepackages(), '*.pth')): 
                        os.remove(pthpath)
                    # Kill the parent process
                    os.kill(int(os.getenv("pyx_poetry_main_pid")), getattr(signal,"CTRL_C_EVENT",signal.SIGTERM))
                except: pass

    class egg_info(_egg_info):
        """
        Compatibility shim for egg_info
        """
        def run(self):
            """
            Shim interface to execute the process
            """
            # Execute original class method
            _egg_info.run(self)
                        
            # Get rid of top_level.txt if it was put in there
            nl = os.path.join(self.egg_info, "top_level.txt")
            if os.path.exists(nl): self.delete_file(nl)

    # Parse settings from poetry when a setup file is generated
    if args: settings = args[-1]

    # Update these settings
    settings.update({"setup_requires":['wheel>=0.30;python_version>="2.7"', 'wheel==0.29;python_version<"2.7"'],
                     "cmdclass":{"bdist_wheel": bdist_wheel, "build_py": build_py, "egg_info": egg_info}})

    try: 
        from poetry.console.application import Application #@UnresolvedImport
        configuration = Application().poetry.local_config
    except (ImportError, RuntimeError) as _: configuration = {}

    # Detect reStructured Text or Markdown based on the the file extension 
    description = configuration.get("readme",[])
    # Only attempt to execute this statement if a readme file is given
    if ((isinstance(description,str) and description.endswith(".md")) or 
        any(x.endswith(".md") for x in description)):
        settings.update({"long_description_content_type":"text/markdown"})
    # Set a default value
    else: settings.update({"long_description_content_type":"text/x-rst"})

    # Loop over all poetry exclusive keys to reconstruct all metadata information
    include_keys = ["classifiers","keywords","urls","repository","documentation"]
    settings.update({k: v for k, v in configuration.items() if k in include_keys})
    # Merge all urls
    urls = settings.pop("urls",{});
    urls.update({k.title(): v for k, v in settings.items() if k in ["repository","documentation"]})
    _ = [settings.pop(k,None) for k in ["repository","documentation"]]
    # Update all settings
    settings.update({"project_urls":urls})

    # Remove all unsupported options and update settings with kwargs
    exclude_keys = ["abi_tag","python_tag","platform_tag","exclude_source_files"]
    settings.update({k: kwargs[k] for k in set(list(kwargs.keys())) - set(exclude_keys)})

    try: 
        # Verify that the maintainer tag is correctly set
        if settings.get("maintainer","") and settings.get("maintainer","") in ["None"]:
            settings.pop("maintainer"); settings.pop("maintainer_email")
    except: pass
    
    # When a meta package is created - remove all modules from the package
    try:
        # Always remove modules entry
        modules = settings.pop("py_modules","")
        ## Source code should be added. Use setuptools to find all packages and
        # update package data to automatically add all files within the package directory. 
        if not kwargs.get("exclude_source_files",False):
            # Collect all packages on the fly
            settings.update({"packages":[next(iter(find_packages(path))) for _, path in settings["package_dir"].items()]})
            # Collect all associated package data. We use everything here.
            settings.update({"package_data":{x:["**/*"] for x in settings["packages"]}})
            # Check if modules actually contains meaningful data. If True, readd everything
            if modules and next(iter(modules)) not in ["__init__"]: settings.update({"py_modules":modules})
    except: pass
   
    ## Save the parent PID. Deprecated and kept here for legacy support. The PID should be already captured here.
    # This value is used to kill the parent process runing poetry when the wheel is build from within this script.
    if not os.getenv("pyx_poetry_main_pid",""): os.environ["pyx_poetry_main_pid"] = str(os.getppid())
    
    # Return nothing.
    pass
    
if __name__ == "__main__":
    pass