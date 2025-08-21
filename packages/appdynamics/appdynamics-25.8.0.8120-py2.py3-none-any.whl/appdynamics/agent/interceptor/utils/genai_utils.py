import appdynamics.agent.models.custom_metrics as custom_metrics_mod
from appdynamics.lang import items, urlparse
from collections import defaultdict


class GenaiConstants():
    TOKENS_METRIC_NAME = "Tokens"
    CALLS_METRIC_NAME = "Calls per minute"
    ERROR_METRIC_NAME = "Errors per minute"
    LATENCY_METRIC_NAME = "Latency"
    ALL_MODELS_STRING = "All Models"
    METRIC_NAME_SEGREGATOR = " - "
    APPLICATION_METRIC_PATH = "BTM|Application Summary"
    METRIC_PATH_SEGREGATOR = "|"
    INPUT_TOKENS_METRIC_NAME = "Input Tokens"
    COMPLETION_TOKENS_METRIC_NAME = "Completion Tokens"


class OpenaiConstants():
    FLAGGED_QUERIES_METRIC_NAME = "Flagged queries"
    TOTAL_QUERIES_METRIC_NAME = "Total queries"
    OPENAI = "OpenAI"
    OPENAI_PREFIX = OPENAI + GenaiConstants.METRIC_NAME_SEGREGATOR
    TIER_METRIC_PATH = "Agent|OpenAI"
    PROMPT_TOKENS_STRING = "prompt_tokens"
    COMPLETION_TOKENS_STRING = "completion_tokens"
    TOTAL_TOKENS_STRING = "total_tokens"
    TIME_ROLLUP_STRING = "time_rollup_type"
    CLUSTER_ROLLUP_STRING = "cluster_rollup_type"
    HOLE_HANDLING_STRING = "hole_handling_type"
    DEFAULT_HOST = "api.openai.com"
    DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1"
    MODERATION = "moderations"
    MODERATION_METRIC_PATH = TIER_METRIC_PATH + GenaiConstants.METRIC_PATH_SEGREGATOR + MODERATION
    MODERATION_CATERGORY_FOLDER_NAME = "Flagged Calls by category"
    MODERATION_APPLICATION_LEVEL_PREFIX = OPENAI_PREFIX + \
        MODERATION_CATERGORY_FOLDER_NAME + GenaiConstants.METRIC_NAME_SEGREGATOR
    MODERATION_TIER_LEVEL_PREFIX = TIER_METRIC_PATH + GenaiConstants.METRIC_PATH_SEGREGATOR + MODERATION + \
        GenaiConstants.METRIC_PATH_SEGREGATOR + MODERATION_CATERGORY_FOLDER_NAME
    MODERATION_QUERY_KEY = "Moderation input query"
    CATEGORIES_STRING = "categories"
    CATEGORY_SCORES_STRING = "category_scores"
    MODERATION_RESPONSE_STRING = "Moderation response"
    OPENAI_EXIT_CREATED_HEADER = "appd_openai_exit_created"
    BASE_ENCODING_TYPE_STRING = "cl100k_base"
    SUPPORTED_OPENAI_APIS_URISUFFIX_LIST = ["moderation", "chat/completion", "completion", "embedding"]
    CHOICES_FIELD = "choices"
    DELTA_FIELD = "delta"
    ROLE_FIELD = "role"
    NAME_FIELD = "name"
    CONTENT_FIELD = "content"
    MODEL_FIELD = "model"
    USAGE_FIELD = "usage"
    INPUT_QUERY_KEY = "Input query"
    MODEL_OUTPUT_KEY = "Output"


class BedrockConstants():
    BEDROCK_PROMPT_TOKENS_STRING = "inputTokens"
    BEDROCK_COMPLETION_TOKENS_STRING = "outputTokens"
    BEDROCK_TOTAL_TOKENS_STRING = "totalTokens"
    BEDROCK_TIER_METRIC_PATH = "Agent|Bedrock"
    BEDROCK = "Bedrock"
    BEDROCK_PREFIX = BEDROCK + GenaiConstants.METRIC_NAME_SEGREGATOR


