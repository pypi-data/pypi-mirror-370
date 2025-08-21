# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %            Poetry wrapper module - Classes and functions     %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Poetry configuration and management assistance wrapper.
 
@note: 
Created on 09.08.2022

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""
import os
import copy
import ast
import sys
import site
import shlex
import tomlkit
import argparse
import importlib
import subprocess
import logging
import platform
import posixpath
import ntpath

from packaging.version import parse

# Legacy support to build platform packages for Python 2.7 and below
try: 
    from cleo.io.io import IO #@UnusedImport
    from cleo.commands.command import Command as _Command #@UnusedImport
except:
    from builtins import object as IO #@UnusedImport @Reimport
    from builtins import object as _Command #@UnusedImport @Reimport

# Support custom events
try: from cleo.events.console_events import COMMAND as _COMMAND #@UnusedImport 
except: from builtins import object as _COMMAND #@UnusedImport @Reimport

try: 
    from poetry.plugins.plugin import Plugin as _Plugin #@UnresolvedImport @UnusedImport
    from poetry.plugins.application_plugin import ApplicationPlugin as _ApplicationPlugin #@UnresolvedImport #@UnusedImport
except: 
    from builtins import object as _Plugin #@Reimport
    from builtins import object as _ApplicationPlugin #@Reimport

try:
    # Import core version of poetry. Deprecated
    from poetry.core.semver.version import Version as PoetryCoreVersion #@UnresolvedImport #@UnusedImport
except:
    # Import core version of poetry in version above 1.6+
    from poetry.core.constraints.version import Version as PoetryCoreVersion #@UnresolvedImport @Reimport

from packaging.utils import canonicalize_name

from poetry.poetry import Poetry #@UnresolvedImport
from poetry.utils._compat import metadata #@UnresolvedImport
from poetry.repositories.installed_repository import InstalledRepository #@UnresolvedImport

from .__git import main as _cli_git
from .__gitlab import main as _cli_gitlab

logger = logging.getLogger(__name__)

class Plugin(_Plugin):
    """
    Poetry plugin interface 
    """
    def activate(self, poetry, io):
        # type: (Poetry, IO) -> None
        """
        Poetry plugin execution interface.
        """
        # Get current work directory.
        cwd = os.getcwd()
        ## Only apply this method when installing or building locally.
        # Also skip rest of routine when root is explicitly excluded.
        if not sys.argv[1] in ["build","install","version"] or "--no-root" in sys.argv: return
        # Jump into directory of toml file.
        os.chdir(os.path.dirname(str(poetry.file)))
        # Create base command for subshell execution 
        command = " ".join([sys.executable,"-c",'"from PyXMake.Plugin.__poetry import setup; setup(silent_install=False)"'])
        # Only during install command.
        if sys.argv[1] in ["install"]: 
            # Use direct call on POSIX systems only.
            if not os.name.lower() in ["nt"]: setup(silent_install=False)
            else: subprocess.check_call(command, shell=True)
        # Obtain all relevant information about this project.
        project = poetry.local_config.get("name")
        packages = poetry.local_config.get("packages")
        # Auto-detect project name and package location, adding support for all POSIX systems.
        if not packages: 
            if not os.path.exists("src"): poetry._package.packages = [{"include":str(project)}] 
            else: poetry._package.packages = [{"include":str(project), "from":"src"}]
        ## When using PyXMake with the dynamic versioning plugin, this code snippets results in an error.
        # Since this part also only handles dynamic versioning, we rely on the other plugin and continue w/o error.
        try: dynamic_versioning_handle = parse(poetry.local_config.get("version",""))
        except: dynamic_versioning_handle = parse("0.0.0")
        # Check for dynamic version support during development
        if dynamic_versioning_handle == parse("0.0.0dev") and len(poetry._package.packages) == 1:
            # Get the correct internal project name
            project = poetry._package.packages[0].get("include")
            # Deal with nested include statements in the main package definition
            project = str(project).split(posixpath.sep)[0]
            # Add the current project temporarily to the PYTHONPATH
            try: sys.modules.pop(str(project))
            except: pass
            # Current project path takes precedence above all other paths
            sys.path.insert(0,
                os.path.normpath(
                os.path.join(os.path.abspath(os.getcwd()),
                poetry._package.packages[0].get("from",""))))
            # Import programmatically
            try: 
                importlib.import_module(str(poetry.local_config.get("name")))
                project = poetry.local_config.get("name")
            except: importlib.import_module(str(project))
            finally: handle = sys.modules[str(project)]
            # Remove the path from the overall system path
            sys.path.pop(0); sys.modules.pop(str(project)) 
            version = getattr(handle,"__version__","")
            version = version or poetry.local_config.get("version")
            # Do not add dev suffix when building the package.
            if not sys.argv[1] in ["build","version"]: version += "dev"
            poetry._package._version = PoetryCoreVersion.parse(version)
            poetry._package._pretty_version = version
        # Only during install and build command.
        settings = {"packages":copy.deepcopy(poetry._package.packages)}
        # Has no meanningful effect when no build script is given.
        if sys.argv[1] in ["install","build"]: build(**settings)
        # Jump back to initial working directory
        os.chdir(cwd)
        pass
        
