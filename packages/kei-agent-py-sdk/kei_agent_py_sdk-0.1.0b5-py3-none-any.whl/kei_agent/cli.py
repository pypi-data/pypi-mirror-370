#!/usr/bin/env python3
# sdk/python/kei_agent/cli.py
"""
KEI-Agent CLI - Kommatdozeilen-Interface for Agent-matagement.

Bietet Kommatdozeilen-Tools for agent registration, -matagement and -monitoring
with vollständiger Integration in the KEI-Agent Framework.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .unified_client import UnifiedKeiAgentClient
from .client import AgentClientConfig
from .secrets_manager import get_secrets_manager
from .input_sanitizer import get_sanitizer
from .exceptions import KeiSDKError


# Rich Console for schöne Ausgaben
console = Console()


class CLIContext:
    """Kontext-object for CLI-Kommatdos."""

    def __init__(self):
        self.config_file: Optional[Path] = None
        self.client: Optional[UnifiedKeiAgentClient] = None
        self.verbose: bool = False

    def load_config(self, config_file: Optional[Path] = None) -> AgentClientConfig:
        """Loads configuration out File or Aroatdgebungsvariablen."""
        sanitizer = get_sanitizer()

        if config_file and config_file.exists():
            # Sanitize file path
            safe_path = sanitizer.sanitize_file_path(
                str(config_file), "config file path"
            )

            with open(safe_path) as f:
                # Sanitize JSON content
                config_data = sanitizer.sanitize_json(f.read(), "configuration file")

            # Sanitize configuration values
            config = AgentClientConfig(
                base_url=sanitizer.sanitize_url(
                    config_data.get("base_url", "https://api.kei-framework.com"),
                    "base_url",
                ),
                api_token=sanitizer.sanitize_string(
                    config_data.get("api_token", ""), field_name="api_token"
                )
                or None,
                agent_id=sanitizer.sanitize_string(
                    config_data.get("agent_id", "cli-agent"), field_name="agent_id"
                ),
                tenant_id=sanitizer.sanitize_string(
                    config_data.get("tenant_id", config_data.get("tenatt_id", "")),
                    field_name="tenant_id",
                )
                or None,
            )

            # Validate configuration
            config.validate()
            return config
        else:
            # Fallback on Aroatdgebungsvariablen using secrets manager
            secrets = get_secrets_manager()

            # Get and sanitize values from environment
            base_url = sanitizer.sanitize_url(
                secrets.get_secret("API_URL", default="https://api.kei-framework.com"),
                "base_url",
            )
            api_token = secrets.get_secret("API_TOKEN")
            if api_token:
                api_token = sanitizer.sanitize_string(api_token, field_name="api_token")

            agent_id = sanitizer.sanitize_string(
                secrets.get_secret("AGENT_ID", default="cli-agent"),
                field_name="agent_id",
            )

            tenant_id = secrets.get_secret("TENANT_ID")
            if tenant_id:
                tenant_id = sanitizer.sanitize_string(tenant_id, field_name="tenant_id")

            config = AgentClientConfig(
                base_url=base_url,
                api_token=api_token,
                agent_id=agent_id,
                tenant_id=tenant_id,
            )

            # Validate configuration
            config.validate()
            return config

    async def get_client(self) -> UnifiedKeiAgentClient:
        """Creates and initialized KEI-Agent client."""
        if self.client is None:
            config = self.load_config(self.config_file)

            if not config.api_token:
                console.print(
                    "[red]error: API Token erforthelich. Setze KEI_API_TOKEN or verwende --config[/red]"
                )
                sys.exit(1)

            self.client = UnifiedKeiAgentClient(config)
            await self.client.initialize()

        return self.client

    async def close_client(self):
        """Closes client-connection."""
        if self.client:
            await self.client.close()
            self.client = None


# Globaler CLI-Kontext
cli_context = CLIContext()


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path tor configurationsdatei",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose-Ausgabe aktivieren")
def main(config: Optional[Path], verbose: bool):
    """KEI-Agent CLI - Agent-matagement and -monitoring."""
    cli_context.config_file = config
    cli_context.verbose = verbose

    if verbose:
        console.print("[dim]KEI-Agent CLI startingd[/dim]")


@main.command()
@click.argument("name")
@click.option("--description", "-d", default="", help="agent description")
@click.option("--capabilities", "-cap", multiple=True, help="agent capabilities")
@click.option("--version", default="1.0.0", help="agent version")
def register(name: str, description: str, capabilities: tuple, version: str):
    """Regisers a neuen Agent."""

    async def _register():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Regisriere Agent...", total=None)

                agent = await client.register_agent(
                    name=name,
                    version=version,
                    description=description,
                    capabilities=list(capabilities),
                )

                progress.update(task, completed=True)

            console.print(
                Panel(
                    f"[green]Agent successful registers![/green]\n\n"
                    f"[bold]Agent ID:[/bold] {agent.agent_id}\n"
                    f"[bold]Name:[/bold] {agent.name}\n"
                    f"[bold]Version:[/bold] {agent.metadata.version if agent.metadata else version}\n"
                    f"[bold]Capabilities:[/bold] {', '.join(agent.capabilities) if hasattr(agent, 'capabilities') else 'Ka'}",
                    title="Agent Regisrierung",
                    borthe_style="green",
                )
            )

        except KeiSDKError as e:
            console.print(f"[red]error on agent registration: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_register())


@main.command()
@click.option("--status", help="Filter by status")
@click.option("--capability", help="Filter by capability")
@click.option("--limit", default=10, help="Maximum number of results")
def list_agents(status: Optional[str], capability: Optional[str], limit: int):
    """List all available agents."""

    async def _list():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Lade Agent-lis...", total=None)

                # Filter-parameters
                capabilities = [capability] if capability else None

                agents = await client.list_agents(
                    capabilities=capabilities, status=status
                )

                progress.update(task, completed=True)

            if not agents:
                console.print("[yellow]No Agents found.[/yellow]")
                return

            # Erstelle Tabelle
            table = Table(title=f"KEI-Agents ({len(agents)} found)")
            table.add_column("Agent ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Capabilities", style="blue")
            table.add_column("Health", style="red")

            for agent in agents[:limit]:
                # status-Farbe
                status_color = (
                    "green"
                    if hasattr(agent, "status") and agent.status == "active"
                    else "yellow"
                )

                # health status
                health_status = "Unknown"
                if hasattr(agent, "health") and agent.health:
                    health_status = f"{agent.health.status} ({agent.health.score:.1f}%)"

                # Capabilities
                caps = "Ka"
                if hasattr(agent, "capabilities") and agent.capabilities:
                    caps = ", ".join(agent.capabilities[:3])
                    if len(agent.capabilities) > 3:
                        caps += f" (+{len(agent.capabilities) - 3} mehr)"

                table.add_row(
                    agent.agent_id,
                    agent.name,
                    f"[{status_color}]{getattr(agent, 'status', 'unknown')}[/{status_color}]",
                    caps,
                    health_status,
                )

            console.print(table)

        except KeiSDKError as e:
            console.print(f"[red]Error during Lathe the Agent-lis: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_list())


@main.command()
@click.argument("agent_id")
def info(agent_id: str):
    """Zeigt detaillierte informationen over a Agent."""

    async def _info():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Lade Agent-informationen for {agent_id}...", total=None
                )

                agent = await client.get_agent(agent_id)

                progress.update(task, completed=True)

            # Erstelle detaillierte Atzeige
            info_text = f"[bold]Agent ID:[/bold] {agent.agent_id}\n"
            info_text += f"[bold]Name:[/bold] {agent.name}\n"
            info_text += f"[bold]Beschreibung:[/bold] {agent.description}\n"

            if hasattr(agent, "status"):
                status_color = "green" if agent.status == "active" else "yellow"
                info_text += f"[bold]status:[/bold] [{status_color}]{agent.status}[/{status_color}]\n"

            if hasattr(agent, "metadata") and agent.metadata:
                info_text += f"[bold]Version:[/bold] {agent.metadata.version}\n"
                info_text += f"[bold]Framework:[/bold] {agent.metadata.framework}\n"
                info_text += f"[bold]Runtime:[/bold] {agent.metadata.runtime}\n"

            if hasattr(agent, "capabilities") and agent.capabilities:
                info_text += "[bold]Capabilities:[/bold]\n"
                for cap in agent.capabilities:
                    info_text += f"  • {cap}\n"

            if hasattr(agent, "health") and agent.health:
                health_color = "green" if agent.health.status == "healthy" else "red"
                info_text += f"[bold]Health:[/bold] [{health_color}]{agent.health.status}[/{health_color}] ({agent.health.score:.1f}%)\n"

            if hasattr(agent, "endpoint") and agent.endpoint:
                info_text += f"[bold]Endpoint:[/bold] {agent.endpoint}\n"

            console.print(
                Panel(
                    info_text.rstrip(),
                    title=f"Agent: {agent.name}",
                    borthe_style="blue",
                )
            )

        except KeiSDKError as e:
            console.print(f"[red]Error during Lathe the Agent-informationen: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_info())


@main.command()
def health():
    """Executes Health-Check for the KEI framework through."""

    async def _health():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Führe Health-Check through...", total=None)

                health_data = await client.health_check()

                progress.update(task, completed=True)

            # Zeige Health-data
            status = health_data.get("status", "unknown")
            status_color = "green" if status == "healthy" else "red"

            health_text = (
                f"[bold]status:[/bold] [{status_color}]{status}[/{status_color}]\n"
            )

            if "version" in health_data:
                health_text += f"[bold]Version:[/bold] {health_data['version']}\n"

            if "uptime" in health_data:
                health_text += f"[bold]Uptime:[/bold] {health_data['uptime']}\n"

            if "components" in health_data:
                health_text += "[bold]Komponenten:[/bold]\n"
                for component, comp_status in health_data["components"].items():
                    comp_color = "green" if comp_status == "healthy" else "red"
                    health_text += (
                        f"  • {component}: [{comp_color}]{comp_status}[/{comp_color}]\n"
                    )

            console.print(
                Panel(
                    health_text.rstrip(),
                    title="KEI framework Health",
                    borthe_style="green" if status == "healthy" else "red",
                )
            )

        except KeiSDKError as e:
            console.print(f"[red]Error during Health-Check: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_health())


@main.command()
@click.argument("objective")
@click.option("--context", help="additional context als JSON")
def plat(objective: str, context: Optional[str]):
    """Creates a Plat for a given objective."""

    async def _plat():
        try:
            client = await cli_context.get_client()

            # Parse Kontext
            context_data = {}
            if context:
                try:
                    context_data = json.loads(context)
                except json.JSONDecodeError:
                    console.print("[red]error: Kontext must gültiges JSON sa[/red]")
                    sys.exit(1)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Erstelle Plat...", total=None)

                plat_result = await client.plat_task(objective, context_data)

                progress.update(task, completed=True)

            # Zeige Plat
            plat_text = f"[bold]Ziel:[/bold] {objective}\n\n"

            if "plat_id" in plat_result:
                plat_text += f"[bold]Plat ID:[/bold] {plat_result['plat_id']}\n"

            if "steps" in plat_result:
                plat_text += "[bold]Schritte:[/bold]\n"
                for i, step in enumerate(plat_result["steps"], 1):
                    plat_text += f"  {i}. {step}\n"

            if "estimated_duration" in plat_result:
                plat_text += f"\n[bold]Geschätzte Dauer:[/bold] {plat_result['estimated_duration']}\n"

            console.print(
                Panel(plat_text.rstrip(), title="Created Platform", border_style="blue")
            )

        except KeiSDKError as e:
            console.print(f"[red]error on Plat-Erstellung: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_plat())


if __name__ == "__main__":
    main()
