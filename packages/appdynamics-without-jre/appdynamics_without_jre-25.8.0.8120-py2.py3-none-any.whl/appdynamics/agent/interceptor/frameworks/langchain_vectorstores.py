from __future__ import unicode_literals
import appdynamics.agent.interceptor.utils.langchain_utils as langchain_utils

from appdynamics.agent.interceptor.utils.langchain_utils import LangchainConstants
from appdynamics.agent.interceptor.base import BaseInterceptor
import threading
import contextvars


class LangchainVectorstoresInterceptor(BaseInterceptor):

    def __init__(self, agent, cls):
        super().__init__(agent, cls)
        self.agent = agent
        self.cls = cls
        self.thread_context = threading.local()
        self.is_async_caller = contextvars.ContextVar('is_async_caller', default=False)

    def search(self, search, *args, **kwargs):
        # In some versions and vectorstores impls, metrics are already reported in async asearch interception
        # which might have called this 'search' in a different thread(See, Vectorstores.adelete)
        if self.is_async_caller.get():
            return search(*args, **kwargs)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = search.__name__
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = method_name
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = search(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            langchain_utils.set_search_score_metric_vectordb(reporting_values, response)
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.thread_context, self.cls, self.agent)
            self.thread_context.entry_method = None
        return response

    def add_texts(self, add_texts, *args, **kwargs):
        if self.is_async_caller.get():
            return add_texts(*args, **kwargs)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = add_texts.__name__
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method =  method_name
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = add_texts(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            texts_len = len(args[1]) if len(args) > 1 else len(kwargs.get('texts', []))
            if texts_len > 0:
                reporting_values[LangchainConstants.INSERTIONCOUNT_METRIC_NAME] = texts_len
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.thread_context, self.cls, self.agent)
            self.thread_context.entry_method = None
        return response

    def delete(self, delete, *args, **kwargs):
        if self.is_async_caller.get():
            return delete(*args, **kwargs)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = delete.__name__
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method =  method_name
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = delete(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            deleted_count = \
                len(args[1]) if len(args) > 1 else len(kwargs.get('ids', []))
            if deleted_count > 0:
                reporting_values[LangchainConstants.DELETIONCOUNT_METRIC_NAME] = deleted_count
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.thread_context, self.cls, self.agent)
            self.thread_context.entry_method = None
        return response

    # async methods
    async def asearch(self, asearch, *args, **kwargs):
        self.is_async_caller.set(True)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = asearch.__name__
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = method_name
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = await asearch(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            langchain_utils.set_search_score_metric_vectordb(reporting_values, response)
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.thread_context, self.cls, self.agent)
            self.thread_context.entry_method = None
            self.is_async_caller.set(False)
        return response

    async def aadd_texts(self, aadd_texts, *args, **kwargs):
        self.is_async_caller.set(True)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = aadd_texts.__name__
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = method_name
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = await aadd_texts(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            texts_len = len(args[1]) if len(args) > 1 else len(kwargs.get('texts', []))
            if texts_len > 0:
                reporting_values[LangchainConstants.INSERTIONCOUNT_METRIC_NAME] = texts_len
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.thread_context, self.cls, self.agent)
            self.thread_context.entry_method = None
            self.is_async_caller.set(False)
        return response

    async def adelete(self, adelete, *args, **kwargs):
        self.is_async_caller.set(True)
        reporting_values = dict()
        reporting_values[LangchainConstants.CALLS_METRIC_NAME] = 1
        method_name = adelete.__name__
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method =  method_name
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = await adelete(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_METRIC_NAME] = 1
            raise
        finally:
            deleted_count = \
                len(args[1]) if len(args) > 1 else len(kwargs.get('ids', []))
            if deleted_count > 0:
                reporting_values[LangchainConstants.DELETIONCOUNT_METRIC_NAME] = deleted_count
            langchain_utils.capture_time_and_report_metrics(reporting_values, method_name, 
                                                            self.thread_context, self.cls, self.agent)
            self.thread_context.entry_method = None
            self.is_async_caller.set(False)
        return response


def intercept_vectorstores_methods(vector_cls, vectorstores_interceptor):
    # patched_method_name Vs list of methods to instrument
    patched_name_to_methods = {
        # vectorstore search methods, checking with hasattr as 
        # not all implementations of vectorstores had implemented the methods
        'search' : ['similarity_search',
                    'similarity_search_with_score',
                    'similarity_search_with_score_by_vector',
                    'similarity_search_by_vector',
                    'max_marginal_relevance_search',
                    'max_marginal_relevance_search_with_score_by_vector',
                    'max_marginal_relevance_search_by_vector'],
        # vectorstore add and delete methods
        'add_texts' : ['add_texts'],
        'delete' : ['delete'],
        # async methods
        'asearch' : ['asimilarity_search',
                    'asimilarity_search_with_score',
                    'asimilarity_search_with_score_by_vector',
                    'asimilarity_search_by_vector',
                    'amax_marginal_relevance_search',
                    'amax_marginal_relevance_search_with_score_by_vector',
                    'amax_marginal_relevance_search_by_vector'],
        'aadd_texts' : ['aadd_texts'],
        'adelete' : ['adelete'],   
    }
    for patched_name, list_of_methods_to_instrument in patched_name_to_methods.items():
        for method_name in list_of_methods_to_instrument:
            if patched_name in ['search', 'asearch'] and ("Chroma" in vector_cls.__name__ or
                                                          "PGVector" in vector_cls.__name__):
                # For pgvector and chromadb metrics are reported from existing interceptors
                continue
            if hasattr(vector_cls, method_name):
                vectorstores_interceptor.attach([method_name], patched_method_name=patched_name)


def intercept_langchain_community_vectorstores(agent, mod):
    try:
        for vector_store_id in mod.__all__:
            if not hasattr(mod, vector_store_id):
                continue
            vector_cls = getattr(mod, vector_store_id)
            vectorstores_interceptor = LangchainVectorstoresInterceptor(agent, vector_cls)
            intercept_vectorstores_methods(vector_cls, vectorstores_interceptor)
    except Exception as exc:
        print(f"Error occured while patching langchain community vectordbs, {repr(exc)}")


# instrumentation of langchain-{vendor} vectorstores
def intercept_langchain_vendorspecific_vectorstores(agent, mod):
    try:
        for vector_store_id in mod.__all__:
            # assumption that langchain--{vendor}.vectorstores.$VendorClass is the hierarchy
            if not hasattr(mod.vectorstores, vector_store_id):
                continue
            vector_cls = getattr(mod.vectorstores, vector_store_id)
            vectorstores_interceptor = LangchainVectorstoresInterceptor(agent, vector_cls)
            intercept_vectorstores_methods(vector_cls, vectorstores_interceptor)
    except Exception as exc:
        print(f"Error occured while patching langchain-vendorspecific vectordbs, {repr(exc)}")