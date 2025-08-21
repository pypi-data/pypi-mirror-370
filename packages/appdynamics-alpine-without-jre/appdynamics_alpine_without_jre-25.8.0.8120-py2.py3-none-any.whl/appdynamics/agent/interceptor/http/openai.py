# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept boto to ensure that HTTPS is reported correctly.

"""

from __future__ import unicode_literals
from . import HTTPConnectionInterceptor
import appdynamics.agent.interceptor.utils.genai_utils as genai_utils
from appdynamics.agent.interceptor.utils.genai_utils import OpenaiConstants, GenaiConstants
from abc import ABC, abstractmethod
from appdynamics import config


class ApiModel(ABC):
    @abstractmethod
    def report_metrics(self, response, reporting_values, model_name):
        pass

    @abstractmethod
    def create_metrics(self, model_name=None):
        pass


class CompletionApiModel(ApiModel):
    def __init__(self, agent):
        self.agent = agent
        self.tier_model_metrics_mapping = dict()
        self.app_model_metrics_mapping = dict()

    def report_streaming_metrics(self, reporting_values, model_name, token_usage):
        try:
            reporting_values.update(genai_utils.get_reporting_values_streaming_type(
                model_name=model_name,
                token_usage=token_usage,
                agent=self.agent,
            ))

            # Reporting indiviual tier level performance metrics
            for metrics in (self.tier_model_metrics_mapping, self.app_model_metrics_mapping):
                genai_utils.report_metrics(
                    metrics_dict=metrics[model_name],
                    reporting_values=reporting_values,
                    agent=self.agent
                )
            # Reporting indiviual app level performance metrics
            for metrics in (self.tier_all_models_metrics_mapping, self.application_all_models_metrics_mapping):
                genai_utils.report_metrics(
                    metrics_dict=metrics,
                    reporting_values=reporting_values,
                    agent=self.agent
                )

        except Exception as exec:
            self.agent.logger.error(f"""Error in sending metrics.{str(exec)} \n
            Please check completion's streaming_report_metrics method""")

    def report_metrics(self, response, reporting_values, model_name):
        # Reporting completion api's metrics
        modified_response = None
        try:
            # modifying response class to dict if execption not raised
            if GenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                modified_response = genai_utils.convert_to_dict(agent=self.agent, response=response)

            if modified_response:
                reporting_values.update(genai_utils.get_reporting_values_per_request(
                    model_name=model_name,
                    agent=self.agent,
                    endpoint_response=modified_response
                ))

            # Reporting indiviual tier level performance metrics
            for metrics in (self.tier_model_metrics_mapping, self.app_model_metrics_mapping):
                genai_utils.report_metrics(
                    metrics_dict=metrics[model_name],
                    reporting_values=reporting_values,
                    agent=self.agent
                )
            # Reporting indiviual app level performance metrics
            for metrics in (self.tier_all_models_metrics_mapping, self.application_all_models_metrics_mapping):
                genai_utils.report_metrics(
                    metrics_dict=metrics,
                    reporting_values=reporting_values,
                    agent=self.agent
                )

        except Exception as exec:
            self.agent.logger.error(f"""Error in sending metrics.{str(exec)} \n
            Please check completion's report_metrics method""")
            raise

    def create_metrics(self, model_name=None):
        if model_name and model_name not in self.tier_model_metrics_mapping:
            self.tier_model_metrics_mapping[model_name] = genai_utils.initialize_metrics(
                metric_prefix_path=OpenaiConstants.TIER_METRIC_PATH +
                GenaiConstants.METRIC_PATH_SEGREGATOR + model_name,
                metric_dict=genai_utils.METRICS_DICT
            )
        if model_name and model_name not in self.app_model_metrics_mapping:
            self.app_model_metrics_mapping[model_name] = genai_utils.initialize_metrics(
                metric_prefix_path=GenaiConstants.APPLICATION_METRIC_PATH,
                metric_prefix=OpenaiConstants.OPENAI_PREFIX,
                metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + model_name,
                metric_dict=genai_utils.METRICS_DICT
            )
        self.tier_all_models_metrics_mapping = genai_utils.initialize_metrics(
            metric_prefix_path=OpenaiConstants.TIER_METRIC_PATH,
            metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + GenaiConstants.ALL_MODELS_STRING,
            metric_dict=genai_utils.METRICS_DICT,
        )
        self.application_all_models_metrics_mapping = genai_utils.initialize_metrics(
            metric_prefix_path=GenaiConstants.APPLICATION_METRIC_PATH,
            metric_prefix=OpenaiConstants.OPENAI_PREFIX,
            metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + GenaiConstants.ALL_MODELS_STRING,
            metric_dict=genai_utils.METRICS_DICT,
        )


