# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                PlugIn Module - Classes and Functions         %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Imports all utility features provided by and for 3rd party packages.
 
@note: PyXMake plug-in manager       
Created on 22.08.2022   

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os, sys
import signal
import warnings

## @package PyXMake.Plugin
# Imports additional features provided by and for 3rd party packages.
## @author 
# Marc Garbade
## @date
# 22.08.2022
## @par Notes/Changes
# - Added documentation // mg 22.08.2022

try:
    ## These imports are mandatory when using with poetry.
    # It can be safely ignored in all other cases
    from .__poetry import build as build
    from .__poetry import Plugin as RuntimePlugin
    from .__poetry import ApplicationPlugin as ApplicationPlugin

    ## This block is only meaningful when poetry is installed and a 
    # custom build command is requested. 
    from .__build import build as bdist_wheel
    from .__gitlab import check as check
    
    ## Provide a custom error handler for the interruption event
    # triggered by this wrapper to prevent multiple wheels from being
    # created. Only affects exit codes when using CI runners
    with warnings.catch_warnings(): #@UndefinedVariable
        warnings.simplefilter("ignore") #@UndefinedVariable
        ## Check system information. 
        # Only required on MacOS and Linux
        if not getattr(signal,"CTRL_C_EVENT",None): 
            signal.signal(signal.SIGINT, lambda *args: sys.exit(0))
            signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    # Ignore import or module not found errors.
except ImportError: pass

## Added option to increase the default recursion limit through an environment variable.
# The given default limit is never used in practice, but gives viewers an idea of the limit range.
if os.getenv("pyx_recursion_limit",""): sys.setrecursionlimit(int(os.getenv("pyx_recursion_limit",5000)))

# Save the current PID. This value is used to kill the parent process runing poetry when the wheel is build from within this script.
if not os.getenv("pyx_poetry_main_pid",""):
    # Backwards compatibility. Function n/a in Python 2.7
    try: os.environ["pyx_poetry_main_pid"] = str(os.getpid())
    except AttributeError: pass

def main():
    """
    This is the main entry point. Acts as a compatibility shim for poetry.
    """
    result = -1
    # Provide a shim to poetry
    try: from poetry.console.application import main
    except ImportError: from poetry.console import main
    from packaging import version
    # Print debugging info
    if sys.argv[1] in ["debug"]:
        # Print debugging information indicating that poetry executable has been modified.
        print('==================================')
        print('Running poetry with PyXMake plugin')
        print('==================================')
    # Execute build function when creating a platform python wheel. Only meaningful for legacy python versions.
    if sys.argv[1] in ["build"] and version.parse(".".join([str(x) for x in sys.version_info[:2]])) < version.parse("3.7"): build()
    # Return poetry application.
    try: result = main()
    except Exception as e: #@UnusedVariable
        ## Perform operation check. Exception is only acceptable when running 
        # platform independent builds with mandatory compilation task
        if sys.argv[1] in ["build"]: result = 0
    # Always return
    return result

if __name__ == '__main__':
    main(); sys.exit()
    pass