METRICS_DICT = {
    GenaiConstants.CALLS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    GenaiConstants.ERROR_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    GenaiConstants.TOKENS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    GenaiConstants.LATENCY_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    GenaiConstants.INPUT_TOKENS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    GenaiConstants.COMPLETION_TOKENS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
}

MODERATION_CATEGORY = {
    "sexual": "sexual",
    "hate": "hate",
    "harassment": "harassment",
    "self-harm": "selfHarm",
    "sexual/minors": "sexualMinors",
    "hate/threatening": "hateThreatening",
    "violence/graphic": "violenceGraphic",
    "self-harm/intent": "selfHarmIntent",
    "self-harm/instructions": "selfHarmInstructions",
    "harassment/threatening": "harassmentThreatening",
    "violence": "violence",
}


MODERATION_METRIC_DICT = {
    GenaiConstants.CALLS_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
    OpenaiConstants.FLAGGED_QUERIES_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    OpenaiConstants.TOTAL_QUERIES_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_SUM,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.REGULAR_COUNTER
    },
    GenaiConstants.ERROR_METRIC_NAME: {
        OpenaiConstants.TIME_ROLLUP_STRING: custom_metrics_mod.TIME_AVERAGE,
        OpenaiConstants.CLUSTER_ROLLUP_STRING: None,
        OpenaiConstants.HOLE_HANDLING_STRING: custom_metrics_mod.RATE_COUNTER
    },
}

MODERATION_CATEGORY_METRICS = {
    value: MODERATION_METRIC_DICT[OpenaiConstants.FLAGGED_QUERIES_METRIC_NAME]
    for key, value in items(MODERATION_CATEGORY)
}


def get_tokens_per_request(method_response, token_type=OpenaiConstants.PROMPT_TOKENS_STRING):
    try:
        return method_response['usage'][token_type]
    except Exception as exec:
        if token_type == OpenaiConstants.COMPLETION_TOKENS_STRING:
            return None
        raise UnsupportedResponseException(f"""UnsupportedResponseException: create method response struct changed.
                    Please contact admin or use the latest agent for updates \n [Error]:
                    {str(exec)}""")


def calculate_token_usage_from_string(model_name, messages, agent=None):
    try:
        # pylint: disable=import-error
        import tiktoken
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError as ex:
        # no such model_name in tiktoken
        if agent:
            agent.logger.error(f"Failed to get tiktoken encoding for model_name {model_name},\
                                error: {str(ex)}, defaulting to {OpenaiConstants.BASE_ENCODING_TYPE_STRING}")
        encoding = tiktoken.get_encoding(OpenaiConstants.BASE_ENCODING_TYPE_STRING)
    except ImportError:
        return None
    # ref:https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    if model_name == "gpt-3.5-turbo-0301":
        # every message follows <|start|>{role/name}\n{content}<|end|>\n
        # if there's a name, the role is omitted
        tokens_per_message = 4
        tokens_per_name = -1
    else:
        tokens_per_message = 3
        tokens_per_name = 1

    total_tokens = 0
    for message in messages:
        total_tokens += tokens_per_message
        for key, value in message.items():
            total_tokens += len(encoding.encode(value))
            if key == "name":
                total_tokens += tokens_per_name
    # every reply is primed with <|start|>assistant<|message|>
    total_tokens += 3
    return total_tokens


def initialize_metrics(metric_prefix_path="", metric_prefix="", metric_suffix="", metric_dict=dict()):
    model_metrics_dict = dict()
    for metric_name, metric_attr in items(metric_dict):
        model_metrics_dict[metric_name] = custom_metrics_mod.CustomMetric(
            name=metric_prefix_path + GenaiConstants.METRIC_PATH_SEGREGATOR +
            metric_prefix + metric_name + metric_suffix,
            time_rollup_type=metric_attr[OpenaiConstants.TIME_ROLLUP_STRING],
            hole_handling_type=metric_attr[OpenaiConstants.HOLE_HANDLING_STRING])
    return model_metrics_dict


