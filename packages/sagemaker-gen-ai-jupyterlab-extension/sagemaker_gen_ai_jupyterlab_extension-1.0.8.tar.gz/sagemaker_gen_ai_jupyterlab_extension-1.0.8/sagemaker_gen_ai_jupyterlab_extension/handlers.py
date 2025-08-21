import json
from tornado import ioloop
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from tornado.web import StaticFileHandler
from .websocket_manager import manager
from .websocket_handler import WebSocketHandler
import logging
import os

logger = logging.getLogger('SageMakerGenAIJupyterLabExtension')
CLIENT_HTML_PATH = str(os.path.join(os.path.dirname(__file__), "static", "client.html"))
logger.info(f"CLIENT_HTML_PATH: {CLIENT_HTML_PATH}")
print(f"CLIENT_HTML_PATH: {CLIENT_HTML_PATH}")

class RouteHandler(APIHandler):
    # Removed authentication requirement for development
    def get(self):
        self.finish(json.dumps({
            "data": "This is /sagemaker_gen_ai_jupyterlab_extension/get-example endpoint!"
        }))

def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # Add CORS headers to allow requests from any origin
    def _set_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with, content-type, authorization")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        
    # Handle OPTIONS requests for CORS preflight
    def _options(self):
        self.set_status(204)
        self.finish()

    try:
        # Patch the handler classes to add CORS headers and OPTIONS method
        RouteHandler.set_default_headers = _set_headers
        RouteHandler.options = _options

        route_pattern = url_path_join(base_url,"sagemaker_gen_ai_jupyterlab_extension", "get-example")
        websocket_pattern = url_path_join(base_url,"sagemaker_gen_ai_jupyterlab_extension", "ws")
        static_pattern = url_path_join(base_url, "sagemaker_gen_ai_jupyterlab_extension", "static") + "/(.*)"
        
        handlers = [
            (route_pattern, RouteHandler),
            (websocket_pattern, WebSocketHandler),
            (static_pattern, StaticFileHandler, {"path": os.path.dirname(CLIENT_HTML_PATH)}),
        ]
        web_app.add_handlers(host_pattern, handlers)

        # Set the IOLoop reference
        manager.set_io_loop(ioloop.IOLoop.current())

    except Exception as e:
        print(f"Error setting up handlers: {e}")
        logger.error(f"Error setting up handlers: {e}")
    