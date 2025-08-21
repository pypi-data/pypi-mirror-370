# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Intercept bedrock-runtime service to ensure that HTTPS is reported correctly.

"""

from . import HTTPConnectionInterceptor
import appdynamics.agent.interceptor.utils.genai_utils as genai_utils
from appdynamics.agent.interceptor.utils.genai_utils import BedrockConstants, GenaiConstants
from itertools import tee


CONVERSE = 'Converse'
CONVERSE_STREAM = 'ConverseStream'


class BedrockMethodInstrumentor(HTTPConnectionInterceptor):
    def __init__(self, agent, cls):
        self.tier_model_metrics_mapping = dict()
        self.app_model_metrics_mapping = dict()
        self.operation_map = {
            CONVERSE: self.converse_api_call,
            CONVERSE_STREAM: self.converse_stream_api_call
        }
        super(BedrockMethodInstrumentor, self).__init__(agent, cls)

    def update_reporting_values(self, reporting_values, usage, metrics):
        reporting_values[GenaiConstants.INPUT_TOKENS_METRIC_NAME] = usage.get('inputTokens', 0)
        reporting_values[GenaiConstants.COMPLETION_TOKENS_METRIC_NAME] = usage.get('outputTokens', 0)
        reporting_values[GenaiConstants.TOKENS_METRIC_NAME] = usage.get('totalTokens', 0)
        reporting_values[GenaiConstants.LATENCY_METRIC_NAME] = metrics.get('latencyMs', 0)

    def fetch_metric_data_from_streaming_response(self, stream_data, reporting_values):
        token_usage = dict()
        try:
            for chunk in stream_data:
                if 'metadata' in chunk:
                    usage = chunk['metadata'].get('usage', {})
                    metrics = chunk['metadata'].get('metrics', {})

                    self.update_reporting_values(reporting_values, usage, metrics)
                    token_usage = usage
        except Exception as exec:
            self.agent.logger.error(f"""Error in fetching usage data and metrics.{str(exec)} \n
            Please check Bedrock streaming_report_metrics method""")
        return token_usage


    def converse_stream_api_call(self, request, client, operation_name, *args, **kwargs):
        reporting_values = dict()
        token_usage = dict()
        create_response = None
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        region_name = getattr(client.meta, 'region_name', 'us-west-2')
        model_id = args[0].get('modelId') if args and 'modelId' in args[0] else kwargs.get('modelId')
        model_id = genai_utils.get_metric_complaint_string(model_id)
        self.create_metrics(model_name=model_id)
        try:
            create_response = request(client, operation_name, *args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if GenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                stream_data, create_response['stream'] = tee(create_response['stream'])
                if stream_data:
                    token_usage = self.fetch_metric_data_from_streaming_response(
                        stream_data, reporting_values)
            self.report_streaming_metrics(
                reporting_values=reporting_values,
                model_name=model_id,
                token_usage=token_usage,
                region_name=region_name
            )

        return create_response

    def converse_api_call(self, request, client, operation_name, *args, **kwargs):
        reporting_values = dict()
        create_response = None
        reporting_values[GenaiConstants.CALLS_METRIC_NAME] = 1
        model_id = args[0].get('modelId') if args and 'modelId' in args[0] else kwargs.get('modelId')
        model_id = genai_utils.get_metric_complaint_string(model_id)
        region_name = getattr(client.meta, 'region_name', 'us-west-2')
        self.create_metrics(model_name=model_id)
        try:
            create_response = request(client, operation_name, *args, **kwargs)
        except:
            reporting_values[GenaiConstants.ERROR_METRIC_NAME] = 1
            raise
        finally:
            if GenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                usage = create_response.get('usage', {})
                metrics = create_response.get('metrics', {})
                self.update_reporting_values(reporting_values, usage, metrics)
            try:
                self.report_metrics(
                    response=create_response,
                    reporting_values=reporting_values,
                    model_name=model_id,
                    region_name=region_name
                )
            except Exception as exec:
                self.agent.logger.error(f"""Error in sending metrics.{str(exec)} \n
            Please check converse_api_call's report_metrics method""")
        return create_response

    def __make_api_call(self, request, client, operation_name, *args, **kwargs):
        if operation_name in self.operation_map:
            return self.operation_map[operation_name](request, client, operation_name, *args, **kwargs)
        return request(client, operation_name, *args, **kwargs)

    def create_metrics(self, model_name=None):
        if model_name and model_name not in self.tier_model_metrics_mapping:
            self.tier_model_metrics_mapping[model_name] = genai_utils.initialize_metrics(
                metric_prefix_path=BedrockConstants.BEDROCK_TIER_METRIC_PATH +
                GenaiConstants.METRIC_PATH_SEGREGATOR + model_name,
                metric_dict=genai_utils.METRICS_DICT
            )
        if model_name and model_name not in self.app_model_metrics_mapping:
            self.app_model_metrics_mapping[model_name] = genai_utils.initialize_metrics(
                metric_prefix_path=GenaiConstants.APPLICATION_METRIC_PATH,
                metric_prefix=BedrockConstants.BEDROCK_PREFIX,
                metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + model_name,
                metric_dict=genai_utils.METRICS_DICT
            )
        self.tier_all_models_metrics_mapping = genai_utils.initialize_metrics(
            metric_prefix_path=BedrockConstants.BEDROCK_TIER_METRIC_PATH,
            metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + GenaiConstants.ALL_MODELS_STRING,
            metric_dict=genai_utils.METRICS_DICT,
        )
        self.application_all_models_metrics_mapping = genai_utils.initialize_metrics(
            metric_prefix_path=GenaiConstants.APPLICATION_METRIC_PATH,
            metric_prefix=BedrockConstants.BEDROCK_PREFIX,
            metric_suffix=GenaiConstants.METRIC_NAME_SEGREGATOR + GenaiConstants.ALL_MODELS_STRING,
            metric_dict=genai_utils.METRICS_DICT,
        )

    def report_metrics(self, response, reporting_values, model_name, region_name=None):
        # Reporting completion api's metrics
        modified_response = None
        try:
            # modifying response class to dict if execption not raised
            if GenaiConstants.ERROR_METRIC_NAME not in reporting_values:
                modified_response = genai_utils.convert_to_dict(agent=self.agent, response=response)

            if modified_response:
                reporting_values.update(genai_utils.get_reporting_bedrock_values_per_request(
                    agent=self.agent,
                    endpoint_response=modified_response,
                    region_name=region_name
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
            Please check converse api report_metrics method""")

    def report_streaming_metrics(self, reporting_values, model_name, token_usage, region_name=None):
        try:
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
            Please check converse stream streaming_report_metrics method""")


def intercept_bedrock(agent, mod):
    BedrockMethodInstrumentor(agent, mod.BaseClient).attach("_make_api_call")
