# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                                                            API Module - Classes and Functions                                                                                    %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Contains all classes and functions to define a web interface
 
@note: PyXMake module                   
Created on 19.11.2020

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-FA,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package PyXMake.API
# Contains all classes and functions to create a web application.
## @author 
# Marc Garbade
## @date
# 19.11.2020
## @par Notes/Changes
# - Added documentation // mg 19.11.2020

import os, sys
import abc, six
import platform
import shutil
import socket
import time
import io
import ntpath
import datetime
import posixpath
import zipfile
import random
import uuid
import urllib

try:
    # API requires 3.6 and higher
    import uvicorn
    import json
    import base64
    import requests
    
    from fastapi import FastAPI, APIRouter, File, UploadFile, Query, Body
    from starlette.responses import Response, RedirectResponse, FileResponse, JSONResponse, HTMLResponse  
    from fastapi.encoders import jsonable_encoder #@UnresolvedImport
    from starlette.staticfiles import StaticFiles
    from starlette.requests import Request
    from enum import Enum
    from starlette.middleware.cors import CORSMiddleware
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from typing import List, Optional, Any, Dict #@UnresolvedImport
    from pydantic import SecretStr #@UnresolvedImport

except ImportError: pass

try:
    import PyXMake
except ImportError:
    # Script is executed as a plug-in
    sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import PyXMake
finally:
    from PyXMake.Tools import Utility #@UnresolvedImport
    from PyXMake import VTL  #@UnresolvedImport

## @class PyXMake.API.Base
# Abstract base class for all API objects. Inherited from built-in ABCMeta & FastAPI. 
# Only compatible with Python 3.6+
@six.add_metaclass(abc.ABCMeta)
class Base(object):
    """
    Parent class for graphical user interface objects. 
    """
    def __init__(self, *args, **kwargs):
        """
        Low-level initialization of parent class.
        """
        # Initialize a new TK main window widget.
        self.API = FastAPI(*args,**kwargs); self.Router = APIRouter(); 
        self.APIObjectKind = "Base"
        
    def RedirectException(self, url):
        @self.API.exception_handler(StarletteHTTPException)
        def custom_http_exception_handler(request, exc):
            return RedirectResponse(url=url)
        
    def StaticFiles(self, url, path, index="index.html", html=True):
        """
        Serve additional static files. Mount them appropriately.
        """
        if os.path.isdir(path) and os.path.exists(os.path.join(path,index)):
            # Check if directory contains an index.html. If not, create one.
            if not index.startswith("index") and not os.path.exists(os.path.join(path,"index.html")) and html: # pragma: no cover
                shutil.copy(os.path.join(path,index),os.path.join(path,"index.html"))
        # Mount directory with static files to given url, serving index.html if required.
        self.mount(url, StaticFiles(directory=path, html=html))
        
    def mount(self, *args):
        """
        Return current API's main instance handle.
        """
        self.API.mount(*args)
        
    def include(self, *args):
        """
        Return current API's main instance handle.
        """
        self.API.include_router(*args); 
        
    def create(self):
        """
        Return current API's main instance handle.
        """
        # Include all defined routers
        self.include(self.Router)
        # Return current API's handle
        return self.API
    
    def run(self, Hostname=str(platform.node()), PortID=8020): # pragma: no cover
        """
        Run the current API. 
        """
        # Current API is the main API
        handle = self.create()
        # Run current API as main instance 
        uvicorn.run(handle, host=Hostname, port=PortID)
        pass

