# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptors hook into imports to modify third-party module behavior.

"""

from __future__ import unicode_literals
import sys

try:
    from importlib.machinery import ModuleSpec
except ImportError:
    pass

# These definitions must come before the subsequent imports to avoid a circular reference.
URL_PROPERTY_MAX_LEN = 100
HOST_PROPERTY_MAX_LEN = 50
DB_NAME_PROPERTY_MAX_LEN = 50
VENDOR_PROPERTY_MAX_LEN = 50

from . import cache, frameworks, http, logging, mongodb, sql
from appdynamics.lang import reload
from appdynamics import config
from appdynamics.agent.services.proxycontrol import AgentMetaDataInfo

SUPPORTED_FRAMEWORKS = {'bottle', 'flask', 'cherrypy', 'fastapi', 'django', 'tornado', 'pyramid', 'aiohttp'}

BT_INTERCEPTORS = (
    # Entry points
    ('bottle', frameworks.intercept_bottle),
    ('flask', frameworks.intercept_flask),
    ('django.core.handlers.wsgi', frameworks.intercept_django_wsgi_handler),
    ('django.core.handlers.base', frameworks.intercept_django_base_handler),
    ('cherrypy', frameworks.intercept_cherrypy),
    ('pyramid.router', frameworks.intercept_pyramid),
    ('tornado.web', frameworks.intercept_tornado_web),
    ('fastapi', frameworks.intercept_fastapi),
    ('aiohttp.web', frameworks.intercept_aiohttp_web),
    ('uvicorn.middleware.proxy_headers', frameworks.intercept_uvicorn),

    # HTTP exit calls
    ('httplib', http.intercept_httplib),
    ('http.client', http.intercept_httplib),
    ('urllib3', http.intercept_urllib3),
    ('requests', http.intercept_requests),
    ('boto.https_connection', http.intercept_boto),
    ('tornado.httpclient', http.intercept_tornado_httpclient),
    ('aiohttp', http.intercept_aiohttp_client),


    # SQL exit calls
    ('cx_Oracle', sql.cx_oracle.intercept_cx_oracle_connection),
    ('psycopg2', sql.psycopg2.intercept_psycopg2_connection),
    ('pymysql.connections', sql.pymysql.intercept_pymysql_connections),
    ('mysql.connector.connection', sql.mysql_connector.intercept_mysql_connector_connection),
    ('MySQLdb.connections', sql.mysqldb.intercept_MySQLdb_connection),
    ('tormysql.client', sql.tormysql.intercept_tormysql_client),

    # Caches
    ('redis.connection', cache.intercept_redis),
    ('memcache', cache.intercept_memcache),

    # Logging
    ('logging', logging.intercept_logging),

    # MongoDB
    ('pymongo', mongodb.intercept_pymongo),
)

# Instrumentating only when flag is enable for ENABLE_OPENAI
if config.ENABLE_OPENAI:
    BT_INTERCEPTORS += ('openai', http.intercept_openai),

# Instrumentating only when flag is enable for ENABLE_LANGCHAIN
if config.ENABLE_LANGCHAIN:
    BT_INTERCEPTORS += ('langchain_ollama.llms', frameworks.intercept_langchain_ollama_llms),
    BT_INTERCEPTORS += ('langchain_ollama.embeddings', frameworks.intercept_langchain_ollama_embeddings),
    BT_INTERCEPTORS += ('langchain_ollama.chat_models',
                        frameworks.intercept_langchain_ollama_chat_models),

    BT_INTERCEPTORS += ('langchain_community.llms', frameworks.intercept_langchain_community_llms),
    BT_INTERCEPTORS += ('langchain_community.chat_models',
                        frameworks.intercept_langchain_community_chat_models),
    BT_INTERCEPTORS += ('langchain_community.embeddings', frameworks.intercept_langchain_community_embeddings),
    BT_INTERCEPTORS += ('langchain_core.language_models', frameworks.intercept_langchain_core_language_models),

    BT_INTERCEPTORS += ('chromadb.api.models.Collection', sql.chromadb.intercept_chromadb_similarity_search),
    BT_INTERCEPTORS += ('langchain_community.vectorstores.chroma',
                        sql.chromadb.intercept_chromadb_collection_operations),
    BT_INTERCEPTORS += ('langchain_chroma.vectorstores', sql.chromadb.intercept_chromadb_collection_operations),

    BT_INTERCEPTORS += ('langchain_community.vectorstores.pgvector', sql.pgvector.intercept_pg_vector),
    BT_INTERCEPTORS += ('langchain_postgres.vectorstores', sql.pgvector.intercept_langchain_postgres),

    # langchain-{provider} integration packages, for vectorstores, can be added via config flag:
    if isinstance(config.LANGCHAIN_VECTORSTORES_INSTRUMENTED_MODULES, list):
        for vectorstore_module in config.LANGCHAIN_VECTORSTORES_INSTRUMENTED_MODULES:
            BT_INTERCEPTORS +=  (vectorstore_module, frameworks.intercept_langchain_vendorspecific_vectorstores),
    # e.g. ('langchain_postgres', frameworks.intercept_langchain_vendorspecific_vectorstores) 
    
    # langchain community all vectorstores instrumentation:
    BT_INTERCEPTORS += ('langchain_community.vectorstores', frameworks.intercept_langchain_community_vectorstores),    


if config.ENABLE_BEDROCK:
    BT_INTERCEPTORS += ('botocore.client', http.intercept_bedrock),


def add_hook(agent):
    """Add the module interceptor hook for AppDynamics, if it's not already registered.

    """

    interceptor = ModuleInterceptor(agent)
    sys.meta_path.insert(0, interceptor)
    return interceptor


class ModuleInterceptor(object):
    """Intercepts finding and loading modules in order to monkey patch them on load.

    """

    def __init__(self, agent):
        super(ModuleInterceptor, self).__init__()
        self.agent = agent
        self.module_hooks = {}
        self.intercepted_modules = set()

    def find_spec(self, full_name, path, target=None):
        if full_name in self.module_hooks:
            return ModuleSpec(full_name, self)
        return None

    def find_module(self, full_name, path=None):
        if full_name in self.module_hooks:
            return self
        return None

    def load_module(self, name):
        # Remove the module from the list of hooks so that we never see it again.
        hooks = self.module_hooks.pop(name, [])

        for framework in SUPPORTED_FRAMEWORKS:
            if framework in name:
                AgentMetaDataInfo.set_framework_name(framework)

        if name in sys.modules:
            # Already been loaded. Return it as is.
            return sys.modules[name]

        self.agent.logger.debug('Intercepting import %s', name)

        __import__(name)  # __import__('a.b.c') returns <module a>, not <module a.b.c>
        module = sys.modules[name]  # ...so get <module a.b.c> from sys.modules

        self._intercept_module(module, hooks)
        return module

    def call_on_import(self, module_name, cb):
        if module_name in sys.modules:
            self._intercept_module(sys.modules[module_name], [cb])
        else:
            self.module_hooks.setdefault(module_name, [])
            self.module_hooks[module_name].append(cb)

    def _intercept_module(self, module, hooks):
        try:
            for hook in hooks:
                self.agent.logger.debug('Running %s hook %r', module.__name__, hook)
                hook(self.agent, module)
            self.intercepted_modules.add(module)
        except:
            self.agent.logger.exception('Exception in %s hook.', module.__name__)

            # Re-import to ensure the module hasn't been partially patched.
            self.agent.logger.debug('Re-importing %s after error in module hook', module.__name__)
            reload(module)
