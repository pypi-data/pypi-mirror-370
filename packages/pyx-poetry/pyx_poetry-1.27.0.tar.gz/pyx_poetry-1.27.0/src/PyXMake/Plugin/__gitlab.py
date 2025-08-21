# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %            GitLab wrapper module - Classes and functions     %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
GitLab release configuration and management assistance wrapper.
 
@note: 
Created on 16.08.2022

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
import copy
import requests
import posixpath
import warnings
import argparse

try: # pragma: no cover
    from packaging.version import Version as StrictVersion
    LooseVersion = StrictVersion
except ImportError: from distutils.version import StrictVersion, LooseVersion

from packaging import version
from datetime import datetime, timedelta

try: from urllib.parse import urlparse  #@UnusedImport
except: from urlparse import urlparse  #@UnresolvedImport @Reimport

def check():
    """
    GitLab CI methods are only available in CI environment.
    """
    if not os.getenv("GITLAB_CI",""): warnings.warn("Method executed outside Gitlab CI. It will have no effect.", RuntimeWarning) #@UndefinedVariable
    # Return a boolean value
    return os.getenv("GITLAB_CI","") != ""

def housekeeping(**kwargs):
    """
    Entry point for housekeeping job.
    """
    # We are outside GitLab CI. Do nothing.
    if not check(): return 0
    # Predefined variables
    outdated = []; headers = {}
    # Fetch GitLab CI URL
    url = "%s/projects/%s/pipelines" % (os.getenv("CI_API_V4_URL"), os.getenv("CI_PROJECT_ID"), )
    # Update request header
    headers.update({"PRIVATE-TOKEN":os.getenv("GIT_PASSWORD")})
    # Get time offset from now. Defaults to 14 days
    d = datetime.today() - timedelta(days=int(os.getenv("since",7)))
    # Fetch all outdated IDs. Fail gracefully
    try: outdated = [ x["id"] for x in requests.get(url, headers=headers, params={"updated_before":d}).json() ]
    except: pass
    # Loop over all pipelines
    for pipeline in outdated:
        # Attempt to delete the pipeline
        try: requests.delete(posixpath.join(url,str(pipeline)), headers=headers)
        except: pass
    return 0

