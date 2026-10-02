import urllib.request
import json

def check_endpoint(url, name):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            content = resp.read()
            print(f"[SUCCESS] {name} ({url})")
            print(f"          Status: {resp.status}")
            print(f"          Content-Type: {resp.headers.get('Content-Type')}")
            print(f"          Length: {len(content)} bytes")
            if 'json' in url:
                parsed = json.loads(content.decode('utf-8'))
                title = parsed.get("info", {}).get("title")
                version = parsed.get("openapi")
                paths = len(parsed.get("paths", {}))
                print(f"          OpenAPI Title: '{title}'")
                print(f"          OpenAPI Version: {version}")
                print(f"          Total Routes Defined: {paths}")
            elif 'redoc' in url:
                html = content.decode('utf-8')
                print(f"          Contains Redoc.init: {'Redoc.init' in html}")
                print(f"          Contains redoc.standalone.js: {'redoc.standalone.js' in html}")
                print(f"          Contains redoc-container: {'redoc-container' in html}")
            elif 'docs' in url:
                html = content.decode('utf-8')
                print(f"          Contains swagger-ui: {'swagger-ui' in html}")
    except Exception as e:
        print(f"[FAILED] {name} ({url}): {e}")

if __name__ == "__main__":
    check_endpoint("http://127.0.0.1:8000/openapi.json", "GET /openapi.json")
    print("-" * 60)
    check_endpoint("http://127.0.0.1:8000/docs", "GET /docs")
    print("-" * 60)
    check_endpoint("http://127.0.0.1:8000/redoc", "GET /redoc")
