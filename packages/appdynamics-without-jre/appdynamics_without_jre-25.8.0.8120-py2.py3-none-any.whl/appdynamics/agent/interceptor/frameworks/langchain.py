import threading
import appdynamics.agent.models.custom_metrics as custom_metrics_mod
import appdynamics.agent.interceptor.utils.langchain_utils as langchain_utils

from appdynamics.agent.interceptor.utils.langchain_utils import LangchainConstants
from appdynamics.agent.interceptor.base import BaseInterceptor
import contextvars


class LangchainCommunityLLMInterceptor(BaseInterceptor):

    def __init__(self, agent, cls):
        super().__init__(agent, cls)
        self.agent = agent
        self.cls = cls
        self.model_attr_name = None

        if LangchainConstants.OPENAI_STRING in str(cls).lower():
            self.model_attr_name = LangchainConstants.MODEL_NAME_ATTR
        elif LangchainConstants.OLLAMA_STRING in str(cls).lower():
            self.model_attr_name = LangchainConstants.MODEL_ATTR

        self.thread_context = threading.local()
        self.thread_context.entry_method = None

    def report_metrics(self, model_name=None, reporting_values=dict()):
        try:
            for metric_name in reporting_values:
                if metric_name in langchain_utils.AVG_METRICS_LIST:
                    self.agent.report_custom_metric(
                        custom_metrics_mod.CustomMetric(
                            name=langchain_utils.get_metric_path_from_params(
                                model_name,
                                LangchainConstants.LANGCHAIN_LLM_METRIC_PREFIX,
                                metric_name
                            ),
                            cluster_rollup_type=custom_metrics_mod.INDIVIDUAL,
                            time_rollup_type=custom_metrics_mod.TIME_AVERAGE,
                            hole_handling_type=custom_metrics_mod.REGULAR_COUNTER),
                        reporting_values[metric_name]
                    )
                    continue
                if model_name:
                    self.agent.report_custom_metric(
                        custom_metrics_mod.CustomMetric(
                            name=langchain_utils.get_metric_path_from_params(
                                model_name,
                                LangchainConstants.LANGCHAIN_LLM_METRIC_PREFIX,
                                metric_name
                            ),
                            time_rollup_type=custom_metrics_mod.TIME_SUM),
                        reporting_values[metric_name]
                    )
                # Aggregate metric, - All models string
                self.agent.report_custom_metric(
                    custom_metrics_mod.CustomMetric(
                        name=langchain_utils.get_metric_path_from_params(
                            None,
                            LangchainConstants.LANGCHAIN_LLM_METRIC_PREFIX,
                            metric_name
                        ),
                        time_rollup_type=custom_metrics_mod.TIME_SUM),
                    reporting_values[metric_name]
                )
        except Exception as e:
            self.agent.logger.error(f"Error occured while reporting langchain metrics, error = {repr(e)}")

    def set_output_token_metric(self, reporting_values, response, get_num_tokens, cls_inst):
        output_tokens = 0
        if response:
            for n_generations in response.generations:
                for generation in n_generations:
                    output_tokens += get_num_tokens(cls_inst, generation.text)

            reporting_values[LangchainConstants.OUTPUT_TOKENS_STRING] = output_tokens

    def do_calculate_and_report_metrics_generate(self, reporting_values, method_name, prompts, cls_inst, response):
        time_taken_by_call = langchain_utils.capture_time_and_reset_timer(self.thread_context)
        if self.thread_context.entry_method == method_name:
            try:
                if time_taken_by_call is not None:
                    reporting_values[LangchainConstants.AVERAGE_RESPONSE_TIME] = \
                        time_taken_by_call
                input_prompts = prompts if isinstance(prompts, list) else [prompts]
                reporting_values[LangchainConstants.PROMPTS_PERMIN_STRING] = \
                    len(input_prompts)
                get_num_tokens = getattr(self.cls, 'get_num_tokens', None)
                if get_num_tokens:
                    # input tokens metrics
                    input_tokens = 0
                    for prompt in input_prompts:
                        input_tokens += get_num_tokens(cls_inst, prompt)

                    reporting_values[LangchainConstants.INPUT_TOKENS_STRING] = input_tokens

                    # output tokens metrics
                    self.set_output_token_metric(reporting_values, response, get_num_tokens, cls_inst)
            except Exception as e:
                self.agent.logger.debug(f'Error occurred while capturing metrics: {str(e)}')
            finally:
                model_name = None
                if self.model_attr_name:
                    model_name = getattr(cls_inst, self.model_attr_name, None)
                self.report_metrics(model_name, reporting_values)
                self.thread_context.entry_method = None

    def calculate_time_per_output_token(self, time_taken_by_call, time_to_first_token, output_tokens):
        time_per_output_token = None
        if output_tokens > 0 and time_taken_by_call and time_to_first_token:
            time_per_output_token = (time_taken_by_call - time_to_first_token) / output_tokens
        return time_per_output_token

    async def __agenerate(self, _agenerate, cls_inst, prompts, *args, **kwargs):
        """
        Instrumentation for langchain_community.llms.<ThirdPartyLLMModel>'s _agenerate method
        The base method is is the asynchronous completion generation method for the LLM Model
        """
        response = None
        reporting_values = dict()
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = '_agenerate'
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = await _agenerate(cls_inst, prompts, *args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_PERMIN_STRING] = 1
            raise
        finally:
            self.do_calculate_and_report_metrics_generate(reporting_values, '_agenerate', prompts, cls_inst, response)
        return response

    def __generate(self, _generate, cls_inst, prompts, *args, **kwargs):
        """
        Instrumentation for langchain_community.llms.<ThirdPartyLLMModel>'s _generate method
        The base method is is the synchronous completion generation method for the LLM Model
        """
        response = None
        reporting_values = dict()
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = '_generate'
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = _generate(cls_inst, prompts, *args, **kwargs)
        except:
            reporting_values[LangchainConstants.ERRORS_PERMIN_STRING] = 1
            raise
        finally:
            self.do_calculate_and_report_metrics_generate(reporting_values, '_generate', prompts, cls_inst, response)
        return response

    def do_calculate_and_report_metrics_stream(self, reporting_values, method_name, prompt, cls_inst, output_tokens, time_to_first_token):
        time_taken_by_call = langchain_utils.capture_time_and_reset_timer(self.thread_context)
        time_per_output_token = self.calculate_time_per_output_token(time_taken_by_call, 
                                                                     time_to_first_token, output_tokens)
        if self.thread_context.entry_method == method_name:
            try:
                if time_taken_by_call:
                    reporting_values[LangchainConstants.AVERAGE_RESPONSE_TIME] = \
                        time_taken_by_call
                if time_to_first_token:
                    reporting_values[LangchainConstants.TIME_TO_FIRST_TOKEN] = \
                        time_to_first_token
                if time_per_output_token:
                    reporting_values[LangchainConstants.TIME_PER_OUTPUT_TOKEN] = \
                        round(time_per_output_token)
                reporting_values[LangchainConstants.PROMPTS_PERMIN_STRING] = 1
                get_num_tokens = getattr(self.cls, 'get_num_tokens', None)
                if get_num_tokens:
                    # input tokens metrics
                    input_tokens = get_num_tokens(cls_inst, prompt)

                    reporting_values[LangchainConstants.INPUT_TOKENS_STRING] = input_tokens

                    # output tokens metrics
                    if output_tokens > 0:
                        reporting_values[LangchainConstants.OUTPUT_TOKENS_STRING] = output_tokens
            except Exception as e:
                self.agent.logger.debug(f'Error occurred while capturing llm metrics: {repr(e)}')
            finally:
                model_name = None
                if self.model_attr_name:
                    model_name = getattr(cls_inst, self.model_attr_name, None)
                self.report_metrics(model_name, reporting_values)
                self.thread_context.entry_method = None
    
    async def __astream(self, _astream, cls_inst, prompt, *args, **kwargs):
        output_tokens = 0
        reporting_values = dict()
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = '_astream'
        time_to_first_token = None
        timer_started = langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = _astream(cls_inst, prompt, *args, **kwargs)
            async for chunk in response:
                output_tokens += 1
                if time_to_first_token is None and timer_started:
                    time_to_first_token = self.thread_context.timer_obj.duration_ms
                yield chunk
        except:
            reporting_values[LangchainConstants.ERRORS_PERMIN_STRING] = 1
            raise
        finally:
            self.do_calculate_and_report_metrics_stream(reporting_values, '_astream', 
                                                        prompt, cls_inst, output_tokens, time_to_first_token)

    def __stream(self, _stream, cls_inst, prompt, *args, **kwargs):
        output_tokens = 0
        reporting_values = dict()
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = '_stream'
        time_to_first_token = None
        timer_started = langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            response = _stream(cls_inst, prompt, *args, **kwargs)
            for chunk in response:
                output_tokens += 1
                if time_to_first_token is None and timer_started:
                    time_to_first_token = self.thread_context.timer_obj.duration_ms
                yield chunk

        except:
            reporting_values[LangchainConstants.ERRORS_PERMIN_STRING] = 1
            raise
        finally:
            self.do_calculate_and_report_metrics_stream(reporting_values, '_stream', 
                                                        prompt, cls_inst, output_tokens, time_to_first_token)


