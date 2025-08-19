#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

import multiprocessing
import uvicorn
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from typing import Callable, Any, Literal, TypeVar
from fastapi import FastAPI
import gradio as gr
from fastmcp.prompts.prompt import PromptResult
from fastapi.middleware.cors import CORSMiddleware
from collections.abc import Awaitable

from ..Application.Abstractions.base_manager_mcp_service import BaseManagerMCPService
from ..Application.Logging.manager_logging import ManagerLogging
from ..Utilites.ext_global_setting import ExtGlobalSetting
from ..Domain.Configure.global_setting_service import GlobalSettingService
from ..Application.DependencyInjection.resolve_provider import ResolveProviderFWDI
from ..Application.Abstractions.base_controller import BaseControllerFWDI

from ..Application.dependency_injection import DependencyInjection as ApplicationDependencyInjection
from ..Persistence.dependency_injection import DependencyInjection as PersistenceDependencyInjection
from ..Infrastructure.dependency_injection import DependencyInjection as InfrastructureDependencyInjection

T = TypeVar('T', bound='WebApplication')

class WebApplication():
    def __init__(self, config:GlobalSettingService = None, **kwargs):
        from ..Application.Logging.manager_logging import ManagerLogging
        from .web_application_builder import WebApplicationBuilder
                
        if config is None:
            config = GlobalSettingService
        
        self._config:GlobalSettingService = config
        self.__log__ = ManagerLogging.get_logging('WebApplication', self._config) #SysLogging(logging_level=TypeLogging.DEBUG, filename='WebApplication')
        
        self.__log__(f"{__name__}:{kwargs}")
        self.__app:FastAPI = FastAPI()
        self.instance:'WebApplicationBuilder' = None
        self.mcp_services:BaseManagerMCPService = None
        
        self.resolver:ResolveProviderFWDI = None
        self.Name:str = kwargs['name'] if 'name' in kwargs else ''

    @property
    def Debug(self)->bool:
        return self.__debug

    @property
    def app(self)->FastAPI:
        return self.__app

    def has_mcp(self)->bool:
        return True if self.instance.mcp_services.count() else False

    def update_cors(self, 
                    origins:list[str], 
                    allow_credentials:bool, 
                    allow_methods:list[str], 
                    allow_headers:list[str]):
        try:
            self.__app.add_middleware(
                                CORSMiddleware,
                                allow_origins=origins,  # List of allowed origins
                                allow_credentials=allow_credentials,  # Allow credentials (cookies, authorization headers)
                                allow_methods=allow_methods,  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
                                allow_headers=allow_headers,  # Allow all headers
                            )
            return True
        except Exception as ex:
            self.__log__(f"ERROR:{ex}", 'error')
            return False

    def map_controller(self, controller:BaseControllerFWDI)->None:
        self.__log__(f"{__name__}:{controller}")
        if hasattr(controller, "routes"):
            self.__app.include_router(controller)
        else:
            raise Exception(f"{controller} has no have attribute routes !")

    def add_web_page(self, inst: gr.Blocks, path:str="/panel", is_auth:bool=False, allowed_paths:list[str]=None):
        from ..Presentation.DefaultControllers.http_auth import HttpAuthFWDI

        self.__log__(f"{__name__}:{path}:{inst}", 'debug')
        if not is_auth:
            self.__app = gr.mount_gradio_app(self.__app, inst, path=path, allowed_paths=allowed_paths, favicon_path='icons')
        else:
            self.__app = gr.mount_gradio_app(self.__app, inst, path=path, auth=HttpAuthFWDI.login, allowed_paths=allowed_paths, favicon_path='icons')
    
    def map_route(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_route(path=path, route=endpoint)

    def map_get(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["GET"])
    
    def map_post(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["POST"])

    def map_delete(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["DELETE"])

    def map_put(self, path:str, endpoint:Callable[..., Any]):
        self.__log__(f"{__name__}:{path}:{endpoint}", 'debug')
        self.__app.add_api_route(path=path, endpoint=endpoint, methods=["PUT"])
    
    def add_tool(self, mcp_name:str, fn_tool:Callable[..., Any], description:str, tags:set[str]=str(), name:str=str(), title:str=str()):
        self.instance.mcp_services[mcp_name].add_tool(fn_tool=fn_tool, 
                                                      description=description, 
                                                      tags=tags, 
                                                      name=name, 
                                                      title=title)
    
    def add_prompt(self, mcp_name:str, fn_tool:Callable[..., PromptResult | Awaitable[PromptResult]], description:str, tags:set[str]=str(), name:str=str(), title:str=str()):
        self.instance.mcp_services[mcp_name].add_prompt(fn_tool=fn_tool, 
                                                      description=description, 
                                                      tags=tags, 
                                                      name=name, 
                                                      title=title)
        
    def add_resource(self, mcp_name:str, fn_tool:Callable[..., Any], uri:str, description:str, tags:set[str]=str(), name:str=str(), title:str=str()):
        self.instance.mcp_services[mcp_name].add_resource(fn_tool=fn_tool,
                                                        uri=uri,
                                                        description=description, 
                                                        tags=tags, 
                                                        name=name, 
                                                        title=title)        

    @classmethod
    def create_builder(cls:type[T], **kwargs):
        from .web_application_builder import WebApplicationBuilder
        ExtGlobalSetting.load('service_config.json')

        __log__ = ManagerLogging.get_logging('WebApplicationBuilder', GlobalSettingService)
        
        webapp_instance = cls(GlobalSettingService, **kwargs)
        webapp_instance.instance = WebApplicationBuilder(webapp_instance)
        
        #----------------------DEFAULT SERVICES DEPENDENCY------------------------------------
        
        __log__(f"Create dependency injection Persistence")
        PersistenceDependencyInjection.AddPersistence(webapp_instance.instance.services)
        __log__(f"Create dependency injection Application")
        ApplicationDependencyInjection.AddApplication(webapp_instance.instance.services)
        __log__(f"Create dependency injection Infrastructure")
        InfrastructureDependencyInjection.AddInfrastructure(webapp_instance.instance.services)
        
        from ..Presentation.dependency_injection import DependencyInjection as PresentationDependencyInjection
        PresentationDependencyInjection.AddPresentation(webapp_instance.instance.services)
        
        #----------------------/DEFAULT SERVICES DEPENDENCY-----------------------------------

        return webapp_instance.instance
    
    def __run_rest(self, **kwargs):
        self.__log__(f"Run service:{__name__}:{kwargs}")
        if not kwargs:
            if GlobalSettingService.ssl_keyfile and GlobalSettingService.ssl_certfile:
                self.__app.add_middleware(HTTPSRedirectMiddleware)

                uvicorn.run(self.__app, 
                            host=GlobalSettingService.current_host, 
                            port=GlobalSettingService.current_port, 
                            ssl_keyfile=GlobalSettingService.ssl_keyfile,
                            ssl_certfile=GlobalSettingService.ssl_certfile,
                            ssl_keyfile_password=GlobalSettingService.ssl_keyfile_password,
                            )
            else:
                uvicorn.run(self.__app, host=GlobalSettingService.current_host, port=GlobalSettingService.current_port)
        else:
            GlobalSettingService.current_host = kwargs.get('host', 'localhost')
            GlobalSettingService.current_port = kwargs.get('port', 5000)
            GlobalSettingService.ssl_keyfile = kwargs.get('ssl_keyfile', "")
            GlobalSettingService.ssl_certfile = kwargs.get('ssl_certfile', "")
            GlobalSettingService.ssl_keyfile_password = kwargs.get('ssl_keyfile_password', "")
            
            # ssl_keyfile="/etc/letsencrypt/live/my_domain/privkey.pem", 
            # ssl_certfile="/etc/letsencrypt/live/my_domain/fullchain.pem"
            
            # ssl_keyfile="./key.pem",
            # ssl_certfile="./cert.pem",
            
            # ssl_keyfile="/path/to/your/private.key",
            # ssl_certfile="/path/to/your/certificate.crt"

            uvicorn.run(self.__app, **kwargs)
    
    def __run_mcp(self, **kwargs):
        if kwargs:
            self.instance.mcp_services.run(**kwargs)
        else:
            self.instance.mcp_services.run()
    
    def __multi_run(self, **kwargs):
        processes = []

        rest_srv = multiprocessing.Process(target=self.__run_rest, kwargs=kwargs)
        processes.append(rest_srv)

        mcp_srv = multiprocessing.Process(target=self.__run_mcp, kwargs=kwargs)
        processes.append(mcp_srv)
        
        for p in processes:        
            p.start()

        for p in processes:
            p.join()

    def run(self, mode:Literal['REST', 'MCP', 'MULTI'] = None, **kwargs):
        if mode:
            match mode:
                case 'REST':
                    self.__run_rest(**kwargs)
                case 'MCP':
                    self.__run_mcp(**kwargs)
                case 'MULTI':
                    self.__multi_run(**kwargs)
        else:
            if self.has_mcp():
                self.__multi_run(**kwargs)
            elif not self.has_mcp():
                self.__run_rest(**kwargs)
            else:
                raise Exception("Error start service without any endpoint or tools")