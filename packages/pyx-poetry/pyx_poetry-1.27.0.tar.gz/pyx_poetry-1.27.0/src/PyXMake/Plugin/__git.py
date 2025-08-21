# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %            GIT wrapper module - Classes and functions        %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
GIT configuration and management assistance wrapper.
 
@note: 
Created on 08.08.2022

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os
import sys
import git
import shlex
import argparse
import subprocess

try: from urllib.parse import urlparse #@UnusedImport
except: from urlparse import urlparse #@UnresolvedImport @Reimport

def setup():
    """
    GIT configuration helper interface 
    """
    # All variables
    __commands = []
    __settings_check = [os.getenv("GIT_USER",""), os.getenv("GIT_PASSWORD","")]
    # Check if the current path is a GIT repository
    if os.path.exists(".git"):
        # Do not execute configuration more than once
        if os.path.exists(os.path.expanduser("~/.gitconfig_old")): return
        # Reset all settings
        with open(os.path.expanduser("~/.gitconfig"), mode='a'): pass
        os.replace(os.path.expanduser("~/.gitconfig"),os.path.expanduser("~/.gitconfig_old"))
        # Define all commands
        __commands = ["git config --global pull.ff only", 
                      "git config --global http.sslverify false",
                      "git config --global core.ignorecase false",
                      "git config --global credential.helper %s" % ("wincred" if os.name.lower() in ["nt"] else "cache",)]
        # Add user credentials (if available)
        if all(__settings_check):
            __commands.extend(['git config --global user.name "%s"' % os.getenv("GIT_USER"),
                               'git config --global user.password "%s"' % os.getenv("GIT_PASSWORD")])
            # We are running this script within a GitLab runner.
            __settings_check.extend([os.getenv("CI_SERVER_URL","")])
        # Check if script is executed within a GitLab runner.
        if len(__settings_check) > 2 and all(__settings_check):
            __commands.extend(['git config --global url."%s://%s:%s@%s/".insteadOf "%s/"' % (
                      str(urlparse(os.getenv("CI_SERVER_URL")).scheme),
                      os.getenv("GIT_USER"), os.getenv("GIT_PASSWORD"), 
                      str(urlparse(os.getenv("CI_SERVER_URL")).netloc), 
                      os.getenv("CI_SERVER_URL"), )])
            # Only execute this part on Linux
            if not os.name.lower() in ["nt"]: 
                # Verify that LFS support is enabled. 
                for x in ["apt-get update","apt-get install -y git-lfs"][::-1]: __commands.insert(0,x)      
    # Execute all commands
    for command in __commands: 
        subprocess.call(shlex.split(command,posix=not os.name.lower() in ["nt"]),stderr=sys.stderr, stdout=sys.stdout)
    pass
    
def update():
    """
    GIT pull command with recursive submodule and LFS support
    """
    # All variables
    __commands = []
    __settings_check = [ os.getenv("GIT_USER",""), os.getenv("GIT_PASSWORD",""), os.getenv("CI_SERVER_URL","") ]
    # Execute GIT configuration function
    if not os.path.exists("~/.gitconfig_old"): setup()
    # Check if the current path is a GIT repository
    if os.path.exists(".git"):
        __commands = ["git lfs install","git submodule sync --recursive"]
        # Check if script is executed within a GitLab runner.
        if all(__settings_check):
            __commands.extend(["""git submodule foreach --recursive 'git config --local url."%s://%s:%s@%s/".insteadOf "%s/"'""" % (
                      str(urlparse(os.getenv("CI_SERVER_URL")).scheme),
                      os.getenv("GIT_USER"), os.getenv("GIT_PASSWORD"), 
                      str(urlparse(os.getenv("CI_SERVER_URL")).netloc), 
                      os.getenv("CI_SERVER_URL"), )]) 
        # Execute all checkout commands
        for command in __commands: 
            subprocess.call(shlex.split(command,posix=not os.name.lower() in ["nt"]),stderr=sys.stderr, stdout=sys.stdout) 
        # Pull latest revision for each submodule
        g = git.Repo(os.getcwd())
        # Try to catch the current active branch
        try: branch = str(g.active_branch.name)
        except: branch = "HEAD"
        # Also pull latest changes in the main directory.
        g.git.pull("origin",branch)
        # Also pull latest changes in the main directory.
        g.git.pull("origin",branch)
        # Solving dependencies w/o detached head.
        try: g.git.submodule('update', '--init', "--recursive")
        # Fail gracefully, which happens when all submodules are already initiased.
        except: pass
        # Fixing detached head during recursive dependency resolving.  
        try: g.git.submodule('update', '--init', "--recursive","--remote")
        except: pass
        finally: g.git.submodule('foreach','--recursive',"git pull origin $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master) || git pull origin main")
    # Download all LFS data blobs
    try: os.replace(os.path.expanduser("~/.gitconfig"),os.path.expanduser("~/.gitlfs"))
    except: pass
    # Use credential helper for backwards compatibility.
    if all(__settings_check) and any(__commands): 
        cache = """-c credential.helper='!f() { sleep 1; echo "username=%s"; echo "password=%s"; }; f'""" % (os.getenv("GIT_USER"),os.getenv("GIT_PASSWORD"),)
    else: cache = ""
    try: g.git.submodule('foreach','--recursive',"git %s lfs pull" % cache)
    except: pass
    try:
        # Has no effect on NT systems
        os.replace(os.path.expanduser("~/.gitlfs"),os.path.expanduser("~/.gitconfig"))
        os.replace(os.path.expanduser("~/.gitconfig_old"),os.path.expanduser("~/.gitconfig"))
        # Configuration file is empty.
        if os.stat( os.path.expanduser("~/.gitconfig") ).st_size == 0: os.remove(os.path.expanduser("~/.gitconfig"))
    except: pass
    pass
    
def main(**kwargs):
    """
    Main command line parser.
    """
    if not kwargs.get("method",""): 
        parser = argparse.ArgumentParser(description='CLI wrapper options for GIT.')
        parser.add_argument('method', metavar='option', type=str, nargs=1, 
            help='An option identifier. Either <setup> or <update>. All other CLI arguments are directly parsed to GIT.')
        # Select method
        args, _ = parser.parse_known_args()
        method = str(args.method[0])
    else: method = kwargs.get("method")
    # Execute wrapper within this script or parse the command to git
    command = " ".join(["git"] + sys.argv[1:])
    # Internal command shall always take precedence
    if not method in globals() or ( len(sys.argv[1:]) > 1 and not method in globals() ): 
        subprocess.call(shlex.split(command,posix=not os.name.lower() in ["nt"]),stderr=sys.stderr, stdout=sys.stdout)
    else: globals()[method]()
    pass

if __name__ == "__main__":
    pass
