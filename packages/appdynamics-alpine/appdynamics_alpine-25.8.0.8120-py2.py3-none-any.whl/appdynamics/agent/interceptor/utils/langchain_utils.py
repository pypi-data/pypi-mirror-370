import appdynamics.agent.models.custom_metrics as custom_metrics_mod


class LangchainConstants():
    LANGCHAIN_METRIC_PREFIX = "Agent|Langchain"
    LLM_METRIC_SUBPATH = "|LLM|"
    METRIC_PATH_SEGREGATOR = "|"
    EMBEDDINGS_METRIC_SUBPATH = "|Embeddings|"
    LANGCHAIN_EMBEDDINGS_PREFIX = "Agent|Langchain|Embeddings|"
    LANGCHAIN_LLM_METRIC_PREFIX = "Agent|Langchain|LLM|"
    LANGCHAIN_VECTORSTORES_METRIC_PREFIX = "Agent|Langchain|VectorStores|"
    CACHE_ERROR_METRIC_STRING = LANGCHAIN_METRIC_PREFIX + LLM_METRIC_SUBPATH + \
        "Cache Errors per minute - All Models"
    CACHE_MISSES_METRIC_STRING = LANGCHAIN_METRIC_PREFIX + LLM_METRIC_SUBPATH + \
        "Cache Misses - All Models"
    CACHE_HITS_METRIC_STRING = LANGCHAIN_METRIC_PREFIX + LLM_METRIC_SUBPATH + \
        "Cache Hits - All Models"
    ALL_MODELS_STRING = " - All Models"
    ERRORS_PERMIN_STRING = "Errors per minute"
    PROMPTS_PERMIN_STRING = "Prompts per minute"
    INPUT_TOKENS_STRING = "Input Tokens"
    OUTPUT_TOKENS_STRING = "Output Tokens"
    EMBEDDING_QUERIES = "Embedding queries"
    EMBEDDING_ERRORS_PERMIN = "Embedding Errors per minute"
    EMBEDDING_QUERIES_ALL_MODELS = EMBEDDING_QUERIES + " - All Models"
    CLUSTER_ROLLUP_STRING = "cluster_rollup_type"
    HOLE_HANDLING_STRING = "hole_handling_type"
    TIME_ROLLUP_STRING = "time_rollup_type"
    OPENAI_STRING = "openai"
    OLLAMA_STRING = "ollama"
    MODEL_NAME_ATTR = "model_name"
    MODEL_ATTR = "model"
    AVERAGE_RESPONSE_TIME = "Average Response Time (ms)"
    TIME_TO_FIRST_TOKEN = "Time to First Token (ms)"
    TIME_PER_OUTPUT_TOKEN = "Time per Output Token (ms)"
    SEARCH_SCORE_METRIC_NAME = "Search Score"
    ERRORS_METRIC_NAME = "Errors"
    CALLS_METRIC_NAME = "Calls"
    INSERTIONCOUNT_METRIC_NAME = "Vector Insertion Count"
    DELETIONCOUNT_METRIC_NAME = "Vector Deletion Count"


METRICS_DICT = {
    LangchainConstants.CACHE_ERROR_METRIC_STRING: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    LangchainConstants.CACHE_MISSES_METRIC_STRING: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    LangchainConstants.CACHE_HITS_METRIC_STRING: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    # langchain_vectorstores metrics
    LangchainConstants.SEARCH_SCORE_METRIC_NAME: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    LangchainConstants.ERRORS_METRIC_NAME: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    LangchainConstants.AVERAGE_RESPONSE_TIME: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    LangchainConstants.CALLS_METRIC_NAME: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    LangchainConstants.INSERTIONCOUNT_METRIC_NAME: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    LangchainConstants.DELETIONCOUNT_METRIC_NAME: {
        LangchainConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        LangchainConstants.CLUSTER_ROLLUP_STRING: None,
        LangchainConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    }
}