def get_backend_details(base_url=None) -> tuple:
    backend_details = None
    try:
        # importing openai package since api's hostname
        # change will different api's getting hostname
        # on every exitcall
        if base_url and hasattr(base_url, 'host') and hasattr(base_url, 'port') and hasattr(base_url, 'scheme'):
            port = base_url.port or ('443' if base_url.scheme == 'https' else '80')
            backend_details = (base_url.host, port, base_url.scheme, base_url.host)
        else:
            from openai import api_base
            parsed_url = urlparse(api_base)
            port = parsed_url.port or ('443' if parsed_url.scheme == 'https' else '80')
            backend_details = (parsed_url.hostname, port, parsed_url.scheme, api_base)
    except Exception:
        backend_details = (
            OpenaiConstants.DEFAULT_HOST,
            '443', 'https',
            OpenaiConstants.DEFAULT_OPENAI_ENDPOINT
        )
    return backend_details


def prompt_flagged_counter(agent=None, response=None) -> int:
    flagged_calls = 0
    try:
        if not response:
            response = list()
        flagged_calls = sum([int(moderation_data.get("flagged", False)) for moderation_data in response])
    except Exception as e:
        agent.logger.error(f"Moderation API response changed. {str(e)} \n. Please raise a bug")
    return flagged_calls


def get_moderation_category_values(input_response=None, agent=None) -> dict:
    output_response = defaultdict(int)
    try:
        for prompts in input_response.get('results'):
            for category, is_flagged in items(prompts.get("categories", {})):
                if category in MODERATION_CATEGORY:
                    if is_flagged:
                        output_response[MODERATION_CATEGORY[category]] += 1
                else:
                    agent.logger.warning(
                        "Category not support {0}".format(category))
    except Exception as e:
        agent.logger.error("Moderation API response changed. Please raise a bug" + str(e))
    return output_response


def report_metrics(metrics_dict=None, reporting_values=None, agent=None):
    if not metrics_dict or not reporting_values:
        raise MissingReportingValuesExcepion(" Metric Reporting\
           values not found .Please provide proper method arguments\
        ")
    try:
        for metric_name, metric_value in items(reporting_values):
            if metric_name in metrics_dict:
                agent.report_custom_metric(
                    metrics_dict[metric_name],
                    metric_value
                )
    except Exception as exec:
        agent.logger.warn("MetricReportingError: " + repr(exec))
        pass


def convert_to_dict(agent=None, response=None):
    modified_response = response
    try:
        if hasattr(response, 'model_dump') and not isinstance(response, dict):
            modified_response = response.model_dump(exclude_unset=True)
    except Exception as exc:
        agent.logger.error("Cannot convert api class to dict " + str(exc))
    return modified_response


def get_reporting_values_per_request(model_name=None, agent=None, endpoint_response=None):
    reporting_values = dict()
    # Calculating current request tokens
    try:
        reporting_values[GenaiConstants.TOKENS_METRIC_NAME] = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=OpenaiConstants.TOTAL_TOKENS_STRING
        )
        input_tokens = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=OpenaiConstants.PROMPT_TOKENS_STRING
        )
        if input_tokens:
            reporting_values[GenaiConstants.INPUT_TOKENS_METRIC_NAME] = input_tokens
        completion_tokens = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=OpenaiConstants.COMPLETION_TOKENS_STRING
        )
        if completion_tokens:
            reporting_values[GenaiConstants.COMPLETION_TOKENS_METRIC_NAME] = completion_tokens
    except UnsupportedResponseException as exec:
        agent.logger.error(str(exec))
        raise
    return reporting_values


def get_reporting_bedrock_values_per_request(agent=None,
                                             endpoint_response=None, region_name=None):
    reporting_values = dict()
    # Calculating current request tokens
    try:
        reporting_values[GenaiConstants.TOKENS_METRIC_NAME] = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=BedrockConstants.BEDROCK_TOTAL_TOKENS_STRING
        )
        prompt_tokens = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=BedrockConstants.BEDROCK_PROMPT_TOKENS_STRING
        )
        reporting_values[GenaiConstants.INPUT_TOKENS_METRIC_NAME] = prompt_tokens
        completion_tokens = get_tokens_per_request(
            method_response=endpoint_response,
            token_type=BedrockConstants.BEDROCK_COMPLETION_TOKENS_STRING
        )
        reporting_values[GenaiConstants.COMPLETION_TOKENS_METRIC_NAME] = completion_tokens
    except UnsupportedResponseException as exec:
        agent.logger.error(str(exec))
    return reporting_values


