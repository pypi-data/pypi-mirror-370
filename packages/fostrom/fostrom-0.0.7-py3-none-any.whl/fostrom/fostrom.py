"""
Fostrom Device SDK for Python

A simple and clean SDK for connecting IoT devices to the Fostrom platform.

Example Usage:
    ```python
    from fostrom import Fostrom

    # Create SDK instance
    fostrom = Fostrom({
        "fleet_id": "<your-fleet-id>",
        "device_id": "<your-device-id>",
        "device_secret": "<your-device-secret>",
    })

    # Setup mail handler
    fostrom.on_mail = lambda mail: (
        print(f"Received: {mail.name}"),
        mail.ack()
    )

    # Connect and start sending data
    fostrom.connect()
    fostrom.send_datapoint("sensors", {"temperature": 23.5})
    fostrom.send_msg("status", {"online": True})
    ```
"""

import asyncio
import concurrent.futures
import contextlib
import http.client
import json
import os
import socket
import subprocess
import threading
from pathlib import Path
from typing import Any, Callable, Dict, Mapping, Optional, Union


def _get_agent_path() -> Path:
    """Get the path to the Fostrom Device Agent binary."""
    package_dir = Path(__file__).parent
    return package_dir / ".agent" / "fostrom-device-agent"


class FostromError(Exception):
    """Custom exception for Fostrom SDK errors."""

    def __init__(self, atom: str, message: str) -> None:
        self.atom = atom
        self.message = message
        # Format like JS version with colors
        formatted = (
            f"\x1b[31m\x1b[1mFostrom Error\x1b[0m \x1b[34m[{atom}]\x1b[0m {message}"
        )
        super().__init__(formatted)

    def __str__(self) -> str:
        return (
            f"\x1b[31m\x1b[1mFostrom Error\x1b[0m "
            f"\x1b[34m[{self.atom}]\x1b[0m {self.message}"
        )


class Mail:
    """An incoming mail from Fostrom."""

    def __init__(
        self,
        fostrom_instance: "Fostrom",
        mail_id: str,
        name: str,
        payload: Optional[Dict[str, Any]],
        mailbox_size: int,
    ) -> None:
        self._instance = fostrom_instance
        self.id = mail_id
        self.name = name
        self.payload = payload
        self.mailbox_size = mailbox_size

    def ack(self) -> None:
        """Acknowledge the mail"""
        return self._instance.mail_op("ack", self.id)

    def reject(self) -> None:
        """Reject the mail"""
        return self._instance.mail_op("reject", self.id)

    def requeue(self) -> None:
        """Requeue the mail"""
        return self._instance.mail_op("requeue", self.id)