AVG_METRICS_LIST = {
    LangchainConstants.AVERAGE_RESPONSE_TIME,
    LangchainConstants.TIME_TO_FIRST_TOKEN,
    LangchainConstants.TIME_PER_OUTPUT_TOKEN
}


def get_metric_path_from_params(model_name=None, metric_prefix="", metric_suffix=""):
    if model_name:
        # Replace special char as it changes metric hierarchy
        model_name = model_name.replace(":", "_")
        return metric_prefix + model_name + LangchainConstants.METRIC_PATH_SEGREGATOR + metric_suffix
    else:
        return metric_prefix + metric_suffix + LangchainConstants.ALL_MODELS_STRING

def set_search_score_metric_vectordb(reporting_values, response):
    if response and isinstance(response, list):
        score_list = []
        for entry in response:
            if isinstance(entry, tuple) and len(entry) > 1:
                score_list.append(round(entry[1]*100))
        reporting_values[LangchainConstants.SEARCH_SCORE_METRIC_NAME] = score_list

def initialize_and_start_timer_obj(curr_thread_ctx, agent):
    timer_started = False
    if not (hasattr(curr_thread_ctx, 'timer_obj') and curr_thread_ctx.timer_obj) and agent:
        curr_thread_ctx.timer_obj = agent.timer()
    if hasattr(curr_thread_ctx, 'timer_obj') and curr_thread_ctx.timer_obj:
        # resets if the timer was already started(upon cascading method calls which're intercepted)
        curr_thread_ctx.timer_obj.reset()
        curr_thread_ctx.timer_obj.start()
        timer_started = True
    return timer_started

def capture_time_and_reset_timer(curr_thread_ctx):
    time_taken_by_call = None
    if hasattr(curr_thread_ctx, 'timer_obj') and curr_thread_ctx.timer_obj:
        time_taken_by_call = curr_thread_ctx.timer_obj.stop()
        curr_thread_ctx.timer_obj.reset()
    return time_taken_by_call

def capture_time_and_report_metrics(reporting_values, method_name, threadlocal_storage, cls, agent):
    time_taken_by_call = capture_time_and_reset_timer(threadlocal_storage)
    if threadlocal_storage.entry_method == method_name:
        if time_taken_by_call:
            reporting_values[LangchainConstants.AVERAGE_RESPONSE_TIME] = time_taken_by_call
        report_vectorstore_metrics(reporting_values, cls.__name__, agent)

def get_vectordb_metric_path(vectordb_name=None, metric_prefix="", metric_suffix=""):
    if vectordb_name:
        return metric_prefix + vectordb_name + LangchainConstants.METRIC_PATH_SEGREGATOR + metric_suffix
    return None  

def report_vectorstore_metrics(reporting_values, vectordb_name, agent):
    try:
        for metric_name in reporting_values:
            metric_path = get_vectordb_metric_path(
                vectordb_name,
                LangchainConstants.LANGCHAIN_VECTORSTORES_METRIC_PREFIX,
                metric_name
            )
            if isinstance(reporting_values[metric_name], list):
                for metric_value in reporting_values[metric_name]:
                    do_report_metric(metric_path, metric_name, metric_value, agent)
            else:
                do_report_metric(metric_path, metric_name, reporting_values[metric_name], agent)
    except Exception as e:
        agent.logger.error(f"Error occured while reporting langchain metrics, error = {repr(e)}")

def do_report_metric(metric_path, metric_name, metric_value, agent):
    agent.report_custom_metric(
        custom_metrics_mod.CustomMetric(
            name=metric_path,
            cluster_rollup_type=custom_metrics_mod.INDIVIDUAL,
            time_rollup_type=METRICS_DICT[metric_name][LangchainConstants.TIME_ROLLUP_STRING],
            hole_handling_type=METRICS_DICT[metric_name][LangchainConstants.HOLE_HANDLING_STRING]),
            metric_value
    )