class ApplicationPlugin(_ApplicationPlugin):
    """
    Poetry application plugin interface 
    """
    class Command(_Command):
        """
        Poetry application command interface 
        """
        # Fully qualified names of the command (default)
        name = "housekeeping"
        # Additional supported commands
        supported = ["housekeeping", "release"]
        def handle(self): _cli_gitlab(method=self.name)
        @classmethod
        def factory(cls): return cls()
        
    def run(self, application):
        """
        Poetry application command line interface
        """
        try:
            from PyXMake.Tools import Utility #@UnusedImport
            scripts = {"poetry-auto-cli":"default"};
        except ImportError: scripts = {}
        # Default variables
        result = -1
        scripts.update(application.poetry.local_config.get("scripts",{}))
        scripts = scripts.keys();
        # Check if a valid configuration can be fetched from the supplied TOML file. Defaults to False.
        toml = str(application.poetry.file)
        # Scan the TOML file for potential supported candidates. False positives are handled later.
        configuration = list(tomlkit.parse(open(toml).read())["tool"].keys())
        configuration += list(tomlkit.parse(open(toml).read())["tool"].get("pyxmake",{}).keys())
        # Remove duplicate entries from the list
        configuration = list(set(configuration))
        # Only execute this command when first trailing parameter does not start with a dash
        if len(sys.argv) >= 3 and not sys.argv[2].startswith("-") and not any([x in sys.argv for x in scripts]):
            # Fetch all possible shims
            commands = [" ".join([x] + sys.argv[2:]) for x in scripts]
            for command in commands:
                try:
                    ## Check if a valid configuration is present in the local toml file. 
                    # Parse its path if true.
                    if sys.argv[2] in configuration: os.environ["pyx_poetry_config"] = toml
                    # Try if a shim works. Fail gracefully.
                    result = subprocess.check_call(command, stderr=sys.stderr, stdout=sys.stdout, shell=True); 
                    if result == 0: break
                # Ignore all erros here. 
                except Exception: pass
        # The command was executed sucessfully. Terminate the process.
        if result == 0: sys.exit()
        pass

    def events(self, *args, **kwargs):
        """
        Poetry application events dispatcher interface
        """
        # Local variables
        handles = ()
        delimn = ntpath.pathsep
        # Get the correct internal installed package name
        try: 
            handles = ( str(self._application.poetry._package.packages[0].get("from","")), 
                                 str(self._application.poetry._package.packages[0].get("include")).split(posixpath.sep)[0] )
        except: pass
        # Create a prebuild event and execute it
        if sys.argv[1] in ["build"] and handles:
            # Default prebuild event
            script = r"""
                import os;import sys;
                sys.path.insert(0,os.path.normpath(os.path.join(os.path.abspath(os.getcwd()),'%s')));
                setattr(sys,'frozen',False);
                import %s;
                """ % handles
            script = delimn.join(x.strip() for x in script.split(delimn))
            # We are trying to import the package in a new shell
            command = " ".join([sys.executable,"-c",'"%s"' % script])
            # Try to execute prebuild command
            try: subprocess.check_call(command, stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), shell=True)
            except: pass # Fail gracefully
        pass

    def activate(self, application):
        """
        Poetry application registration interface
        """
        try: 
            # Verify that the current virtual environment can be accessed.
            output, _ = subprocess.Popen(["poetry","env","info","-p","--no-plugins"], stdout=subprocess.PIPE).communicate(); path = output.decode().strip();
            os.environ["PATH"] = os.pathsep.join([os.path.join(path,x) for x in next(os.walk(path))[1] if x not in os.getenv("PATH","")] + [os.getenv("PATH","")])
        except: pass
        # Provide a handle to application for child classes
        self._application = application
        # Always try to add custom events to dispatcher
        try: application.event_dispatcher.add_listener(_COMMAND, self.events)
        except: pass
        # Check if the command can be shimmed
        if sys.argv[1] in ["run"]: self.run(application)
        # Check if the given CLI options is supported.
        if sys.argv[1] in self.Command.supported: setattr(self.Command,"name",str(sys.argv[1]))
        # Register CLI command.
        if hasattr(self.Command,"name"): application.command_loader.register_factory(self.Command.name, self.Command.factory)
        pass