## @class PyXMake.API.Backend
# Class instance to define PyXMake's web API instance
class Backend(Utility.AbstractBase):
    """
    Class instance to define PyXMake's server instance for a web API.
    """    
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Initialization of PyXMake's Backend API.
        """
        # Establish all methods
        super(Backend, self).__init__()
        # Collect all hidden attributes
        __attributes__ = {x:self.APIObjectKind for x in dir(self) if self.APIObjectKind in x}
        # Set ObjectKind
        self.APIObjectKind = "Backend"
        # Definition of all predefined path variables
        Archive = Enum("ArchiveObjectKind",{"zip":"zip","tar":"tar","gzip":"gzip","lzma":"lzma","bz2":"bz2"})
        ## Adding support for external file manager.
        FileManager = Enum("FileObjectKind",{"full":"all","local":"private","shared":"public"})
        # Merge all class attributes
        for key, value in __attributes__.items(): setattr(self, key.replace(value,self.APIObjectKind), getattr(self, key))
        # Delete since not used anymore
        del __attributes__
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %                                                                                    PyXMake - Guide                                                                                            %
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","documentation"]), tags=[str(self.__pyx_guide)])
        def api_self_guide():
            """
            Method pointing to the main documentation of the API.
            """
            return RedirectResponse(url=self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","documentation",""]))
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"user","documentation"]), tags=[str(self.__pyx_guide)],response_class=HTMLResponse)
        def api_user_guide():
            """
            Method pointing to the user documentation of the underlying package.
            """
            response = str(self.__pyx_url_path)
            # Build HTML response
            html_content = \
            """
            <!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
            <meta http-equiv="refresh" content="1;url="""+'"'+response+'"'+""" />
            <script>setTimeout(function() {window.location.href = """+'"'+response+'"'+""";}, 1000);
            </script></head><body></body></html>
            """
            return HTMLResponse(html_content)
         
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"dev","documentation"]), tags=[str(self.__pyx_guide)])
        def api_dev_guide():
            """
            Method pointing to the developer documentation of the underlying package.
            """
            return RedirectResponse(url=self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"dev","documentation",""]))
        
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %                                                                                PyXMake - Interface                                                                                           %
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","abaqus","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_abaqus(kind: Archive, BuildID: str, Source: List[str] = Query(["mcd_astandard"]), ZIP: UploadFile = File(...)):
            """
            API for PyXMake to create an ABAQUS compatible Fortran library for Windows machines by using the Intel Fortran Compiler.  
            """    
            # Check if an old file is present in the current workspace. Delete it.
            if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)):
                os.remove(os.path.join(VTL.Scratch,ZIP.filename))
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=False):       
                # Get all relevant uploaded files.
                files = Utility.FileWalk(Source, path=os.getcwd())
                # Monitor the build process. Everything is returned to a file     
                with Utility.FileOutput('result.log'):
                    VTL.abaqus(BuildID, files, source=os.getcwd(), scratch=os.getcwd(), output=os.getcwd(), verbosity=2)
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename)
        
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","client","{kind}"]), tags=[str(self.__pyx_interface)],
          description=
          """
          API for PyXMake. Connect with a remote OpenAPI generator service to construct a client library from an Open API scheme given as either a file or an accessible URL. 
          The result is returned as a ZIP folder. If no ZIP folder has been provided, one is generated in the process.
          """ )
        def api_client(
              kind: Archive, 
              request: Request, 
              URI: str = Query(...,
              description=
              """
              The name of the main input file present in the supplied ZIP archive or the full URL address. The API scheme will be downloaded automatically. 
              Note that the URI is always interpreted as an URL if a file with the name cannot be found in the archive. 
              """
              ), 
              ClientID: Optional[str] = Query("python",
              description=
              """
              This is the generated client format. Defaults to python.
              """
              ),
              CLI: List[str] = Query(["--skip-validate-spec"],
              description=
              """
              Additional command line arguments. Please refer to the official documentation of OpenAPI generator to get a glimpse of all available options.
              """
              ),
              ZIP: UploadFile = File(None,
              description=
              """
              An compressed archive containing all additional files required for this job. This archive is updated and returned. All input files are preserved.
              It additionally acts as an on-demand temporary user directory. It prohibits access from other users preventing accidental interference.
              However, the scratch workspace is cleaned constantly. So please download your result immediately.
              """
              )):
            """
            API to connect to the OpenAPI client generator.
            """
            import tempfile
            import subprocess
            
            from pathlib import Path
            from packaging.version import parse
            # Local variables
            delimn = "."; 

            # Create some temporary variables
            canditate = str(next(tempfile._get_candidate_names()));

            # Check if a ZIP folder has been given. Create a default entry (empty archive)
            if not ZIP: ZIP = Utility.UpdateZIP.create(delimn.join([canditate,"zip"]))
                
            try:
                # Check if an old file is present in the current workspace. Delete it.
                if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)): os.remove(os.path.join(VTL.Scratch,ZIP.filename))
            except: pass
            
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Preserve the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=True):
                root = Utility.AsDrive("mnt")
                p = Path(os.path.abspath(os.getcwd())).parts; path = posixpath.join(root, *p[1 if Utility.GetPlatform() in ["windows"] else 2:])

                # This is the required base image
                image = "docker.io/openapitools/openapi-generator-cli"
                
                # Create a common mount point
                mount = [{"ReadOnly": False,"Source": "stmlab_scratch","Target": "/mnt","Type":"volume"}]
                
                # Create base command
                openapi_cli = ["docker","run","--rm","-v","/mnt:%s" % root,image.split(posixpath.sep, 1)[-1]]
               
                # URI is not a file (or does not exist in the directory). Attempt to download the resource. Fail if unsuccessful
                if not os.path.exists(URI): 
                    response = requests.get(URI)
                    with open(Utility.PathLeaf(URI), "w") as f: f.write(response.text)
                    URI = Utility.PathLeaf(URI)
                    ## Update base URL for client to automatically connect to the server from which is setup is derived. This is only meaningful
                    # when a definition file is published alongside with a public API interface. Does not affect JSON files presented directly through
                    # the ZIP archive  
                    try: 
                        # If response was successful, URL now contains the servers net location
                        url = '{uri.scheme}://{uri.netloc}'.format(uri= urllib.parse.urlparse(response.url))             
                        # Opening OpenAPI definition as JSON file
                        with open(URI,'r') as openfile: openapi_file = json.load(openfile)
                        # Update the default list of servers to include the complete URL by default
                        servers =  [{'url': posixpath.sep.join([url,Utility.PathLeaf(x["url"])]).rstrip(posixpath.sep)} for x in openapi_file.get("servers",[{"url":""}])]
                        # Restrict version of specification for now
                        if parse(openapi_file.get("openapi")) >= parse("3.1.0"): openapi_file.update({'openapi':'3.0.3'})
                        # Update configuration
                        openapi_file.update({'servers':servers})
                        # Overwrite existing file
                        with open(URI,'w') as openfile: openfile.write(json.dumps(openapi_file))
                    except: pass
 
                # If Java is available - use generator directly.
                if Utility.GetExecutable("java") and Utility.GetOpenAPIGenerator(): 
                    ## Java executable in a Docker container should take precedence
                    openapi_cli = [Utility.GetExecutable("java", get_path=True, path=os.pathsep.join(['/usr/bin'] if all([
                                              Utility.IsDockerContainer(), Utility.GetPlatform() in ["linux"]]) else [] + os.getenv("PATH",os.defpath).split(os.pathsep)))[-1],"-jar",
                                              Utility.GetOpenAPIGenerator()]; 

                # The command line used in the container                
                if not openapi_cli[0] in ["docker"]: command = ["generate","-i",posixpath.join(os.getcwd(),URI),"-g",str(ClientID),"-o",posixpath.join(os.getcwd(),str(ClientID))] 
                else: command = ["generate","-i",posixpath.join(path,URI),"-g",str(ClientID),"-o",posixpath.join(path,str(ClientID))] 
                # Merge executable and command
                command = openapi_cli + command
                # Add user-specific command line options
                ind = command.index("generate") + 1; command[ind:ind] = CLI

                # Assemble request body
                data = {"image":image,"command":command[6:],"keep":False,"template":{"TaskTemplate":{"ContainerSpec":{"Mounts":mount}}}}
                    
                # Execute Java command
                if not command[0] in ["docker"]: subprocess.check_call(command)
                # Lecacy version
                else:
                    # Attempt direct invocation using remote docker instance
                    requests.post(str(request.url.scheme)+"://%s/0/Lab/UI/Orchestra" % self.APIBase,params={"name":"stm_openapi"}, json=data)
                    # Check if attempt was successful. Attempt orchestra in case of failure.
                    if not os.path.exists(os.path.join(os.getcwd(),ClientID)):
                        r = requests.post(str(request.url.scheme)+"://%s/0/Lab/UI/Orchestra" % self.APIBase, 
                                          params={"name":"stm_openapi"}, json={"mounts":mount, "command":command})
                        r.raise_for_status()
                
                # Get all permissions for the current folder
                if Utility.GetPlatform() not in ["windows"]: subprocess.check_call(["sudo","chmod","-R",str(777),os.path.abspath(os.getcwd())])
                pass
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename) 
           
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","cxx","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_cxx(kind: Archive, string_to_channel_through: str) -> dict:
            """
            Dummy function for showing a quick response
            """
            # from PyXMake.VTL import cxx
            string = "hello"
            return {"return_code": string}
           
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","doxygen","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_doxygen(kind: Archive, string_to_channel_through: str) -> dict:
            """
            Dummy function for showing a quick response
            """
            # from PyXMake.VTL import doxygen
            string = "hello"
            return {"return_code": string}
         
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","ifort","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_ifort(kind: Archive, BuildID: str, Source: List[str] = Query([x for x in VTL.GetSourceCode(0)]), ZIP: UploadFile = File(...)):
            """
            API for PyXMake to create a static library for Windows machines by using the Intel Fortran Compiler.  
            """
            # Check if an old file is present in the current workspace. Delete it.
            if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)):
                os.remove(os.path.join(VTL.Scratch,ZIP.filename))
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=False):       
                # Get all relevant uploaded files.
                files = Utility.FileWalk(Source, path=os.getcwd())
                # Create two dummy directories to avoid problems during build event.
                os.makedirs("include",exist_ok=True); os.makedirs("lib",exist_ok=True)
                # Monitor the build process. Everything is returned to a file     
                with Utility.FileOutput('result.log'):
                    VTL.ifort(BuildID, files, source=os.getcwd(), scratch=os.getcwd(), make=os.getcwd(), verbosity=2)   
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename)
         
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","java","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_java(kind: Archive, BuildID: str, Source: List[str] = Query([x for x in VTL.GetSourceCode(0)]), ZIP: UploadFile = File(...)):
            """
            API for PyXMake to create a Java compatible Fortran library for Windows machines by using the Intel Fortran Compiler.  
            """
            # Check if an old file is present in the current workspace. Delete it.
            if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)):
                os.remove(os.path.join(VTL.Scratch,ZIP.filename))
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=False):       
                # Get all relevant uploaded files.
                files = Utility.FileWalk(Source, path=os.getcwd())
                # Monitor the build process. Everything is returned to a file     
                with Utility.FileOutput('result.log'):
                    VTL.java(BuildID, files, source=os.getcwd(), scratch=os.getcwd(), output=os.getcwd(), verbosity=2) 
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename)
        
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","latex","{kind}"]), tags=[str(self.__pyx_interface)],
          description=
          """
          API for PyXMake. Connect with a remote Overleaf service to compile a given Latex archive. The result PDF is added to the archive and returned.
          """ )
        def api_latex(kind: Archive, 
              BuildID: str, 
              ZIP: UploadFile = File(..., 
              description=
              """
              An compressed archive containing all additional files required for this job. This archive is updated and returned. All input files are preserved.
              It additionally acts as an on-demand temporary user directory. It prohibits access from other users preventing accidental interference.
              However, the scratch workspace is cleaned constantly. So please download your result immediately.
              """)):
            """
            API for PyXMake to compile a Latex document remotely using Overleaf.
            """
            # Check if an old file is present in the current workspace. Delete it.
            if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)): os.remove(os.path.join(VTL.Scratch,ZIP.filename))
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch): 
                # Collapse temporary spooled file
                Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=False)
                # Monitor the remote build process. Everything is returned to a file     
                with Utility.FileOutput('result.log'): VTL.latex(BuildID, ZIP.filename, API="Overleaf", verbosity=2, keep=False)
                # Add results to ZIP archive.
                archive = zipfile.ZipFile(ZIP.filename,'a'); [archive.write(x, os.path.basename(x)) for x in os.listdir() if not x.endswith(".zip")]; archive.close()
                shutil.copy(ZIP.filename, VTL.Scratch)
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename)
           
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","f2py","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_py2x(kind: Archive, BuildID: str, Source: List[str] = Query([x for x in VTL.GetSourceCode(0)]), ZIP: UploadFile = File(...)):
            """
            API for PyXMake to create a Python compatible Fortran library for Windows machines by using the Intel Fortran Compiler.  
            """
            # Check if an old file is present in the current workspace. Delete it.
            if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)):
                os.remove(os.path.join(VTL.Scratch,ZIP.filename))
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=False):       
                # Get all relevant uploaded files.
                files = Utility.FileWalk(Source, path=os.getcwd())
                # Monitor the build process. Everything is returned to a file     
                with Utility.FileOutput('result.log'):
                    VTL.py2x(BuildID, files, source=os.getcwd(), scratch=os.getcwd(), output=os.getcwd(), verbosity=2)
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename)
          
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","ssh_f2py","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_ssh_f2py(kind: Archive, time_sleep: int) -> dict:
            """
            Dummy function for showing a long response time
            """
            # from PyXMake.VTL import ssh_f2py
            return {"return_code":str(time_sleep)}
           
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","ssh_ifort","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_ssh_ifort(kind: Archive, time_sleep: int) -> dict:
            """
            Dummy function for showing a long response time
            """
            # from PyXMake.VTL import ssh_ifort
            return {"return_code":str(time_sleep)}
           
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","ssh_make","{kind}"]), tags=[str(self.__pyx_interface)])
        def api_ssh_make(kind: Archive, time_sleep: int) -> dict:
            """
            Dummy function for showing a long response time
            """
            # from PyXMake.VTL import ssh_make
            return {"return_code":str(time_sleep)}

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # %                                                                                PyXMake - Professional                                                                                     %
        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        @self.Router.put(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","self"]), tags=[str(self.__pyx_professional)])        
        def api_self_access(Attribute: Optional[str] = "PyXMake.Tools.Utility.IsDockerContainer", args: List[Any] = [],  kwargs: Dict[str,Any] = None):
            """
            API to remotely access PyXMake methods.
            """
            import numpy as np
            import PyXMake as pyx #@UnresolvedImport
            from PyXMake.Build.Make import Py2X #@UnresolvedImport
            # Default status code (Not Documented Error)
            status_code = 500
            # Evaluate an arbitrary attribute. Get its callback method.
            callback = Py2X.callback(pyx,Attribute)
            with Utility.TemporaryDirectory(): result = [x.tolist()  if hasattr(x, "tolist")  else x for x in np.atleast_1d(callback(*args,**kwargs))]; 
            if result: status_code = 200
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.head(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","user","{kind}"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for user info service. Verifies that a given token can be verified against a given service.
          """ )             
        def api_get_user(request: Request, 
              kind: Enum("TokenObjectKind",{"portainer":"portainer","shepard":"shepard","gitlab":"gitlab","user":"client"}), 
              Token: SecretStr = Query(...,
              description=
              """
              A valid X-API-Token.
              """
              ),
              ClientID: str = Query(None,
              description=
              """
              An user-defined client. Only meaningful when a non-default client is requested.
              """
              )):
            """
            API to verify a given token. Returns information about the token holder if exists.
            """
            result = {}
            # Fail gracefully if service is not reachable
            try: 
                # A non-default client is requested
                if kind.name in ["user"] and ClientID: 
                    r = requests.post("https://token-api.fa-services.intra.dlr.de/decode_and_verify?token=%s&expected_client_id=%s" % (Token.get_secret_value(), ClientID,), verify=False)
                # A non-default client is requested but not explicitly given
                elif kind.name in ["user"] and not ClientID: return JSONResponse(status_code=406, content="ClientID cannot be blank in non-default client mode")
                # A default client is requested
                else: r = requests.get(str(request.url.scheme)+"://%s/2/PyXMake/api/%s/user" % (self.APIBase,kind.value,), 
                                 params={"Token":Token.get_secret_value()}, verify=False)
                result = r.json()
            except: pass
            # Modify response with respect to the content of result
            if result: return JSONResponse(status_code=r.status_code, content=result,)
            else: return JSONResponse(status_code=404, 
                                content="There is no match for the given token and client %s." % str(kind.value.title() if not kind.name in ["user"] else ClientID),)

        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","info","{kind}"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for user info service. Verifies that a given attribute can be found in a given category.
          """ )             
        def api_get_info(
              kind: Enum("UserObjectKind",{"dlr-username":"user","email":"mail"}), 
              attribute: str = Query(..., 
              description="")):
            """
            API to verify that a given user actual exists or is another service.
            """
            result = []
            # Fail gracefully if service is not reachable
            try: 
                from PyCODAC.Tools.IOHandling import Shepard #@UnresolvedImport
                result = [x for x in requests.get(Shepard.user_url).json() if x[kind.name] == attribute]
            except: return JSONResponse(status_code=404,content="User info service not available",)
            # We have got our information
            status_code = 200; 
            # Found an user. Return the information:
            if result: return JSONResponse(status_code=status_code,content=result[0],)
            # Return a message if no user data was found.
            else: return JSONResponse(status_code=status_code,content="There is no match for the given attribute in the category %s." % kind.value,)
            
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","generator","{kind}"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for generator service. Generates a random response depending on the given path parameter.
          """ )            
        def api_generator(request: Request, kind: Enum("GeneratorObjectKind",{"message":"message"})):
            """
            Generates a random response in dependence of a given path parameter.
            """
            import git
            import ast
            # Procedure
            result = ""; gist = "6440b706a97d2dd71574769517e7ed32"
            # Construct the response
            try: 
                with Utility.TemporaryDirectory(VTL.Scratch):
                    # We cannot reach the API or reached the limit. Fall back to cloning
                    if not os.path.exists(gist) and not os.getenv("pyx_message",""): 
                        git.Repo.clone_from(posixpath.join("https://gist.github.com",gist),gist) #@UndefinedVariable
                        with io.open(os.path.join(gist,"loading_messages.js"),mode="r",encoding="utf-8") as f: result = f.read()
                        # Always refer to the environment variable directly
                        result = result.replace("\n","").replace("export default ","").replace(";","")
                        os.environ["pyx_message"] = result
                        # Remove directory with no further use
                        try: git.rmtree(gist)
                        except: pass
                # Return only one element
                result = ast.literal_eval(os.getenv("pyx_message",result)); result = random.choice(result); 
                status_code = 200
            except: 
                result = "Service not available"; status_code = 500
            # Return the generated response
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","database"]), tags=[str(self.__pyx_professional)],  include_in_schema=False, 
          description=
          """
          API for internal database service. Use to collect information about all available internal database references.
          """ )            
        def api_database():
            """
            API to fetch information about all internal databases.
            """            
            # Initialize everything
            result = {}; status_code = 500
            # Construct the response
            from PyCODAC.Database import Mongo
            # Construct a valid JSON response
            try: result =  { "DataContainer" : Mongo.base_table, "DataTypes" : Mongo.base_reference }
            except: pass
            # Try to return the response directly. 
            try: return (Enum("DataObjectKind",result["DataContainer"]),result["DataTypes"] )
            except: pass
            if result: status_code = 200
            # Return license servers as a dictionary
            return JSONResponse(status_code=status_code,content=result,)

        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","license"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for FlexLM license manager services. Use to collect information about all supported license servers.
          """ )            
        def api_license(request: Request):
            """
            API to fetch FlexLM license server information
            """            
            # Initialize everything
            result = {}; status_code = 500
            # Construct the response
            try: 
                result["intel"] =[ "28518@INTELSD2.intra.dlr.de" ]
                result["ansys"] = [ "1055@ansyssz1.intra.dlr.de" ]
                result["nastran"] = [ "1700@nastransz1.intra.dlr.de", "1700@nastransz2.intra.dlr.de" ]
                result["abaqus"] = [ "27018@abaqussd1.intra.dlr.de" ]
                result["hypersizer"] = [ "27010@hypersizersd1.intra.dlr.de" ]
                result["altair"] = ["47474@altairsz1.intra.dlr.de"]
                status_code = 200
            except: pass

            # Return license servers as a dictionary
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","flexlm"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for FlexLM license manager services. Returns the complete response as a JSON string.
          """ )            
        def api_flexlm(license_query: Optional[str] = Query("27018@abaqussd1", description=
              """
              Qualified name or IP address and port number of the license server. The license server must be active and supporting FlexLM.
              """
              )):
            """
            API to fetch FlexLM all license server information
            """
            import tempfile
            
            from collections import defaultdict #@UnresolvedImport
            from PyXMake.Build import Make #@UnresolvedImport
            # Default status code (Not Documented Error)
            status_code = 500
            # Check whether a connection with FlexLM can be established or not.
            default_user = "f_testpa"; default_host = "cluster.bs.dlr.de"
            secrets = os.path.join(Utility.AsDrive("keys"),default_host)
            try: default_key = os.path.join(secrets,[x for x in os.listdir(secrets) if x.split(".")[-1] == x][0])
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Evaluate an arbitrary attribute. Get its callback method.
            result = defaultdict(list)
            try:
                # Operate fully in a temporary directory
                with Utility.TemporaryDirectory():
                    # Create a temporary file name
                    tmp =  str(next(tempfile._get_candidate_names()))
                    command = "/cluster/software/flexlm/bin/lmutil lmstat -c %s -a" % license_query
                    connect = Make.SSH("FlexLM",[]); connect.Settings(default_user, key=default_key, timeout=1)
                    # Execute the SSH script and log the result
                    with Utility.FileOutput(tmp):  Utility.SSHPopen(connect.ssh_client, ntpath.pathsep.join([command]),verbosity=2)
                    # Read logging information into memory
                    with open(tmp,"r") as f: content = f.read()
                # Success
                result = json.dumps(content); status_code = 200
            # Prevent endless loops if service is not reachable
            except TimeoutError: return JSONResponse(status_code=404,content="FlexLM service not reachable",)
            except: pass
            # Return license status
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","flexlm","show"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for FlexLM license manager services. Use to collect license occupancy rate information for a given query and attributes parameters.
          Defaults to ABAQUS licensing information and occupancy of CAE and solver tokens.
          """ )            
        def api_flexlm_show(request: Request, 
              license_query: Optional[str] = Query("27018@abaqussd1.intra.dlr.de",
              description=
              """
              Qualified name or IP address and port number of the license server. The license server must be active and supporting FlexLM.
              """
              ), 
              license_attributes: List[str] =  Body(['abaqus','cae'],
              description=
               """
               List of attributes to be searched for in the FlexLM response. Defaults to ABAQUS CAE and solver token occupancy.
               """                                       
               )):
            """
            API to fetch FlexLM license occupancy information
            """            
            from collections import defaultdict #@UnresolvedImport
            
            # Evaluate an arbitrary attribute. Get its callback method.
            result = defaultdict(list)
            
            # Create default request
            license_request = defaultdict(lambda:[1,0])
            # Create an dictionary with all requests
            for x in license_attributes: license_request[x]
            
            # Fetch content from FlexLM license services
            r = requests.get(str(request.url.scheme)+"://%s/2/PyXMake/api/flexlm" % self.APIBase, 
                                  params={"license_query":license_query}, verify=False)
            if r.status_code == 404: return JSONResponse(status_code=r.status_code,content=r.json(),)
            elif not r.status_code == 200: return JSONResponse(status_code=r.status_code,content=r.content,)
            content = json.loads(r.json())
            
            try:
                # Default status code (Not Documented Error)
                status_code = 500
                # Collect license information
                for key, value in license_request.items():
                    for output in value: result[key].append(int(content.split("Users of %s:" % key)[1].split("licenses")[output].split("Total of")[1].split()[0]))
                # Success
                result = json.dumps(result); status_code = 200
            except: pass
            # Return license status
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","flexlm","inspect"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for FlexLM license manager services. Use to collect information about license holders as well as number of licenses being used by each user. 
          """ )            
        def api_flexlm_inspect(request: Request, 
              license_query: Optional[str] = Query("27018@abaqussd1.intra.dlr.de",
              description=
              """
              Qualified name or IP address and port number of the license server. The license server must be active and supporting FlexLM.
              """
              ), 
              license_attributes: List[str] =  Body(['abaqus','cae'],
              description=
               """
               List of attributes to be searched for in the FlexLM response. Defaults to ABAQUS CAE and solver token user information.
               """                                       
               )):
            """
            API to fetch FlexLM license holder information and number of licenses in use.
            """            
            from collections import defaultdict #@UnresolvedImport
            
            # Evaluate an arbitrary attribute. Get its callback method.
            result = defaultdict(list)
            
            # Fetch content from FlexLM license services
            r = requests.get(str(request.url.scheme)+"://%s/2/PyXMake/api/flexlm" % self.APIBase, 
                                  params={"license_query":license_query}, verify=False)
            if r.status_code == 404: return JSONResponse(status_code=r.status_code,content=r.json(),)
            elif not r.status_code == 200: return JSONResponse(status_code=r.status_code,content=r.content,)
            content = json.loads(r.json())
            
            try:
                # Default status code (Not Documented Error)
                status_code = 500
                # Collect license information
                for key in license_attributes: 
                    result[key].append([x.strip() for x in content.split("Users of %s:" % key)[1].split("Users of")[0].split("\n")[4:] if Utility.IsNotEmpty(x)])
                # Success
                result = json.dumps(result); status_code = 200
            except: pass
            # Return license holders and detailed job information
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","f2py","inspect"]), tags=[str(self.__pyx_professional)], include_in_schema=False)
        def api_py2x_inspect(ModuleID: Optional[str] = "mcd_corex64", ZIP: Optional[UploadFile] = File(None)):
            """
            Inspect and return all qualified symbols of an existing shared object library.
            Optionally, upload a compiled Python extension library and return all qualified symbols.
            """
            # Local import definitions
            import importlib, contextlib
            from PyXMake.Build.Make import Py2X #@UnresolvedImport
            # Attempt to import PyCODAC. Fail gracefully
            try: import PyCODAC.Core #@UnresolvedImport
            except: pass
            # Check if an old file is present in the current workspace. Delete it.
            try: 
                if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)): os.remove(os.path.join(VTL.Scratch,ZIP.filename))
                filename = ZIP.filename; archive = ZIP.file
            except: 
                filename ='Default.zip'; 
                # Create an empty dummy archive if non has been provided. This is the default.
                empty_zip_data = b'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                with open(os.path.join(VTL.Scratch,filename), 'wb') as ZIP: ZIP.write(empty_zip_data)
                archive = open(os.path.join(VTL.Scratch,filename),"rb")
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(filename, archive, VTL.Scratch, update=False):
                # Search for an supplied shared library. Default to an empty list of non has been found.
                try: default = str(Utility.PathLeaf([os.path.abspath(x) for x in os.listdir(os.getcwd()) if x.endswith(".pyd")][0]).split(".")[0])
                except: default = list([])
                # Import the supplied module. 
                try:
                    if not ModuleID and default: mod = importlib.import_module(default)
                    else: mod = importlib.import_module(ModuleID)
                except: pass
                ## Special case. MCODAC is loaded by default. However, when the user supplies a custom version of the library, this should be used instead.
                # Attempt to reload - but fail gracefully.
                try:
                    from importlib import reload
                    sys.path.insert(0,os.getcwd())
                    mod = reload(mod)
                except:  pass
            # Inspect content of the supplied shared library. Return all methods or throw an error.
            try: AllModules = jsonable_encoder(Py2X.inspect(mod))
            except: AllModules = JSONResponse(status_code=404,content={"message": "No module named %s" % ModuleID or default},)
            return AllModules
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","f2py","show"]), tags=[str(self.__pyx_professional)], include_in_schema=False)
        def api_py2x_show(ModuleID: Optional[str] = "mcd_corex64", Attribute: Optional[str] = ".", ZIP: Optional[UploadFile] = File(None)):
            """
            Return the doc string of an existing symbol in a shared library.
            Optionally, upload a compiled Python extension library.
            """
            # Local import definitions
            import importlib, contextlib
            from PyXMake.Build.Make import Py2X #@UnresolvedImport
            # Attempt to import PyCODAC. Fail gracefully
            try: import PyCODAC.Core #@UnresolvedImport
            except: pass
            # Check if an old file is present in the current workspace. Delete it.
            try: 
                if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)): os.remove(os.path.join(VTL.Scratch,ZIP.filename))
                filename = ZIP.filename; archive = ZIP.file
            except: 
                filename ='Default.zip'; 
                # Create an empty dummy archive if non has been provided. This is the default.
                empty_zip_data = b'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                with open(os.path.join(VTL.Scratch,filename), 'wb') as ZIP: ZIP.write(empty_zip_data)
                archive = open(os.path.join(VTL.Scratch,filename),"rb")
            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Delete the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(filename, archive, VTL.Scratch, update=False):
                # Search for an supplied shared library. Default to an empty list of non has been found.
                try: default = str(Utility.PathLeaf([os.path.abspath(x) for x in os.listdir(os.getcwd()) 
                                        if x.endswith(".pyd" if Utility.GetPlatform() in ["windows"] else ".so")][0]).split(".")[0])
                except: default = list([])
                # Import the supplied module. 
                try:
                    if not ModuleID and default: mod = importlib.import_module(default)
                    else: mod = importlib.import_module(ModuleID)
                except: pass
                ## Special case. MCODAC is loaded by default. However, when the user supplies a custom version of the library, this should be used instead.
                # Attempt to reload - but fail gracefully.
                try:
                    from importlib import reload
                    sys.path.insert(0,os.getcwd())
                    mod = reload(mod)
                except:  pass
            # Inspect content of the supplied shared library. Return all methods or throw an error.
            try: AllModules = jsonable_encoder(Py2X.show(mod,Attribute))
            except: AllModules = JSONResponse(status_code=404,content={"message": "No such combination exists %s" % ".".join([ModuleID or default,Attribute])},)
            return AllModules
 
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","projects"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab group service. List all projects inside a given group.
          """)            
        def api_gitlab_projects(
              Token: SecretStr =Query(...,
              description=
              """
              GitLab X-API-Token valid for the group.
              """
               ),
              GroupID: Optional[str] = Query("6371",
              description=
               """
               The group identifier. Defaults to group STMLab.
               """                                       
               )):
            """
            API to fetch information about all projects within a group.
            """
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Fetch URL and HEADER
            url, header = gitlab.datacheck(token=Token.get_secret_value())
            # Execute command
            r = requests.get(posixpath.join(url,"groups",str(GroupID),"projects"), headers= header)
            # Return a dictionary of projects with their id.
            return JSONResponse(json.dumps({x["name"]:x["id"] for x in r.json()}))
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","groups"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab. List all groups avoiding decoding error. A dictionary for filtering the results can be provided.
          """)            
        def api_gitlab_groups(
              Token: SecretStr =Query(...,
              description=
              """
              GitLab X-API-Token valid for the instance.
              """
               ),
              Filter: Optional[dict] = Body({"name":"STMLab"},
              description=
               """
               Filtering results for key, value pairs. Defaults to filtering for group STMLab.
               """                                       
               )):
            """
            API to fetch information about all groups within an instance.
            """
            import ast
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Fetch URL and HEADER
            url, header = gitlab.datacheck(token=Token.get_secret_value())
            # Default variables
            status_code = 500; result = {}
            try:
                r = requests.get(posixpath.join(url,"groups?per_page=100"), headers=header)
                # Avoid encoding or decoding errors.
                encoded_valid = str(r.content).encode("ascii","ignore").decode()
                decoded_valid = json.loads(ast.literal_eval(encoded_valid).decode("ascii",errors="ignore"))
                status_code = r.status_code; result = decoded_valid
                # Apply filter (if given)
                if Filter: result = [x for x in result if all([x[key] in [value] for key, value in Filter.items()])]
            except: pass
            # Return response if successful. An empty dictionary and an error code otherwise.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","packages"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab group service. List all packages available within a given group.
          """)            
        def api_gitlab_packages(
              Token: SecretStr =Query(...,
              description=
              """
              GitLab X-API-Token valid for the group.
              """
               ),
              GroupID: Optional[str] = Query("6371",
              description=
               """
               The group identifier. Defaults to group STMLab.
               """                                       
               ),
              Filter: Optional[dict] = Body({"package_type":"generic","name":"STMLab"},
              description=
               """
               Filtering results for key, value pairs. Defaults to filtering for the installer of STMLab.
               """                                       
               )):
            """
            API to fetch information about all packages with a group sorted by their version.
            """
            import operator
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Fetch URL and HEADER
            url, header = gitlab.datacheck(token=Token.get_secret_value())
            # Procedure
            status_code = 500; result = {}
            try:
                r = requests.get(posixpath.join(url,"groups",str(GroupID),"packages"), params={"exclude_subgroups":False}, headers= header)
                unsorted = [x for x in r.json() if all([x[key] in [value] for key, value in Filter.items()])]
                result =sorted(unsorted, key=operator.itemgetter("version"))[::-1]
                if result: status_code = 200; 
            except: pass
            # Return response if successful. An empty dictionary and an error code otherwise.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.put(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","job"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab job service. Run a given project pipeline job with non-default environment variables.
          """)            
        def api_gitlab_job(
              Token: SecretStr = Query(...,
              description=
              """
              GitLab X-API-Token valid for the project.
              """
              ), 
              ProjectID: Optional[str] = Query(str(12702),
              description=
               """
               The project identifier. Defaults to PyXMake's CI pipeline.
               """                                       
               ),
              Job: Optional[str] = Query("pyx_core_docs",
              description=
               """
               A job name. Defaults to a pipeline job for documenting PyXMake.
               """                                       
               )):
            """
            API to run a GitLab CI job with non-default environment variables.
            """
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Execute the command and return the result
            return JSONResponse(json.dumps(gitlab.pipeline(Token.get_secret_value(), ProjectID, job_name=Job)))
        
        @self.Router.put(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","pipeline"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab pipeline service. Run a given project pipeline with non-default environment variables.
          """)            
        def api_gitlab_pipeline(
              Token: SecretStr = Query(...,
              description=
              """
              GitLab X-API-Token valid for the project.
              """
              ), 
              ProjectID: Optional[str] =  Query(str(12702),
              description=
               """
               The project identifier. Defaults to PyXMake's CI pipeline.
               """                                       
               )):
            """
            API to run a GitLab CI pipeline.
            """
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Execute the command and return the result
            return JSONResponse(json.dumps(gitlab.pipeline(Token.get_secret_value(), ProjectID)))
        
        @self.Router.api_route(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","variable","{kind}"]), 
          methods=["GET", "PUT","POST", "PATCH","DELETE","HEAD"],
          tags=[str(self.__pyx_professional)], include_in_schema=False,
          openapi_extra={"requestBody": {"content": {"application/json": {},},"required": False},},
          description=
          """
          API for GitLab pipeline service. Interact with a given group-level variable. 
          """)            
        async def api_gitlab_variable(
              request: Request, 
              kind: Enum("VariableObjectKind",{"groups":"group","projects":"project"}),
              Token: SecretStr = Query(...,
              description=
              """
              GitLab X-API-Token valid for the call.
              """
              ), 
              ID: str =  Query(str(6371),
              description=
               """
               The project or group identifier. Defaults to group STMLab.
               """                                       
               )):
            """
            API shim to interact with GitLab variables on both project and group level. 
            """
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Fetch URL and HEADER
            url, header = gitlab.datacheck(token=Token.get_secret_value())
            # Get method from current request
            method = str(request.method).lower()
            # Default variables
            body=b""; headers={"Content-Type":"application/json"}; result = {}; status_code = 500;
            try: 
                # Obtain request body. This always exists - so always "checking" works just fine.
                body = await request.body()
                # Forward the request
                if body: body = json.loads(body)
                url = posixpath.join(url,str(kind.name), ID,"variables"); 
                # Add path parameter
                if isinstance(body,dict) and not method in ["post"]: url = posixpath.join(url,body.get("key","")); 
                # Call API
                r = requests.request(method, url, params=request.query_params, data=body, headers=header)
                # Collect the result
                status_code = r.status_code; result = r.content; headers.update(r.headers)
                try: headers.pop("Content-Encoding") # Remove encoding 
                except: pass
            except: pass
            # Return the forwarded response
            return Response(status_code=status_code, content=result, headers=headers)

        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","runner"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab service. Creates a GitLab runner dedicated for the given project registration token on FA-Services.
          """)            
        def api_gitlab_runner(
              Registration: str = Query(...,
              description=
              """
              GitLab registration token (mandatory).
              """
              ),
              Token: SecretStr = Query("",
              description=
              """
              Portainer X-API-Token.
              """
              )):
            """
            API to create a GitLab runner dedicated for the given project registration token.
            """
            # Local variables
            delimn = "_"; 
            # Default values
            is_service = True; with_tmpfs = True; with_persistent = True
            tmpfs = []; mounts = []; result = {}; status_code = 500;
            try: 
                from PyXMake.VTL import portainer #@UnresolvedImport
                from PyCODAC.API.Remote import Server
                # Procedure
                runner = str(delimn.join(["stmlab_runner",str(uuid.uuid4())]))
                umlshm = runner.split(delimn); umlshm.insert(2,"umlshm"); umlshm = str(delimn.join(umlshm))
                persistent = runner.split(delimn); persistent.insert(2,"persistent"); persistent = str(delimn.join(persistent))
                # Fetch base url and login information from the given token
                url, header = portainer.main(str(getattr(Token,"get_secret_value",str)()) or Server.auth['X-API-KEY'], datacheck=True); 
                # Get any valid docker agent and node
                node = str([x["Id"] for x in requests.get(posixpath.join(url,"endpoints"), headers=header).json()][-1])
                agent = list(random.choice(Server.GetNodeID()).keys())[0]; header.update({"X-PortainerAgent-Target":agent})
                # Add fast scratch storage and persistent docker storage (if requested)
                if (with_tmpfs or with_persistent) and is_service: 
                    mounts.extend([{"ReadOnly": False,"Source": umlshm,"Target": "/umlshm", "Type":"volume"}])
                    mounts.extend([{"ReadOnly": False,"Source": persistent,"Target": "/persistent", "Type":"volume"}])
                # Both mounts are temporary
                if mounts and (with_tmpfs and not with_persistent): tmpfs = [umlshm, persistent]
                elif mounts and (with_tmpfs and with_persistent): tmpfs = [umlshm]
                # Create a new shared memory volume with the host for each instance
                for x in tmpfs:
                    data = {"Name": x,"DriverOpts": {"device": "tmpfs","o": "rw,nosuid,nodev,exec","type": "tmpfs"}}
                    # Create a new associated shared storage volume for each instance.
                    r = requests.post(posixpath.join(url,"endpoints",node,"docker","volumes","create"), 
                                  json=data, headers=header); r.raise_for_status()
                # Create a persistent volume. Only meaningful when a service is created.
                if with_persistent and is_service: 
                    # Create a volume in the process
                    r = requests.post(posixpath.join(url,"endpoints",node,"docker","volumes","create"), 
                                      json={"Name":persistent}, headers=header); r.raise_for_status()
                # Create a new GitLab runner with predefined properties. Defined as a service definition
                data = {
                "Name": runner,"TaskTemplate": {
                "Placement": {"Constraints": ["node.hostname==%s" % agent]},
                "ContainerSpec": {"Image": "harbor.fa-services.intra.dlr.de/stmlab/orchestra:latest","Mounts": mounts,
                "Args": ["./runner.sh","--token=%s" % str(Registration),"--return=false","--locked=true"],
                "Env": ["DISK=80G","MEM=8G"], "Mode": {"Replicated": {"Replicas": 1}}}}
                }
                # Create as a new service
                if is_service: 
                    r = requests.post(posixpath.join(url,"endpoints",node,"docker","services","create"), json=data, headers=header); 
                    result = r.json()
                else: 
                    ## Just create a container instance (more stable)
                    # Apply changes
                    data = data["TaskTemplate"].get('ContainerSpec'); data["Cmd"] = data.pop("Args"); 
                    r = requests.post(posixpath.join(url,"endpoints",node,"docker","containers","create"), 
                          params={"name":runner}, json=data, headers=header); r.raise_for_status()
                    # Actually start the container.
                    r = requests.post(posixpath.join(url,"endpoints",node,"docker","containers",r.json()["Id"],"start"), headers=header); 
                    if r.status_code in [204,304,404]: result = "Success"
                if result: status_code = 200
            # Always exit gracefully
            except Exception: pass
            # Return a dictionary of projects with their id.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","gitlab","user"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for GitLab service. Returns the current user for a given API token.
          """)            
        def api_gitlab_user(
              Token: SecretStr = Query(...,
              description=
              """
              GitLab X-API-Token.
              """
              )):
            """
            API to get the current active user from an API Token.
            """
            # Import GitLab API interface from minimum working example
            from PyXMake.VTL import gitlab #@UnresolvedImport
            # Fetch URL and HEADER
            url, header = gitlab.datacheck(token=Token.get_secret_value())
            # Default values
            result = {}; status_code = 500;
            try: 
                r = requests.get(posixpath.join(url,"user"), headers= header); result = r.json()
                if result: status_code = r.status_code
            except: pass
            # Return a dictionary of projects with their id.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","portainer","user"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for Portainer service. Returns the current user for a given API token.
          """)            
        def api_portainer_user(
              Token: SecretStr = Query(...,
              description=
              """
              Portainer X-API-Token.
              """
              )):
            """
            API to get the current active user from an API Token.
            """
            # Default variables
            status_code = 500; result = []
            # Import Portainer API interface from minimum working example
            from PyXMake.VTL import portainer #@UnresolvedImport
            # Execute the command and return the result
            try: 
                result = portainer.main(Token.get_secret_value()); 
                # Result must be a list with one element.
                if isinstance(result, list): 
                    status_code = 200; result = result[0]
                # The token is invalid and result contains a message.
                else: status_code = 401
            except: pass
            # Return the current active user.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","shepard","user"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for Shepard service. Returns the current user for a given API token.
          """)            
        def api_shepard_user(
              Token: SecretStr = Query(...,
              description=
              """
              Shepard X-API-Token.
              """
              )):
            """
            API to get the current active user from an API Token.
            """
            # Default variables
            status_code = 500; result = {}
            try: 
                # Import Shepard API interface from minimum working example
                from PyCODAC.Tools.IOHandling import Shepard #@UnresolvedImport
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Execute the command and return the result
            try: 
                result = Shepard.GetUser(header= {'X-API-KEY':Token.get_secret_value()}, full=True); 
                # The token is valid and result contains the user.
                if result: status_code = 200; 
            except: pass
            # Return the current active user.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","shepard","{kind}"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
              description=
              """
              API for PyXMake. Browse through all publicly available Shepard identifiers present within the scope of this API.
              """ )       
        def api_shepard_show(
              kind: api_database()[0],
              ID: Optional[str] = Query(None,
              description=
              """
              An user-defined container ID.
              """
              ),
              Token: SecretStr = Query(None,
              description=
              """
              Shepard X-API-Token.
              """
              )):
            """
            API to connect to all available data identifiers using PyXMake.
            """
            # Default variables
            result = []; status_code = 500; delimn = "_"; 
            DB = ID or str(kind.name); options = api_database()[-1]
            try: 
                from PyCODAC.Tools.IOHandling import Shepard #@UnresolvedImport
                # Try non-default Shepard Token
                try: Shepard.SetHeader( {'X-API-KEY':Token.get_secret_value()} )
                except: pass
                finally: Shepard.GetContainerID(DB) # Check if file database can be accessed.
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Connect to an accessible data browser.
            try: 
                # Collect all public data
                vault = list(Utility.ArbitraryFlattening([ Shepard.GetContent(DB, query=options[str(kind.value)], latest=False) ]))
                result.extend([{ next(iter(x)) : {"id":x[next(iter(x))][0],"created":x[list(x.keys())[0]][-1],"parent":DB.split(delimn)[-1].lower()}} for x in vault])
                status_code = 200 # Result can be empty, but the command has succeeded anyways.
            except ConnectionRefusedError: 
                # Do not consider an empty time series as an error
                if options[str(kind.value)] in ["timeseries"]: status_code = 200
            except: 
                # If an ID is explicitly given and cannot be reached.
                if ID: return JSONResponse(status_code=404,content="The given ID '%s' cannot be resolved for kind '%s'" % (ID,options,options[str(kind.value)]),)
                pass # Fail gracefully        
            finally:
                result = list(Utility.ArbitraryFlattening(result))
            if result: status_code = 200
            # Present result to FAST API
            return JSONResponse(status_code=status_code, content=result,)
        
        @self.Router.delete(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","shepard","{kind}"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
              description=
              """
              API for PyXMake. Delete an available data object identifier present within the scope of this API.
              """ )       
        def api_shepard_delete(
              kind: api_database()[0],
              OID: Optional[str] = Query(...,
              description=
              """
              The object identifier of the data.
              """
              ),
              ID: Optional[str] = Query(None,
              description=
              """
              An user-defined container ID.
              """
              ),
              Token: SecretStr = Query(None,
              description=
              """
              Shepard X-API-Token.
              """
              )):
            """
            API to delete any available data identifier using PyXMake.
            """
            # Default variables
            result = []; status_code = 500; DB = ID or str(kind.name); options = api_database()[-1]
            try: 
                from PyCODAC.Tools.IOHandling import Shepard #@UnresolvedImport
                # Try non-default Shepard Token
                try: Shepard.SetHeader( {'X-API-KEY':Token.get_secret_value()} )
                except: pass
                finally: Shepard.GetContainerID(DB) # Check if file database can be accessed.
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Delete the requested object.
            try: 
                Shepard.DeleteContent(DB, OID, query=options[str(kind.value)], latest=False)
                status_code = 200; 
            except: 
                # If an ID is explicitly given and cannot be reached.
                if ID: return JSONResponse(status_code=404,content="The given ID '%s' cannot be resolved for kind '%s'" % (ID,options,options[str(kind.value)]),)
            finally: result = "Success" 
            # Present result to FAST API
            return JSONResponse(status_code=status_code, content=result)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","overleaf","session"]), tags=[str(self.__pyx_professional)], include_in_schema=False, 
          description=
          """
          API for Overleaf service. Creates a valid API session token for Overleaf to automate tasks.
          """)            
        def api_overleaf_session(
              Token: SecretStr = Query(...,
              description=
              """
              Credentials given as Overleaf X-API-Token with its value set to the result of: 
              "echo -n "<'YourUserName'>:<'YourPasswort'>" | base64"
              """
              ), 
              base_url: Optional[str] = Query("", include_in_schema=False, 
              description=
              """
              Base URL of the Overleaf instance in question. Defaults to Overleaf running on FA-Services.
              """)):
            """
            Creates a valid API session token for Overleaf.
            """
            # Default variables
            status_code = 500; result = {}
            # Import Overleaf API interface from minimum working example
            from PyXMake.Build.Make import Latex #@UnresolvedImport
            # Execute the command and return the result
            try: status_code, result = Latex.session(*base64.b64decode(Token.get_secret_value()).decode('utf-8').split(":",1), base_url=base_url, use_cache=False); 
            except: pass
            # Return the current active user.
            return JSONResponse(status_code=status_code,content=result,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","overleaf","show"]), tags=[str(self.__pyx_professional)], include_in_schema=False, 
          description=
          """
          API for Overleaf service. Compile an Overleaf project remotely and return all files.
          """)            
        def api_overleaf_show(
              Token: SecretStr = Query(...,
              description=
              """
              Credentials given as Overleaf X-API-Token with its value set to the result of: 
              "echo -n "<'YourUserName'>:<'YourPasswort'>" | base64"
              """
              ),
              ProjectID: str = Query(..., description=
              """
              An Overleaf Project ID.
              """
              ),
              base_url: Optional[str] = Query("", include_in_schema=False, description=
              """
              Base URL of the Overleaf instance in question. Defaults to Overleaf running on FA-Services.
              """)):
            """
            Compile an Overleaf project remotely and return all files.
            """
            # Default variables
            status_code = 500; result = {}
            # Import Overleaf API interface from minimum working example
            from PyXMake.Build.Make import Latex #@UnresolvedImport
            # Execute the command and return the result
            try: 
                result = Latex.show(ProjectID, *base64.b64decode(Token.get_secret_value()).decode('utf-8').split(":",1), base_url=base_url, use_cache=False) ; 
                if result: status_code = 200 ; 
            except: pass
            # Return the current active user.
            return JSONResponse(status_code=status_code,content=result,)

        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","overleaf","download","{kind}"]), tags=[str(self.__pyx_professional)], include_in_schema=False, 
          description=
          """
          API for Overleaf service. Compile an Overleaf project remotely and return all files.
          """)            
        def api_overleaf_download(
              kind: Enum("DataObjectKind",{"zip":"zip","pdf":"pdf"}), 
              Token: SecretStr = Query(...,
              description=
              """
              Credentials given as Overleaf X-API-Token with its value set to the result of: 
              "echo -n "<'YourUserName'>:<'YourPasswort'>" | base64"
              """
              ),
              ProjectID: str = Query(..., description=
              """
              An Overleaf Project ID.
              """
              ),
              base_url: Optional[str] = Query("", include_in_schema=False, description=
              """
              Base URL of the Overleaf instance in question. Defaults to Overleaf running on FA-Services.
              """)):
            """
            Compile an Overleaf project remotely and return all files.
            """
            # Import Overleaf API interface from minimum working example
            from PyXMake.Build.Make import Latex #@UnresolvedImport
            # Execute the command and return the result
            try: 
                with Utility.ChangedWorkingDirectory(VTL.Scratch):
                    FilePath = Latex.download(ProjectID, *base64.b64decode(Token.get_secret_value()).decode('utf-8').split(":",1), output_format=str(kind.value), base_url=base_url, use_cache=False) ; 
                    if not os.path.exists(FilePath): raise FileNotFoundError
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Present result to FAST API            
            return FileResponse(path=FilePath,filename=Utility.PathLeaf(FilePath))
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","time"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for time service. Get the current system time of this API in ISO 8601 format (UTC).
          """ )            
        def api_time_show(request: Request):
            """
            Get the current system time of this API in ISO 8601 format (UTC).
            """  
            # Initialize everything
            timestamp = "Unknown system time"
            # Construct the response
            try: 
                timestamp = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
                status_code = 200
            except: status_code = 500
            # Return current time in ISO 8601 format (UTC).
            return JSONResponse(status_code=status_code,content=timestamp,)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","time"]), tags=[str(self.__pyx_professional)], include_in_schema=False,
          description=
          """
          API for time service. Return the given time from any time format in UTC format (nanoseconds).
          """ )            
        def api_time_inspect(request: Request,
              Time: str = Query(...,
              description=
              """
              Arbitrary valid time string. The string is parsed into an internal date object.
              """
              )):
            """
            Return the given time from any time format in UTC format (nanoseconds).
            """
            from dateutil.parser import parse
            # Initialize everything
            timestamp = "Unknown input time"
            # Construct the response
            try: 
                timestamp = int(parse(Time).replace(tzinfo=datetime.timezone.utc).timestamp() * 1e9)
                status_code = 200
            except: status_code = 500
            # Return current time in UTC format (nanoseconds).
            return JSONResponse(status_code=status_code,content=timestamp,)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","secret"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for PyXMake. Show a list of all available secrets for a given token.
          """)            
        def api_secret_show(request: Request, 
              Token: SecretStr = Query(...,
              description=
              """
              Portainer X-API-Token. The token is stored in your personal user space.
              """
              )):
            """
            API to get the current active user from an API Token.
            """
            try: 
                from PyXMake.VTL import portainer #@UnresolvedImport
                result = portainer.main(Token.get_secret_value()); 
                if not isinstance(result, list): raise ValueError
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Operate fully in a temporary directory
            with Utility.TemporaryDirectory(): 
                # Fetch header and base address
                url, header = portainer.main(Token.get_secret_value(), datacheck=True); 
                # Create a new secret
                secret_url = posixpath.join(url,"endpoints",str([x["Id"] for x in requests.get(posixpath.join(url,"endpoints"), headers=header).json()][-1]),"docker","secrets")
                r = requests.get(secret_url, headers=header)
            # Return the current active user.
            return JSONResponse(status_code=r.status_code,content=r.json(),)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","secret"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for PyXMake. Create a new secret for the given token.
          """)            
        def api_secret_upload(request: Request, 
              payload: UploadFile = File(...,
              description=
              """
              Binary data stream.
              """
              ),
              Token: SecretStr = Query(...,
              description=
              """
              Portainer X-API-Token. The token is stored in your personal user space.
              """
              ),
              SecretID: str = Query(None,
              description=
              """
              An optional name for the secret. Defaults to the name of the given file.
              """
              )):
            """
            API to get the current active user from an API Token.
            """
            try: 
                from PyXMake.VTL import portainer #@UnresolvedImport
                result = portainer.main(Token.get_secret_value()); 
                if not isinstance(result, list): raise ValueError
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Operate fully in a temporary directory
            with Utility.TemporaryDirectory(): 
                # Collapse data block in current workspace
                with open(payload.filename,'wb+') as f: f.write(payload.file.read())
                with io.open(payload.filename,'r',encoding='utf-8')as f: content = f.read()
                # Create a base64 encoded string
                content = requests.post(str(request.url.scheme)+"://%s/2/PyXMake/api/encoding/base64" % self.APIBase, params={"message":content}, verify=False).json()
                url, header = portainer.main(Token.get_secret_value(), datacheck=True); 
                # Assemble request body
                body = { 'Data': content,'Name':SecretID or payload.filename,'Labels': None } ; 
                # Create a new secret
                secret_url = posixpath.join(url,"endpoints",
                str([x["Id"] for x in requests.get(posixpath.join(url,"endpoints"), headers=header).json()][-1]),"docker","secrets","create")
                r = requests.post(secret_url, json=body, headers=header)
            # Return the current active user.
            return JSONResponse(status_code=r.status_code,content=r.json(),)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","file","{kind}"]), tags=[str(self.__pyx_professional)], 
              description=
              """
              API for PyXMake. Browse through all available file identifiers present within the scope of this API.
              """ )       
        def api_file_show(request: Request, kind: FileManager):
            """
            API to connect to all available file identifiers using PyXMake.
            """
            # Default variables
            result = []; status_code = 500;
            try: 
                from PyCODAC.VTL import Fetch #@UnresolvedImport
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Initialize random seed generator
            rd = random.Random(); 
            # Connect to an accessible file browser.
            try: 
                # Collect all public data
                if str(kind.value) in ["all","public"]:
                    result = requests.get(str(request.url.scheme)+"://%s/2/PyXMake/api/shepard/file" % self.APIBase, verify=False).json()
                # Collect all private data
                if kind.value in ["all","private"]:
                    private = [];
                    for root, _, files in Utility.PathWalk(Fetch, startswith=(".","__")): 
                        if files and Utility.PathLeaf(root).split("_")[0].isnumeric(): 
                            private.extend([{x:{"parent":Utility.PathLeaf(root),"created":time.ctime(os.path.getctime(os.path.join(root,x)))}} for x in files])
                    # Add an unique identifier for compatibility
                    for i,x in enumerate(private):
                        # Create a pseudo-random UUID
                        rd.seed(int(i)); x[next(iter(x))].update({"id": str(uuid.UUID(int=rd.getrandbits(128), version=4))})
                        result.append(x)
            except: pass # Fail gracefully        
            finally:
                result = list(Utility.ArbitraryFlattening(result))
            if result: status_code = 200
            # Present result to FAST API
            return JSONResponse(status_code=status_code, content=result,)

        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","file"]), tags=[str(self.__pyx_professional)], 
              description=
              """
              API for PyXMake. Download a file from an available data source by its id.
              """ )       
        def api_file_download(request: Request, FileID: str = Query(...)):
            """
            API to upload a given file using PyXMake.
            """
            # Default variables
            FileDB = [data.name for data in api_database()[0] if data.value == Utility.PathLeaf(str(request.url).split("?")[0])][0]
            try: 
                from PyCODAC.VTL import Fetch #@UnresolvedImport
                from PyCODAC.Tools.IOHandling import Shepard #@UnresolvedImport
                Shepard.GetContainerID(FileDB) # Check if file database can be accessed.
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Test for data consistency
            try:
                # Fetch content from other service
                AllFiles = requests.get(str(request.url.scheme)+"://%s/2/PyXMake/api/file/all" % self.APIBase, verify=False).json()
                ListofIDs = [x[next(iter(x))].get("id") for x in AllFiles]
                if len(ListofIDs) != len(set(ListofIDs)): raise IndexError # List are not of equal length: There are duplicates, which should never happen.
            except: return JSONResponse(status_code=500,content="Internal database error: There are multiple files sharing the same ID.",)
            # Check if the given ID is valid. Return if False.
            if not FileID in ListofIDs: return JSONResponse(status_code=404,content="File not found",)
            # Operate fully in a temporary directory
            with Utility.TemporaryDirectory(): 
                # Collect meta data of the file in question. Required properties are its id, parent and name.
                data = [(x[next(iter(x))].get("id"),x[next(iter(x))].get("parent"),next(iter(x))) for x in AllFiles if FileID == x[next(iter(x))].get("id") ][0]
                try: 
                    # Try to download the file from internal vault. Allow multiple files sharing the same name. 
                    if FileDB.split("_")[-1].lower() in [data[1]]: FilePath = Shepard.DownloadFile(FileDB, FileID, latest=False)[0]
                    # An internal resource is requested. Provide a reference to its path.
                    else: FilePath = os.path.join(Fetch,data[1],data[-1])
                except IndexError: return JSONResponse(status_code=500,content="Internal database error: Permission denied.",)
            # Present result to FAST API            
            return FileResponse(path=FilePath,filename=Utility.PathLeaf(FilePath))
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","file","{kind}"]), tags=[str(self.__pyx_professional)], 
              description=
              """
              API for PyXMake. Connects an user with an available file browser and uploads the given data.
              """ )       
        def api_file_upload(request: Request,
              kind: Enum("ScopeObjectKind",{"local":"private","shared":"public"}),
              payload: UploadFile = File(...,
              description=
              """
              Binary data stream.
              """
              )):
            """
            API to upload a given file using PyXMake.
            """
            import functools
            # Default variables
            status_code = 500; 
            FileDB = [data.name for data in api_database()[0] if data.value ==Utility.PathLeaf(posixpath.dirname(str(request.url)))][0]
            try: 
                if str(kind.value) in ["public"]:
                    from PyCODAC.Tools.IOHandling import Shepard #@UnresolvedImport
                    Shepard.GetContainerID(FileDB) # Check if file database can be accessed.
                elif str(kind.value) in ["private"]:
                    from PyCODAC.Database import MatDB
            except ValueError: return JSONResponse(status_code=404,content="Service not available",)
            # Operate fully in a temporary directory
            with Utility.TemporaryDirectory(): 
                # Refer to MongoDB explicitly
                from PyCODAC.Database import Mongo
                # Collapse data block in current workspace
                with open(payload.filename,'wb+') as f: f.write(payload.file.read())
                # Upload the given file, including large file support.
                if str(kind.value) in ["public"]:
                    Shepard.UploadFile(FileDB, payload.filename, os.getcwd(), unique=False)
                    Shepard.UpdateContainer(FileDB, collections=Mongo.base_collection, latest=False)
                    # Return OID for the user
                    result = Shepard.GetContent(FileDB)[payload.filename]
                elif str(kind.value) in ["private"]:
                    # Store data inaccessible w/o its explicit id
                    url = functools.reduce(lambda a, kv: a.replace(*kv), (("eoddatamodel","filemanager"),("materials","files"),),MatDB.base_url)
                    result = [Utility.FileUpload(posixpath.join(url,""), payload.filename, None, verify=False).json()["file_id"],
                                   datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%SZ')]
                # This should never happen. 
                else: raise NotImplementedError
            if result: status_code = 200
            # Present result to FAST API
            return JSONResponse(status_code=status_code, content=result,)
        
        @self.Router.patch(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","file","format","{kind}"]), tags=[str(self.__pyx_professional)], 
              description=
              """
              API for PyXMake. Connects an user with various file formatting options present within the scope of this API.
              """ )       
        def api_file_converter(
              kind: Archive, 
              OutputID: Enum("FormatObjectKind",{"xls":"xls"}),
              SourceID: Optional[str] = Query("Settings.xlsx",
              description=
              """
              The name of the main file present in the supplied ZIP archive. The requested output format is given by OutputID.
              """),
              ZIP: UploadFile = File(...,
              description=
              """
              An compressed archive containing all additional files required for this job. This archive is updated and returned. All input files are preserved.
              It additionally acts as an on-demand temporary user directory. It prohibits access from other users preventing accidental interference.
              However, the scratch workspace is cleaned constantly. So please download your result immediately.
              """
              )):
            """
            API to connect to various file formatting options using PyXMake.
            """                
            # Check if an old file is present in the current workspace. Delete it.
            if os.path.exists(os.path.join(VTL.Scratch,ZIP.filename)): os.remove(os.path.join(VTL.Scratch,ZIP.filename))

            # Everything is done within a temporary directory. Update the uploaded ZIP folder with new content. Preserve the input.
            with Utility.TemporaryDirectory(VTL.Scratch), Utility.UpdateZIP(ZIP.filename, ZIP.file, VTL.Scratch, update=True):       
                # Procedure
                with Utility.FileOutput('result.log'):
                    try: 
                        # Create a legacy XLS file from input. Required for MRO process.
                        if str(OutputID.name) in ["xls"] : Utility.ConvertExcel(str(SourceID), os.getcwd())
                    except: print("File conversion error. Could not convert %s into %s format." % (str(SourceID), str(OutputID.value).upper(),) )
                pass
                
            # Present result to FAST API
            return FileResponse(path=os.path.join(VTL.Scratch,ZIP.filename),filename=ZIP.filename)
        
        @self.Router.get(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","image","{kind}"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for PyXMake. Obtain information about an image.
          """)            
        def api_image_show(kind: Enum("ImageObjectKind",{"public":"public","user":"user"}), 
              request: Request, 
              image: str = Query(...,
              description=
              """
              Fully qualified name of the image.
              """
              )):
            """
            API to obtain image information
            """
            # Default status code (Not Documented Error)
            result = {}
            try: 
                # Add the correct repository to the front.
                if kind.name in ["public"] and not image.startswith("docker.io"): search = posixpath.join("docker.io",str(image))
                # We cannot determine assume any named registry. The user is responsible
                elif kind.name in ["user"]: search = str(image)
                else: raise NotImplementedError
                # Refer to internal portainer reference.
                base_url = str(request.url.scheme)+"://%s/api/portainer" % self.APIBase
                # Use any active instance:
                r = requests.get(posixpath.join(base_url,"endpoints")); endpoint = [str(x["Id"]) for x in r.json()][-1]
                # Verify that the image exists. Download the image if not.
                requests.post(posixpath.join(base_url,"endpoints",endpoint,"docker","images","create"), params={"fromImage":search})
                # Return all information about the image as JSON.
                result.update(requests.get(posixpath.join(base_url,"endpoints",endpoint,"docker","images",image,"json")).json())
                # Success
                if result: return JSONResponse(status_code=200, content=result)
            # Something bad happened...
            except: return JSONResponse(status_code=404, content="Could not determine info for image %s. Image probably not in scope." % image)
        
        @self.Router.post(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","encoding","{kind}"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for PyXMake. Encode a given secret string.
          """)            
        def api_encode_message(kind: Enum("EncodingObjectKind",{"base64":"base64"}),
              message: SecretStr = Query(...,
              description=
              """
              Message (string) to be encoded
              """
              )):
            """
            API to encode a message
            """
            # Use internal base64 encryption method
            try: 
                message = message.get_secret_value()
                base64_message = Utility.GetDockerEncoding(message, encoding='utf-8')
                return JSONResponse(content=base64_message)
            except: return JSONResponse(404, content="Encoding failed.")
            
        @self.Router.put(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","notification","{kind}"]), tags=[str(self.__pyx_professional)],
          description=
          """
          API for PyXMake. Connect with a notification service to send arbitrary mail or Mattermost notifications.
          """ )            
        def api_notification(
              kind: Enum("NotificationObjectKind",{"mail":"mail","mattermoost":"mattermost"}), 
              recipient: str = Query(..., description=
              """
              Qualified mail address or mattermost channel.
              """
              ), 
              notification: dict = Body({"subject":"MyFancyHeader","content":"MyFancyMessage"},
              description=
              """
              A dictionary containing the subject line and the content.
              """
              )):
            """
            API for PyXMake. Connect with a notification service.
            """
            import tempfile
            
            from collections import defaultdict #@UnresolvedImport
            from PyXMake.Build import Make #@UnresolvedImport
            # Default status code (Not Documented Error)
            status_code = 500
            # Check whether a connection with FlexLM can be established or not.
            default_user = "f_testpa"; default_host = "cara.dlr.de"
            secrets = os.path.join(Utility.AsDrive("keys"),default_host)
            # Check for Mattermost notification first
            if kind.value in ["mattermost"]: 
                try: 
                    # Retain compatibility
                    payload={"text": notification.pop("text","") or "\n".join(
                                                [notification.pop("subject"),notification.pop("content")]), "username":notification.pop("username",str(kind.value).title())}
                    # Add all leftover keys
                    payload.update(notification)
                    requests.post(recipient, json=payload) 
                    # We executed the command successfully.
                    return JSONResponse(status_code=200,content="Success",)
                except: return JSONResponse(status_code=404,content="%s service not available" % str(kind.value).title(),)
            try: default_key = os.path.join(secrets,[x for x in os.listdir(secrets) if x.split(".")[-1] == x][0])
            except: return JSONResponse(status_code=404,content="Service not available",)
            # Fail gracefully
            try:
                # Operate fully in a temporary directory
                with Utility.TemporaryDirectory():
                    # Create a temporary file name
                    tmp =  str(next(tempfile._get_candidate_names()))
                    command = "echo '%s' | mail -s '%s' %s" % (notification["content"], notification["subject"], recipient, )
                    connect = Make.SSH("Notification",[]); connect.Settings(default_user, key=default_key, host=default_host, timeout=1)
                    # Execute the SSH script and log the result
                    with Utility.FileOutput(tmp):  Utility.SSHPopen(connect.ssh_client, ntpath.pathsep.join([command]),verbosity=2)
                    # Read logging information into memory
                    with open(tmp,"r") as f: content = f.read()
                # Success
                _ = json.dumps(content); status_code = 200
            # Prevent endless loops if service is not reachable
            except TimeoutError: return JSONResponse(status_code=404,content="%s service not available" % str(kind.value).title(),)
            except: pass
            # Just return a success status
            return JSONResponse(status_code=status_code,content="Success",)

## @class PyXMake.API.Frontend
# Class instance to define PyXMake's web API instance
class Frontend(Base,Backend):
    """
    Class instance to define PyXMake's server instance for a web API.
    """
    # Some immutable variables
    __pyx_api_delimn = "/"
    __pyx_doc_path = os.path.normpath(os.path.join(os.path.dirname(VTL.__file__),"doc","pyx_core","html"))
    __pyx_url_path  = __pyx_api_delimn.join(["https:","","fa_sw.pages.gitlab.dlr.de","stmlab",str(PyXMake.__name__),"index.html"])
    
    # These are the captions for the Swagger UI
    __pyx_guide = "Guide"
    __pyx_interface = "Interface"
    __pyx_professional = "Professional"
        
    def __init__(self, *args, **kwargs):
        """
        Initialization of PyXMake's Frontend API.
        """        
        super(Frontend, self).__init__(*args, **kwargs)
        self.APIObjectKind = "Frontend"
        
        # Collection API meta data information
        self.APIMeta = kwargs.get("Meta", {})
        
        # Added API subsection meta data information
        self.APITags = [
            {"name": self.__pyx_guide,"description": "Operations to obtain server documentation."},
            {"name": self.__pyx_interface,"description": "Operations for all users."},
            {"name": self.__pyx_professional,"description": "Operations for experienced users and developers."}]
        
        # Added default swagger mode. Defaults to hiding the schema section
        self.APISwagger = {"defaultModelsExpandDepth": -1}
        
        # Redefine API to create the correct description
        self.API = FastAPI(title="PyXMake API", 
                          # Use internal package version instead of global package number. Kept for backwards compatibility
                          version = getattr(PyXMake,"__version__", self.APIMeta.pop("version","1.0.0")), 
                          description ="Simplifying complex compilations",
                          docs_url = self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"api","documentation"]), 
                          swagger_ui_parameters = self.APISwagger, openapi_tags = self.APITags, **self.APIMeta)
        
        # Define variables for self access
        self.APIHost = kwargs.get("HostID",socket.gethostname())
        self.APIPort = kwargs.get("PortID",str(8020))
        self.APIBase = ":".join([self.APIHost,self.APIPort])
        
        # Define custom redirect for current instance
        self.RedirectException(self.__pyx_api_delimn.join(["",str(2),str(PyXMake.__name__),"api","documentation"]))
        
        # Mount static HTML files created by DoxyGen to created web application 
        self.StaticFiles(self.__pyx_api_delimn.join(["",str(PyXMake.__name__),"dev","documentation"]),self.__pyx_doc_path)
        
        # Allow cross-site references
        self.API.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
        
        # Add all API methods explicitly
        Backend.__init__(self, *args, **kwargs)
        
if __name__ == '__main__':    
    pass