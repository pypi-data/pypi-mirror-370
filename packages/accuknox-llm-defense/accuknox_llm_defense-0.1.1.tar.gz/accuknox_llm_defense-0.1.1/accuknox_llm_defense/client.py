import requests
import jwt
class LLMDefenseClient:
    def __init__(self, llm_defense_api_key,user_info=""):
        """
        Initialize the LLM Defence Client.

        :param llm_defence_api_key: Bearer token for authentication
        :param user_info: Value for 'User' header
        :param secret_token: Optional secret token for header
        :param environment: One of ('dev', 'stage', 'demo', 'prod', 'localhost')
                            Defaults to 'prod' if not provided or invalid
        """
        token_environment=jwt.decode(llm_defense_api_key, options={"verify_signature": False})
        base_url=token_environment.get("iss")
        self.base_url = f"https://{base_url}/llm-defence/application-query"
        self.headers = {
            "Authorization": f"Bearer {llm_defense_api_key}",
            "Content-Type": "application/json",
            "User": user_info
        }

    def scan_prompt(self, content):
        """
        Scan a prompt for vulnerabilities.
        """
        payload = {
            "query_type": "prompt",
            "content": content
        }
        return self._post_request(payload)

    def scan_response(self,content,prompt="",session_id=""):
        """
        Scan a response for vulnerabilities.
        """
        payload = {
            "query_type": "response",
            "prompt": prompt,
            "content": content,
            "session_id": session_id
        }
        return self._post_request(payload)

    def _post_request(self, payload):
        """
        Internal helper to send POST request.
        """
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
