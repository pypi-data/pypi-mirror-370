import requests

class GraphRAG:
    def __init__(self, api_key: str = None, endpoint: str = "http://localhost:8000"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")

    def _headers(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(self, question: str) -> str:
        url = f"{self.endpoint}/api/v1/chat"
        resp = requests.post(url, headers=self._headers(), json={"question": question})
        resp.raise_for_status()
        return resp.json().get("answer", "")

    def upload_data(self, file_path: str, lang: str = "vie") -> dict:
        url = f"{self.endpoint}/api/v1/upload"
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "application/pdf")}
            data = {"lang": lang}
            resp = requests.post(url, headers=self._headers(), files=files, data=data)
        resp.raise_for_status()
        return resp.json()
