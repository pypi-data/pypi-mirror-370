"""Tests End-to-End Workflows without externe Abhängigkeiten.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from kei_agent import (
    UnifiedKeiAgentClient,
    AgentClientConfig,
    CapabilityManager,
    CapabilityProfile,
    Protocoltypee,
    Authtypee,
    ProtocolConfig,
    SecurityConfig
)
from kei_agent.exceptions import ValidationError


class TestCriticalWorkflows:
    """Tests for kritische SDK-Workflows."""

    def test_basic_client_workflow(self):
        """Tests gratdlegenthe client-Workflow."""
        # 1. configuration erstellen
        config = AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )

        # 2. client erstellen
        client = UnifiedKeiAgentClient(config)

        # 3. Valithere client-status
        assert client.config == config
        assert not client._initialized
        assert not client._closed

        # 4. Valithere Sub-Komponenten exisieren
        assert hasattr(client, 'protocol_config')
        assert hasattr(client, 'security_config')

    def test_protocol_configuration_workflow(self):
        """Tests protocol-configuration Workflow."""
        # 1. Erstelle protocol-configuration
        protocol_config = ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =False,
            bus_enabled =True,
            mcp_enabled =False
        )

        # 2. Valithere configuration
        assert protocol_config.rpc_enabled is True
        assert protocol_config.stream_enabled is False
        assert protocol_config.bus_enabled is True
        assert protocol_config.mcp_enabled is False

        # 3. Teste Endpunkt-Togriff
        rpc_endpoint = protocol_config.get_endpoint(Protocoltypee.RPC)
        assert rpc_endpoint == "/api/v1/rpc"

        bus_endpoint = protocol_config.get_endpoint(Protocoltypee.BUS)
        assert bus_endpoint == "/api/v1/bus"

    def test_security_configuration_workflow(self):
        """Tests securitys-configuration Workflow."""
        # 1. Erstelle Security-configuration
        security_config = SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token ="sk-1234567890abcdef1234567890abcdef12345678",
            rbac_enabled =True,
            audit_enabled =True
        )

        # 2. Valithere configuration
        assert security_config.auth_type == Authtypee.BEARER
        assert security_config.api_token == "sk-1234567890abcdef1234567890abcdef12345678"
        assert security_config.rbac_enabled is True
        assert security_config.audit_enabled is True

        # 3. Teste Valitherung
        security_config.validate()  # Sollte not fehlschlagen

        # 4. Teste Token-basierte authentication
        assert security_config.is_token_based() is True

    def test_capability_matagement_workflow(self):
        """Tests Capability-matagement Workflow."""
        # 1. Erstelle Mock-client
        mock_client = Mock()

        # 2. Erstelle Capability-Manager
        manager = CapabilityManager(mock_client)

        # 3. Erstelle Capability-Profil
        profile = CapabilityProfile(
            name="test-capability",
            version="1.0.0",
            description="Test capability for workflow",
            tags=["test", "workflow"],
            category="testing"
        )

        # 4. Valithere Profil
        assert profile.name == "test-capability"
        assert profile.version == "1.0.0"
        assert "test" in profile.tags

        # 5. Teste Profil-Serialisierung
        profile_dict = profile.to_dict()
        assert isinstance(profile_dict, dict)
        assert profile_dict["name"] == "test-capability"

        # 6. Teste Profil-Of theerialisierung
        restored_profile = CapabilityProfile.from_dict(profile_dict)
        assert restored_profile.name == profile.name
        assert restored_profile.version == profile.version

    def test_unified_client_with_custom_configs(self):
        """Tests UnifiedKeiAgentClient with benutzerdefinierten configurationen."""
        # 1. Erstelle Agent-configuration
        agent_config = AgentClientConfig(
            agent_id ="custom-agent",
            base_url ="https://api.example.com",
            api_token ="custom-token",
            tenant_id ="custom-tenant"
        )

        # 2. Erstelle protocol-configuration
        protocol_config = ProtocolConfig(
            rpc_enabled =True,
            stream_enabled =True,
            bus_enabled =False,
            mcp_enabled =True,
            auto_protocol_selection =False
        )

        # 3. Erstelle securitys-configuration
        security_config = SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token ="custom-token",
            rbac_enabled =False,
            audit_enabled =True
        )

        # 4. Erstelle client with benutzerdefinierten configurationen
        client = UnifiedKeiAgentClient(
            config=agent_config,
            protocol_config =protocol_config,
            security_config =security_config
        )

        # 5. Valithere client-configuration
        assert client.config == agent_config
        assert client.protocol_config == protocol_config
        assert client.security_config == security_config

        # 6. Valithere specific Astellungen
        assert client.config.tenant_id == "custom-tenant"
        assert client.protocol_config.auto_protocol_selection is False
        assert client.security_config.rbac_enabled is False

    def test_error_hatdling_workflow(self):
        """Tests Error-Hatdling Workflow."""
        # 1. Teste ungültiges protocol
        protocol_config = ProtocolConfig()

        with pytest.raises(ValueError):
            protocol_config.get_endpoint("invalid_protocol")

        # 2. Teste Security-Valitherung with fehlenthe data
        security_config = SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token =None  # Fehlenof the Token
        )

        with pytest.raises((ValueError, ValidationError)):
            security_config.validate()

        # 3. Teste OIDC-configuration without erfortheliche Felthe
        oidc_config = SecurityConfig(
            auth_type =Authtypee.OIDC,
            oidc_issuer =None  # Fehlende OIDC-configuration
        )

        with pytest.raises((ValueError, ValidationError)):
            oidc_config.validate()

    def test_package_metadata_workflow(self):
        """Tests Package-metadata Workflow."""
        import kei_agent

        # 1. Teste Version
        assert hasattr(kei_agent, '__version__')
        assert isinstance(kei_agent.__version__, str)
        assert len(kei_agent.__version__) > 0

        # 2. Teste Autor
        assert hasattr(kei_agent, '__author__')
        assert isinstance(kei_agent.__author__, str)

        # 3. Teste Lizenz
        assert hasattr(kei_agent, '__license__')
        assert isinstance(kei_agent.__license__, str)

        # 4. Teste Titel
        assert hasattr(kei_agent, '__title__')
        assert isinstance(kei_agent.__title__, str)

    def test_import_consisency_workflow(self):
        """Tests Import-Konsisenz Workflow."""
        # 1. Teste direkte Imports
        from kei_agent import UnifiedKeiAgentClient
        from kei_agent import AgentClientConfig
        from kei_agent import CapabilityManager
        from kei_agent import CapabilityProfile

        # 2. Teste, thes all classn callable are
        assert callable(UnifiedKeiAgentClient)
        assert callable(AgentClientConfig)
        assert callable(CapabilityManager)
        assert callable(CapabilityProfile)

        # 3. Teste __all__ Export
        import kei_agent
        assert hasattr(kei_agent, '__all__')
        assert isinstance(kei_agent.__all__, list)

        # 4. Teste, thes all __all__ Exports available are
        for export_name in kei_agent.__all__:
            assert hasattr(kei_agent, export_name), f"Export '{export_name}' not available"

    def test_configuration_inheritatce_workflow(self):
        """Tests configurations-Vererbung Workflow."""
        # 1. Erstelle Basis-configuration
        base_config = AgentClientConfig(
            agent_id ="base-agent",
            base_url ="http://localhost:8000",
            api_token ="base-token"
        )

        # 2. Teste Sub-configurationen
        assert hasattr(base_config, 'connection')
        assert hasattr(base_config, 'retry')
        assert hasattr(base_config, 'tracing')

        # 3. Teste Default-valuee
        assert base_config.connection.timeout == 30.0
        assert base_config.retry.max_attempts == 3
        assert base_config.tracing.enabled is True

        # 4. Teste Feature-Flags
        assert base_config.enable_service_discovery is True
        assert base_config.enable_health_monitoring is True
        assert base_config.enable_capability_advertisement is True

    def test_enaroatd_consisency_workflow(self):
        """Tests Enaroatd-Konsisenz Workflow."""
        # 1. Teste Protocoltypee Enaroatd
        assert Protocoltypee.RPC == "rpc"
        assert Protocoltypee.STREAM == "stream"
        assert Protocoltypee.BUS == "bus"
        assert Protocoltypee.MCP == "mcp"
        assert Protocoltypee.AUTO == "auto"

        # 2. Teste Authtypee Enaroatd
        assert Authtypee.BEARER == "bearer"
        assert Authtypee.OIDC == "oidc"
        assert Authtypee.MTLS == "mtls"

        # 3. Teste Enaroatd-Iteration
        protocol_types = list(Protocoltypee)
        assert len(protocol_types) == 5

        auth_types = list(Authtypee)
        assert len(auth_types) == 3


class TestPackageIntegration:
    """Tests for Package-Integration."""

    def test_full_package_import(self):
        """Tests vollständigen Package-Import."""
        # Teste, thes the Package without error importiert werthe katn
        import kei_agent

        # Teste wichtige Attribute
        assert hasattr(kei_agent, 'UnifiedKeiAgentClient')
        assert hasattr(kei_agent, 'AgentClientConfig')
        assert hasattr(kei_agent, 'CapabilityManager')
        assert hasattr(kei_agent, 'CapabilityProfile')

    def test_package_structure_integrity(self):
        """Tests Package-Struktur Integrität."""
        import kei_agent
        import os

        # Teste, thes the Package a Directory is
        package_path = os.path.dirname(kei_agent.__file__)
        assert os.path.isdir(package_path)

        # Teste, thes wichtige Module exisieren
        expected_modules = [
            '__init__.py',
            'unified_client.py',
            'capabilities.py',
            'protocol_types.py',
            'client.py'
        ]

        for module_file in expected_modules:
            module_path = os.path.join(package_path, module_file)
            assert os.path.exists(module_path), f"Module {module_file} fehlt"