@classmethod
def load(cls, env=None, with_dependencies=False):
    """
    Load installed packages.
    """
    from pathlib import Path
    
    from poetry.utils.env import Env as sys_env #@UnresolvedImport
    from poetry.core.packages.dependency import Dependency #@UnresolvedImport
    
    from dulwich.errors import NotGitRepository

    repo = cls()
    seen = set()
    skipped = set()
    
    if not env: env = sys_env
    for entry in reversed(env.sys_path):
        if not entry.strip():
            logger.debug(
                "Project environment contains an empty path in <c1>sys_path</>,"
                " ignoring."
            )
            continue

        for distribution in sorted(
            metadata.distributions(path=[entry]),
            key=lambda d: str(d._path),  # type: ignore[attr-defined]
        ):
            path = Path(str(distribution._path))  # type: ignore[attr-defined]

            if path in skipped:
                continue

            name = distribution.metadata.get("name")  # type: ignore[attr-defined]
            if name is None:
                logger.warning(
                    (
                        "Project environment contains an invalid distribution"
                        " (<c1>%s</>). Consider removing it manually or recreate"
                        " the environment."
                    ),
                    path,
                )
                skipped.add(path)
                continue

            name = canonicalize_name(name)

            if name in seen:
                continue

            try: package = cls.create_package_from_distribution(distribution, env)
            except NotGitRepository: continue 

            if with_dependencies:
                for require in distribution.metadata.get_all("requires-dist", []):
                    dep = Dependency.create_from_pep_508(require)
                    package.add_dependency(dep)

            seen.add(package.name)
            repo.add_package(package)

    return repo

@classmethod
def install(cls, path, hash_, size):
    # type: (str, str, str) -> "RecordEntry"
    r"""
    Build a RecordEntry object, from values of the elements.

    Typical usage::

        for row in parse_record_file(f):
            record = RecordEntry.from_elements(row[0], row[1], row[2])

    Meaning of each element is specified in :pep:`376`.

    :param path: first element (file's path)
    :param hash\_: second element (hash of the file's contents)
    :param size: third element (file's size in bytes)
    :raises InvalidRecordEntry: if any element is invalid
    """
    from typing import Optional #@UnusedImport @UnresolvedImport
    from installer.records import Hash, InvalidRecordEntry
    # Validate the passed values.
    issues = []
    # Path can be empty
    if not path.strip():
        issues.append("`path` cannot be empty")
    # Hash can be empty
    if hash_.strip():
        try:
            hash_value = Hash.parse(hash_)  # type: Optional[Hash]
        except ValueError:
            issues.append("`hash` does not follow the required format")
    else:
        hash_value = None
    # Size can be empty
    if size.strip():
        try:
            size_value = int(size) # type: Optional[int]
        except ValueError:
            issues.append("`size` cannot be non-integer")
    else:
        size_value = None
    # Issues must be empty. Otherwise the installation process using poetry fails.
    if issues:
        raise InvalidRecordEntry(elements=(path, hash_, size), issues=issues)
    # Return the class
    return cls(path=path, hash_=hash_value, size=size_value)

