import pathlib
import textwrap
from google import genai
from google.genai import types
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from aibridgecore.output_validation.convertors import FromJson, IntoJson
from openai import OpenAI
import time
import uuid
from aibridgecore.exceptions import GeminiException, AIBridgeException, ValidationException
from aibridgecore.prompts.prompt_completion import Completion
from aibridgecore.ai_services.ai_abstraction import AIInterface
from aibridgecore.output_validation.active_validator import ActiveValidator
import json
from aibridgecore.constant.common import get_function_from_json, parse_fromat, parse_api_key


class GeminiAIService(AIInterface):
    """
    Base class for Gemini Services
    """

    @classmethod
    def generate(
        self,
        prompts: list[str] = [],
        prompt_ids: list[str] = [],
        prompt_data: list[dict] = [],
        variables: list[dict] = [],
        output_format: list[str] = [],
        format_strcture: list[str] = [],
        model="gemini-pro",
        variation_count: int = 1,
        max_tokens: int = None,
        temperature: float = 0.5,
        message_queue=False,
        api_key=None,
        output_format_parse=True,
        stop_subsequence: list[str] = None,
        stream=False,
        context=[],
    ):
        try:
            if prompts and prompt_ids:
                raise GeminiException(
                    "please provide either prompts or prompts ids at atime"
                )
            if not prompts and not prompt_ids:
                raise GeminiException(
                    "Either provide prompts or prompts ids to generate the data"
                )
            if prompt_ids:
                prompts_list = Completion.create_prompt_from_id(
                    prompt_ids=prompt_ids,
                    prompt_data_list=prompt_data,
                    variables_list=variables,
                )
            if prompts:
                if prompt_data or variables:
                    prompts_list = Completion.create_prompt(
                        prompt_list=prompts,
                        prompt_data_list=prompt_data,
                        variables_list=variables,
                    )
                else:
                    prompts_list = prompts
            if output_format:
                if len(output_format) != len(prompts_list):
                    raise ValidationException(
                        "length of output_format must be equal to length of the prompts"
                    )
            if format_strcture:
                if len(format_strcture) != len(prompts_list):
                    raise ValidationException(
                        "length of format_strcture must be equal to length of the prompts"
                    )
            updated_prompts = []
            for _prompt in prompts_list:
                format = None
                format_str = None
                if output_format:
                    format = output_format[prompts_list.index(_prompt)]
                if format_strcture:
                    format_str = format_strcture[prompts_list.index(_prompt)]
                if output_format_parse:
                    u_prompt = parse_fromat(
                        _prompt, format=format, format_structure=format_str
                    )
                    updated_prompts.append(u_prompt)
            if not updated_prompts:
                updated_prompts = prompts_list
            if message_queue:
                id = uuid.uuid4()
                message_data = {
                    "id": str(id),
                    "prompts": json.dumps(updated_prompts),
                    "model": model,
                    "variation_count": variation_count,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "ai_service": "gemini_ai",
                    "output_format": json.dumps(output_format),
                    "format_structure": json.dumps(format_strcture),
                    "api_key": api_key,
                    "stop_subsequence": stop_subsequence,
                    "stream": stream,
                    "context": context,
                }
                message = {"data": json.dumps(message_data)}
                from aibridgecore.queue_integration.message_queue import MessageQ

                MessageQ.mq_enque(message=message)
                return {"response_id": str(id)}
            return self.get_response(
                updated_prompts,
                model,
                variation_count,
                max_tokens,
                temperature,
                output_format,
                format_strcture,
                api_key=api_key,
                stop_subsequence=stop_subsequence,
                stream=stream,
                context=context,
            )
        except Exception as e:
            raise GeminiException(e)


    @classmethod
    def execute_text_prompt(
        self,
        api_key,
        model,
        messages,
        n,
        max_tokens=None,
        temperature=0.5,
        stop_subsequence=None,
        stream=False,
        prompt=""
    ):
        google_search_tool = Tool(
            google_search = GoogleSearch()
        )
        prompt=f"""prompt:{prompt}
        context:{messages}
        """
        client = genai.Client(api_key=api_key)
        if max_tokens:
            return (
                client.models.generate_content(
                    model=model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        candidate_count=n,
                        stop_sequences=stop_subsequence,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    )
                )
            )
        else:
            return (
                client.models.generate_content(
                    model=model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        candidate_count=n,
                        stop_sequences=stop_subsequence,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                    )
                )
            )

    @classmethod
    def execute_prompt_function_calling(
        self,
        api_key,
        model,
        messages,
        n,
        functions_call,
        max_tokens=None,
        temperature=0.5,
        stop_subsequence=None,
        stream=False,
        prompt=""
    ):
        client = genai.Client(api_key=api_key)
        prompt=f"""prompt:{prompt}
        context:{messages}
        """
        get_data = types.FunctionDeclaration(
            name="get_data",
            description="Get information",
            parameters=functions_call,
        )
        story_tools = types.Tool(
            function_declarations=[get_data],
        )
        if max_tokens:
            return (
                client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        candidate_count=n,
                        stop_sequences=stop_subsequence,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                        tools=[story_tools]
                    )
                )
            )
        else:
            return (
                client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        candidate_count=n,
                        stop_sequences=stop_subsequence,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                        tools=[story_tools]
                    )
                )
            )

    @classmethod
    def get_prompt_context(self, context):
        context_list = []
        prev_role = ""
        if context:
            for _context in context:
                if _context["role"] not in ["user", "system", "assistant"]:
                    raise GeminiException(
                        "Invalid role provided. Please provide either user or system, assistant"
                    )
                key = "user"
                if _context["role"] in ["assistant", "system"]:
                    key = "model"
                if prev_role == key:
                    if key == "user":
                        context_list.append({"role": "model", "parts": ["understood"]})
                    elif key == "model":
                        context_list.append({"role": "user", "parts": ["generated"]})
                else:
                    context_list.append({"role": key, "parts": [_context["context"]]})
                prev_role = key
            if context_list:
                data_test = context_list[-1]
                if data_test["role"] == "user":
                    context_list.append({"role": "model", "parts": ["understood"]})
                data = context_list[0]
                if data["role"] == "model":
                    context_list = [
                        {"role": "user", "parts": ["you are friendly assistance"]}
                    ] + context_list

        context_string=""
        for context in context_list:
            context_string+=f"{context['role']}: {context['parts'][0]}\n"
        return context_string


    @classmethod
    def get_response(
        self,
        prompts,
        model="gemini-pro",
        variation_count=1,
        max_tokens=None,
        temperature=0.5,
        output_format=[],
        format_structure=[],
        api_key=None,
        stop_subsequence=None,
        stream=False,
        context=[],
    ):
        try:
            if output_format:
                if isinstance(output_format, str):
                    output_format = json.loads(output_format)
            if format_structure:
                if isinstance(format_structure, str):
                    format_structure = json.loads(format_structure)
            if not prompts:
                raise GeminiException("No prompts provided")
            api_key = api_key if api_key else parse_api_key("gemini_ai")
            context_string = self.get_prompt_context(context) if context else []
            model_output = []
            token_used = 0
            input_tokens = 0
            output_tokens = 0
            _formatter = "string"
            for index, prompt in enumerate(prompts):
                if output_format:
                    _formatter = output_format[index]
                # message_data.append({"role": "user", "parts": [prompt]})
                # message_data.append(prompt)
                if _formatter not in ["json", "csv", "xml"]:
                    response = self.execute_text_prompt(
                        api_key,
                        model=model,
                        messages=context_string,
                        n=variation_count,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop_subsequence=stop_subsequence,
                        stream=stream,
                        prompt=prompt
                    )
                    print(response)
                else:
                    if _formatter == "csv":
                        schema = IntoJson.csv_to_json(format_structure[index])
                    elif _formatter == "xml":
                        schema = IntoJson.xml_to_json(format_structure[index])
                    elif _formatter == "json":
                        schema = json.loads(format_structure[index])
                    functions = [get_function_from_json(schema, call_from="gemini_ai")]
                    functions=functions[0]["parameters"]
                    print(functions)
                    response = self.execute_prompt_function_calling(
                        api_key=api_key,
                        model=model,
                        messages=context_string,
                        n=variation_count,
                        functions_call=functions,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        prompt=prompt
                    )
                print(response)
                if response.candidates[0].content.parts[0].text:
                    content = response.candidates[0].content.parts[0].text
                else:
                    content = response.candidates[0].content.parts[0].function_call
                    content = json.dumps(type(content).to_dict(content))
                    content = json.loads(content)
                    content = content["args"]
                usage_metadata = response.usage_metadata
                # Extract token counts
                tokens = usage_metadata.total_token_count
                print(tokens, type(tokens))
                token_used = token_used + tokens
                input_tokens += usage_metadata.prompt_token_count
                for res in response.candidates:
                    if response.candidates[0].content.parts[0].text:
                        content = response.candidates[0].content.parts[0].text
                    else:
                        content = response.candidates[0].content.parts[0].function_call
                        content = json.dumps(type(content).to_dict(content))
                        content = json.loads(content)
                        content = content["args"]
                    output_tokens += usage_metadata.candidates_token_count 
                    if output_format:
                        try:
                            if _formatter == "csv":
                                content = FromJson.json_to_csv(content)
                            elif _formatter == "xml":
                                content = FromJson.json_to_xml(content)
                        except AIBridgeException as e:
                            raise ValidationException(
                                f"Ai response is not in valid {_formatter}"
                            )
                        if _formatter == "json":
                            _validate_obj = ActiveValidator.get_active_validator(
                                _formatter
                            )
                            try:
                                content = _validate_obj.validate(
                                    content,
                                    schema=(
                                        format_structure[index]
                                        if format_structure
                                        else None
                                    ),
                                )
                            except AIBridgeException as e:
                                content_error = {
                                    "error": f"{e}",
                                    "ai_response": content,
                                }
                                content = json.dumps(content_error)
                    if index >= len(model_output):
                        model_output.append({"data": [content]})
                    else:
                        model_output[index]["data"].append(content)
            message_value = {
                "items": {
                    "response": model_output,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "token_used": token_used,
                    "created_at": int(time.time()),
                    "ai_service": "gemini_ai",
                }
            }
            return message_value
        except Exception as e:
            raise GeminiException(e)
