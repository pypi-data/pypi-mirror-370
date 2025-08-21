from __future__ import unicode_literals

from ..base import ExitCallInterceptor, BaseInterceptor
from appdynamics.agent.models.exitcalls import EXIT_DB, EXIT_SUBTYPE_DB
from appdynamics.lib import MissingConfigException
import appdynamics.agent.interceptor.utils.langchain_utils as langchain_utils
from appdynamics.agent.interceptor.utils.langchain_utils import LangchainConstants
import threading
from appdynamics import config
import contextvars


class ChromadbInterceptor(ExitCallInterceptor):

    def __init__(self, agent, cls):
        super(ChromadbInterceptor, self).__init__(agent, cls)
        self.num = 0

    def get_db_backend(self, client_obj):
        host = 'unknown'
        port = 'unknown'
        naming_format_string = None
        if "fastapi" in client_obj.__class__.__name__.lower():
            naming_format_string = '{HOST}:{PORT} - {DATABASE} - {VENDOR} - {VERSION}'
            try:
                url_string = getattr(client_obj, '_api_url', None)
                if url_string:
                    host_port_path = url_string.split('//')[1]
                    host_port = host_port_path.split('/')[0]
                    host = host_port.split(':')[0]
                    port = host_port.split(':')[1]
            except Exception as exc:
                self.agent.logger.warn(f"Error occured while parsing chromadb backend props: {repr(exc)}")
        else:
            host = 'localhost'
            naming_format_string = '{HOST} - {DATABASE} - {VENDOR} - {VERSION}'

        backend_properties = {
            'VENDOR': 'Chroma',
            'HOST': str(host),
            'PORT': str(port),
            'DATABASE': 'ChromaDB',
            'VERSION': 'unknown',
        }
        return backend_properties, naming_format_string

    def report_metrics_end_exit_call(self, exit_call, db_input_query, response_obj, query_type, err):
        if exit_call:
            if config.ENABLE_GENAI_DATA_CAPTURE and db_input_query:
                exit_call.optional_properties["VectorDB input query"] = str(db_input_query)
            if config.ENABLE_GENAI_DATA_CAPTURE and response_obj:
                exit_call.optional_properties["VectorDB response"] = self.get_db_output_res(response_obj)
        self.end_exit_call(exit_call)

    def run_command(self, command_func, *args, **kwargs):
        response_obj = None
        bt = self.bt
        backend = None
        try:
            client_obj = getattr(args[0], '_client', None)
            if client_obj:
                if self.agent.backend_registry is None:
                    raise MissingConfigException
                backend_properties, naming_format_string = self.get_db_backend(client_obj)
                backend = self.agent.backend_registry.get_backend(EXIT_DB, EXIT_SUBTYPE_DB,
                                                                  backend_properties, naming_format_string)
        except MissingConfigException:
            pass
        except Exception as e:
            self.agent.logger.error(f"Error occured while creating appd backend: {repr(e)}")

        query_type = getattr(command_func, '__name__', 'Query')
        db_input_query = None
        # for Collection.upsert operation, db query string is not retrieved from appd_db_query
        if "appd_db_query" in kwargs:
            db_input_query = kwargs.get('appd_db_query')
            kwargs.pop("appd_db_query")
        elif "documents" in kwargs:
            db_input_query = kwargs.get('documents')

        exit_call = None
        err = False
        try:
            if bt and backend:
                exit_call = self.start_exit_call(bt, backend, operation=f"Collection.{query_type}")
            response_obj = command_func(*args, **kwargs)
        except:
            err = True
            raise
        finally:
            self.report_metrics_end_exit_call(exit_call, db_input_query, response_obj, query_type, err)
        return response_obj

    def get_db_output_res(self, create_response):
        db_output_res = []
        try:
            for result in zip(create_response["distances"][0],
                              create_response["documents"][0],
                              create_response["metadatas"][0]):
                score_doc_dict = dict()
                score_doc_dict["Search score"] = result[0]
                score_doc_dict["Document"] = result[1]
                score_doc_dict["Metadata"] = result[2]
                db_output_res.append(score_doc_dict)
        except Exception as exc:
            self.agent.logger.warn(f"Error occured while parsing vectorDB response = {str(exc)}")
        return db_output_res


class ChromaQuerySearchInterceptor(BaseInterceptor):
    
    def __init__(self, agent, cls):
        super().__init__(agent, cls)
        self.agent = agent
        self.cls = cls
        self.threadlocal_storage = threading.local()
        self.is_async_caller = contextvars.ContextVar('is_async_caller', default=False)

    def search(self, search, *args, **kwargs):
        # for stashing query string used in the exit call context and populating in SEC
        appd_db_query = None
        method_name = search.__name__
        if config.ENABLE_GENAI_DATA_CAPTURE and method_name in ['similarity_search',
            'similarity_search_with_score',
            'max_marginal_relevance_search',
            'max_marginal_relevance_search_with_score']:
            if 'query' in kwargs:
                appd_db_query = kwargs.get('query')
            elif args and len(args) > 1:
                appd_db_query = args[1]

        # report chroma search query metrics, repetition of code in langchain_vectorstores.py
        # as double patching same method didn't work

        # metrics were already reported in async asearch call, which might have called this 'search' 
        # in a different thread
        if self.is_async_caller.get():
            return search(*args, **kwargs)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = search.__name__
        self.threadlocal_storage.entry_method = method_name
        langchain_utils.initialize_and_start_timer_obj(self.threadlocal_storage, self.agent)
        try:
            response = search(*args, appd_db_query=appd_db_query, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            langchain_utils.set_search_score_metric_vectordb(reporting_values, response)
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.threadlocal_storage, self.cls, self.agent)
            self.threadlocal_storage.entry_method = None
        return response

    async def asearch(self, asearch, *args, **kwargs):
        self.is_async_caller.set(True)
        # report pgvector search query metrics, repetition of code in langchain_vectorstores.py
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = asearch.__name__
        self.threadlocal_storage.entry_method = method_name
        langchain_utils.initialize_and_start_timer_obj(self.threadlocal_storage, self.agent)
        try:
            response = await asearch(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            langchain_utils.set_search_score_metric_vectordb(reporting_values, response)
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.threadlocal_storage, self.cls, self.agent)
            self.threadlocal_storage.entry_method = None
            self.is_async_caller.set(False)
        return response


def intercept_chromadb_similarity_search(agent, mod):
    ChromadbInterceptor(agent, mod.Collection).attach([
        'add',
        'get',
        'peek',
        'delete',
        'upsert',
        'query',
        'modify',
        'update',
    ], patched_method_name='run_command')


def intercept_chromadb_collection_operations(agent, mod):
    chromaquery_interceptor = ChromaQuerySearchInterceptor(agent, mod.Chroma)
    chromaquery_interceptor.attach(['similarity_search_with_score',
                                    'similarity_search_by_vector',
                                    'max_marginal_relevance_search_by_vector'],
                                    patched_method_name="search")
    chromaquery_interceptor.attach(['asimilarity_search_with_score',
                                    'asimilarity_search_by_vector',
                                    'amax_marginal_relevance_search_by_vector'],
                                    patched_method_name="asearch")