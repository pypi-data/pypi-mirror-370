# kei_agent/config_api.py
"""
Configuration API endpoints for runtime configuration management.

This module provides:
- REST API endpoints for configuration CRUD operations
- Authentication and authorization for configuration changes
- Configuration validation and error handling
- Audit logging for all configuration operations
- WebSocket endpoints for real-time configuration updates
"""

import json
import time
from typing import Dict, Any, Optional
import logging

try:
    from aiohttp import web, WSMsgType
    from aiohttp.web import Request, Response, WebSocketResponse

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from .config_manager import get_config_manager, ConfigManager

logger = logging.getLogger(__name__)


class ConfigAPI:
    """REST API for configuration management."""

    def __init__(
        self, config_manager: Optional[ConfigManager] = None, require_auth: bool = True
    ):
        """Initialize configuration API.

        Args:
            config_manager: Configuration manager instance
            require_auth: Whether to require authentication for config changes
        """
        self.config_manager = config_manager or get_config_manager()
        self.require_auth = require_auth
        self.websocket_connections = set()

        # Add callback to notify WebSocket clients of changes
        self.config_manager.add_change_callback(self._notify_websocket_clients)

    def create_routes(self, app: web.Application) -> None:
        """Add configuration API routes to the application.

        Args:
            app: aiohttp application
        """
        if not AIOHTTP_AVAILABLE:
            logger.error("aiohttp not available for configuration API")
            return

        # Configuration CRUD endpoints
        app.router.add_get("/api/config", self.get_config_handler)
        app.router.add_get("/api/config/{key:.*}", self.get_config_value_handler)
        app.router.add_put("/api/config", self.update_config_handler)
        app.router.add_put("/api/config/{key:.*}", self.update_config_value_handler)
        app.router.add_post("/api/config/reload", self.reload_config_handler)
        app.router.add_post("/api/config/rollback", self.rollback_config_handler)

        # Configuration management endpoints
        app.router.add_get("/api/config/history", self.get_config_history_handler)
        app.router.add_get("/api/config/validation", self.validate_config_handler)
        app.router.add_post("/api/config/validate", self.validate_config_post_handler)

        # WebSocket endpoint for real-time updates
        app.router.add_get("/ws/config", self.websocket_config_handler)

        logger.info("Configuration API routes added")

    async def get_config_handler(self, request: Request) -> Response:
        """Handle GET /api/config - get full configuration."""
        try:
            config = self.config_manager.get_config()

            return web.json_response(
                {"success": True, "config": config, "timestamp": time.time()}
            )

        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def get_config_value_handler(self, request: Request) -> Response:
        """Handle GET /api/config/{key} - get specific configuration value."""
        try:
            key = request.match_info["key"]
            default = request.query.get("default")

            value = self.config_manager.get_config_value(key, default)

            return web.json_response(
                {"success": True, "key": key, "value": value, "timestamp": time.time()}
            )

        except Exception as e:
            logger.error(f"Error getting configuration value: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def update_config_handler(self, request: Request) -> Response:
        """Handle PUT /api/config - update full configuration."""
        try:
            # Check authentication if required
            user_id = await self._get_user_id(request)
            if self.require_auth and not user_id:
                return web.json_response(
                    {"success": False, "error": "Authentication required"}, status=401
                )

            # Parse request body
            data = await request.json()
            new_config = data.get("config", {})
            reason = data.get("reason", "API update")

            # Apply configuration change
            success = await self.config_manager._apply_config_change(
                new_config, source="api", user_id=user_id, reason=reason
            )

            if success:
                return web.json_response(
                    {
                        "success": True,
                        "message": "Configuration updated successfully",
                        "timestamp": time.time(),
                    }
                )
            else:
                return web.json_response(
                    {"success": False, "error": "Configuration validation failed"},
                    status=400,
                )

        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def update_config_value_handler(self, request: Request) -> Response:
        """Handle PUT /api/config/{key} - update specific configuration value."""
        try:
            # Check authentication if required
            user_id = await self._get_user_id(request)
            if self.require_auth and not user_id:
                return web.json_response(
                    {"success": False, "error": "Authentication required"}, status=401
                )

            key = request.match_info["key"]
            data = await request.json()
            value = data.get("value")
            reason = data.get("reason", f"API update of {key}")

            # Create update dictionary
            keys = key.split(".")
            updates = {}
            current = updates

            for k in keys[:-1]:
                current[k] = {}
                current = current[k]

            current[keys[-1]] = value

            # Apply update
            success = await self.config_manager.update_config(
                updates, user_id=user_id, reason=reason
            )

            if success:
                return web.json_response(
                    {
                        "success": True,
                        "message": f"Configuration value '{key}' updated successfully",
                        "timestamp": time.time(),
                    }
                )
            else:
                return web.json_response(
                    {"success": False, "error": "Configuration validation failed"},
                    status=400,
                )

        except Exception as e:
            logger.error(f"Error updating configuration value: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def reload_config_handler(self, request: Request) -> Response:
        """Handle POST /api/config/reload - reload configuration from files."""
        try:
            # Check authentication if required
            user_id = await self._get_user_id(request)
            if self.require_auth and not user_id:
                return web.json_response(
                    {"success": False, "error": "Authentication required"}, status=401
                )

            # Reload all watched files
            success = True
            reloaded_files = []

            for file_path in self.config_manager.watched_files:
                if await self.config_manager._load_config_file(file_path):
                    reloaded_files.append(str(file_path))
                else:
                    success = False

            return web.json_response(
                {
                    "success": success,
                    "message": "Configuration reload completed",
                    "reloaded_files": reloaded_files,
                    "timestamp": time.time(),
                }
            )

        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def rollback_config_handler(self, request: Request) -> Response:
        """Handle POST /api/config/rollback - rollback configuration."""
        try:
            # Check authentication if required
            user_id = await self._get_user_id(request)
            if self.require_auth and not user_id:
                return web.json_response(
                    {"success": False, "error": "Authentication required"}, status=401
                )

            # Parse request body
            data = (
                await request.json()
                if request.content_type == "application/json"
                else {}
            )
            change_id = data.get("change_id")

            # Perform rollback
            success = await self.config_manager.rollback_config(change_id)

            if success:
                return web.json_response(
                    {
                        "success": True,
                        "message": "Configuration rollback completed",
                        "timestamp": time.time(),
                    }
                )
            else:
                return web.json_response(
                    {"success": False, "error": "Rollback failed"}, status=400
                )

        except Exception as e:
            logger.error(f"Error rolling back configuration: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def get_config_history_handler(self, request: Request) -> Response:
        """Handle GET /api/config/history - get configuration change history."""
        try:
            limit = int(request.query.get("limit", 50))
            history = self.config_manager.get_change_history(limit)

            return web.json_response(
                {
                    "success": True,
                    "history": history,
                    "count": len(history),
                    "timestamp": time.time(),
                }
            )

        except Exception as e:
            logger.error(f"Error getting configuration history: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def validate_config_handler(self, request: Request) -> Response:
        """Handle GET /api/config/validation - get validation rules."""
        try:
            validation_info = {
                "required_fields": self.config_manager.validator.required_fields,
                "field_types": {
                    k: v.__name__
                    for k, v in self.config_manager.validator.field_types.items()
                },
                "validation_rules_count": len(
                    self.config_manager.validator.validation_rules
                ),
            }

            return web.json_response(
                {
                    "success": True,
                    "validation": validation_info,
                    "timestamp": time.time(),
                }
            )

        except Exception as e:
            logger.error(f"Error getting validation info: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def validate_config_post_handler(self, request: Request) -> Response:
        """Handle POST /api/config/validate - validate configuration."""
        try:
            data = await request.json()
            config = data.get("config", {})

            is_valid = self.config_manager.validator.validate(config)

            return web.json_response(
                {"success": True, "valid": is_valid, "timestamp": time.time()}
            )

        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def websocket_config_handler(self, request: Request) -> WebSocketResponse:
        """Handle WebSocket connection for real-time configuration updates."""
        ws = WebSocketResponse()
        await ws.prepare(request)

        self.websocket_connections.add(ws)
        logger.info(
            f"Configuration WebSocket connection established. Total: {len(self.websocket_connections)}"
        )

        try:
            # Send current configuration
            current_config = self.config_manager.get_config()
            await ws.send_str(
                json.dumps(
                    {
                        "type": "current_config",
                        "config": current_config,
                        "timestamp": time.time(),
                    }
                )
            )

            # Keep connection alive
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get("type") == "ping":
                            await ws.send_str(
                                json.dumps({"type": "pong", "timestamp": time.time()})
                            )
                    except json.JSONDecodeError:
                        pass
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"Configuration WebSocket error: {ws.exception()}")
                    break

        except Exception as e:
            logger.error(f"Configuration WebSocket error: {e}")

        finally:
            self.websocket_connections.discard(ws)
            logger.info(
                f"Configuration WebSocket connection closed. Remaining: {len(self.websocket_connections)}"
            )

        return ws

    async def _notify_websocket_clients(self, new_config: Dict[str, Any]) -> None:
        """Notify WebSocket clients of configuration changes.

        Args:
            new_config: New configuration that was applied
        """
        if not self.websocket_connections:
            return

        message = json.dumps(
            {"type": "config_change", "config": new_config, "timestamp": time.time()}
        )

        # Send to all connected clients
        disconnected = set()
        for ws in self.websocket_connections:
            try:
                await ws.send_str(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.add(ws)

        # Remove disconnected clients
        self.websocket_connections -= disconnected

    async def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request for authentication.

        Args:
            request: HTTP request

        Returns:
            User ID if authenticated, None otherwise
        """
        # Simple authentication - in production, use proper auth
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # In production, validate token and extract user ID
            return f"user_{hash(token) % 1000}"  # Simplified for demo

        return None


# Global configuration API instance
_config_api: Optional[ConfigAPI] = None


def get_config_api() -> ConfigAPI:
    """Get the global configuration API instance."""
    global _config_api
    if _config_api is None:
        _config_api = ConfigAPI()
    return _config_api


def initialize_config_api(
    config_manager: Optional[ConfigManager] = None, require_auth: bool = True
) -> ConfigAPI:
    """Initialize the global configuration API.

    Args:
        config_manager: Configuration manager instance
        require_auth: Whether to require authentication

    Returns:
        Initialized configuration API
    """
    global _config_api
    _config_api = ConfigAPI(config_manager, require_auth)
    return _config_api