def get_reporting_values_streaming_type(model_name=None, token_usage=None, agent=None):
    reporting_values = dict()
    try:
        if token_usage[OpenaiConstants.PROMPT_TOKENS_STRING] and token_usage[OpenaiConstants.COMPLETION_TOKENS_STRING]:
            reporting_values[GenaiConstants.TOKENS_METRIC_NAME] = token_usage[OpenaiConstants.PROMPT_TOKENS_STRING] \
                + token_usage[OpenaiConstants.COMPLETION_TOKENS_STRING]
            reporting_values[GenaiConstants.INPUT_TOKENS_METRIC_NAME] = token_usage[
                OpenaiConstants.PROMPT_TOKENS_STRING]
            reporting_values[GenaiConstants.COMPLETION_TOKENS_METRIC_NAME] = token_usage[
                OpenaiConstants.COMPLETION_TOKENS_STRING]
    except UnsupportedModelException as exec:
        agent.logger.error(str(exec))
    return reporting_values


def parse_completion_response(completion_response=None, openai_major_version=0, agent=None):
    completion_res_list = None
    try:
        if openai_major_version < 1:
            completion_res_list = completion_response.to_dict_recursive().get('choices')
        else:
            completion_res_list = completion_response.to_dict().get('choices')
        return str(completion_res_list)
    except Exception as exc:
        agent.logger.error(f"Error occured while parsing resp: {str(exc)}")
        return None


def parse_moderation_response(moderation_response=None, openai_major_version=0, agent=None):
    moderation_res_list = None
    try:
        if openai_major_version < 1:
            moderation_res_list = moderation_response.to_dict_recursive().get('results')
        else:
            moderation_res_list = moderation_response.to_dict().get('results')
        return get_parsed_moderation_results(moderation_res_list, agent)
    except Exception as exc:
        agent.logger.error(f"Error occured while parsing moderation resp: {str(exc)}")
        return None


def get_parsed_moderation_results(moderation_res_list=None, agent=None):
    try:
        moderation_response_parsed = []
        if moderation_res_list:
            for dict_response in moderation_res_list:
                dict_categories = dict_response[OpenaiConstants.CATEGORIES_STRING]
                dict_category_scores = dict_response[OpenaiConstants.CATEGORY_SCORES_STRING]
                moderation_response = "{"

                for index, category in enumerate(dict_categories):
                    score = str(dict_category_scores[category])
                    modified_score = format(float(score), '.9f')
                    moderation_response += f"\"{category}\" : [{dict_categories[category]}, {modified_score}]"
                    if index < len(dict_categories) - 1:
                        moderation_response += ", "
                moderation_response += "}"
                moderation_response_parsed.append(moderation_response)
        return moderation_response_parsed
    except Exception as exc:
        agent.logger.error(f"Error occured while parsing moderation dict: {str(exc)}")
        return None


def get_token_usage_data(usage_data=None, model_name=None, input_messages=None, response_messages=None, agent=None):
    token_usage = dict()
    try:
        if usage_data:
            token_usage[OpenaiConstants.PROMPT_TOKENS_STRING] = usage_data.prompt_tokens \
                if hasattr(usage_data, OpenaiConstants.PROMPT_TOKENS_STRING) \
                else usage_data.get(OpenaiConstants.PROMPT_TOKENS_STRING)
            token_usage[OpenaiConstants.COMPLETION_TOKENS_STRING] = usage_data.completion_tokens \
                if hasattr(usage_data, OpenaiConstants.COMPLETION_TOKENS_STRING) \
                else usage_data.get(OpenaiConstants.COMPLETION_TOKENS_STRING)
        elif model_name and response_messages:
            # if tiktoken is not added as import, then this returns none
            token_usage[OpenaiConstants.PROMPT_TOKENS_STRING] = \
                calculate_token_usage_from_string(model_name, input_messages, agent)
            token_usage[OpenaiConstants.COMPLETION_TOKENS_STRING] = \
                calculate_token_usage_from_string(model_name, response_messages, agent)
    except Exception as exc:
        agent.logger.error(f"Error occured while streaming token calculation, error={str(exc)}.")
    return token_usage


