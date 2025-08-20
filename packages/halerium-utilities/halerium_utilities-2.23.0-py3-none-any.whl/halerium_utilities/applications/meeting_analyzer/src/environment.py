import os
from urllib.parse import urljoin


class HaleriumEnvironment:
    def __init__(self):
        self.tenant = os.getenv("HALERIUM_TENANT_KEY", "")
        self.workspace = os.getenv("HALERIUM_PROJECT_ID", "")
        self.runner_id = os.getenv("HALERIUM_ID", "")
        self.base_url = os.getenv("HALERIUM_BASE_URL", "")
        self.prompt_url = urljoin(
            self.base_url,
            "/api"
            f"/tenants/{self.tenant}"
            f"/projects/{self.workspace}"
            f"/runners/{self.runner_id}"
            "/prompt",
        )

        self.headers = {"halerium-runner-token": os.getenv("HALERIUM_TOKEN", "")}
