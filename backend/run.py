import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.api import app


async def _serve_http(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        request_line = await reader.readline()
        if not request_line:
            writer.close()
            await writer.wait_closed()
            return

        method, raw_path, _http_version = request_line.decode("latin-1").strip().split(" ", 2)
        path, _, query_string = raw_path.partition("?")

        headers: list[tuple[str, str]] = []
        content_length = 0

        while True:
            line = await reader.readline()
            if line in {b"\r\n", b"\n", b""}:
                break
            header_line = line.decode("latin-1").rstrip("\r\n")
            name, value = header_line.split(":", 1)
            value = value.lstrip()
            headers.append((name.lower(), value))
            if name.lower() == "content-length":
                content_length = int(value)

        body = await reader.readexactly(content_length) if content_length else b""

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": path,
            "raw_path": raw_path.encode("latin-1"),
            "query_string": query_string.encode("latin-1"),
            "headers": [(name.encode("latin-1"), value.encode("latin-1")) for name, value in headers],
            "client": ("127.0.0.1", 0),
            "server": ("127.0.0.1", int(os.getenv("APP_PORT", "8000"))),
        }

        response_status = 500
        response_headers: list[tuple[str, str]] = []
        response_body = bytearray()

        received = False

        async def receive():
            nonlocal received
            if received:
                return {"type": "http.disconnect"}
            received = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            nonlocal response_status, response_headers, response_body
            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = [
                    (name.decode("latin-1"), value.decode("latin-1"))
                    for name, value in message.get("headers", [])
                ]
            elif message["type"] == "http.response.body":
                response_body.extend(message.get("body", b""))

        await app(scope, receive, send)

        reason = {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            404: "Not Found",
            500: "Internal Server Error",
        }.get(response_status, "OK")

        if not any(name.lower() == "content-length" for name, _ in response_headers):
            response_headers.append(("content-length", str(len(response_body))))

        if not any(name.lower() == "content-type" for name, _ in response_headers):
            response_headers.append(("content-type", "application/json"))

        header_lines = "".join(f"{name}: {value}\r\n" for name, value in response_headers)
        writer.write(
            f"HTTP/1.1 {response_status} {reason}\r\n{header_lines}\r\n".encode("latin-1")
            + bytes(response_body)
        )
        await writer.drain()
    except Exception as exc:
        error_body = str(exc).encode("utf-8", errors="replace")
        writer.write(
            b"HTTP/1.1 500 Internal Server Error\r\n"
            b"content-type: text/plain; charset=utf-8\r\n"
            + f"content-length: {len(error_body)}\r\n\r\n".encode("latin-1")
            + error_body
        )
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def _main() -> None:
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8001"))

    server = await asyncio.start_server(_serve_http, host, port)
    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    print(f"Serving backend on {addresses}")

    async with server:
        await server.serve_forever()


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
