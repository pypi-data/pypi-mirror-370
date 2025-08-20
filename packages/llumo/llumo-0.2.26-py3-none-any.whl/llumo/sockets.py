import socketio
import threading
import time


class LlumoSocketClient:
    def __init__(self, socket_url):
        self.socket_url = socket_url
        self._received_data = []
        self._last_update_time = None
        self._listening_done = threading.Event()
        self._connection_established = threading.Event()
        self._lock = threading.Lock()
        self._connected = False
        self.server_socket_id = None  # Store the server-assigned socket ID
        self._expected_results = None  # NEW

        # Initialize client
        self.sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            reconnection=True,
            reconnection_attempts=1,
            reconnection_delay=1,
        )

        @self.sio.on("connect")
        def on_connect():
            self.sio.emit("ready")
            # print("Socket connection established")
            self._connected = True
            # Don't set connection_established yet - wait for server confirmation

        # Listen for the connection-established event from the server
        @self.sio.on("connection-established")
        def on_connection_established(data):
            # print(
            #     f"Server acknowledged connection with 'connection-established' event: {data}"
            # )
            if isinstance(data, dict) and "socketId" in data:
                self.sio.emit("ready")
                self.server_socket_id = data["socketId"]
                # print(f"Received server socket ID: {self.server_socket_id}")
            self._connection_established.set()

        @self.sio.on("result-update")
        def on_result_update(data, callback=None):
            with self._lock:
                # print(f"Received result-update event: {data}")
                self._received_data.append(data)
                self._last_update_time = time.time()

                # ✅ Stop if all expected results are received
                if (
                    self._expected_results
                    and len(self._received_data) >= self._expected_results
                ):
                    # print("✅ All expected results received.")
                    self._listening_done.set()
            if callback:
                callback(True)

        @self.sio.on("disconnect")
        def on_disconnect():
            # print("Socket disconnected")
            self._connected = False

        @self.sio.on("connect_error")
        def on_connect_error(error):
            # print(f"Socket connection error: {error}")
            pass

        @self.sio.on("error")
        def on_error(error):
            print(f"Socket error event: {error}")

    def connect(self, timeout=20):
        self._received_data = []
        self._connection_established.clear()
        self._listening_done.clear()
        self.server_socket_id = None
        self._connected = False

        try:
            # print("[DEBUG] Connecting to socket...")
            self.sio.connect(self.socket_url, transports=["websocket"], wait=True)

            # Wait for socket connection
            start = time.time()
            while not self.sio.connected:
                if time.time() - start > timeout:
                    raise RuntimeError(
                        "Timed out waiting for low-level socket connection."
                    )
                time.sleep(0.1)
            # print("[DEBUG] SocketIO low-level connection established.")

            # Wait for server "connection-established" event
            if not self._connection_established.wait(timeout):
                raise RuntimeError(
                    "Timed out waiting for connection-established event."
                )

            self._connected = True
            self._last_update_time = time.time()
            # print(f"[DEBUG] Full connection established. Connected: {self._connected}")

            return self.server_socket_id or self.sio.sid

        except Exception as e:
            # print(f"[DEBUG] Connection failed with error: {e}")
            self._connected = False
            # raise RuntimeError(f"WebSocket connection failed: {e}")
            print("It seems your internet connection is a bit unstable. This might take a little longer than usual—thanks for your patience!")

    def listenForResults(
        self, min_wait=30, max_wait=300, inactivity_timeout=50, expected_results=None
    ):
        # if not self._connected:
        #     raise RuntimeError("WebSocket is not connected. Call connect() first.")

        # total records
        self._expected_results = expected_results  # NEW
        start_time = time.time()
        self._last_update_time = time.time()

        def timeout_watcher():
            while not self._listening_done.is_set():
                current_time = time.time()
                time_since_last_update = current_time - self._last_update_time
                total_elapsed = current_time - start_time

                if total_elapsed < min_wait:
                    time.sleep(0.5)
                    continue

                if total_elapsed > max_wait:
                    # print(f"⚠️ Max wait time {max_wait}s exceeded.")
                    self._listening_done.set()
                    break

                if time_since_last_update > inactivity_timeout:
                    # print(f"⚠️ Inactivity timeout {inactivity_timeout}s exceeded.")
                    self._listening_done.set()
                    break

        timeout_thread = threading.Thread(target=timeout_watcher, daemon=True)
        timeout_thread.start()
        self._listening_done.wait()

    def getReceivedData(self):
        with self._lock:
            # print("Total received:", len(self._received_data))  # DEBUG
            return self._received_data.copy()

    def disconnect(self):
        try:
            if self._connected:
                self.sio.disconnect()
                self._connected = False
                # print("WebSocket client disconnected")
        except Exception as e:
            print(f"Error during WebSocket disconnect: {e}")
