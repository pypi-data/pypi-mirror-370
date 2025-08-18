import sys
import http.client
import time
import uuid
import socket
import platform

from cirrondly_cli.conf import set_api_key
from cirrondly_cli.events.sender import send_event, send_initialization_event
from cirrondly_cli.exceptions.handler import exception_hook
from cirrondly_cli.frameworks.auto_apply_middleware import auto_apply_middleware
from cirrondly_cli.http.request import traced_request, begin_with_capture
from cirrondly_cli.logging.handlers import InterceptStdout, InterceptStderr
from cirrondly_cli.monitoring.lifecycle import detect_restarts
from cirrondly_cli.monitoring.metrics import track_runtime
from cirrondly_cli.queue.manager import flush_queue
from cirrondly_cli.tools.detection.environment import detect_environment

APIKEY = None  # Global API key for event sending
last_resource_check = time.time()
class Cirrondly:
    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Cirrondly requires a valid API key.")

        set_api_key(api_key)
        send_initialization_event(api_key)
        detect_restarts(api_key)
        http.client.HTTPConnection.request = traced_request
        http.client.HTTPResponse.begin = begin_with_capture
        sys.excepthook = exception_hook
        sys.stdout = InterceptStdout()
        sys.stderr = InterceptStderr()
        try:
            import psutil
            track_runtime(last_resource_check)
        except ImportError:
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                import psutil
                track_runtime(last_resource_check)
            except:
                track_runtime(last_resource_check)

        flush_queue()
        auto_apply_middleware(api_key)
        send_event({
            "provider_name": "cirrondly",
            "service_name": "initialization",
            "region": socket.gethostname(),
            "path": "/",
            "request_method": "INIT",
            "request_headers": {},
            "request_id": str(uuid.uuid4()),
            "timestamp": str(int(time.time())),
            "method": "initialization",
            "status_code": 200,
            "response_time": 0,
            "error_details": None,
            "response_body": {},
            "request_data": {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "environment": detect_environment()
            }
        }, api_key)
        print("[Cirrondly] Monitoring initialized with your API key.")

# For backward compatibility, keep the function
def cirrondly(api_key: str):
    return Cirrondly(api_key)