class LangchainCoreBaseModelInteceptor(BaseInterceptor):

    def report_metrics(self, reporting_values=dict()):
        try:
            for metric_name in reporting_values:
                self.agent.report_custom_metric(
                    custom_metrics_mod.CustomMetric(
                        name=metric_name,
                        cluster_rollup_type=None,
                        time_rollup_type=langchain_utils
                        .METRICS_DICT[metric_name][LangchainConstants.TIME_ROLLUP_STRING],
                        hole_handling_type=langchain_utils
                        .METRICS_DICT[metric_name][LangchainConstants.HOLE_HANDLING_STRING]
                    ),
                    reporting_values[metric_name]
                )
        except Exception as e:
            self.agent.logger.error(f"Error occured while reporting langchain metrics, error = {repr(e)}")

    def do_calculate_and_report_metrics(self, reporting_values, missing_prompt_idxs, existing_prompts):
        try:
            reporting_values[LangchainConstants.CACHE_MISSES_METRIC_STRING] = len(missing_prompt_idxs)
            reporting_values[LangchainConstants.CACHE_HITS_METRIC_STRING] = len(existing_prompts)
            self.report_metrics(reporting_values)
        except Exception as e1:
            self.agent.logger.warn(
                f'error occurred while reporting LangchainCoreBaseModelInteceptor metrics: {repr(e1)}')
    
    async def _aget_prompts(self, aget_prompts, *args, **kwargs):
        reporting_values = dict()
        (existing_prompts, llm_string, missing_prompt_idxs, missing_prompts) = ({}, "[]", [], [])
        try:
            existing_prompts, llm_string, missing_prompt_idxs, missing_prompts = await aget_prompts(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.CACHE_ERROR_METRIC_STRING] = 1
            raise
        finally:
            self.do_calculate_and_report_metrics(reporting_values, missing_prompt_idxs, existing_prompts)
        return existing_prompts, llm_string, missing_prompt_idxs, missing_prompts

    def _get_prompts(self, get_prompts, *args, **kwargs):
        reporting_values = dict()
        (existing_prompts, llm_string, missing_prompt_idxs, missing_prompts) = ({}, "[]", [], [])
        try:
            existing_prompts, llm_string, missing_prompt_idxs, missing_prompts = get_prompts(*args, **kwargs)
        except:
            reporting_values[LangchainConstants.CACHE_ERROR_METRIC_STRING] = 1
            raise
        finally:
            self.do_calculate_and_report_metrics(reporting_values, missing_prompt_idxs, existing_prompts)
        return existing_prompts, llm_string, missing_prompt_idxs, missing_prompts


