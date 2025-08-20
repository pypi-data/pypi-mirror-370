import os
import json
import requests
from json_autocomplete import json_autocomplete


class Vectocore:
    def __init__(self, base_url="", tenant_key="", ai_url=""):
        # 변수 은닉화
        self.__VECTOR_URL = "https://exapi.vectocore.com"
        if base_url != "":
            self.__VECTOR_URL = base_url

        self.__tenant_key = os.environ.get("VECTOCORE_TENANT_KEY", tenant_key)
        if self.__tenant_key == "" or self.__tenant_key is None:
            raise ValueError("Tenant key is none")

    def __request_post(self, data):
        headers = {"Content-Type": "application/json", "x-api-key": self.__tenant_key}
        response = requests.post(url=self.__VECTOR_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def put_index(self, index_name: str, desc=""):
        params = {"command": "put_index", "index_name": index_name, "index_desc": desc}
        result = self.__request_post(params)
        return result

    def delete_index(self, index_name: str):
        params = {
            "command": "delete_index",
            "index_name": index_name,
        }
        result = self.__request_post(params)
        return result

    def list_index(self):
        params = {"command": "list_index"}
        result = self.__request_post(params)
        return result

    def put_extream_data(self, index_name: str, doc_body: dict):
        params = {"command": "put_extream_data", "index_name": index_name, "doc_body": doc_body}
        result = self.__request_post(params)
        return result

    def get_extream_data(self, index_name: str, document_id: str):
        params = {"command": "get_extream_data", "index_name": index_name, "document_id": document_id}
        result = self.__request_post(params)
        return result

    def list_extream_data(self, index_name: str, last_key=None):
        params = {"command": "list_extream_data", "index_name": index_name}
        if last_key is not None:
            params["last_key"] = last_key
        result = self.__request_post(params)
        return result

    def delete_extream_data(self, index_name: str, document_id: str):
        params = {"command": "delete_extream_data", "index_name": index_name, "document_id": document_id}
        result = self.__request_post(params)
        return result

    def extream_search(self, question: str, index_name="", max_count=10, mode="VECTOR", web_search={}, find_index_prompt="", doc_only=False):
        params = {
            "command": "extream_search",
            "question": question,
            "index_name": index_name,
            "max_count": max_count,
            "mode": mode,
            "web_search": web_search,
            "find_index_prompt": find_index_prompt,
            "doc_only": doc_only,
        }
        result = self.__request_post(params)
        return result

    def web_search(self, question: str):
        params = {"command": "web_search", "question": question}
        result = self.__request_post(params)
        return result


class Lens:
    def __init__(
        self,
        base_url="",
        ai_url="",
        tenant_key="",
        role=None,
        rule=None,
        output_format=None,
        mode=None,
        web_search=None,
        agentic=None,
        max_his_count=None,
        session_key=None,
        num_of_ref=3,
        custom_system_prompt="",
        static_info=None
    ):
        # 변수 은닉화
        self.__VECTOR_URL = "https://exapi.vectocore.com"
        if base_url != "":
            self.__VECTOR_URL = base_url

        self.__AI_URL = "https://exai.vectocore.com"
        if ai_url != "":
            self.__AI_URL = ai_url

        self.__tenant_key = os.environ.get("VECTOCORE_TENANT_KEY", tenant_key)
        if self.__tenant_key == "" or self.__tenant_key is None:
            raise ValueError("Tenant key is none")
        self.role = role
        self.rule = rule
        self.output_format = output_format
        self.mode = mode
        self.web_search = web_search
        self.agentic = agentic
        self.max_his_count = max_his_count
        self.session_key = session_key
        self.num_of_ref = num_of_ref
        self.custom_system_prompt = custom_system_prompt
        self.static_info = static_info

    def __request_stream(self, data):
        headers = {"x-api-key": self.__tenant_key}
        response = requests.post(url=self.__AI_URL, headers=headers, json=data, stream=True)
        return response

    def __gen_stream_response(self, stream_response):
        stream_response.raise_for_status()
        decoded_str = ""
        jsonText = None
        for line in stream_response.iter_lines():
            if line:
                decoded_str += line.decode("utf-8")
                jsonText = json_autocomplete(decoded_str)

        return json.loads(jsonText)

    def chat(
        self,
        question,
        stream=False,
        index_name=None,
        custom_data=None,
        model=None,
        text_only_ref=False,
        is_first_msg=True,
        with_status=False,
    ):
        params = {"command": "lensChat", "question": question, "numOfRef": self.num_of_ref}
        if self.role is not None:
            params["role"] = self.role
        if self.rule is not None:
            params["rule"] = self.rule
        if self.output_format is not None:
            params["outputFormat"] = self.output_format
        if self.mode is not None:
            params["mode"] = self.mode
        if self.web_search is not None:
            params["web_search"] = self.web_search
        if self.agentic is not None:
            params["agentic"] = self.agentic
        if self.max_his_count is not None:
            params["maxHisCount"] = self.max_his_count
        if self.session_key is not None:
            params["sessionKey"] = self.session_key
        if custom_data is not None:
            params["customData"] = custom_data
        if index_name is not None:
            params["indexName"] = index_name
        if self.custom_system_prompt != "":
            params["customSystemPrompt"] = self.custom_system_prompt
        if self.static_info is not None:
            params["staticInfo"] = self.static_info
        if model is not None:
            params["model"] = model
        params["textOnlyRef"] = text_only_ref
        params["isFirstMsg"] = is_first_msg
        params["withStatus"] = with_status

        result = self.__request_stream(params)
        if stream:
            return result
        else:
            res = self.__gen_stream_response(result)
            return res

    def history(self, sessionKey, limit=5):
        params = {"command": "lensChatHistory", "sessionKey": sessionKey, "limit": limit}
        result = self.__request_stream(params)
        res = self.__gen_stream_response(result)
        return res

    def json_auto_complete(self, jsonText):
        return json_autocomplete(jsonText)


class AIMS:
    def __init__(self, ai_url="", tenant_key=""):
        # 변수 은닉화
        self.__AI_URL = "https://exai.vectocore.com"
        if ai_url != "":
            self.__AI_URL = ai_url

        self.__tenant_key = os.environ.get("VECTOCORE_TENANT_KEY", tenant_key)
        if self.__tenant_key == "" or self.__tenant_key is None:
            raise ValueError("Tenant key is none")

    def __request_stream(self, data):
        headers = {"x-api-key": self.__tenant_key}
        response = requests.post(url=self.__AI_URL, headers=headers, json=data, stream=True)
        return response

    def __gen_stream_response(self, stream_response):
        stream_response.raise_for_status()
        decoded_str = ""
        jsonText = None
        for line in stream_response.iter_lines():
            if line:
                decoded_str += line.decode("utf-8")
                jsonText = json_autocomplete(decoded_str)

        return json.loads(jsonText)

    def keypoint(
        self,
        text,
    ):
        params = {"command": "keywords", "text": text}

        result = self.__request_stream(params)
        res = self.__gen_stream_response(result)
        return res

    def im_cap(
        self,
        image_url,
    ):
        params = {"command": "imCap", "imageUrl": image_url}

        result = self.__request_stream(params)
        res = self.__gen_stream_response(result)
        return res

    def translate(self, language, text, stream=False):
        params = {"command": "translate", "language": language, "text": text}

        result = self.__request_stream(params)
        if stream:
            return result
        else:
            res = self.__gen_stream_response(result)
            return res

    def json_auto_complete(self, jsonText):
        return json_autocomplete(jsonText)