class ModerationApiModel(ApiModel):
    def __init__(self, agent):
        self.agent = agent
        self.moderation_model_metrics_mapping = dict()

    def report_metrics(self, response, reporting_values, model_name):
        # Reporting completion api's metrics
        modified_response = None
        try:
            # modifying response class to dict
            if GenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                modified_response = genai_utils.convert_to_dict(agent=self.agent, response=response)

            if modified_response:
                reporting_values[OpenaiConstants.FLAGGED_QUERIES_METRIC_NAME] = genai_utils.prompt_flagged_counter(
                    agent=self.agent,
                    response=modified_response.get('results')
                )
                reporting_values[OpenaiConstants.TOTAL_QUERIES_METRIC_NAME] = len(modified_response.get('results', []))
                reporting_values.update(genai_utils.get_moderation_category_values(
                    input_response=modified_response,
                    agent=self.agent
                ))
            # Reporting moderation api metrics tier level
            genai_utils.report_metrics(
                metrics_dict=self.moderation_model_metrics_mapping[model_name],
                reporting_values=reporting_values,
                agent=self.agent
            )
            genai_utils.report_metrics(
                metrics_dict=self.moderartion_all_tier_metrics_mapping,
                reporting_values=reporting_values,
                agent=self.agent
            )

            # Reporting moderation api metrics application level
            genai_utils.report_metrics(
                metrics_dict=self.moderation_app_level_metrics_mapping,
                reporting_values=reporting_values,
                agent=self.agent
            )
        except Exception as exec:
            self.agent.logger.error(f"""Error in sending metrics. {str(exec)} \n
            Please check moderation's report_metrics method""")
            raise

    def create_metrics(self, model_name=None):
        if model_name and model_name not in self.moderation_model_metrics_mapping:
            self.moderation_model_metrics_mapping[model_name] = genai_utils.initialize_metrics(
                metric_prefix_path=OpenaiConstants.MODERATION_METRIC_PATH,
                metric_dict=genai_utils.MODERATION_METRIC_DICT,
            )
            self.moderation_model_metrics_mapping[model_name].update(
                genai_utils.initialize_metrics(
                    metric_prefix_path=OpenaiConstants.MODERATION_TIER_LEVEL_PREFIX,
                    metric_dict=genai_utils.MODERATION_CATEGORY_METRICS,
                )
            )

        self.moderation_app_level_metrics_mapping = genai_utils.initialize_metrics(
            metric_prefix_path=GenaiConstants.APPLICATION_METRIC_PATH,
            metric_prefix=OpenaiConstants.OPENAI_PREFIX,
            metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.MODERATION,
            metric_dict=genai_utils.MODERATION_METRIC_DICT,
        )
        self.moderation_app_level_metrics_mapping.update(
            genai_utils.initialize_metrics(
                metric_prefix_path=GenaiConstants.APPLICATION_METRIC_PATH,
                metric_prefix=OpenaiConstants.MODERATION_APPLICATION_LEVEL_PREFIX,
                metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + OpenaiConstants.MODERATION,
                metric_dict=genai_utils.MODERATION_CATEGORY_METRICS,
            )
        )
        self.moderartion_all_tier_metrics_mapping = genai_utils.initialize_metrics(
            metric_prefix_path=OpenaiConstants.TIER_METRIC_PATH,
            metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + GenaiConstants.ALL_MODELS_STRING,
            metric_dict=genai_utils.METRICS_DICT,
        )


