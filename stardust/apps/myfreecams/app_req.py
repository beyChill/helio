from mitmproxy import http

BLOCK_WORDS = [
    "assets",
    "favicon",
    "google",
    "google-analytics",
    "mobile",
    "snap.mfcimg",
]
BLOCK_EXTENSIONS = [
    ".gif",
    ".jpg",
    ".jpeg",
    ".js",
    ".png",
    ".svg",
    ".webp",
]
class AppRequest:
    def __init__(self):
        pass
    
    def request(self,flow: http.HTTPFlow) -> None:
        del flow.request.headers["accept-encoding"]
        flow.request.headers["accept-encoding"] = "gzip"
        url = flow.request.pretty_url

        if url.__contains__("playlist"):
            print("Request", url)

        block_extension = any(url.endswith(ext) for ext in BLOCK_EXTENSIONS)
        block_words = any(block in url for block in BLOCK_WORDS)
        if block_extension:
            return

        if block_words:
            return

        if url.endswith("&debug=cams"):
            pass
            