class LangchainCommunityEmbeddingsInterceptor(BaseInterceptor):

    def __init__(self, agent, cls):
        super().__init__(agent, cls)
        self.agent = agent
        self.cls = cls

        self.model_attr_name = None
        if any(llm_module in str(cls).lower() for llm_module in
               [LangchainConstants.OPENAI_STRING, LangchainConstants.OLLAMA_STRING]):
            self.model_attr_name = LangchainConstants.MODEL_ATTR

        self.thread_context = threading.local()
        self.thread_context.entry_method = None
        self.is_async_caller = contextvars.ContextVar('is_async_caller', default=False)

    def report_metrics(self, model_name=None, reporting_values=dict()):
        try:
            for metric_name in reporting_values:
                if model_name:
                    self.agent.report_custom_metric(
                        custom_metrics_mod.CustomMetric(
                            name=langchain_utils.get_metric_path_from_params(
                                model_name,
                                LangchainConstants.LANGCHAIN_EMBEDDINGS_PREFIX,
                                metric_name
                            ),
                            cluster_rollup_type=None,
                            time_rollup_type=custom_metrics_mod.TIME_AVERAGE,
                            hole_handling_type=custom_metrics_mod.RATE_COUNTER
                        ),
                        reporting_values[metric_name]
                    )
                # Aggregate metric, - All models string, when not ART metric
                if LangchainConstants.AVERAGE_RESPONSE_TIME != metric_name:
                    self.agent.report_custom_metric(
                        custom_metrics_mod.CustomMetric(
                            name=langchain_utils.get_metric_path_from_params(
                                None,
                                LangchainConstants.LANGCHAIN_EMBEDDINGS_PREFIX,
                                metric_name
                            ),
                            cluster_rollup_type=None,
                            time_rollup_type=custom_metrics_mod.TIME_AVERAGE,
                            hole_handling_type=custom_metrics_mod.RATE_COUNTER
                        ),
                        reporting_values[metric_name]
                    )
        except Exception as e:
            self.agent.logger.error(f"Error occured while reporting langchain metrics, error = {repr(e)}")

    def do_report_embed_data(self, reporting_values, method_name, cls_inst):
        time_taken_by_call = langchain_utils.capture_time_and_reset_timer(self.thread_context)
        if self.thread_context.entry_method == method_name:
            try:
                if time_taken_by_call is not None:
                    reporting_values[LangchainConstants.AVERAGE_RESPONSE_TIME] = \
                        time_taken_by_call
                model_name = None
                if self.model_attr_name:
                    model_name = getattr(cls_inst, self.model_attr_name, None)
                self.report_metrics(model_name, reporting_values)
            except Exception as e:
                self.agent.logger.warn(
                    f'error occurred while reporting LangchainCommunityEmbeddingsInterceptor metrics: {str(e)}')
            finally:
                self.thread_context.entry_method = None

    async def _aembed_query(self, aembed_query, cls_inst, text):
        self.is_async_caller.set(True)
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = 'aembed_query'
        embeddings = []
        reporting_values = dict()
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            embeddings = await aembed_query(cls_inst, text)
        except:
            reporting_values[LangchainConstants.EMBEDDING_ERRORS_PERMIN] = 1
            raise
        finally:
            reporting_values[LangchainConstants.EMBEDDING_QUERIES] = 1
            self.do_report_embed_data(reporting_values, 'aembed_query', cls_inst)
            self.is_async_caller.set(False)
        return embeddings

    async def _aembed_documents(self, aembed_documents, cls_inst, texts):
        self.is_async_caller.set(True)
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = 'aembed_documents'
        embeddings = []
        reporting_values = dict()
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            embeddings = await aembed_documents(cls_inst, texts)
        except:
            reporting_values[LangchainConstants.EMBEDDING_ERRORS_PERMIN] = 1
            raise
        finally:
            reporting_values[LangchainConstants.EMBEDDING_QUERIES] = len(texts)
            self.do_report_embed_data(reporting_values, 'aembed_documents', cls_inst)
            self.is_async_caller.set(False)
        return embeddings

    def _embed_query(self, embed_query, cls_inst, text):
        if self.is_async_caller.get():
            return embed_query(cls_inst, text)
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = 'embed_query'
        embeddings = []
        reporting_values = dict()
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            embeddings = embed_query(cls_inst, text)
        except:
            reporting_values[LangchainConstants.EMBEDDING_ERRORS_PERMIN] = 1
            raise
        finally:
            reporting_values[LangchainConstants.EMBEDDING_QUERIES] = 1
            self.do_report_embed_data(reporting_values, 'embed_query', cls_inst)
        return embeddings

    def _embed_documents(self, embed_documents, cls_inst, texts):
        if self.is_async_caller.get():
            return embed_documents(cls_inst, texts)
        if not self.thread_context:
            self.thread_context = threading.local()
        self.thread_context.entry_method = 'embed_documents'
        embeddings = []
        reporting_values = dict()
        langchain_utils.initialize_and_start_timer_obj(self.thread_context, self.agent)
        try:
            embeddings = embed_documents(cls_inst, texts)
        except:
            reporting_values[LangchainConstants.EMBEDDING_ERRORS_PERMIN] = 1
            raise
        finally:
            reporting_values[LangchainConstants.EMBEDDING_QUERIES] = len(texts)
            self.do_report_embed_data(reporting_values, 'embed_documents', cls_inst)
        return embeddings


