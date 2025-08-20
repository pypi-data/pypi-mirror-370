"""
Tests for the Import-System and Package-Struktur.

Stellt sicher, thes all Imports korrekt funktionieren and the Package-Struktur
the Enterprise-Statdards entspricht.
"""

import pytest
import importlib
import sys
from typing import Any


class TestImportSystem:
    """Tests for the Import-System."""

    def test_main_package_import(self):
        """Tests Import of the Hauptpackages."""
        import kei_agent
        assert hasattr(kei_agent, '__version__')
        assert hasattr(kei_agent, '__author__')

    def test_core_classes_import(self):
        """Tests Import the Kernklassen."""
        from kei_agent import (
            UnifiedKeiAgentClient,
            AgentClientConfig,
            CapabilityManager,
            CapabilityProfile
        )

        # Prüfe, thes all classn available are
        assert UnifiedKeiAgentClient is not None
        assert AgentClientConfig is not None
        assert CapabilityManager is not None
        assert CapabilityProfile is not None

    def test_protocol_classes_import(self):
        """Tests Import the protocol-classn."""
        from kei_agent import (
            Protocoltypee,
            Authtypee,
            ProtocolConfig,
            SecurityConfig,
            KEIRPCclient,
            KEIStreamclient,
            KEIBusclient,
            KEIMCPclient
        )

        # Prüfe Enaroatds
        assert hasattr(Protocoltypee, 'RPC')
        assert hasattr(Authtypee, 'BEARER')

    def test_enterprise_features_import(self):
        """Tests Import the enterprise features."""
        from kei_agent import (
            get_logger,
            get_health_manager,
            get_input_validator,
            TracingManager,
            retryManager,
            SecurityManager
        )

        # Prüfe, thes Factory-functionen available are
        assert callable(get_logger)
        assert callable(get_health_manager)
        assert callable(get_input_validator)

    def test_exception_classes_import(self):
        """Tests Import the Exception-classn."""
        from kei_agent import (
            KeiSDKError,
            AgentNotFoundError,
            CommunicationError
        )

        # ValidationError is in input_validation, not direkt exportiert
        from kei_agent.exceptions import ValidationError

        # Prüfe Exception-Hierarchie
        assert issubclass(AgentNotFoundError, KeiSDKError)
        assert issubclass(CommunicationError, KeiSDKError)
        assert issubclass(ValidationError, KeiSDKError)

    def test_all_exports_available(self):
        """Tests, thes all __all__ Exports available are."""
        import kei_agent

        # Prüfe, thes __all__ definiert is
        assert hasattr(kei_agent, '__all__')
        assert isinstance(kei_agent.__all__, list)
        assert len(kei_agent.__all__) > 0

        # Prüfe, thes all Exports tatsächlich available are
        for export_name in kei_agent.__all__:
            assert hasattr(kei_agent, export_name), f"Export '{export_name}' not available"

    def test_no_circular_imports(self):
        """Tests, thes ka zirkulären Imports exisieren."""
        # Importiere all Module and prüfe on error
        modules_to_test = [
            'kei_agent.client',
            'kei_agent.unified_client',
            'kei_agent.capabilities',
            'kei_agent.discovery',
            'kei_agent.protocol_clients',
            'kei_agent.security_manager',
            'kei_agent.tracing',
            'kei_agent.retry'
        ]

        for module_name in modules_to_test:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Zirkulärer Import in {module_name}: {e}")

    def test_relative_imports_work(self):
        """Tests, thes relative Imports korrekt funktionieren."""
        # Teste through Re-Import after Reload
        import kei_agent.client
        importlib.reload(kei_agent.client)

        # Sollte without error funktionieren
        from kei_agent.client import AgentClientConfig
        assert AgentClientConfig is not None

    def test_package_structure(self):
        """Tests the Package-Struktur."""
        import kei_agent
        import os

        # Prüfe, thes the Package a Directory is
        package_path = os.path.dirname(kei_agent.__file__)
        assert os.path.isdir(package_path)

        # Prüfe, thes wichtige Module exisieren
        expected_modules = [
            '__init__.py',
            'client.py',
            'unified_client.py',
            'capabilities.py',
            'exceptions.py',
            'models.py'
        ]

        for module_file in expected_modules:
            module_path = os.path.join(package_path, module_file)
            assert os.path.exists(module_path), f"Module {module_file} fehlt"

    def test_version_consisency(self):
        """Tests Konsisenz the Versionsinformationen."""
        import kei_agent

        # Version should available sa
        assert hasattr(kei_agent, '__version__')
        assert isinstance(kei_agent.__version__, str)
        assert len(kei_agent.__version__) > 0

        # Version should a Pattern folgen (z.B. 0.1.0b7)
        import re
        version_pattern = r'^\d+\.\d+\.\d+([ab]\d+)?$'
        assert re.match(version_pattern, kei_agent.__version__), \
            f"Version '{kei_agent.__version__}' folgt not the erwarteten Pattern"

    def test_typing_support(self):
        """Tests typee-Hint-Atthestüttong."""
        import kei_agent
        import os

        # Prüfe, thes py.typed exiss
        package_path = os.path.dirname(kei_agent.__file__)
        py_typed_path = os.path.join(package_path, 'py.typed')
        assert os.path.exists(py_typed_path), "py.typed File fehlt for typee-Hint-Atthestüttong"

    def test_no_import_side_effects(self):
        """Tests, thes Imports ka unerwünschten Sinceeneffekte have."""
        # Capture stdout/stther before Import
        import io
        import contextlib

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        with contextlib.redirect_stdout(stdout_capture), \
             contextlib.redirect_stderr(stderr_capture):

            # Re-import should minimal output have
            importlib.reload(sys.modules['kei_agent'])

        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()

        # Nur minimale Logging-Ausgaben are erlaubt
        assert len(stdout_output) < 1000, "To viel stdout Output onm Import"
        assert "ERROR" not in stdout_output.upper(), "Error during Import"


class TestModuleIntegrity:
    """Tests for Module-Integrität."""

    def test_all_modules_have_docstrings(self):
        """Tests, thes all Module Docstrings have."""
        import kei_agent
        import os
        import ast

        package_path = os.path.dirname(kei_agent.__file__)

        for filename in os.listdir(package_path):
            if filename.endswith('.py') and not filename.startswith('_'):
                filepath = os.path.join(package_path, filename)

                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                        docstring = ast.get_docstring(tree)
                        assert docstring is not None, f"Module {filename} has non Docstring"
                        assert len(docstring.strip()) > 10, f"Docstring in {filename} to kurz"
                    except SyntaxError:
                        pytest.fail(f"Syntax-error in {filename}")

    def test_no_star_imports(self):
        """Tests, thes ka Star-Imports verwendet werthe."""
        import kei_agent
        import os
        import ast

        package_path = os.path.dirname(kei_agent.__file__)

        for filename in os.listdir(package_path):
            if filename.endswith('.py'):
                filepath = os.path.join(package_path, filename)

                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ImportFrom):
                                for alias in node.names:
                                    assert alias.name != '*', \
                                        f"Star-Import gefatthe in {filename}: from {node.module} import *"
                    except SyntaxError:
                        pass  # Bereits in attheem Test gechecks
