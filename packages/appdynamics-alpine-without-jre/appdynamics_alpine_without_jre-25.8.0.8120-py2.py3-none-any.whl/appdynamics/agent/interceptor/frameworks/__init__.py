# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Entry-point interceptors for various web/application frameworks.

"""

from __future__ import unicode_literals

from .bottle import intercept_bottle
from .flask import intercept_flask
from .django import intercept_django_wsgi_handler, intercept_django_base_handler
from .cherrypy import intercept_cherrypy
from .pyramid import intercept_pyramid
from .tornado_web import intercept_tornado_web
from .fastapi import intercept_fastapi
from .aiohttp_web import intercept_aiohttp_web
from .langchain import intercept_langchain_core_language_models
from .langchain import intercept_langchain_community_llms
from .langchain import intercept_langchain_community_embeddings
from .langchain import intercept_langchain_community_chat_models
from .langchain import intercept_langchain_ollama_llms
from .langchain import intercept_langchain_ollama_embeddings
from .langchain import intercept_langchain_ollama_chat_models
from .langchain_vectorstores import intercept_langchain_community_vectorstores
from .langchain_vectorstores import intercept_langchain_vendorspecific_vectorstores
from .uvicorn import intercept_uvicorn

__all__ = [
    'intercept_bottle',
    'intercept_flask',
    'intercept_django_wsgi_handler',
    'intercept_django_base_handler',
    'intercept_cherrypy',
    'intercept_pyramid',
    'intercept_tornado_web',
    'intercept_fastapi',
    'intercept_aiohttp_web',
    'intercept_uvicorn',
    'intercept_langchain_community_llms',
    'intercept_langchain_community_chat_models',
    'intercept_langchain_core_language_models',
    'intercept_langchain_community_embeddings',
    'intercept_langchain_ollama_llms',
    'intercept_langchain_ollama_embeddings',
    'intercept_langchain_ollama_chat_models',
    'intercept_langchain_community_vectorstores',
    'intercept_langchain_vendorspecific_vectorstores'
]