# langchain-ollama
def intercept_langchain_ollama_llms(agent, mod):
    LangchainCommunityLLMInterceptor(agent, mod.OllamaLLM).attach(['_agenerate', '_generate', '_astream', '_stream'])


def intercept_langchain_ollama_embeddings(agent, mod):
    LangchainCommunityEmbeddingsInterceptor(agent, mod.OllamaEmbeddings).attach(
        ['embed_query', 'embed_documents', 'aembed_query', 'aembed_documents'])


def intercept_langchain_ollama_chat_models(agent, mod):
    LangchainCommunityLLMInterceptor(agent, mod.ChatOllama).attach(['_agenerate', '_generate', '_astream', '_stream'])


# langchain
def intercept_langchain_community_llms(agent, mod):
    # Ollama interceptor
    LangchainCommunityLLMInterceptor(agent, mod.Ollama).attach(['_agenerate', '_generate', '_astream', '_stream'])


def intercept_langchain_community_chat_models(agent, mod):
    # Ollama async interceptor
    LangchainCommunityLLMInterceptor(agent, mod.ChatOllama).attach(['_agenerate', '_generate', '_astream', '_stream'])


def intercept_langchain_community_embeddings(agent, mod):
    # Ollama embeddings model interceptors
    LangchainCommunityEmbeddingsInterceptor(agent, mod.OllamaEmbeddings).attach(
        ['embed_query', 'embed_documents', 'aembed_query', 'aembed_documents'])


def intercept_langchain_core_language_models(agent, mod):
    LangchainCoreBaseModelInteceptor(agent, mod.llms).attach(['aget_prompts', 'get_prompts'])
