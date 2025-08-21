# Original Copyright https://github.com/yeger00/pylspclient. Licensed under MIT License.
from __future__ import print_function
import threading
import json
from typing import Any, Dict, Callable, Union, Optional, Tuple, TypedDict
from .lsp_errors import ErrorCodes, ResponseError
from .json_rpc_endpoint import JsonRpcEndpoint
from .utils import log_pylspclient_action
import logging

ResultType = Optional[Dict[str, Any]]

class ErrorType(TypedDict):
    code: ErrorCodes
    message: str
    data: Optional[Any]


class LspEndpoint(threading.Thread):
    def __init__(
            self,
            json_rpc_endpoint: JsonRpcEndpoint,
            method_callbacks: Dict[str, Callable[[Any], Any]] = {},
            notify_callbacks: Dict[str, Callable[[Any], Any]] = {},
            timeout: int = 2
        ):
        threading.Thread.__init__(self)
        self.json_rpc_endpoint = json_rpc_endpoint
        self.notify_callbacks = notify_callbacks
        self.method_callbacks = method_callbacks
        self.event_dict: dict = {}
        self.response_dict: Dict[Union[str, int], Tuple[ResultType, ErrorType]] = {}
        self.next_id: int = 0
        self._timeout: int = timeout
        self.shutdown_flag: bool = False


    def handle_result(self, rpc_id: Union[str, int], result: ResultType, error: ErrorType):
        """Handle responses to requests we sent to the server"""
        log_pylspclient_action("Handling result from LSP server", rpc_id=rpc_id, result=result, error=error)
        if rpc_id not in self.event_dict:
            logging.error(f"Received response for unknown request ID: {rpc_id}")
            return
        
        self.response_dict[rpc_id] = (result, error)
        cond = self.event_dict[rpc_id]
        cond.acquire()
        cond.notify()
        cond.release()

    def stop(self) -> None:
        self.shutdown_flag = True


    def run(self) -> None:
        while not self.shutdown_flag:
            try:
                if self.json_rpc_endpoint is None:
                    logging.error("Error: json_rpc_endpoint is None, stopping")
                    break
                jsonrpc_message = self.json_rpc_endpoint.recv_response()
                if jsonrpc_message is None:
                    print("server quit")
                    break
                method = jsonrpc_message.get("method")
                result = jsonrpc_message.get("result")
                error = jsonrpc_message.get("error")
                rpc_id = jsonrpc_message.get("id")
                params = jsonrpc_message.get("params")
                logging.debug(f"Message received: {jsonrpc_message}")

                if method:
                    if rpc_id is not None:
                        # Method call from server to client
                        log_pylspclient_action("Method call from server", method=method, params=params, rpc_id=rpc_id)
                        if method not in self.method_callbacks:
                            raise ResponseError(ErrorCodes.MethodNotFound, "Method not found: {method}".format(method=method))
                        result = self.method_callbacks[method](params)
                        self.send_response(rpc_id, result, None)
                    else:
                        # a call for notify
                        if method not in self.notify_callbacks:
                            # Have nothing to do with this.
                            log_pylspclient_action("Notify method not found", method=method, params=params, result=result)
                        else:
                            log_pylspclient_action("Notify method found", method=method, params=params)
                            self.notify_callbacks[method](params)
                else:
                    self.handle_result(rpc_id, result, error)
            except ResponseError as e:
                if 'rpc_id' in locals():
                    self.send_response(rpc_id, None, e)
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error in LSP response: {e}")
                logging.error(f"Response length: {len(str(jsonrpc_message)) if 'jsonrpc_message' in locals() else 'unknown'}")
                # Continue processing other messages instead of breaking
                continue
            except Exception as e:
                logging.error(f"Unexpected error in run: {e}", exc_info=True)
                break


    def send_response(self, id: Union[str, int, None], result: Any = None, error: Optional[Exception] = None) -> None:
        log_pylspclient_action("Sending response", id=id, result=result, error=error)
        message_dict: dict = {}
        message_dict["jsonrpc"] = "2.0"
        message_dict["id"] = id
        if result is not None:
            message_dict["result"] = result
        if error is not None:
            message_dict["error"] = error
        self.json_rpc_endpoint.send_request(message_dict)


    def send_message(self, method_name: str, params: dict, id = None) -> None:
        """Send a message to the server"""
        log_pylspclient_action("Sending message to LSP server", method=method_name, params=params, id=id)
        if self.json_rpc_endpoint is None:
            logging.error("Cannot send message: json_rpc_endpoint is None")
            return
  
        if method_name is None:
            logging.error("Cannot send message: method_name is None")
            return
  
        if params is None:
            logging.debug("params is None, using empty dict instead")
            params = {}

        message_dict = {
            "jsonrpc": "2.0",
            "method": method_name,
            "params": params
        }
  
        if id is not None:
            message_dict["id"] = id
  
        logging.debug(f"Sending message: method={method_name}, params={params}, id={id}")
  
        try:
            self.json_rpc_endpoint.send_request(message_dict)
            logging.debug("Message sent successfully")
        except Exception as e:
            logging.error(f"Error sending message: {e}", exc_info=True)


    def call_method(self, method_name: str, **kwargs) -> Any:
        log_pylspclient_action("Calling method", method=method_name, kwargs=kwargs)
        current_id = self.next_id
        self.next_id += 1
        cond = threading.Condition()
        self.event_dict[current_id] = cond

        cond.acquire()
        self.send_message(method_name, kwargs, current_id)
        if self.shutdown_flag:
            cond.release()
            return None

        if not cond.wait(timeout=self._timeout):
            cond.release()
            self.event_dict.pop(current_id, None)
            raise TimeoutError()
        
        cond.release()

        self.event_dict.pop(current_id)

        if current_id not in self.response_dict:
            raise Exception(f"No response received for {method_name}")
    
        result, error = self.response_dict.pop(current_id)
        if error:
            raise ResponseError(error["code"], error["message"], error.get("data"))
        return result


    def send_notification(self, method_name, **kwargs):
        """
          Send a notification to the server.
          This is used for sending information to the server that doesn't require a response.
        """
        log_pylspclient_action("Sending notification to LSP Server", method=method_name, kwargs=kwargs)
        logging.debug(f"[LSP_ENDPOINT] send_notification called with method: {method_name}, kwargs: {kwargs}")
        self.send_message(method_name, kwargs)