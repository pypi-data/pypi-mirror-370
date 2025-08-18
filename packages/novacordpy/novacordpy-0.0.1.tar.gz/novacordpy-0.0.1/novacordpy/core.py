class NovaClient:
    def __init__(self, token: str):
        self.token = token

    def run(self):
        print(f"NovaCordpy-Client läuft mit Token: {self.token[:5]}***")