class OpenAiMethodInstrumentor(HTTPConnectionInterceptor):
    def __init__(self, agent, cls):
        super(OpenAiMethodInstrumentor, self).__init__(agent, cls)
        self.completionApiModelInstance = CompletionApiModel(self.agent)
        self.moderationApiModelInstance = ModerationApiModel(self.agent)
        self.completionApiModelInstance.create_metrics()
        self.moderationApiModelInstance.create_metrics()

    def make_exit_call(self, path=None):
        exit_call = None
        base_url = None
        with self.log_exceptions():
            bt = self.bt
            if bt:
                """
                For getting the openai endpoint in openai >= 1
                we are getting the openai class instance in 0th index of
                any create api, from where we are fetching the base_url or the
                endpoint its calling to. Below in self.openai_client which
                stores the openai client instance during interception
                """
                # pylint: disable=E1101
                if self.openai_major_version >= 1 and self.openai_client \
                        and hasattr(self.openai_client, '_client') \
                        and hasattr(self.openai_client._client, 'base_url'):
                    base_url = self.openai_client._client.base_url
                host, port, scheme, url = genai_utils.get_backend_details(
                    base_url=base_url
                )
                backend = self.get_backend(
                    host=host,
                    port=port,
                    scheme=scheme,
                    url=url
                )

                if backend:
                    exit_call = self.start_exit_call(bt, backend, operation=path)
        return exit_call


