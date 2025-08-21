import threading

class WebSocketManager:
    def __init__(self):
        self.connections = set()
        self.lock = threading.Lock()
        self.io_loop = None  # Will be set when server starts
    
    def set_io_loop(self, loop):
        """Set the main IOLoop instance"""
        self.io_loop = loop
        print("IOLoop set in WebSocketManager")
    
    def add_connection(self, conn):
        with self.lock:
            self.connections.add(conn)
        print(f"New connection. Total: {len(self.connections)}")
    
    def remove_connection(self, conn):
        with self.lock:
            if conn in self.connections:
                self.connections.remove(conn)
        print(f"Connection closed. Total: {len(self.connections)}")
    
    def broadcast(self, message):
        """Thread-safe broadcasting"""
        with self.lock:
            connections = list(self.connections)
        
        if not connections:
            return
        
        def _send():
            for conn in connections:
                try:
                    if conn.ws_connection:
                        conn.write_message(message)
                except Exception as e:
                    print(f"Error sending message: {e}")
        
        if self.io_loop:
            self.io_loop.add_callback(_send)
        else:
            print("IOLoop not available. Message not sent.")

manager = WebSocketManager()