def get_moderation_input_query(args, kwargs):
    input_query = None
    if kwargs and "input" in kwargs:
        input_query = kwargs.get('input')
    elif args and len(args) > 0:
        input_query = args[0]
    return input_query


def get_completion_opr_string(module_name=""):
    return "chat.completions" if "chat_completion" in module_name \
        or "chat.completions" in module_name else "completions"


def get_streaming_message_obj(delta, agent=None):
    message_obj = dict()
    try:
        if isinstance(delta, dict):
            message_role = delta.get(OpenaiConstants.ROLE_FIELD)
            message_name = delta.get(OpenaiConstants.NAME_FIELD)
            message_content = delta.get(OpenaiConstants.CONTENT_FIELD)
        else:
            message_role = delta.role if hasattr(delta, OpenaiConstants.ROLE_FIELD) else None
            message_name = delta.name if hasattr(delta, OpenaiConstants.NAME_FIELD) else None
            message_content = delta.content if hasattr(delta, OpenaiConstants.CONTENT_FIELD) else None
    except KeyError as ex:
        agent.logger.error(str(ex))
    if message_role:
        message_obj[OpenaiConstants.ROLE_FIELD] = message_role
    if message_name:
        message_obj[OpenaiConstants.NAME_FIELD] = message_name
    if message_content:
        message_obj[OpenaiConstants.CONTENT_FIELD] = message_content
    return message_obj


def set_complete_response_obj(choices, complete_response, response_content, agent):
    for choice in choices:
        delta = choice.delta if hasattr(choice, OpenaiConstants.DELTA_FIELD) \
            else choice.get(OpenaiConstants.DELTA_FIELD)
        if delta:
            message_obj = get_streaming_message_obj(delta, agent)
            if OpenaiConstants.CONTENT_FIELD in message_obj:
                response_content += message_obj[OpenaiConstants.CONTENT_FIELD]

            if message_obj:
                complete_response["response"].append(message_obj)


def set_parsed_chunk_values(chunk, response_content, complete_response, usage_data, agent=None):
    try:
        choices = chunk.choices if hasattr(chunk, OpenaiConstants.CHOICES_FIELD) \
            else chunk.get(OpenaiConstants.CHOICES_FIELD)
        
        set_complete_response_obj(choices, complete_response, response_content, agent)

        if not complete_response["model"]:
            complete_response["model"] = chunk.model if hasattr(chunk, OpenaiConstants.MODEL_FIELD) \
                else chunk.get(OpenaiConstants.MODEL_FIELD)
        # when stream_options: {"include_usage": true}, usage data is returned in one of the chunks
        if not usage_data:
            if isinstance(chunk, dict):
                usage_data = chunk.get(OpenaiConstants.USAGE_FIELD, None)
            elif hasattr(chunk, OpenaiConstants.USAGE_FIELD):
                usage_data = chunk.usage
    except Exception as ex:
        agent.logger.error(f"Error occured while parsing streaming response, error = {str(ex)}")
        response_content = ""
        complete_response = {"response": [], "model": ""}
        usage_data = None
    return response_content, complete_response, usage_data


def add_multiple_exit_suppression_header(url_string, headers):
    add_suppression_header = False
    for openai_api_type in OpenaiConstants.SUPPORTED_OPENAI_APIS_URISUFFIX_LIST:
        if openai_api_type in url_string:
            add_suppression_header = True
    # Below check to add suppression header(appd_exit_created) only if we are already intercepting the call
    if url_string and add_suppression_header:
        headers[OpenaiConstants.OPENAI_EXIT_CREATED_HEADER] = "True"


def get_metric_complaint_string(name):
    name = name.replace(":", "-")
    name = name.replace("|", "-")
    return name


class UnsupportedModelException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UnsupportedModelException: {self.message}"


class UnsupportedResponseException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"UnsupportedResponseException: {self.message}"


class MissingReportingValuesExcepion(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"MissingReportingValuesExcepion: {self.message}"