class Fostrom:
    """Main Fostrom SDK class."""

    def __init__(self, config: Mapping[str, Union[str, bool]]) -> None:
        # Validate required config
        if not config.get("fleet_id"):
            raise ValueError("[Fostrom] Fleet ID required.")
        if not config.get("device_id"):
            raise ValueError("[Fostrom] Device ID required.")
        if not config.get("device_secret"):
            raise ValueError("[Fostrom] Device Secret required.")

        # Store credentials
        self._creds = {
            "fleet_id": config["fleet_id"],
            "device_id": config["device_id"],
            "device_secret": config["device_secret"],
        }

        # Configuration
        self._log = config.get("log", True)

        # Event loop management
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._background_task: Optional[concurrent.futures.Future[None]] = None

        # Event handlers
        self.on_mail: Callable[[Mail], None] = self._default_mail_handler
        self.on_connected: Callable[[], None] = self._default_connected_handler
        self.on_unauthorized: Callable[[str, int], None] = (
            self._default_unauthorized_handler
        )
        self.on_reconnecting: Callable[[str, int], None] = (
            self._default_reconnecting_handler
        )

    def _default_mail_handler(self, mail: Mail) -> None:
        """Default mail handler that auto-acknowledges."""
        if self._log:
            print(
                f"[Fostrom] Received Mail (Mailbox Size: {mail.mailbox_size}): "
                f"{mail.name} -> ID {mail.id}"
            )
            print(
                "              Auto-Acknowledging Mail. Define Mail Handler to "
                "handle incoming mail."
            )
            print("              `fostrom.on_mail = lambda mail: ...`\n")
        mail.ack()

    def _default_connected_handler(self) -> None:
        """Default connected handler."""
        if self._log:
            print("[Fostrom] Connected")

    def _default_unauthorized_handler(self, reason: str, after: int) -> None:
        """Default unauthorized handler."""
        if self._log:
            after_s = after // 1000
            print(
                f"[Fostrom] Unauthorized: {reason}. "
                f"Reconnecting in {after_s} seconds..."
            )

    def _default_reconnecting_handler(self, reason: str, after: int) -> None:
        """Default reconnecting handler."""
        if self._log:
            after_s = after // 1000
            print(
                f"[Fostrom] Failed to connect: {reason}. "
                f"Reconnecting in {after_s} seconds..."
            )

    def _start_agent(self) -> None:
        """Start the Fostrom Device Agent."""
        agent_path = _get_agent_path()

        args = [
            str(agent_path),
            "start",
            "--fleet-id",
            str(self._creds["fleet_id"]),
            "--device-id",
            str(self._creds["device_id"]),
            "--device-secret",
            str(self._creds["device_secret"]),
        ]

        if os.environ.get("FOSTROM_AGENT_MODE") == "dev":
            args.append("--dev")

        try:
            result = subprocess.run(args, capture_output=True, text=True, check=False)

            if result.returncode == 0 and result.stdout.strip() == "started":
                return

            # Handle error case
            if result.stderr:
                error_parts = result.stderr.strip().split(":", 1)
                if len(error_parts) == 2:
                    raise FostromError(error_parts[0], error_parts[1])
                raise FostromError("agent_error", result.stderr.strip())

        except FileNotFoundError:
            raise FostromError(
                "agent_not_found", "Fostrom Device Agent not found"
            ) from None
        except Exception as e:
            raise FostromError("agent_start_failed", str(e)) from None

    def _req(
        self,
        path: str = "/",
        method: str = "GET",
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to agent over UNIX socket."""
        if method not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError(f"Unsupported method: {method}")

        # Create socket connection
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            sock.connect("/tmp/fostrom/agent.sock")

            # Create HTTP connection over socket
            conn = http.client.HTTPConnection("localhost")
            conn.sock = sock

            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            body = None
            if method in ("POST", "PUT") and payload:
                body = json.dumps(payload)

            conn.request(method, path, body, headers)
            response = conn.getresponse()

            response_data = response.read().decode()

            try:
                response_json: Dict[str, Any] = json.loads(response_data)
            except json.JSONDecodeError:
                raise FostromError(
                    "req_failed", "Invalid response from agent"
                ) from None

            if "error" in response_json and "msg" in response_json:
                raise FostromError(response_json["error"], response_json["msg"])

            return response_json

        except OSError:
            raise FostromError(
                "req_failed", "Failed to communicate with device agent"
            ) from None
        finally:
            sock.close()

    def connect(self) -> bool:
        """Connect to Fostrom. Returns True on success."""
        self._start_agent()
        self._start_event_stream()
        return True

    def send_datapoint(self, name: str, payload: Dict[str, Any]) -> None:
        """Send a datapoint to Fostrom."""
        self._req(f"/pulse/datapoint/{name}", "POST", payload)

    def send_msg(self, name: str, payload: Dict[str, Any]) -> None:
        """Send a message to Fostrom."""
        self._req(f"/pulse/msg/{name}", "POST", payload)

    def mailbox_status(self) -> Dict[str, Any]:
        """Get mailbox status."""
        resp = self._req("/mailbox/status")

        if resp.get("mailbox_empty") is True:
            return {
                "mailbox_size": 0,
                "next_mail_id": None,
                "next_mail_name": None,
            }
        return {
            "mailbox_size": resp.get("mailbox_size", 0),
            "next_mail_id": resp.get("pulse_id"),
            "next_mail_name": resp.get("name"),
        }

    def next_mail(self) -> Optional[Mail]:
        """Get the next mail from mailbox."""
        resp = self._req("/mailbox/next")

        if resp.get("mailbox_empty") is True:
            return None

        return Mail(
            self,
            resp["pulse_id"],
            resp["name"],
            resp.get("payload"),
            resp.get("mailbox_size", 0),
        )

    def mail_op(self, operation: str, mail_id: str) -> None:
        """Perform mailbox operation (ack/reject/requeue)."""
        if operation not in ("ack", "reject", "requeue"):
            raise ValueError("Invalid mailbox operation")

        self._req(f"/mailbox/{operation}/{mail_id}", "PUT")

    def _start_event_stream(self) -> None:
        """Start the background event stream for real-time updates."""
        if self._background_task is not None:
            return  # Already running

        if self._loop is None:
            self._loop = asyncio.new_event_loop()
            thread = threading.Thread(target=self._loop.run_forever)
            thread.start()

        self._background_task = asyncio.run_coroutine_threadsafe(
            self._event_stream_loop(), self._loop
        )

    async def _event_stream_loop(self) -> None:
        """Main event stream loop that handles SSE events."""
        while True:
            try:
                await self._open_event_stream()
            except Exception:
                # If event stream fails, try to reconnect after delay
                await asyncio.sleep(5)
                # Try to reconnect by calling connect again
                try:
                    self.connect()
                    break
                except Exception:
                    continue

    async def _open_event_stream(self) -> None:
        """Open SSE event stream and process events."""
        # Create socket connection
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            sock.connect("/tmp/fostrom/agent.sock")
            sock.setblocking(False)

            # Create HTTP request manually for SSE
            request = (
                "GET /events HTTP/1.1\r\n"
                "Host: localhost\r\n"
                "Accept: text/event-stream\r\n"
                "Cache-Control: no-cache\r\n"
                "\r\n"
            )

            await asyncio.get_event_loop().sock_sendall(sock, request.encode())

            # Read response headers
            # Read response headers
            headers_data = b""
            while b"\r\n\r\n" not in headers_data:
                chunk = await asyncio.get_event_loop().sock_recv(sock, 1024)
                if not chunk:
                    raise ConnectionError("Connection closed during headers")
                headers_data += chunk

            # Split headers from SSE data
            header_end = headers_data.find(b"\r\n\r\n")
            leftover_data = headers_data[header_end + 4 :]

            # Process SSE data
            # Process SSE data
            buffer = ""

            # Process any leftover data from headers first
            if leftover_data:
                decoded = leftover_data.decode("utf-8", errors="ignore")
                buffer = self._parse_sse_events(buffer, decoded)

            while True:
                chunk = await asyncio.get_event_loop().sock_recv(sock, 1024)
                if not chunk:
                    break

                decoded = chunk.decode("utf-8", errors="ignore")
                buffer = self._parse_sse_events(buffer, decoded)

        except Exception:
            raise
        finally:
            sock.close()

    def _parse_sse_events(self, buffer: str, chunk: str) -> str:
        """Parse Server-Sent Events from the stream."""
        buffer += chunk
        lines = buffer.split("\n")

        # Keep the last incomplete line in buffer
        buffer = lines.pop() or ""

        event: Dict[str, Any] = {}

        for line in lines:
            line = line.rstrip("\r")

            # Empty line indicates end of event
            if line == "":
                if event.get("data"):
                    with contextlib.suppress(json.JSONDecodeError):
                        event["data"] = json.loads(event["data"])

                if event.get("event"):
                    self._handle_event(event)
                event = {}
            elif line.startswith("data: "):
                event["data"] = event.get("data", "") + line[6:]
            elif line.startswith("event: "):
                event["event"] = line[7:]
            elif line.startswith("id: "):
                with contextlib.suppress(ValueError):
                    event["timestamp"] = int(line[4:])
            elif line.startswith("retry: "):
                with contextlib.suppress(ValueError):
                    event["retry"] = int(line[7:])

        return buffer

    def _handle_event(self, event: Dict[str, Any]) -> None:
        """Handle incoming SSE events."""
        event_type = event.get("event")
        data = event.get("data", {})
        if event_type == "connected":
            self.on_connected()
        elif event_type == "unauthorized":
            reason = data.get("reason", "Unknown")
            reconnecting_in = data.get("reconnecting_in", 5000)
            self.on_unauthorized(reason, reconnecting_in)
        elif event_type == "connect_failed":
            reason = data.get("reason", "Unknown")
            reconnecting_in = data.get("reconnecting_in", 5000)
            self.on_reconnecting(reason, reconnecting_in)
        elif event_type == "next_mail":
            self._dispatch_next_mail(data)

    def _dispatch_next_mail(self, data: Dict[str, Any]) -> None:
        """Dispatch incoming mail to the mail handler."""
        mail = Mail(
            self,
            data.get("pulse_id", ""),
            data.get("name", ""),
            data.get("payload"),
            data.get("mailbox_size", 0),
        )
        self.on_mail(mail)

    @staticmethod
    def stop_agent() -> None:
        """Stop the Fostrom Device Agent."""
        agent_path = _get_agent_path()

        try:
            subprocess.run([str(agent_path), "stop"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            if __debug__:
                print("[Fostrom] Failed to stop the Fostrom Device Agent")
            pass  # Silently ignore stop failures