def setup(**kwargs):
    """
    Poetry installation helper interface 
    """
    # Bring everything up-to-date
    if not kwargs.get("silent_install",True): _cli_git(method="update")
    # Check if the current path supports Poetry
    if os.path.exists("pyproject.toml") and kwargs.get("silent_install",True):
        with open("pyproject.toml", "r") as f: content = f.readlines()
        project = [line.split("=")[-1].strip() for line in content if line.split("=")[0].strip() in ["name"]][0]
        packages = [line for line in content if line.split("=")[0].strip() in ["packages"]]
        # Script relies on auto-detect, which will fail on all POSIX systems.
        if not packages:
            # Rename old configuration file
            os.replace("pyproject.toml","pyproject_old.toml")
            with open("pyproject.toml", "w") as f:
                # Copy content of old configuration file
                for line in content: 
                    f.write(line)
                    # Add non PEP8 project name explicitly
                    if all([x in line for x in ["name",project]]):
                        # Check for layouts. 
                        if not os.path.exists("src"): f.write('packages = [{include=%s}]\n' % str(project))
                        else: f.write('packages = [{include=%s, from="src"}]\n' % str(project))
        # Install the project regardless of change using the supplied TOML file
        subprocess.call(shlex.split("poetry install", posix=not os.name.lower() in ["nt"]), stderr=sys.stderr, stdout=sys.stdout)
        # Clean up
        try: 
            # Replace the old configuration file
            os.replace("pyproject_old.toml","pyproject.toml")
            # Delete the temporary configuration file
            os.remove("pyproject_old.toml")
        except: pass 
    pass
    
