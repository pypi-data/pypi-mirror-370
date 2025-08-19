import asyncio
import json
import os
import threading
from pathlib import Path
from typing import List, Set

from aiohttp import web
class State:
    def __init__(self) -> None:
        self.ui_sessions: Set[web.WebSocketResponse] = set()
        self.backend_sessions: Set[web.WebSocketResponse] = set()
        self.namespaces: List[int] = []
        self.lock = threading.Lock()
        self.scenario = ""
        self.latched_messages_ui: dict[str, dict] = {}
        self.latched_messages_backend: dict[str, dict] = {}

async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse(max_msg_size=1024*1024*100)
    await ws.prepare(request)

    path = request.path
    state: State = request.app["state"]
    is_ui = path == "/ui"

    try:
        with state.lock:
            if is_ui:
                state.ui_sessions.add(ws)
                for msg in state.latched_messages_backend.values():
                    await ws.send_json(msg)
            else:
                state.backend_sessions.add(ws)
                namespace = len(state.namespaces)
                state.namespaces.append(namespace)
                await ws.send_json(
                    {"channel": "handshake", "data": {"namespace": str(namespace)}}
                )
                for msg in state.latched_messages_ui.values():
                    await ws.send_json(msg)

        async for msg in ws:
            if msg.type is web.WSMsgType.TEXT:
                try:
                    parsed = json.loads(msg.data)
                except json.JSONDecodeError:
                    print("bad json:", msg.data)
                    continue

                if parsed.get("latch"):
                    store = (
                        state.latched_messages_ui
                        if is_ui
                        else state.latched_messages_backend
                    )
                    store[parsed["channel"]] = parsed

                # fan-out
                targets = (
                    state.backend_sessions if is_ui else state.ui_sessions
                )
                for peer in list(targets):
                    try:
                        await peer.send_str(msg.data)
                    except Exception:
                        targets.discard(peer)
            elif msg.type is web.WSMsgType.ERROR:
                print("websocket error:", ws.exception())

    finally:
        with state.lock:
            (state.ui_sessions if is_ui else state.backend_sessions).discard(ws)

    return ws


async def handle_static(request: web.Request) -> web.StreamResponse:
    static_root: Path = request.app["static_path"]
    rel = request.match_info["tail"] or "index.html"
    file_path = static_root / rel
    if not file_path.exists():
        return web.Response(status=404, text="File not found")

    return web.FileResponse(file_path)

async def handle_debug(request: web.Request) -> web.Response:
    debug_root = os.path.join(os.path.dirname(Path(__file__)), "..", "debug")
    rel = request.match_info["tail"] or "index.html"
    file_path = os.path.join(debug_root, rel)
    if not Path(file_path).exists():
        return web.Response(status=404, text="File not found")
    body = Path(file_path).read_bytes()
    if rel.endswith(".js"):
        mime_type = "application/javascript"
    else:
        mime_type = "text/html"
    return web.Response(body=body, content_type=mime_type)

async def handle_scenario(request: web.Request) -> web.Response:
    state: State = request.app["state"]
    return web.Response(text=state.scenario, content_type="text/plain")

class Server:
    def __init__(
        self,
        *,
        static_path: str | os.PathLike | None = None,
        port: int = 8080,
        scenario: str = "",
    ) -> None:
        self.port = port
        self.state = State()
        self.state.scenario = scenario

        here = Path(__file__).with_suffix("")
        default_static = here.parent / "rl-tools" / "static" / "ui_server" / "generic"
        self.static_path = Path(static_path) if static_path else default_static

        self.app = web.Application()
        self.app["state"] = self.state
        self.app["static_path"] = self.static_path
        self.app.add_routes(
            [
                web.get("/ui", websocket_handler),
                web.get("/backend", websocket_handler),
                web.get("/scenario", handle_scenario),
                web.get("/{tail:.*}", handle_static),
                web.get("/debug/{tail:.*}", handle_debug),
            ]
        )

        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None

    async def start(self) -> None:
        if self._runner:
            return

        self._runner = web.AppRunner(self.app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "0.0.0.0", self.port)
        await self._site.start()
        print(f"[ui_server] http://localhost:{self.port}")

    async def _serve_forever(self) -> None:
        await self.start()
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        if self._runner:
            await self._runner.cleanup()
            self._runner = self._site = None
            print("[ui_server] stopped")
    def run(self) -> None:
        try:
            asyncio.run(self._serve_forever())
        except KeyboardInterrupt:
            pass

    def run_in_background(self) -> threading.Thread:
        def _thread_target() -> None:
            asyncio.run(self._serve_forever())

        t = threading.Thread(target=_thread_target, daemon=True, name="ui_server")
        t.start()
        return t


def main():
    Server(port=13337, scenario="generic").run()

if __name__ == "__main__":
    main()