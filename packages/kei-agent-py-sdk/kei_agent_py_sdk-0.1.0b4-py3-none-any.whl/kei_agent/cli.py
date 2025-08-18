#!/usr/bin/env python3
# sdk/python/kei_agent/cli.py
"""
KEI-Agent CLI - Kommandozeilen-Interface für Agent-Management.

Bietet Kommandozeilen-Tools für Agent-Registrierung, -Management und -Monitoring
mit vollständiger Integration in das KEI-Agent Framework.
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

from unified_client import UnifiedKeiAgentClient
from client import AgentClientConfig
from exceptions import KeiSDKError


# Rich Console für schöne Ausgaben
console = Console()


class CLIContext:
    """Kontext-Objekt für CLI-Kommandos."""

    def __init__(self):
        self.config_file: Optional[Path] = None
        self.client: Optional[UnifiedKeiAgentClient] = None
        self.verbose: bool = False

    def load_config(self, config_file: Optional[Path] = None) -> AgentClientConfig:
        """Lädt Konfiguration aus Datei oder Umgebungsvariablen."""
        if config_file and config_file.exists():
            with open(config_file) as f:
                config_data = json.load(f)

            return AgentClientConfig(
                base_url=config_data.get("base_url", "https://api.kei-framework.com"),
                api_token=config_data.get("api_token"),
                agent_id=config_data.get("agent_id", "cli-agent"),
                tenant_id=config_data.get("tenant_id"),
            )
        else:
            # Fallback auf Umgebungsvariablen
            import os

            return AgentClientConfig(
                base_url=os.getenv("KEI_API_URL", "https://api.kei-framework.com"),
                api_token=os.getenv("KEI_API_TOKEN"),
                agent_id=os.getenv("KEI_AGENT_ID", "cli-agent"),
                tenant_id=os.getenv("KEI_TENANT_ID"),
            )

    async def get_client(self) -> UnifiedKeiAgentClient:
        """Erstellt und initialisiert KEI-Agent Client."""
        if self.client is None:
            config = self.load_config(self.config_file)

            if not config.api_token:
                console.print(
                    "[red]Fehler: API Token erforderlich. Setze KEI_API_TOKEN oder verwende --config[/red]"
                )
                sys.exit(1)

            self.client = UnifiedKeiAgentClient(config)
            await self.client.initialize()

        return self.client

    async def close_client(self):
        """Schließt Client-Verbindung."""
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
    help="Pfad zur Konfigurationsdatei",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose-Ausgabe aktivieren")
def main(config: Optional[Path], verbose: bool):
    """KEI-Agent CLI - Agent-Management und -Monitoring."""
    cli_context.config_file = config
    cli_context.verbose = verbose

    if verbose:
        console.print("[dim]KEI-Agent CLI gestartet[/dim]")


@main.command()
@click.argument("name")
@click.option("--description", "-d", default="", help="Agent-Beschreibung")
@click.option("--capabilities", "-cap", multiple=True, help="Agent-Capabilities")
@click.option("--version", default="1.0.0", help="Agent-Version")
def register(name: str, description: str, capabilities: tuple, version: str):
    """Registriert einen neuen Agent."""

    async def _register():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Registriere Agent...", total=None)

                agent = await client.register_agent(
                    name=name,
                    version=version,
                    description=description,
                    capabilities=list(capabilities),
                )

                progress.update(task, completed=True)

            console.print(
                Panel(
                    f"[green]Agent erfolgreich registriert![/green]\n\n"
                    f"[bold]Agent ID:[/bold] {agent.agent_id}\n"
                    f"[bold]Name:[/bold] {agent.name}\n"
                    f"[bold]Version:[/bold] {agent.metadata.version if agent.metadata else version}\n"
                    f"[bold]Capabilities:[/bold] {', '.join(agent.capabilities) if hasattr(agent, 'capabilities') else 'Keine'}",
                    title="Agent Registrierung",
                    border_style="green",
                )
            )

        except KeiSDKError as e:
            console.print(f"[red]Fehler bei Agent-Registrierung: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_register())


@main.command()
@click.option("--status", help="Filter nach Status")
@click.option("--capability", help="Filter nach Capability")
@click.option("--limit", default=10, help="Maximale Anzahl Ergebnisse")
def list(status: Optional[str], capability: Optional[str], limit: int):
    """Listet alle verfügbaren Agents auf."""

    async def _list():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Lade Agent-Liste...", total=None)

                # Filter-Parameter
                capabilities = [capability] if capability else None

                agents = await client.list_agents(
                    capabilities=capabilities, status=status
                )

                progress.update(task, completed=True)

            if not agents:
                console.print("[yellow]Keine Agents gefunden.[/yellow]")
                return

            # Erstelle Tabelle
            table = Table(title=f"KEI-Agents ({len(agents)} gefunden)")
            table.add_column("Agent ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Capabilities", style="blue")
            table.add_column("Health", style="red")

            for agent in agents[:limit]:
                # Status-Farbe
                status_color = (
                    "green"
                    if hasattr(agent, "status") and agent.status == "active"
                    else "yellow"
                )

                # Health-Status
                health_status = "Unknown"
                if hasattr(agent, "health") and agent.health:
                    health_status = f"{agent.health.status} ({agent.health.score:.1f}%)"

                # Capabilities
                caps = "Keine"
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
            console.print(f"[red]Fehler beim Laden der Agent-Liste: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_list())


@main.command()
@click.argument("agent_id")
def info(agent_id: str):
    """Zeigt detaillierte Informationen über einen Agent."""

    async def _info():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Lade Agent-Informationen für {agent_id}...", total=None
                )

                agent = await client.get_agent(agent_id)

                progress.update(task, completed=True)

            # Erstelle detaillierte Anzeige
            info_text = f"[bold]Agent ID:[/bold] {agent.agent_id}\n"
            info_text += f"[bold]Name:[/bold] {agent.name}\n"
            info_text += f"[bold]Beschreibung:[/bold] {agent.description}\n"

            if hasattr(agent, "status"):
                status_color = "green" if agent.status == "active" else "yellow"
                info_text += f"[bold]Status:[/bold] [{status_color}]{agent.status}[/{status_color}]\n"

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
                    border_style="blue",
                )
            )

        except KeiSDKError as e:
            console.print(f"[red]Fehler beim Laden der Agent-Informationen: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_info())


@main.command()
def health():
    """Führt Health-Check für das KEI-Framework durch."""

    async def _health():
        try:
            client = await cli_context.get_client()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Führe Health-Check durch...", total=None)

                health_data = await client.health_check()

                progress.update(task, completed=True)

            # Zeige Health-Daten
            status = health_data.get("status", "unknown")
            status_color = "green" if status == "healthy" else "red"

            health_text = (
                f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]\n"
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
                    title="KEI-Framework Health",
                    border_style="green" if status == "healthy" else "red",
                )
            )

        except KeiSDKError as e:
            console.print(f"[red]Fehler beim Health-Check: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_health())


@main.command()
@click.argument("objective")
@click.option("--context", help="Zusätzlicher Kontext als JSON")
def plan(objective: str, context: Optional[str]):
    """Erstellt einen Plan für ein gegebenes Ziel."""

    async def _plan():
        try:
            client = await cli_context.get_client()

            # Parse Kontext
            context_data = {}
            if context:
                try:
                    context_data = json.loads(context)
                except json.JSONDecodeError:
                    console.print("[red]Fehler: Kontext muss gültiges JSON sein[/red]")
                    sys.exit(1)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Erstelle Plan...", total=None)

                plan_result = await client.plan_task(objective, context_data)

                progress.update(task, completed=True)

            # Zeige Plan
            plan_text = f"[bold]Ziel:[/bold] {objective}\n\n"

            if "plan_id" in plan_result:
                plan_text += f"[bold]Plan ID:[/bold] {plan_result['plan_id']}\n"

            if "steps" in plan_result:
                plan_text += "[bold]Schritte:[/bold]\n"
                for i, step in enumerate(plan_result["steps"], 1):
                    plan_text += f"  {i}. {step}\n"

            if "estimated_duration" in plan_result:
                plan_text += f"\n[bold]Geschätzte Dauer:[/bold] {plan_result['estimated_duration']}\n"

            console.print(
                Panel(plan_text.rstrip(), title="Erstellter Plan", border_style="blue")
            )

        except KeiSDKError as e:
            console.print(f"[red]Fehler bei Plan-Erstellung: {e}[/red]")
            sys.exit(1)
        finally:
            await cli_context.close_client()

    asyncio.run(_plan())


if __name__ == "__main__":
    main()