def build(*args, **kwargs):
    """
    Poetry build compatibility helper interface
    """
    # Import build system dependencies
    from poetry import core #@UnresolvedImport
    # Read content of pyproject file
    packages = kwargs.get("packages",[])
    if os.path.exists("pyproject.toml"): 
        with open("pyproject.toml", "r") as f: content = f.readlines()
    else: content = str("")
    # Check if a poetry file can be read
    if not packages and content: 
        packages = [line for line in content if line.split("=")[0].strip() in ["packages"]]
        config = next(iter(packages[0].split("=",1)[1:])); 
        config = config.strip(); config = config.replace("=",":")
        config = config.replace('from','"from"'); config = config.replace('include','"include"')
        packages = ast.literal_eval(config)
    else: packages.append(dict())
    # We do not build a platform specific wheel. Skipping rest of routine.
    if not any([str("tool.poetry.build") in line for line in content]): return
    # Clean up the initial workspace
    _ = [os.remove(x) for x in os.listdir(os.getcwd()) if x.startswith("1.0")]
    ## Recover the original path while running poetry install/build
    sys.path.extend([os.path.join(x,"site-packages") for x in sys.path if "lib" in x.lower()])
    sys.path.extend([os.path.join(os.path.dirname(x),"src","PyXMake","src") for x in sys.path if "lib" in x.lower()])
    ## This handles all virtual environments within the current project.
    venv = os.path.abspath(os.path.join(os.getcwd(),".venv"))
    if os.path.exists(venv):
        # Add all binaries
        os.environ.update({"PATH":os.pathsep.join([os.getenv("PATH")]+[os.path.join(venv,"bin")])})
        # Only meaningful if a virtual environment exists
        sys.path.extend([os.path.join(venv,"src","PyXMake","src")])
        sys.path.extend([os.path.abspath(os.path.join(venv,"lib",os.listdir(os.path.join(venv,"lib"))[0] if str(platform.system()).lower() in ["linux"] else "","site-packages"))])
    # Create a user site directory if not already present
    try: 
        child = subprocess.Popen([sys.executable,"-m","poetry","run","python","-c","import site; print(site.getusersitepackages())"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        usersitepackages = child.communicate()[0].decode().strip()
        # Overwrite if command was not successful
        if child.returncode != 0: raise RuntimeError
        # If output cannot be recovered. Fail back to system implementation
        if not usersitepackages: usersitepackages = site.getusersitepackages()
    # Can happen when poetry is no longer in path
    except: usersitepackages = site.getusersitepackages()
    # Bugfix in poetry core for some python versions.
    output = packages[0].get("from","") or packages[0].get("include","")
    # Create a user site directory if not already present
    if not os.path.exists(usersitepackages): os.makedirs(usersitepackages)
    # Remove all outdated, deprecated files from the previous run
    _ = [os.remove(os.path.abspath(os.path.join(usersitepackages,x))) for x in os.listdir(usersitepackages) if x.startswith("pyx_poetry_build_extension")]
    # Write all current paths to pth files
    for index, path in enumerate(sys.path,0):
        # Skip empty paths
        if not os.path.exists(path): continue
        # Everything poetry related has to go
        if str("poetry") in path.split("site-packages")[-1]: continue
        # Add all paths into a seperate file
        with open(os.path.join(usersitepackages,"pyx_poetry_build_extension_%s.pth" % str(index)),"w+") as f: f.write(path)
    # Check if the output directory is already a valid package. Do not modify the output directory
    if not os.path.exists(os.path.join(output,"__init__.py")): 
        # Loop over all files in the output directory
        for x in os.listdir(output):
            # Ignore all folders in the output directory.
            if os.path.isdir(os.path.join(output,x)): continue
            # Ignore generated files
            try: subprocess.check_call(shlex.split("git ls-files --error-unmatch %s" % x,posix=not os.name.lower() in ["nt"]), 
                 stdout=open(os.devnull, 'wb'), stderr=open(os.devnull, 'wb'), cwd=output)
            except: continue
            # Assume an unchanged index to avoid accidental updated to the repo
            command = "git update-index --assume-unchanged %s" % x
            # Only valid for files
            subprocess.call(shlex.split(command,posix=not os.name.lower() in ["nt"]), cwd=output)
            # Removes initial file. This is done only once.
            if len(os.listdir(output)) <= 1: os.remove(os.path.join(output,x))
    # We have an incomplete setup
    if not os.path.exists(os.path.join(output,"__init__.py")):
        # Add additional init file if not already present. Only required in later versions of Poetry. Never overwrite an existing one.
        if parse(core.__version__) >= parse("1.6.1"): open(os.path.join(output,"__init__.py"),"w+")
        # Add also a dummy init file to the output directory when running on windows or linux with interpreter version above 2.7
        elif str(platform.system()).lower() in ["linux","windows"] and parse(".".join([str(x) for x in sys.version_info[:2]])) > parse("2.6"): open(os.path.join(output,"__init__.py"),"w+")
       
def main(**kwargs):
    """
    Main command line parser.
    """
    if not kwargs.get("method",""): 
        parser = argparse.ArgumentParser(description='CLI wrapper options for Poetry.')
        parser.add_argument('method', metavar='option', type=str, nargs=1, 
            help='An option identifier. Adding one new option named <setup>. All other CLI arguments are directly parsed to Poetry.')
        # Select method
        args, _ = parser.parse_known_args()
        method = kwargs.get("method",str(args.method[0]))
    else: method = kwargs.get("method")
    # Execute wrapper within this script or parse the command to poetry
    command = " ".join(["poetry"] + sys.argv[1:])
    if not method in globals() or ( len(sys.argv[1:]) > 1 and not method in globals() ): 
        subprocess.call(shlex.split(command,posix=not os.name.lower() in ["nt"]),stderr=sys.stderr, stdout=sys.stdout)
    else: globals()[method](**kwargs)
    pass

# Apply shim to poetry if version is sufficient.
if parse(Poetry.VERSION) > parse("1.4.0"):
    setattr(InstalledRepository,"load",load)

try: 
    # Apply shim to installer package
    from installer import __version__ as VERSION
    from installer.records import RecordEntry
    # Only apply shim for latest versions
    if parse(VERSION) >= parse("0.7.0"):
        setattr(RecordEntry, "from_elements", install)
except ImportError: pass

if __name__ == "__main__":
    pass