class AsyncCreateInstrumentor(OpenAiMethodInstrumentor):
    def __init__(self, agent, cls, openai_major_version):
        self.openai_major_version = openai_major_version
        super().__init__(agent, cls)

    def set_exit_call_properties(self, acreate_response, exit_call_obj):
        if config.ENABLE_GENAI_DATA_CAPTURE:
            output_messages = genai_utils.parse_completion_response(acreate_response,
                                                                    self.openai_major_version, self.agent)
            if exit_call_obj and output_messages:
                exit_call_obj.optional_properties[OpenaiConstants.MODEL_OUTPUT_KEY] = str(output_messages)

    async def _moderation_acreate(self, acreate, *args, **kwargs):
        # args[0]: AsyncModerations(AsyncAPIResource) (if openaiv>=1) else openai_client is not used
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        moderation_acreate_response = dict()
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        self.moderationApiModelInstance.create_metrics(model_name=OpenaiConstants.MODERATION)
        exit_call_obj = None
        try:
            exit_call_obj = self.make_exit_call(path="moderations")
            moderation_acreate_response = await acreate(*args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if config.ENABLE_GENAI_DATA_CAPTURE:
                input_query = genai_utils.get_moderation_input_query(args, kwargs)
                moderation_response_parsed = genai_utils.parse_moderation_response(
                    moderation_acreate_response, self.openai_major_version, self.agent)
                if exit_call_obj:
                    if input_query:
                        exit_call_obj.optional_properties[OpenaiConstants.MODERATION_QUERY_KEY] = str(input_query)
                    if moderation_response_parsed:
                        exit_call_obj.optional_properties[OpenaiConstants.MODERATION_RESPONSE_STRING] =  \
                            str(moderation_response_parsed)

            self.end_exit_call(exit_call=exit_call_obj)
            self.moderationApiModelInstance.report_metrics(
                response=moderation_acreate_response,
                reporting_values=reporting_values,
                model_name=OpenaiConstants.MODERATION
            )
            reporting_values.clear()
            # returning response
        return moderation_acreate_response

    async def _embedding_acreate(self, acreate, *args, **kwargs):
        # args struct: [self, ...] (if openaiv>=1, ie. AsyncAPIResource) else openai_client is not used
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        model = kwargs.get('model') or kwargs.get('engine')
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        self.completionApiModelInstance.create_metrics(model_name=model)
        exit_call_obj = None
        embedding_acreate_response = None
        try:
            exit_call_obj = self.make_exit_call(path="embeddings")
            embedding_acreate_response = await acreate(*args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if config.ENABLE_GENAI_DATA_CAPTURE:
                input_query = kwargs.get("input", None)
                if exit_call_obj and input_query:
                    exit_call_obj.optional_properties[OpenaiConstants.INPUT_QUERY_KEY] = str(input_query)
            self.end_exit_call(exit_call=exit_call_obj)
            self.completionApiModelInstance.report_metrics(
                response=embedding_acreate_response,
                reporting_values=reporting_values,
                model_name=model
            )
            reporting_values.clear()
            # returning response
        return embedding_acreate_response

    async def _create(self, create, *args, **kwargs):
        create_response = await self._acreate(create, *args, **kwargs)
        return create_response

    async def _acreate(self, acreate, *args, **kwargs):
        if 'moderation' in acreate.__module__.lower():
            acreate_response = await self._moderation_acreate(acreate, *args, **kwargs)
            return acreate_response
        elif 'embedding' in acreate.__module__.lower():
            acreate_response = await self._embedding_acreate(acreate, *args, **kwargs)
            return acreate_response
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        acreate_response = dict()
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        model = kwargs.get('model') or kwargs.get('engine')
        # creating model specfic metrics
        self.completionApiModelInstance.create_metrics(model_name=model)
        is_streaming_response = kwargs.get("stream", False)
        exit_call_obj = None
        exit_call_operation = genai_utils.get_completion_opr_string(acreate.__module__.lower())
        try:
            exit_call_obj = self.make_exit_call(path=exit_call_operation)
            acreate_response = await acreate(*args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            input_messages = kwargs.get('messages', None)
            if "chat.completions" not in exit_call_operation:
                input_messages = kwargs.get("prompt", None)
            if config.ENABLE_GENAI_DATA_CAPTURE and exit_call_obj and input_messages:
                exit_call_obj.optional_properties[OpenaiConstants.INPUT_QUERY_KEY] = str(input_messages)
            if is_streaming_response:
                # used for prompt tokens calc tiktoken
                acreate_response = self._acustom_generator(exit_call_obj, response_generator=acreate_response,
                                                           input_messages=input_messages, model_used=model)

            # for streaming type, report token/calls metrics in the custom generator above when it ends
            if not is_streaming_response or GenaiConstants.ERROR_METRIC_NAME in reporting_values:
                self.set_exit_call_properties(acreate_response, exit_call_obj)
                self.end_exit_call(exit_call=exit_call_obj)
                self.completionApiModelInstance.report_metrics(
                    response=acreate_response,
                    reporting_values=reporting_values,
                    model_name=model
                )
            reporting_values.clear()
        # returning response
        return acreate_response

    async def _acustom_generator(self, exit_call_obj, response_generator, input_messages, model_used):
        complete_response = {"response": [], "model": ""}
        response_content = ""
        usage_data = None
        reporting_values = dict()
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        try:
            async for chunk in response_generator:
                response_content, complete_response, usage_data = \
                    genai_utils.set_parsed_chunk_values(chunk, response_content,
                                                        complete_response, usage_data, self.agent)
                yield chunk
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if exit_call_obj:
                if config.ENABLE_GENAI_DATA_CAPTURE:
                    exit_call_obj.optional_properties[OpenaiConstants.MODEL_OUTPUT_KEY] = \
                        str(response_content)
                self.end_exit_call(exit_call=exit_call_obj)
            token_usage = genai_utils.get_token_usage_data(usage_data, complete_response["model"], input_messages,
                                                           complete_response["response"], self.agent)
            self.completionApiModelInstance.report_streaming_metrics(
                reporting_values=reporting_values,
                model_name=model_used,
                token_usage=token_usage
            )

    async def _arequest(self, arequest, *args, **kwargs):
        url_string = None
        # args structure: [self, method, url, ...]
        if args and len(args) > 2:
            url_string = args[2]
        headers = kwargs.get('headers', None)
        if not headers:
            headers = dict()
            kwargs['headers'] = headers
        genai_utils.add_multiple_exit_suppression_header(url_string, headers)
        response = await arequest(*args, **kwargs)
        return response


class SyncCreateInstrumentor(OpenAiMethodInstrumentor):
    def __init__(self, agent, cls, openai_major_version):
        self.openai_major_version = openai_major_version
        super().__init__(agent, cls)

    def set_exit_call_properties(self, create_response, exit_call_obj):
        if config.ENABLE_GENAI_DATA_CAPTURE:
            output_messages = genai_utils.parse_completion_response(create_response,
                                                                    self.openai_major_version, self.agent)
            if exit_call_obj and output_messages:
                exit_call_obj.optional_properties[OpenaiConstants.MODEL_OUTPUT_KEY] = str(output_messages)

    def _moderation_create(self, create, *args, **kwargs):
        # args struct: [self, ...] (if openaiv>=1, ie. SyncAPIResource) else openai_client is not used
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()

        moderation_create_response = dict()
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        self.moderationApiModelInstance.create_metrics(model_name=OpenaiConstants.MODERATION)
        exit_call_obj = None
        try:
            exit_call_obj = self.make_exit_call(path="moderations")
            moderation_create_response = create(*args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if config.ENABLE_GENAI_DATA_CAPTURE:
                input_query = genai_utils.get_moderation_input_query(args, kwargs)
                moderation_response_parsed = genai_utils.parse_moderation_response(
                    moderation_create_response, self.openai_major_version, self.agent)
                if exit_call_obj:
                    if input_query:
                        exit_call_obj.optional_properties[OpenaiConstants.MODERATION_QUERY_KEY] = str(input_query)
                    if moderation_response_parsed:
                        exit_call_obj.optional_properties[OpenaiConstants.MODERATION_RESPONSE_STRING] = \
                            str(moderation_response_parsed)

            self.end_exit_call(exit_call=exit_call_obj)
            self.moderationApiModelInstance.report_metrics(
                response=moderation_create_response,
                reporting_values=reporting_values,
                model_name=OpenaiConstants.MODERATION
            )
            reporting_values.clear()
            # returning response
        return moderation_create_response

    def _embedding_create(self, create, *args, **kwargs):
        # args struct: [self, ...] (if openaiv>=1, ie. SyncAPIResource) else openai_client is not used
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        model = kwargs.get('model') or kwargs.get('engine')
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        self.completionApiModelInstance.create_metrics(model_name=model)
        exit_call_obj = None
        embedding_create_response = None
        input_query = kwargs.get("input", None)
        try:
            exit_call_obj = self.make_exit_call(path="embeddings")
            embedding_create_response = create(*args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if config.ENABLE_GENAI_DATA_CAPTURE:
                if exit_call_obj and input_query:
                    exit_call_obj.optional_properties[OpenaiConstants.INPUT_QUERY_KEY] = str(input_query)
            self.end_exit_call(exit_call=exit_call_obj)
            self.completionApiModelInstance.report_metrics(
                response=embedding_create_response,
                reporting_values=reporting_values,
                model_name=model
            )
            reporting_values.clear()
            # returning response
        return embedding_create_response

    def _create(self, create, *args, **kwargs):
        if 'moderation' in create.__module__.lower():
            return self._moderation_create(create, *args, **kwargs)
        elif 'embedding' in create.__module__.lower():
            return self._embedding_create(create, *args, **kwargs)
        self.openai_client = None if len(args) == 0 else args[0]
        reporting_values = dict()
        create_response = dict()
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        model = kwargs.get('model') or kwargs.get('engine')
        # creating model specfic metrics
        self.completionApiModelInstance.create_metrics(model_name=model)
        exit_call_obj = None
        is_streaming_response = kwargs.get("stream", False)
        exit_call_operation = genai_utils.get_completion_opr_string(create.__module__.lower())
        try:
            exit_call_obj = self.make_exit_call(path=exit_call_operation)
            create_response = create(*args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            input_messages = kwargs.get('messages', None)
            if "chat.completions" not in exit_call_operation:
                input_messages = kwargs.get("prompt", None)
            if config.ENABLE_GENAI_DATA_CAPTURE and exit_call_obj and input_messages:
                exit_call_obj.optional_properties[OpenaiConstants.INPUT_QUERY_KEY] = str(input_messages)
            if is_streaming_response and exit_call_obj:
                create_response = self._custom_generator(exit_call_obj, response_generator=create_response,
                                                         input_messages=input_messages, model_used=model)
            # for streaming type, report token/calls metrics in the generator above when it ends
            if not is_streaming_response or GenaiConstants.ERROR_METRIC_NAME in reporting_values:
                self.set_exit_call_properties(create_response, exit_call_obj)
                self.end_exit_call(exit_call=exit_call_obj)
                self.completionApiModelInstance.report_metrics(
                    response=create_response,
                    reporting_values=reporting_values,
                    model_name=model
                )

        reporting_values.clear()
        # returning response
        return create_response

    def _custom_generator(self, exit_call_obj, response_generator, input_messages, model_used):
        complete_response = {"response": [], "model": ""}
        usage_data = None
        response_content = ""
        reporting_values = dict()
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        try:
            for chunk in response_generator:
                response_content, complete_response, usage_data = \
                    genai_utils.set_parsed_chunk_values(chunk, response_content,
                                                        complete_response, usage_data, self.agent)
                yield chunk
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if exit_call_obj:
                if config.ENABLE_GENAI_DATA_CAPTURE:
                    exit_call_obj.optional_properties[OpenaiConstants.MODEL_OUTPUT_KEY] = \
                        str(response_content)
                self.end_exit_call(exit_call=exit_call_obj)
            token_usage = genai_utils.get_token_usage_data(usage_data, complete_response["model"], input_messages,
                                                           complete_response["response"], self.agent)
            self.completionApiModelInstance.report_streaming_metrics(
                reporting_values=reporting_values,
                model_name=model_used,
                token_usage=token_usage
            )

    # adding header appd_exit_created for suppression of duplicate exit call created
    def _request(self, request, *args, **kwargs):
        url_string = None
        # args structure: [self, method, url, ...]
        if args and len(args) > 2:
            url_string = args[2]
        headers = kwargs.get('headers', None)
        if not headers:
            headers = dict()
            kwargs['headers'] = headers
        genai_utils.add_multiple_exit_suppression_header(url_string, headers)
        response = request(*args, **kwargs)
        return response


def intercept_openai(agent, mod):
    openai_major_version = int(mod.VERSION.split(".")[0])
    # for openai version 0.x or lower
    if openai_major_version <= 0:
        # create instrumentation
        SyncCreateInstrumentor(agent, mod.Completion, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.ChatCompletion, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.Moderation, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.api_requestor.APIRequestor, openai_major_version).attach("request")
        SyncCreateInstrumentor(agent, mod.Embedding, openai_major_version).attach("create")

        # async create instrumentation
        AsyncCreateInstrumentor(agent, mod.Completion, openai_major_version).attach("acreate")
        AsyncCreateInstrumentor(agent, mod.ChatCompletion, openai_major_version).attach("acreate")
        AsyncCreateInstrumentor(agent, mod.Moderation, openai_major_version).attach("acreate")
        AsyncCreateInstrumentor(agent, mod.api_requestor.APIRequestor, openai_major_version).attach("arequest")
        AsyncCreateInstrumentor(agent, mod.Embedding, openai_major_version).attach("acreate")
    else:
        # create instrumentation
        SyncCreateInstrumentor(agent, mod.resources.Completions, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.resources.chat.Completions, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.resources.Moderations, openai_major_version).attach("create")
        SyncCreateInstrumentor(agent, mod.resources.Embeddings, openai_major_version).attach("create")

        # async create instrumentation
        AsyncCreateInstrumentor(agent, mod.resources.AsyncCompletions, openai_major_version).attach("create")
        AsyncCreateInstrumentor(agent, mod.resources.chat.AsyncCompletions, openai_major_version).attach("create")
        AsyncCreateInstrumentor(agent, mod.resources.AsyncModerations, openai_major_version).attach("create")
        AsyncCreateInstrumentor(agent, mod.resources.AsyncEmbeddings, openai_major_version).attach("create")
