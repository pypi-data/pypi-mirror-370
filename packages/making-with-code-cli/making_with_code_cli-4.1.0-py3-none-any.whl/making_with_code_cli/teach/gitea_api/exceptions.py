class GiteaServerUnavailable(Exception):
    pass

class RequestFailed(Exception):
    def __init__(self, response, *args, **kwargs):
        status_code = response.status_code
        detail = response.content
        msg = f"Gitea server request failed ({status_code}): {detail}"
        super().__init__(msg)

