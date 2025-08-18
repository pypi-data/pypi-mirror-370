# alignment/api/custos_client.py
import requests

class CustosClient:
    def __init__(self, admin_token: str, base_url: str = "https://api.custos.ai/v1"):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }

    def generate_api_key(self, user_id: str, label: str = "default-key"):
        url = f"{self.base_url}/api-keys/"
        payload = {
            "user_id": user_id,
            "label": label
        }
        res = requests.post(url, headers=self.headers, json=payload)

        if res.status_code == 201:
            return res.json()
        else:
            raise Exception(f"Key generation failed: {res.status_code} - {res.text}")

    def evaluate_alignment(self, prompt: str, response: str, api_key: str):
        eval_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        url = f"{self.base_url}/evaluate/"
        payload = {
            "prompt": prompt,
            "response": response
        }

        res = requests.post(url, headers=eval_headers, json=payload)

        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(f"Evaluation failed: {res.status_code} - {res.text}")
