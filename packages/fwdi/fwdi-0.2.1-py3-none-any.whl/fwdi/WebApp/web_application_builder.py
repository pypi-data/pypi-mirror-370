#        _       __        __    __________    _____     __   __     __
#   	/ \	    |  |	  |__|  |__________|  |  _  \   |__|  \ \   / /
#      / _ \	|  |	   __       |  |      | |_)  |   __    \ \_/ /   Alitrix - Modern NLP
#     / /_\ \	|  |	  |  |      |  |      |  _  /   |  |    } _ {    Languages: Python, C#
#    / _____ \	|  |____  |  |      |  |      | | \ \   |  |   / / \ \   http://github.com/Alitrix
#   /_/     \_\	|_______| |__|	    |__|      |_|  \_\  |__|  /_/   \_\

# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2020-2021 The Alitrix Authors <http://github.com/Alitrix>

from typing import TypeVar
from fastapi.security import OAuth2PasswordBearer

from ..Application.MCP.manager_mcp_service import ManagerMCPService
from ..Application.Abstractions.base_manager_mcp_service import BaseManagerMCPService
from ..Application.Abstractions.base_mcp_service import BaseMCPService
from ..Application.Logging.manager_logging import ManagerLogging
from ..Application.Abstractions.base_service_collection import BaseServiceCollectionFWDI
from ..Application.DependencyInjection.resolve_provider import ResolveProviderFWDI
from ..Application.DependencyInjection.service_collection import ServiceCollectionFWDI
from ..Persistence.default_init_db import DefaultInitializeDB
from ..Application.Abstractions.base_jwt_service_instance import BaseAuthServiceV2FWDI
from ..Application.Abstractions.base_jwt_service import BaseAuthServiceFWDI

T = TypeVar('T')


class WebApplicationBuilder():
    def __init__(self, web_app_inst:T) -> None:
        self.__log__ = ManagerLogging.get_logging('WebApplicationBuilder', web_app_inst._config)
        self.__log__(f"{__name__}:{web_app_inst}")
        self.__instance_app:type[T] = web_app_inst
        self.services:BaseServiceCollectionFWDI = ServiceCollectionFWDI()
        self.mcp_services:BaseManagerMCPService = ManagerMCPService()
        self.__scopes:dict[str, str] = {}
        self.__is_build:bool = False

    def build(self)-> type[T]:
        from ..Presentation.dependency_injection import DependencyInjection as DependencyInjectionPresentation
        from ..Utilites.dependency_injection import DependencyInjection as DependencyInjectionUtilites

        if self.__is_build:
            raise Exception('Error is already build.')
        
        self.__log__(f"Build services")
        
        self.__instance_app.instance = self
        self.__instance_app.resolver = ResolveProviderFWDI(self.services.GenerateContainer())
        
        #---------------------- DEFAULT WEB CONTROLLER SERVICES ------------------------------------
        self.__log__(f"Create dependency injection Utilites")
        DependencyInjectionUtilites.AddUtilites(self.services)
        self.__log__(f"Create dependency injection Presentation")
        DependencyInjectionPresentation.AddEndpoints(self.__instance_app)
        #DependencyInjectionPresentation.AddAdminPanel(self.__instance_app)
        
        #---------------------- /DEFAULT WEB CONTROLLER SERVICES -----------------------------------
        self.__log__(f"Inititalize OAuth2PasswordBearer: scope:{self.__scopes}")
        BaseAuthServiceV2FWDI.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scopes=self.__scopes,) if len(self.__scopes) > 0 else OAuth2PasswordBearer(tokenUrl="token")
        BaseAuthServiceFWDI.oauth2_scheme = BaseAuthServiceV2FWDI.oauth2_scheme
        self.__log__(f"Inititalize DB")
        DefaultInitializeDB.init_db(self.__scopes)
        self.__is_build = True
        
        return self.__instance_app
    
    def add_scope(self, scopes:dict[str,str]):
        if self.__is_build:
            raise Exception('Error add dependency after build')
        
        for item in scopes.items():
            if not item in self.__scopes:
                self.__scopes[item[0]] = item[1]
    
    def add_health_checks(self):
        if self.__is_build:
            raise Exception('Error add dependency after build')
        
        from ..Presentation.dependency_injection import DependencyInjection as DependencyInjectionPresentation
        DependencyInjectionPresentation.AddHealthChecks(self.__instance_app)
    
    def add_redirect_root_page(self, new_url:str):
        from ..Presentation.dependency_injection import DependencyInjection as DependencyInjectionPresentation
        DependencyInjectionPresentation.AddRedirectRootPage(self.__instance_app, new_url)
    
    def add_mcp_service(self, name:str, instructions:str, host:str='0.0.0.0', port:int=5000)->BaseMCPService:
        self.mcp_services.add_service(name=name, instructions=instructions, host=host, port=port)