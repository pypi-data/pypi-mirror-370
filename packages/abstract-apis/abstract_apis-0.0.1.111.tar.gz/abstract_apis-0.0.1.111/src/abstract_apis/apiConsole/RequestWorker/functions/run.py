from ..imports import getRequest,postRequest,json
def run(self):
    try:
        # Try to pass timeout; if your helpers don't accept it, fallback.
        try:
            if self.method == "GET":
                res = getRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
            else:
                res = postRequest(url=self.url, headers=self.headers, data=self.params, timeout=self.timeout)
        except TypeError:
            if self.method == "GET":
                res = getRequest(url=self.url, headers=self.headers, data=self.params)
            else:
                res = postRequest(url=self.url, headers=self.headers, data=self.params)

        txt = json.dumps(res, indent=4) if isinstance(res, (dict, list)) else str(res)
        self.success.emit(txt)
    except Exception as ex:
        self.failure.emit(f"✖ Error: {ex}")
