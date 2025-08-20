"""Tests the gratdlegenthe functionen without externe Abhängigkeiten.
"""

import pytest
from unittest.mock import Mock, patch
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


class TestAgentClientConfig:
    """Tests for AgentClientConfig."""

    def test_config_creation_minimal(self):
        """Tests minimale configurationserstellung."""
        config = AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )

        assert config.agent_id == "test-agent"
        assert config.base_url == "http://localhost:8000"
        assert config.api_token == "test-token"

    def test_config_creation_full(self):
        """Tests vollständige configurationserstellung."""
        config = AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token",
            tenant_id ="test-tenant"
        )

        assert config.agent_id == "test-agent"
        assert config.base_url == "http://localhost:8000"
        assert config.api_token == "test-token"
        assert config.tenant_id == "test-tenant"
        # Teste Sub-configurationen
        assert hasattr(config, 'connection')
        assert hasattr(config, 'retry')

    def test_config_validation(self):
        """Tests configurationsvalitherung."""
        # AgentClientConfig has aktuell ka agebaute Valitherung
        # Teste, thes leere valuee akzeptiert werthe (for jetzt)
        config = AgentClientConfig(
            agent_id ="",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )
        assert config.agent_id == ""


class TestCapabilityProfile:
    """Tests for CapabilityProfile."""

    def test_profile_creation_minimal(self):
        """Tests minimale Profilerstellung."""
        profile = CapabilityProfile(
            name="test-capability",
            version="1.0.0"
        )

        assert profile.name == "test-capability"
        assert profile.version == "1.0.0"
        assert profile.description == ""

    def test_profile_creation_full(self):
        """Tests vollständige Profilerstellung."""
        profile = CapabilityProfile(
            name="test-capability",
            version="1.0.0",
            description="Test capability",
            tags=["test", "theo"],
            category="testing"
        )

        assert profile.name == "test-capability"
        assert profile.version == "1.0.0"
        assert profile.description == "Test capability"
        assert profile.tags == ["test", "theo"]
        assert profile.category == "testing"

    def test_profile_to_dict(self):
        """Tests Konvertierung to dictionary."""
        profile = CapabilityProfile(
            name="test-capability",
            version="1.0.0",
            description="Test capability"
        )

        result = profile.to_dict()

        assert isinstance(result, dict)
        assert result["name"] == "test-capability"
        assert result["version"] == "1.0.0"
        assert result["description"] == "Test capability"

    def test_profile_from_dict(self):
        """Tests Erstellung out dictionary."""
        data = {
            "name": "test-capability",
            "version": "1.0.0",
            "description": "Test capability",
            "tags": ["test"]
        }

        profile = CapabilityProfile.from_dict(data)

        assert profile.name == "test-capability"
        assert profile.version == "1.0.0"
        assert profile.description == "Test capability"
        assert profile.tags == ["test"]


class TestProtocolConfig:
    """Tests for ProtocolConfig."""

    def test_protocol_config_creation(self):
        """Tests ProtocolConfig-Erstellung."""
        config = ProtocolConfig()

        # Teste Default-valuee
        assert hasattr(config, 'rpc_enabled')
        assert hasattr(config, 'stream_enabled')
        assert hasattr(config, 'bus_enabled')
        assert hasattr(config, 'mcp_enabled')

    def test_protocol_types_enaroatd(self):
        """Tests Protocoltypee Enaroatd."""
        assert Protocoltypee.RPC
        assert Protocoltypee.STREAM
        assert Protocoltypee.BUS
        assert Protocoltypee.MCP

    def test_auth_types_enaroatd(self):
        """Tests Authtypee Enaroatd."""
        assert Authtypee.BEARER
        assert Authtypee.OIDC
        assert Authtypee.MTLS
        # Teste, thes the Enaroatd-valuee korrekt are
        assert Authtypee.BEARER == "bearer"


class TestSecurityConfig:
    """Tests for SecurityConfig."""

    def test_security_config_creation(self):
        """Tests SecurityConfig-Erstellung."""
        config = SecurityConfig(
            auth_type =Authtypee.BEARER,
            api_token ="test-token"
        )

        assert config.auth_type == Authtypee.BEARER
        assert config.api_token == "test-token"


class TestUnifiedKeiAgentClientBasic:
    """Gratdlegende Tests for UnifiedKeiAgentClient without Netzwerk."""

    def test_client_creation(self):
        """Tests client-Erstellung."""
        config = AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )

        client = UnifiedKeiAgentClient(config)

        assert client.config == config
        assert hasattr(client, 'protocol_config')
        assert hasattr(client, 'security_config')

    def test_client_attributes(self):
        """Tests client-Attribute."""
        config = AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )

        client = UnifiedKeiAgentClient(config)

        # Teste wichtige Attribute
        assert hasattr(client, 'config')
        assert hasattr(client, 'protocol_config')
        assert hasattr(client, 'security_config')
        assert hasattr(client, '_initialized')
        assert hasattr(client, '_closed')

    @patch('kei_agent.unified_client.KeiAgentClient')
    def test_client_with_mocked_depenthecies(self, mock_legacy_client):
        """Tests client with mockethe Abhängigkeiten."""
        config = AgentClientConfig(
            agent_id ="test-agent",
            base_url ="http://localhost:8000",
            api_token ="test-token"
        )

        client = UnifiedKeiAgentClient(config)

        # Teste, thes the client creates wurde
        assert client is not None
        assert client.config.agent_id == "test-agent"


class TestCapabilityManagerBasic:
    """Gratdlegende Tests for CapabilityManager."""

    def test_capability_manager_creation(self):
        """Tests CapabilityManager-Erstellung."""
        # Mock KeiAgentClient
        mock_client = Mock()

        manager = CapabilityManager(mock_client)

        assert manager.base_client == mock_client
        assert hasattr(manager, '_capabilities')
        assert hasattr(manager, '_capability_handlers')

    def test_capability_registration_basic(self):
        """Tests gratdlegende Capability-Regisrierung."""
        mock_client = Mock()
        manager = CapabilityManager(mock_client)

        profile = CapabilityProfile(
            name="test-capability",
            version="1.0.0"
        )

        # Teste, thes the Regisrierung without error läuft
        # (Async-Test würde echte Regisrierung testen)
        assert profile.name == "test-capability"
        assert manager._capabilities == {}


class TestPackageIntegrity:
    """Tests for Package-Integrität."""

    def test_all_main_classes_importable(self):
        """Tests, thes all Hauptklassen importierbar are."""
        # These Imports sollten without error funktionieren
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

        # Teste, thes all classn tatsächlich classn are
        assert callable(UnifiedKeiAgentClient)
        assert callable(AgentClientConfig)
        assert callable(CapabilityManager)
        assert callable(CapabilityProfile)

    def test_version_available(self):
        """Tests, thes Version available is."""
        import kei_agent

        assert hasattr(kei_agent, '__version__')
        assert isinstance(kei_agent.__version__, str)
        assert len(kei_agent.__version__) > 0

    def test_package_metadata(self):
        """Tests Package-metadata."""
        import kei_agent

        assert hasattr(kei_agent, '__author__')
        assert hasattr(kei_agent, '__license__')
        assert hasattr(kei_agent, '__title__')
