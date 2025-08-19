
from __future__ import annotations
import asyncio, socket, ssl
from typing import AsyncIterator, Optional
from urllib.parse import urlparse
from .parser import parse_event
from .models import CoTEvent

class TLSConfig:
    def __init__(self, client_cert: Optional[str]=None, client_key: Optional[str]=None, ca: Optional[str]=None, check_hostname: bool=False):
        self.client_cert = client_cert
        self.client_key = client_key
        self.ca = ca
        self.check_hostname = check_hostname

    def context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        if self.ca:
            ctx.load_verify_locations(self.ca)
        ctx.check_hostname = self.check_hostname
        if self.client_cert:
            ctx.load_cert_chain(self.client_cert, self.client_key)
        return ctx

async def stream_events(url: str, tls: Optional[TLSConfig]=None) -> AsyncIterator[CoTEvent]:
    u = urlparse(url)
    scheme = u.scheme.lower()
    if scheme.startswith("udp"):
        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[bytes] = asyncio.Queue()
        class R(asyncio.DatagramProtocol):
            def datagram_received(self, data, addr): queue.put_nowait(data)
        transport, _ = await loop.create_datagram_endpoint(lambda: R(), local_addr=None, remote_addr=(u.hostname, u.port))
        try:
            while True:
                data = await queue.get()
                try:
                    yield parse_event(data)
                except Exception:
                    continue
        finally:
            transport.close()
    elif scheme in ("tcp","tls"):
        ssl_ctx = tls.context() if (scheme == "tls" and tls) else None
        reader, writer = await asyncio.open_connection(u.hostname, u.port, ssl=ssl_ctx)
        try:
            buf = b""
            while True:
                chunk = await reader.read(65536)
                if not chunk: break
                buf += chunk
                while True:
                    end = buf.find(b"</event>")
                    if end == -1: break
                    packet = buf[:end+8]
                    buf = buf[end+8:]
                    try:
                        yield parse_event(packet)
                    except Exception:
                        continue
        finally:
            writer.close(); await writer.wait_closed()
    elif scheme in ("ws","wss"):
        try:
            import websockets
        except Exception as e:
            raise ImportError("Install extra ws: pip install 'PyCoT[ws]'") from e
        ssl_ctx = tls.context() if (scheme == "wss" and tls) else None
        async with websockets.connect(url, ssl=ssl_ctx, max_size=None) as ws:
            async for message in ws:
                data = message if isinstance(message, (bytes, bytearray)) else message.encode("utf-8")
                try:
                    yield parse_event(data)
                except Exception:
                    continue
    else:
        raise ValueError(f"Unsupported scheme: {scheme}")
