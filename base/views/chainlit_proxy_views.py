"""
Chainlit Proxy View
Forwards requests from Django's /chainlit/ to Chainlit server on port 8001.
This allows the entire app to run on a single URL (port 8000).
"""

import httpx
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

CHAINLIT_BASE_URL = "http://localhost:8001"


@csrf_exempt
def chainlit_proxy(request, path=""):
    """
    Proxy all /chainlit/* requests to the Chainlit server running on port 8001.
    """
    # Build target URL
    target_url = f"{CHAINLIT_BASE_URL}/{path}"
    if request.META.get("QUERY_STRING"):
        target_url += f"?{request.META['QUERY_STRING']}"

    # Forward headers (exclude Host)
    headers = {}
    for key, value in request.META.items():
        if key.startswith("HTTP_") and key != "HTTP_HOST":
            header_name = key[5:].replace("_", "-").title()
            headers[header_name] = value
        elif key in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            header_name = key.replace("_", "-").title()
            if value:
                headers[header_name] = value

    # Fix WebSocket upgrade path prefix
    headers["X-Forwarded-For"] = request.META.get("REMOTE_ADDR", "")
    headers["X-Forwarded-Proto"] = "http"

    try:
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=request.body,
            )

        # Build Django response
        django_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get("content-type", "text/html"),
        )

        # Forward relevant response headers
        skip_headers = {
            "content-encoding", "transfer-encoding",
            "connection", "keep-alive",
        }
        for key, value in response.headers.items():
            if key.lower() not in skip_headers:
                django_response[key] = value

        return django_response

    except httpx.ConnectError:
        return HttpResponse(
            """
            <html>
            <head><title>Chatbot Unavailable</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
                .box { background: white; padding: 40px; border-radius: 12px; display: inline-block; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h2 { color: #e74c3c; }
                p { color: #666; }
            </style>
            </head>
            <body>
                <div class='box'>
                    <h2>&#x1F916; Chatbot Server Unavailable</h2>
                    <p>The Chainlit chatbot server is not running.</p>
                    <p>Please start it with: <code>chainlit run main.py --port 8001</code></p>
                </div>
            </body>
            </html>
            """,
            status=503,
            content_type="text/html",
        )
    except Exception as e:
        return HttpResponse(
            f"<h2>Proxy Error</h2><p>{str(e)}</p>",
            status=500,
            content_type="text/html",
        )
