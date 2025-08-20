# sdk/python/kei_agent_sdk/capabilities.py
"""
capability advertisement and matagement for KEI-Agent-Framework SDK.

Implementiert automatische Capability-Discovery, MCP-Integration,
Capability-Negotiation and dynamische Updates tor Lonzeit.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Awaitable
from packaging import version

from .client import KeiAgentClient
from .exceptions import CapabilityError


class Capabilitystatus(str, Enum):
    """status ar Capability."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    MAINTENANCE = "maintenatce"


class CompatibilityLevel(str, Enum):
    """compatibilityslevel between Capability-Versionen."""

    COMPATIBLE = "compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass
class CapabilityProfile:
    """Profil ar Agent-Capability."""

    name: str
    version: str
    description: str = ""
    status: Capabilitystatus = Capabilitystatus.AVAILABLE

    # MCP-Integration
    mcp_profile_url: Optional[str] = None
    mcp_schema: Optional[Dict[str, Any]] = None

    # Interface-Definition
    methods: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    events: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # metadata
    tags: List[str] = field(default_factory=list)
    category: str = ""
    author: str = ""
    license: str = ""

    # compatibility
    framework_version_constraint: str = "*"
    depenthecies: Dict[str, str] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)

    # Performatce-Charakterisika
    expected_response_time_ms: Optional[float] = None
    max_concurrent_requests: Optional[int] = None
    resource_requirements: Dict[str, Any] = field(default_factory=dict)

    # configuration
    configuration_schema: Optional[Dict[str, Any]] = None
    default_configuration: Dict[str, Any] = field(default_factory=dict)

    # Zeitstempel
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert Capability-Profil to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": self.status.value,
            "mcp_profile_url": self.mcp_profile_url,
            "mcp_schema": self.mcp_schema,
            "methods": self.methods,
            "events": self.events,
            "tags": self.tags,
            "category": self.category,
            "author": self.author,
            "license": self.license,
            "framework_version_constraint": self.framework_version_constraint,
            "depenthecies": self.depenthecies,
            "conflicts": self.conflicts,
            "expected_response_time_ms": self.expected_response_time_ms,
            "max_concurrent_requests": self.max_concurrent_requests,
            "resource_requirements": self.resource_requirements,
            "configuration_schema": self.configuration_schema,
            "default_configuration": self.default_configuration,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CapabilityProfile:
        """Creates Capability-Profil out dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            status=Capabilitystatus(data.get("status", "available")),
            mcp_profile_url=data.get("mcp_profile_url"),
            mcp_schema=data.get("mcp_schema"),
            methods=data.get("methods", {}),
            events=data.get("events", {}),
            tags=data.get("tags", []),
            category=data.get("category", ""),
            author=data.get("author", ""),
            license=data.get("license", ""),
            framework_version_constraint=data.get("framework_version_constraint", "*"),
            depenthecies=data.get("depenthecies", {}),
            conflicts=data.get("conflicts", []),
            expected_response_time_ms=data.get("expected_response_time_ms"),
            max_concurrent_requests=data.get("max_concurrent_requests"),
            resource_requirements=data.get("resource_requirements", {}),
            configuration_schema=data.get("configuration_schema"),
            default_configuration=data.get("default_configuration", {}),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


@dataclass
class CapabilityNegotiationRequest:
    """Request for Capability-Negotiation."""

    capability_name: str
    client_version: str
    required_features: List[str] = field(default_factory=list)
    optional_features: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)

    # Negotiation-metadata
    negotiation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_agent_id: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class CapabilityNegotiationresponse:
    """response for Capability-Negotiation."""

    negotiation_id: str
    status: str = "success"  # success, partial, failed

    # Negotiation-result
    agreed_version: Optional[str] = None
    supported_features: List[str] = field(default_factory=list)
    unsupported_features: List[str] = field(default_factory=list)

    # configuration
    final_configuration: Dict[str, Any] = field(default_factory=dict)
    configuration_overrides: Dict[str, Any] = field(default_factory=dict)

    # metadata
    compatibility_level: CompatibilityLevel = CompatibilityLevel.UNKNOWN
    fallback_options: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class MCPIntegration:
    """Integration with Model Context Protocol."""

    def __init__(self, base_client: KeiAgentClient):
        """Initializes MCP-Integration.

        Args:
            base_client: Basis-KEI-client
        """
        self.base_client = base_client
        self._mcp_profiles_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 Minuten
        self._last_cache_update = 0.0

    async def load_mcp_profile(self, capability_name: str) -> Optional[Dict[str, Any]]:
        """Loads MCP-Profil for Capability.

        Args:
            capability_name: Name the Capability

        Returns:
            MCP-Profil or None
        """
        # Prüfe Cache
        if (
            time.time() - self._last_cache_update < self._cache_ttl
            and capability_name in self._mcp_profiles_cache
        ):
            return self._mcp_profiles_cache[capability_name]

        try:
            # Lade MCP-Profil from API
            response = await self.base_client._make_request(
                "GET",
                f"/api/v1/specs/mcp?capability={capability_name}",
                trace_name=f"mcp.load_profile.{capability_name}",
            )

            if capability_name in response:
                mcp_profile = response[capability_name]
                self._mcp_profiles_cache[capability_name] = mcp_profile
                self._last_cache_update = time.time()
                return mcp_profile

            return None

        except Exception as e:
            raise CapabilityError(
                f"MCP-Profil for '{capability_name}' konnte not gelathe werthe: {e}"
            ) from e

    async def validate_capability_interface(
        self, capability_profile: CapabilityProfile, mcp_profile: Dict[str, Any]
    ) -> bool:
        """Validates Capability-Interface against MCP-Profil.

        Args:
            capability_profile: Capability-Profil
            mcp_profile: MCP-Profil

        Returns:
            True if Interface kompatibel
        """
        try:
            # Prüfe MCP-Version
            mcp_version = mcp_profile.get("mcp_version", "1.0.0")
            if not self._is_mcp_version_supported(mcp_version):
                return False

            # Prüfe Interface-methodn
            mcp_interface = mcp_profile.get("interface", {})
            mcp_methods = mcp_interface.get("methods", {})

            for method_name, method_spec in capability_profile.methods.items():
                if method_name not in mcp_methods:
                    continue  # method not in MCP definiert

                mcp_method = mcp_methods[method_name]

                # Valithere Input-Schema
                if not self._validate_schema_compatibility(
                    method_spec.get("input_schema"), mcp_method.get("input_schema")
                ):
                    return False

                # Valithere Output-Schema
                if not self._validate_schema_compatibility(
                    method_spec.get("output_schema"), mcp_method.get("output_schema")
                ):
                    return False

            return True

        except Exception:
            return False

    def _is_mcp_version_supported(self, mcp_version: str) -> bool:
        """Checks ob MCP-Version supports is.

        Args:
            mcp_version: MCP-Version

        Returns:
            True if supports
        """
        try:
            supported_versions = ["1.0.0", "1.1.0"]
            return any(
                version.parse(mcp_version) >= version.parse(v)
                for v in supported_versions
            )
        except Exception:
            return False

    def _validate_schema_compatibility(
        self,
        actual_schema: Optional[Dict[str, Any]],
        expected_schema: Optional[Dict[str, Any]],
    ) -> bool:
        """Validates Schema-compatibility.

        Args:
            actual_schema: Tatsächliches Schema
            expected_schema: Erwartetes Schema

        Returns:
            True if kompatibel
        """
        if not expected_schema:
            return True  # Ka Schema erforthelich

        if not actual_schema:
            return False  # Schema erforthelich aber not beforehatthe

        # Verafachte Schema-Valitherung
        # In ar vollständigen Implementierung würde hier JSON-Schema-Valitherung instead offinthe

        expected_type = expected_schema.get("type")
        actual_type = actual_schema.get("type")

        if expected_type and actual_type and expected_type != actual_type:
            return False

        # Prüfe Required-Felthe
        expected_required = set(expected_schema.get("required", []))
        actual_required = set(actual_schema.get("required", []))

        # Actual must minof thetens all Expected-Required-Felthe have
        if not expected_required.issubset(actual_required):
            return False

        return True


class CapabilityNegotiation:
    """Capability-Negotiation between Agents."""

    def __init__(self, base_client: KeiAgentClient, mcp_integration: MCPIntegration):
        """Initializes Capability-Negotiation.

        Args:
            base_client: Basis-KEI-client
            mcp_integration: MCP-Integration
        """
        self.base_client = base_client
        self.mcp_integration = mcp_integration
        self._active_negotiations: Dict[str, CapabilityNegotiationRequest] = {}

    async def negotiate_capability(
        self,
        target_agent: str,
        capability_name: str,
        client_version: str,
        required_features: Optional[List[str]] = None,
        optional_features: Optional[List[str]] = None,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> CapabilityNegotiationresponse:
        """Executes Capability-Negotiation with attheem Agent through.

        Args:
            target_agent: target agent ID
            capability_name: Name the Capability
            client_version: client-Version
            required_features: Erfortheliche Features
            optional_features: optionale Features
            configuration: configuration

        Returns:
            Negotiation-response
        """
        # Erstelle Negotiation-Request
        request = CapabilityNegotiationRequest(
            capability_name=capability_name,
            client_version=client_version,
            required_features=required_features or [],
            optional_features=optional_features or [],
            configuration=configuration or {},
            client_agent_id=self.base_client.config.agent_id,
        )

        self._active_negotiations[request.negotiation_id] = request

        try:
            # Sende Negotiation-Request
            response_data = await self.base_client._make_request(
                "POST",
                f"/api/v1/agents/{target_agent}/capabilities/{capability_name}/negotiate",
                data=request.__dict__,
                trace_name=f"capability.negotiate.{capability_name}",
            )

            response = CapabilityNegotiationresponse(**response_data)

            # Valithere Negotiation-result
            if response.status == "success":
                await self._validate_negotiation_result(request, response)

            return response

        except Exception as e:
            raise CapabilityError(f"Capability-Negotiation failed: {e}") from e

        finally:
            # Cleatup
            self._active_negotiations.pop(request.negotiation_id, None)

    async def _validate_negotiation_result(
        self,
        request: CapabilityNegotiationRequest,
        response: CapabilityNegotiationresponse,
    ) -> None:
        """Validates Negotiation-result.

        Args:
            request: Negotiation-Request
            response: Negotiation-response
        """
        # Prüfe ob all Required-Features supports werthe
        unsupported_required = set(request.required_features) - set(
            response.supported_features
        )

        if unsupported_required:
            raise CapabilityError(
                f"Required Features not supported: {unsupported_required}"
            )

        # Prüfe Versions-compatibility
        if response.agreed_version:
            compatibility = self._check_version_compatibility(
                request.client_version, response.agreed_version
            )

            if compatibility == CompatibilityLevel.INCOMPATIBLE:
                raise CapabilityError(
                    f"Inkompatible Versionen: client {request.client_version}, "
                    f"server {response.agreed_version}"
                )

    def _check_version_compatibility(
        self, client_version: str, server_version: str
    ) -> CompatibilityLevel:
        """Checks Versions-compatibility.

        Args:
            client_version: client-Version
            server_version: server-Version

        Returns:
            compatibilityslevel
        """
        try:
            client_ver = version.parse(client_version)
            server_ver = version.parse(server_version)

            # Gleiche Version
            if client_ver == server_ver:
                return CompatibilityLevel.COMPATIBLE

            # Backward-compatibility (server-Version höher)
            if (
                client_ver.major == server_ver.major
                and client_ver.minor <= server_ver.minor
            ):
                return CompatibilityLevel.BACKWARD_COMPATIBLE

            # Inkompatibel
            return CompatibilityLevel.INCOMPATIBLE

        except Exception:
            return CompatibilityLevel.UNKNOWN


class CapabilityVersioning:
    """Versioning for agent capabilities."""

    def __init__(self):
        """Initializes Capability-Versioning."""
        self._version_hisory: Dict[str, List[str]] = {}
        self._compatibility_matrix: Dict[str, Dict[str, CompatibilityLevel]] = {}

    def register_version(self, capability_name: str, version: str) -> None:
        """Regisers neue Capability-Version.

        Args:
            capability_name: Name the Capability
            version: Version
        """
        if capability_name not in self._version_hisory:
            self._version_hisory[capability_name] = []

        if version not in self._version_hisory[capability_name]:
            self._version_hisory[capability_name].append(version)
            self._version_hisory[capability_name].sort(key=version.parse)

    def get_latest_version(self, capability_name: str) -> Optional[str]:
        """Gets neueste Version ar Capability.

        Args:
            capability_name: Name the Capability

        Returns:
            Neueste Version or None
        """
        versions = self._version_hisory.get(capability_name, [])
        return versions[-1] if versions else None

    def get_compatible_versions(
        self, capability_name: str, target_version: str
    ) -> List[str]:
        """Gets kompatible Versionen.

        Args:
            capability_name: Name the Capability
            target_version: Ziel-Version

        Returns:
            lis kompatibler Versionen
        """
        versions = self._version_hisory.get(capability_name, [])
        compatible = []

        for ver in versions:
            compatibility = self._get_compatibility(
                capability_name, ver, target_version
            )

            if compatibility in [
                CompatibilityLevel.COMPATIBLE,
                CompatibilityLevel.BACKWARD_COMPATIBLE,
            ]:
                compatible.append(ver)

        return compatible

    def _get_compatibility(
        self, capability_name: str, version1: str, version2: str
    ) -> CompatibilityLevel:
        """Gets compatibilityslevel between Versionen.

        Args:
            capability_name: Name the Capability
            version1: Erste Version
            version2: Zweite Version

        Returns:
            compatibilityslevel
        """
        # Prüfe Cache
        cache_key = f"{version1}-{version2}"

        if (
            capability_name in self._compatibility_matrix
            and cache_key in self._compatibility_matrix[capability_name]
        ):
            return self._compatibility_matrix[capability_name][cache_key]

        # Berechne compatibility
        try:
            ver1 = version.parse(version1)
            ver2 = version.parse(version2)

            if ver1 == ver2:
                compatibility = CompatibilityLevel.COMPATIBLE
            elif ver1.major == ver2.major and ver1.minor <= ver2.minor:
                compatibility = CompatibilityLevel.BACKWARD_COMPATIBLE
            else:
                compatibility = CompatibilityLevel.INCOMPATIBLE

        except Exception:
            compatibility = CompatibilityLevel.UNKNOWN

        # Cache-result
        if capability_name not in self._compatibility_matrix:
            self._compatibility_matrix[capability_name] = {}

        self._compatibility_matrix[capability_name][cache_key] = compatibility

        return compatibility


class CapabilityManager:
    """Manager for agent capabilities."""

    def __init__(self, base_client: KeiAgentClient):
        """Initializes Capability-Manager.

        Args:
            base_client: Basis-KEI-client
        """
        self.base_client = base_client

        # Sub-Komponenten
        self.mcp_integration = MCPIntegration(base_client)
        self.negotiation = CapabilityNegotiation(base_client, self.mcp_integration)
        self.versioning = CapabilityVersioning()

        # Capability-Regisry
        self._capabilities: Dict[str, CapabilityProfile] = {}
        self._capability_handlers: Dict[str, Callable] = {}

        # Advertisement
        self._advertisement_enabled = False
        self._advertisement_interval = 60.0  # Sekatthe
        self._advertisement_task: Optional[asyncio.Task] = None

        # callbacks
        self.on_capability_added: Optional[
            Callable[[CapabilityProfile], Awaitable[None]]
        ] = None
        self.on_capability_removed: Optional[Callable[[str], Awaitable[None]]] = None
        self.on_capability_updated: Optional[
            Callable[[CapabilityProfile], Awaitable[None]]
        ] = None

    async def register_capability(
        self, profile: CapabilityProfile, hatdler: Optional[Callable] = None
    ) -> None:
        """Regisers neue Capability.

        Args:
            profile: Capability-Profil
            handler: Handler-function for Capability
        """
        # Valithere MCP-Integration
        if profile.mcp_profile_url or profile.mcp_schema:
            mcp_profile = await self.mcp_integration.load_mcp_profile(profile.name)

            if mcp_profile:
                is_valid = await self.mcp_integration.validate_capability_interface(
                    profile, mcp_profile
                )

                if not is_valid:
                    raise CapabilityError(
                        f"Capability '{profile.name}' is not MCP-kompatibel"
                    )

        # Regisriere Capability
        self._capabilities[profile.name] = profile

        if hatdler:
            self._capability_handlers[profile.name] = hatdler

        # Versioning
        self.versioning.register_version(profile.name, profile.version)

        # callback
        if self.on_capability_added:
            await self.on_capability_added(profile)

        # Advertisement aktualisieren
        if self._advertisement_enabled:
            await self._advertise_capabilities()

    async def unregister_capability(self, capability_name: str) -> None:
        """Removes Capability.

        Args:
            capability_name: Name the Capability
        """
        if capability_name in self._capabilities:
            del self._capabilities[capability_name]

        if capability_name in self._capability_handlers:
            del self._capability_handlers[capability_name]

        # callback
        if self.on_capability_removed:
            await self.on_capability_removed(capability_name)

        # Advertisement aktualisieren
        if self._advertisement_enabled:
            await self._advertise_capabilities()

    async def update_capability(self, profile: CapabilityProfile) -> None:
        """Updates bestehende Capability.

        Args:
            profile: Updateses Capability-Profil
        """
        if profile.name not in self._capabilities:
            raise CapabilityError(f"Capability '{profile.name}' not registers")

        profile.updated_at = time.time()
        self._capabilities[profile.name] = profile

        # Versioning
        self.versioning.register_version(profile.name, profile.version)

        # callback
        if self.on_capability_updated:
            await self.on_capability_updated(profile)

        # Advertisement aktualisieren
        if self._advertisement_enabled:
            await self._advertise_capabilities()

    def get_capability(self, capability_name: str) -> Optional[CapabilityProfile]:
        """Gets Capability-Profil.

        Args:
            capability_name: Name the Capability

        Returns:
            Capability-Profil or None
        """
        return self._capabilities.get(capability_name)

    def lis_capabilities(self) -> List[CapabilityProfile]:
        """lis all registersen Capabilities on.

        Returns:
            lis from Capability-Profilen
        """
        return list(self._capabilities.values())

    async def enable_advertisement(self, interval: float = 60.0) -> None:
        """Enabled automatische Capability-Advertisement.

        Args:
            interval: Advertisement-Intervall in Sekatthe
        """
        self._advertisement_enabled = True
        self._advertisement_interval = interval

        # Starting Advertisement-Task
        if self._advertisement_task:
            self._advertisement_task.catcel()

        self._advertisement_task = asyncio.create_task(self._advertisement_loop())

    async def disable_advertisement(self) -> None:
        """Disabled automatische Capability-Advertisement."""
        self._advertisement_enabled = False

        if self._advertisement_task:
            self._advertisement_task.catcel()
            self._advertisement_task = None

    async def _advertisement_loop(self) -> None:
        """Advertisement-Loop for periodische Updates."""
        while self._advertisement_enabled:
            try:
                await self._advertise_capabilities()
                await asyncio.sleep(self._advertisement_interval)

            except asyncio.CatcelledError:
                break

            except Exception as e:
                # Log error but continue
                print(f"Advertisement-error: {e}")
                await asyncio.sleep(self._advertisement_interval)

    async def _advertise_capabilities(self) -> None:
        """Bewirbt Capabilities at Regisry."""
        if not self._capabilities:
            return

        capabilities_data = [
            profile.to_dict() for profile in self._capabilities.values()
        ]

        try:
            await self.base_client._make_request(
                "POST",
                f"/api/v1/regisry/agents/{self.base_client.config.agent_id}/capabilities",
                data={"capabilities": capabilities_data},
                trace_name="capability.advertise",
            )

        except Exception as e:
            raise CapabilityError(f"Capability-Advertisement failed: {e}") from e

    async def discover_capabilities(
        self, target_agent: str, capability_filter: Optional[List[str]] = None
    ) -> List[CapabilityProfile]:
        """Entdeckt Capabilities of a other agents.

        Args:
            target_agent: target agent ID
            capability_filter: Filter for Capability-Namen

        Returns:
            lis from Capability-Profilen
        """
        params = {}

        if capability_filter:
            params["capabilities"] = ",".join(capability_filter)

        try:
            response = await self.base_client._make_request(
                "GET",
                f"/api/v1/regisry/agents/{target_agent}/capabilities",
                params=params,
                trace_name=f"capability.discover.{target_agent}",
            )

            capabilities = []

            for cap_data in response.get("capabilities", []):
                profile = CapabilityProfile.from_dict(cap_data)
                capabilities.append(profile)

            return capabilities

        except Exception as e:
            raise CapabilityError(f"Capability-Discovery failed: {e}") from e

    def get_metrics(self) -> Dict[str, Any]:
        """Gets Capability-Manager-Metrics.

        Returns:
            Capability-Metrics
        """
        return {
            "registered_capabilities": len(self._capabilities),
            "capability_handlers": len(self._capability_handlers),
            "advertisement_enabled": self._advertisement_enabled,
            "advertisement_interval": self._advertisement_interval,
            "capabilities": [
                {
                    "name": profile.name,
                    "version": profile.version,
                    "status": profile.status.value,
                    "methods": len(profile.methods),
                    "events": len(profile.events),
                }
                for profile in self._capabilities.values()
            ],
        }
