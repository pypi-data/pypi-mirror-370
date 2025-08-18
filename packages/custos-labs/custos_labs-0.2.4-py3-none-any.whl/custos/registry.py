# custos/registry.py

class CustosRegistry:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.policies = ["fake identity", "deceive humans"]

    def get_active_policies(self) -> list:
        return self.policies
