from .client import Empty, HttpUrl, SDKClient, SDKResponse


class ClickAgainService:
    def __init__(self, client: SDKClient, url: HttpUrl):
        self._client = client
        self._url = url
        self.delete_url = self._url + "/api/delete_org_from_amocrm/?org_amo_id="

    def delete_amocrm_org(self, org_amo_id: int, token: str) -> SDKResponse[Empty]:
        return self._client.post(
            self.delete_url + f"{org_amo_id}",
            Empty,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"TokenService {token}",
            },
            timeout=60,
        )
