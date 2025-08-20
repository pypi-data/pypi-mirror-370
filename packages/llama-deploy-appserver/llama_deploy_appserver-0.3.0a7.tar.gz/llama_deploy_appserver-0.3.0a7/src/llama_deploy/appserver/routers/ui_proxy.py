import asyncio
import logging
from typing import List

import httpx
import websockets
from fastapi import (
    APIRouter,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
)
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from llama_deploy.appserver.settings import ApiserverSettings
from llama_deploy.core.deployment_config import DeploymentConfig
from starlette.background import BackgroundTask

logger = logging.getLogger(__name__)


async def _ws_proxy(ws: WebSocket, upstream_url: str) -> None:
    """Proxy WebSocket connection to upstream server."""
    await ws.accept()

    # Forward most headers except WebSocket-specific ones
    header_blacklist = {
        "host",
        "connection",
        "upgrade",
        "sec-websocket-key",
        "sec-websocket-version",
        "sec-websocket-extensions",
    }
    hdrs = [(k, v) for k, v in ws.headers.items() if k.lower() not in header_blacklist]

    try:
        # Parse subprotocols if present
        subprotocols: List[websockets.Subprotocol] | None = None
        if "sec-websocket-protocol" in ws.headers:
            # Parse comma-separated subprotocols
            subprotocols = [
                websockets.Subprotocol(p.strip())
                for p in ws.headers["sec-websocket-protocol"].split(",")
            ]

        # Open upstream WebSocket connection
        async with websockets.connect(
            upstream_url,
            additional_headers=hdrs,
            subprotocols=subprotocols,
            open_timeout=None,
            ping_interval=None,
        ) as upstream:

            async def client_to_upstream() -> None:
                try:
                    while True:
                        msg = await ws.receive()
                        if msg["type"] == "websocket.receive":
                            if "text" in msg:
                                await upstream.send(msg["text"])
                            elif "bytes" in msg:
                                await upstream.send(msg["bytes"])
                        elif msg["type"] == "websocket.disconnect":
                            break
                except Exception as e:
                    logger.debug(f"Client to upstream connection ended: {e}")

            async def upstream_to_client() -> None:
                try:
                    async for message in upstream:
                        if isinstance(message, str):
                            await ws.send_text(message)
                        else:
                            await ws.send_bytes(message)
                except Exception as e:
                    logger.debug(f"Upstream to client connection ended: {e}")

            # Pump both directions concurrently
            await asyncio.gather(
                client_to_upstream(), upstream_to_client(), return_exceptions=True
            )

    except Exception as e:
        logger.error(f"WebSocket proxy error: {e}")
    finally:
        try:
            await ws.close()
        except Exception as e:
            logger.debug(f"Error closing client connection: {e}")


def create_ui_proxy_router(name: str, port: int) -> APIRouter:
    deployment_router = APIRouter(
        prefix=f"/deployments/{name}",
        tags=["deployments"],
    )

    @deployment_router.websocket("/ui/{path:path}")
    @deployment_router.websocket("/ui")
    async def websocket_proxy(
        websocket: WebSocket,
        path: str | None = None,
    ) -> None:
        # Build the upstream WebSocket URL using FastAPI's extracted path parameter
        slash_path = f"/{path}" if path else ""
        upstream_path = f"/deployments/{name}/ui{slash_path}"

        # Convert to WebSocket URL
        upstream_url = f"ws://localhost:{port}{upstream_path}"
        if websocket.url.query:
            upstream_url += f"?{websocket.url.query}"

        logger.debug(f"Proxying WebSocket {websocket.url} -> {upstream_url}")

        await _ws_proxy(websocket, upstream_url)

    @deployment_router.api_route(
        "/ui/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        include_in_schema=False,
    )
    @deployment_router.api_route(
        "/ui",
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        include_in_schema=False,
    )
    async def proxy(
        request: Request,
        path: str | None = None,
    ) -> StreamingResponse:
        # Build the upstream URL using FastAPI's extracted path parameter
        slash_path = f"/{path}" if path else ""
        upstream_path = f"/deployments/{name}/ui{slash_path}"

        upstream_url = httpx.URL(f"http://localhost:{port}{upstream_path}").copy_with(
            params=request.query_params
        )

        # Debug logging
        logger.debug(f"Proxying {request.method} {request.url} -> {upstream_url}")

        # Strip hop-by-hop headers + host
        hop_by_hop = {
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",  # codespell:ignore
            "trailers",
            "transfer-encoding",
            "upgrade",
            "host",
        }
        headers = {
            k: v for k, v in request.headers.items() if k.lower() not in hop_by_hop
        }

        try:
            client = httpx.AsyncClient(timeout=None)

            req = client.build_request(
                request.method,
                upstream_url,
                headers=headers,
                content=request.stream(),  # stream uploads
            )
            upstream = await client.send(req, stream=True)

            resp_headers = {
                k: v for k, v in upstream.headers.items() if k.lower() not in hop_by_hop
            }

            # Close client when upstream response is done
            async def cleanup() -> None:
                await upstream.aclose()
                await client.aclose()

            return StreamingResponse(
                upstream.aiter_raw(),  # stream downloads
                status_code=upstream.status_code,
                headers=resp_headers,
                background=BackgroundTask(cleanup),  # tidy up when finished
            )

        except httpx.ConnectError:
            raise HTTPException(status_code=502, detail="Upstream server unavailable")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Upstream server timeout")
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            raise HTTPException(status_code=502, detail="Proxy error")

    return deployment_router


def mount_static_files(
    app: FastAPI, config: DeploymentConfig, settings: ApiserverSettings
) -> None:
    path = settings.app_root / config.build_output_path()
    if not path:
        return

    if not path.exists():
        return

    # Serve index.html when accessing the directory path
    app.mount(
        f"/deployments/{config.name}/ui",
        StaticFiles(directory=str(path), html=True),
        name=f"ui-static-{config.name}",
    )
    return None
