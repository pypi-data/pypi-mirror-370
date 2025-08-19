# SPDX-FileCopyrightText: Copyright (c) 2025 Xronos Inc.
# SPDX-License-Identifier: LicenseRef-Xronos-Commercial-License-v1

# pyright: standard

import asyncio
import importlib.resources
import json
import pathlib
import sys
from typing import Any, Literal, TypedDict

import click
import halo
import jinja2
import platformdirs

import xronos_dashboard

Config = TypedDict(
    "Config",
    {
        "organization": str,
        "database": str,
        "endpoint": str,
        "token": str,
        "fully_local": bool,
    },
)

MaybeConfig = Config | Literal["default"] | Literal["use-previous-config"]

RESOURCE_DIR = importlib.resources.files(xronos_dashboard).joinpath("resources")
CONFIG_DIR = pathlib.Path(platformdirs.user_config_dir("xronos-dashboard"))
CONFIG_FILE = CONFIG_DIR / "config.json"


async def log_stdout(process: asyncio.subprocess.Process) -> None:
    if process.stdout is None:
        return
    async for line in process.stdout:
        click.echo(line.rstrip())


async def capture_stdout(process: asyncio.subprocess.Process) -> list[str]:
    if process.stdout is None:
        return []
    lines = list[str]()
    async for line in process.stdout:
        lines.append(line.decode().rstrip())
    return lines


def apply_template(template_path: str, **args: Any) -> str:
    with importlib.resources.as_file(RESOURCE_DIR) as reseource_dir:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(reseource_dir))
        otel_config_template = env.get_template(template_path)
        return otel_config_template.render(**args)


def generate_docker_compose_file(config: Config):
    with open(CONFIG_DIR / "docker-compose.yml", "w") as f:
        f.write(
            apply_template(
                "docker-compose.yml.jinja2",
                version=xronos_dashboard.IMAGE_TAG,
                **config,
            )
        )


def generate_otel_collector_config(config: Config):
    path = CONFIG_DIR / "otel_collector"
    path.mkdir(exist_ok=True)
    with open(path / "config.yml", "w") as f:
        f.write(apply_template("otel_collector/config.yml.jinja2", **config))


def generate_grafana_datasources_file(config: Config):
    path = CONFIG_DIR / "grafana" / "datasources"
    path.mkdir(parents=True, exist_ok=True)
    with open(path / "datasources.yml", "w") as f:
        f.write(apply_template("grafana/datasources/datasources.yml.jinja2", **config))


def try_load_config_from_config_dir() -> Config | None:
    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None


def write_config_to_config_dir(config: Config):
    config_dir = pathlib.Path(CONFIG_DIR)
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    generate_docker_compose_file(config)
    generate_otel_collector_config(config)
    generate_grafana_datasources_file(config)


def setup_default_config():
    config: Config = {
        "organization": "xronos",
        "database": "dev",
        "endpoint": "http://influxdb:8086",
        "token": "xronostoken",
        "fully_local": True,
    }
    write_config_to_config_dir(config)
    return config


def setup_user_config(config_file: str):
    with open(config_file) as f:
        config = json.load(f)
        write_config_to_config_dir(config)


def initialize_config():
    config = try_load_config_from_config_dir()
    if not config:
        setup_default_config()


async def run_docker_command(args: list[str], show_output: bool = True) -> int:
    process = await asyncio.create_subprocess_exec(
        "docker",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=CONFIG_DIR,
    )

    if show_output:
        stdout_task: asyncio.Task[None] | asyncio.Task[list[str]] = asyncio.create_task(
            log_stdout(process)
        )
    else:
        stdout_task = asyncio.create_task(capture_stdout(process))

    await process.wait()

    output = await stdout_task

    assert process.returncode is not None
    if output and not show_output and process.returncode != 0:
        for line in output:
            click.echo(line)

    return process.returncode


@click.group()
def cli() -> None:
    pass


@click.command(help="Start the dashboard.")
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Show verbose output."
)
@click.option(
    "-c",
    "--config",
    default=None,
    help="Path to a JSON file with your organization's database credentials.",
)
def start(verbose: bool, config: str | None) -> None:
    with halo.Halo(
        "starting", spinner="dots", color="green", enabled=not verbose
    ) as spinner:
        if config is not None:
            setup_user_config(config)
        else:
            setup_default_config()
        returncode = asyncio.run(
            run_docker_command(["compose", "up", "-d"], show_output=verbose)
        )
        if returncode == 0:
            spinner.succeed("dashboard available at http://localhost:3000")
        else:
            spinner.fail("failed to bring up dashboard")
            print('    You may need to call "xronos-dashboard stop" to clean up.')
        sys.exit(returncode)


@click.command(help="Stop the dashboard.")
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Show verbose output."
)
def stop(verbose: bool) -> None:
    returncode = compose_down(verbose, volumes=False)
    sys.exit(returncode)


@click.command(
    help="Permanently delete all dashboard state, including telemetry data, "
    "Grafana configurations, and Grafana queries."
)
@click.option(
    "-v", "--verbose", is_flag=True, default=False, help="Show verbose output."
)
def delete(verbose: bool) -> None:
    returncode = compose_down(verbose, volumes=True)
    sys.exit(returncode)


def compose_down(verbose: bool, volumes: bool) -> int:
    initialize_config()
    description = "shutting down"
    if volumes:
        description += " and deleting Docker volumes"
    with halo.Halo(
        description, spinner="dots", color="green", enabled=not verbose
    ) as spinner:
        command = ["compose", "down"]
        if volumes:
            command.append("--volumes")
        returncode = asyncio.run(run_docker_command(command, show_output=verbose))
        if returncode == 0:
            spinner.succeed("stopped")
        else:
            spinner.fail("failed to shut down dashboard")
        return returncode


@click.command(help="View dashboard logs.")
@click.option("-f", "--follow", is_flag=True, default=False, help="Follow log output.")
def logs(follow: bool) -> None:
    initialize_config()
    cmd = ["compose", "logs"]
    if follow:
        cmd.append("-f")
    returncode = asyncio.run(run_docker_command(cmd, show_output=True))
    sys.exit(returncode)


cli.add_command(start)
cli.add_command(stop)
cli.add_command(delete)
cli.add_command(logs)

if __name__ == "__main__":
    cli()