def release(**kwargs):
    """
    Entry point for release job.
    """
    # We are outside GitLab CI. Do nothing.
    if not check(): return 0
    # Collect all user input
    header = {"PRIVATE-TOKEN": kwargs.get("token",os.getenv("GIT_PASSWORD",None))}
    url = kwargs.get("base_url",os.getenv("CI_API_V4_URL",None))
    project = kwargs.get("project_url",os.getenv("CI_REPOSITORY_URL",None))
    
    # Verify user input. All data must be set.
    if not all([x for x in [header["PRIVATE-TOKEN"], url, project]]): 
        # Issue a warning - but return gracefully
        warnings.warn("Could not validate release CLI input parameters. One or all of <token>, <base_url> and <project_url> are missing.", RuntimeWarning) #@UndefinedVariable
        return 0
    
    # Determine server and namespace from the given URL
    server =  '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(project))
    namespace = os.path.splitext(project.split(server)[-1])[0]
    server = str(2*posixpath.sep).join([server.split(posixpath.sep*2)[0], server.split("@")[-1].split(posixpath.sep*2)[-1]])
    
    # Release asset options
    options = kwargs.get("assets",{"generic":{"tar.gz":"Source code (tar.gz)",
                                              "zip":"Source code (zip)", 
                                              "whl":"Python installer (whl)",
                                              "exe":"Standalone application (exe)"},
                                      "pypi":{"whl":"PyPi package (whl)"}})
    
    # Could not determine all required values. Skipping.
    if not all([x for x in [url, server, namespace]]): pass
    
    # This is the current repository
    repository = namespace.split(posixpath.sep)[-1]
    
    # This is the project group
    group_url = posixpath.dirname(posixpath.join(server, "groups",namespace))
    
    # Search for the given namespace in all groups
    found = [group 
             for page in range(1,int(requests.head(posixpath.join(url,"groups"), headers=header).headers['x-total-pages']) + 1)
             for group in requests.get(posixpath.join(url,"groups"), params={"page":str(page)}, headers=header).json() 
             if group_url in group["web_url"]]
    
    # We found the group
    if found: found = [group for group in found if len(group["web_url"]) == len(group_url)][0]
    else: raise RuntimeError("Could not determine group of current project.")
    
    ## Search for the given project within the group
    # Use case insensitive search
    found = [project
             # Iterate through all pages 
             for page in range(1,int(requests.head(posixpath.join(url,"groups",str(found["id"]),"projects"), headers=header).headers['x-total-pages']) + 1)
             # Iterate through all projects within the current group
             for project in requests.get(posixpath.join(url,"groups",str(found["id"]),"projects"), params={"page":str(page)}, headers=header).json()
             # Collect all entries where repository matches name or path
             if any(repository.lower() in match.lower() for match in [project["name"],project["path"]] ) ][0]
    # Search for the latest release
    releases = [release
                for page in range(1,int(requests.head(posixpath.join(url,"projects",str(found["id"]),"releases"), headers=header).headers.get('x-total-pages',0)) + 1)
                for release in requests.get(posixpath.join(url,"projects",str(found["id"]),"releases"), params={"page":str(page)}, headers=header).json()]
    
    # This is the latest release. Can be empty
    versions = [d["tag_name"][1:] for d in releases]
    # Allow modern naming convention like releases
    try: versions.sort(key=StrictVersion)
    except: versions.sort(key=LooseVersion)
    
    # Check if an older version is found. However, versions can be empty. Acknowledge that
    if not versions: 
        try: tag = kwargs.get("tag",os.getenv("TAG"))
        except: raise RuntimeError("Could not determine project tag. Please create an environment variable explicitly named 'TAG'.")
    else: tag = kwargs.get("tag",os.getenv("TAG","v%s" % versions[-1]))
    
    # Search for all available packages. A package must have the same tag as the release
    package = [package
               for page in range(1,int(requests.head(posixpath.join(url,"projects",str(found["id"]),"packages"), headers=header).headers['x-total-pages']) + 1)
               for package in requests.get(posixpath.join(url,"projects",str(found["id"]),"packages"),  params={"page":str(page)}, headers=header).json() 
               if version.parse(package["version"]) == version.parse(tag.split("v")[-1])]
    
    # There is no package data for the requested release
    if not package: raise RuntimeError("Could not determine latest package associated with tag: %s" % str(tag))
    
    # Collect all assets
    sha = [x["pipeline"]["sha"] for x in package if set([x["pipeline"]["project_id"],x["name"]]) == set([found["id"],found["name"]])]
    assets = {x["package_type"]:posixpath.join(server,x["_links"]["web_path"][1:]) for x in package}
    
    # Fetch all uploaded files within assets
    files = [(key, x) for key, asset in assets.items()
             for x in requests.get(posixpath.join(url,"projects",str(found["id"]),"packages",asset.split(posixpath.sep)[-1],"package_files"), headers=header).json() ]
    
    # Construct download links
    for key in list(assets.keys()): assets.update({key:{"url":posixpath.join(server,namespace,"-","package_files")}})
    for key in list(assets.keys()): assets[key].update({"files": [{ x[-1]["file_name"] : x[-1]["id"] } for x in files if key in x[0] ]})
    
    # Create a collection of all assets
    collector = [{"name":name, "url": posixpath.join(assets[key]["url"],str(ID),"download")} 
                for key in options 
                for extension, name in options[key].items() 
                for entry in assets.get(key,{}).get("files",[]) 
                for file, ID in entry.items() if file.endswith(extension)]
    
    # Validate that only singular and correct entries remain
    collector = [entry for entry in collector if requests.get(entry["url"]).status_code == 200]
    collector = [{"name":key, "url":value} for key, value in {entry["name"]:entry["url"] for entry in collector}.items()]
     
    # Create the request body
    release = {"name":"Release of %s" % tag, "description":"Created using CLI", "tag_name":str(tag),"assets": {"links":collector}}
    
    # Only meaningful if tagged version does not yet exists.
    if sha: release.update({"ref":sha[0]}) 
    elif os.getenv("CI_COMMIT_SHA",""): release.update({"ref":os.getenv("CI_COMMIT_SHA")})
    
    # Delete outdated release. Defaults to True
    if kwargs.get("silent_update",False): requests.delete(posixpath.join(url,"projects",str(found["id"]),"releases",tag), headers=header)
    
    # Execute the release command
    r = requests.post(posixpath.join(url,"projects",str(found["id"]),"releases"), json=release, headers=header)
    try: r.raise_for_status()
    except: 
        warnings.warn("Creating or updating the release raised an unexpected return code. Please verify the result.", RuntimeWarning) #@UndefinedVariable
        warnings.warn("%s" % r.text, RuntimeWarning) #@UndefinedVariable
        warnings.warn("%s" % str(release), RuntimeWarning) #@UndefinedVariable
    # Return the response
    return r

def main(**kwargs):
    """
    Main command line parser.
    """
    settings = {}
    options = {"choices":kwargs.pop("choices",["release","housekeeping"])}
    commands = globals(); commands.update(kwargs.get("register",{}))
    options["choices"] += list(kwargs.pop("register",{}).keys())
    if not kwargs.get("method",""): 
        parser = argparse.ArgumentParser(description='CLI wrapper options for GitLab CI.')
        parser.add_argument('method', metavar='namespace', type=str, nargs=1, choices=options["choices"],
            help='An option identifier. Unknown arguments are ignored. Allowed values are: '+', '.join(options["choices"]))
        # The options are equally valid for all commands
        parser.add_argument('-b', '--base_url', type=str, nargs=1, help="Base API v4 URL of a GitLab instance. Defaults to GitLab instance of DLR.")
        parser.add_argument('-t', '--token', type=str, nargs=1, help="Token to be used for authentication.")
        parser.add_argument('-i', '--identifier', type=str, nargs=1, help="A valid, unique project identifier.")
        parser.add_argument('-p', '--package', type=str, nargs=1, help="A valid project name.")
        parser.add_argument('-v', '--version', type=str, nargs=1, help="A valid version identifier for PyPI.")
        parser.add_argument("-o", '--output', type=str, nargs=1, help="Absolute path to output directory. Defaults to current project folder.")
        # Select method
        args, _ = parser.parse_known_args()
        method = str(args.method[0])
        # Find all given command line parameters
        given = [x for x in vars(args) if getattr(args,x)]
        # Add them to settings
        settings.update({x:next(iter(getattr(args,x))) for x in given})
    else: method = kwargs.get("method")
    settings.update(copy.deepcopy(kwargs))
    # Execute wrapper within this script or parse the command to git
    if not method in globals(): raise RuntimeError("Unknown GitLab CI namespace option.")
    else: commands[method](**settings)
    pass
    
if __name__ == "__main__":
    main(); sys.exit()
