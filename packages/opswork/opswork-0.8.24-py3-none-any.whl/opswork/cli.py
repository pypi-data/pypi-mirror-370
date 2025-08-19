# MIT License
#
# Copyright (c) 2023 Clivern
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import uuid
import click
import logging, json, sys

from opswork import __version__
from opswork.model.host import Host
from opswork.model.secret import Secret
from opswork.command.hosts import Hosts
from opswork.command.configs import Configs
from opswork.command.recipes import Recipes
from opswork.command.secret import Secrets
from opswork.command.random import Random


@click.group(help="🐺 OpsWork Swiss Knife")
@click.version_option(version=__version__, help="Show the current version")
def main():
    pass


# Hosts command
@click.group(help="Manage hosts")
def host():
    pass


# List host sub command
@host.command(help="List hosts")
@click.option("-t", "--tag", "tag", type=click.STRING, default="", help="Host tag")
@click.option(
    "-o", "--output", "output", type=click.STRING, default="", help="Output format"
)
def list(tag, output):
    return Hosts().init().list(tag, output)


# Add host sub command
@host.command(help="Add a host")
@click.argument("name")
@click.option(
    "-c",
    "--connection",
    "connection",
    type=click.STRING,
    default="ssh",
    help="Connection type to the host",
)
@click.option(
    "-i",
    "--ip",
    "ip",
    type=click.STRING,
    default="",
    help="The IP or hostname to connect to",
)
@click.option(
    "-p",
    "--port",
    "port",
    type=click.INT,
    default=22,
    help="The connection port number",
)
@click.option(
    "-u",
    "--user",
    "user",
    type=click.STRING,
    default="root",
    help="The user name to use when connecting to the host",
)
@click.option(
    "-pa",
    "--password",
    "password",
    type=click.STRING,
    default="",
    help="The password to use to authenticate to the host",
)
@click.option(
    "-s",
    "--ssh_private_key_file",
    "ssh_private_key_file",
    required=False,
    type=click.File(),
    help="Private key file used by ssh",
)
@click.option("-t", "--tags", "tags", type=click.STRING, default="", help="Host tags")
@click.option("-f", "--force", "force", is_flag=True, default=False, help="Force add")
def add(name, connection, ip, port, user, password, ssh_private_key_file, tags, force):
    host = Host(
        str(uuid.uuid4()),
        name,
        connection,
        ip,
        port,
        user,
        password,
        ssh_private_key_file.read() if ssh_private_key_file is not None else "",
        tags.split(",") if tags != "" else [],
        None,
        None,
    )

    return Hosts().init().add(host, force)


# Get host sub command
@host.command(help="Get a host")
@click.argument("name")
@click.option(
    "-o", "--output", "output", type=click.STRING, default="", help="Output format"
)
def get(name, output):
    return Hosts().init().get(name, output)


# SSH to a host sub command
@host.command(help="SSH to a host")
@click.argument("name")
def ssh(name):
    return Hosts().init().ssh(name)


# Delete host sub command
@host.command(help="Delete a host")
@click.argument("name")
def delete(name):
    return Hosts().init().delete(name)


# Recipes command
@click.group(help="Manage recipes")
def recipe():
    pass


# Add recipes sub command
@recipe.command(help="Add a recipe")
@click.argument("name")
@click.option(
    "-p",
    "--path",
    "path",
    required=True,
    default="",
    help="Path to the recipe",
)
@click.option(
    "-s",
    "--sub",
    "sub",
    default="",
    help="Sub path to the recipe",
)
@click.option("-t", "--tags", "tags", type=click.STRING, default="", help="Recipe tags")
@click.option("-f", "--force", "force", is_flag=True, default=False, help="Force add")
def add(name, path, sub, tags, force):
    return (
        Recipes()
        .init()
        .add(
            name,
            {"path": path, "sub": sub, "tags": tags.split(",") if tags != "" else []},
            force,
        )
    )


# List recipes sub command
@recipe.command(help="List all recipes")
@click.option("-t", "--tag", "tag", type=click.STRING, default="", help="Recipe tag")
@click.option(
    "-o", "--output", "output", type=click.STRING, default="", help="Output format"
)
def list(tag, output):
    return Recipes().init().list(tag, output)


# Get recipe sub command
@recipe.command(help="Get a recipe")
@click.argument("name")
@click.option(
    "-o", "--output", "output", type=click.STRING, default="", help="Output format"
)
def get(name, output):
    return Recipes().init().get(name, output)


# Delete recipe sub command
@recipe.command(help="Delete a recipe")
@click.argument("name")
def delete(name):
    return Recipes().init().delete(name)


# Run recipe sub command
@recipe.command(help="Run a recipe towards hosts")
@click.argument("name")
@click.option(
    "-h",
    "--host",
    "host",
    type=click.STRING,
    default="",
    help="The name of the host to run recipe towards",
)
@click.option(
    "-t",
    "--tag",
    "tag",
    type=click.STRING,
    default="",
    help="Hosts tag to run recipe towards",
)
@click.option("--var", "-v", multiple=True)
def run(name, host, tag, var):
    return Recipes().init().run(name, host, tag, var)


# Manage configs command
@click.group(help="Manage configs")
def config():
    pass


# Init configs sub command
@config.command(help="Init configurations")
def init():
    return Configs().init()


# Edit configs sub command
@config.command(help="Edit configurations")
def edit():
    return Configs().edit()


# Show configs sub command
@config.command(help="Show configurations")
def dump():
    return Configs().dump()


# Secrets command
@click.group(help="Manage secrets")
def secret():
    pass


# Add secrets sub command
@secret.command(help="Add a secret")
@click.argument("name")
@click.argument("value")
@click.option("-t", "--tags", "tags", type=click.STRING, default="", help="Secret tags")
@click.option("-f", "--force", "force", is_flag=True, default=False, help="Force add")
def add(name, value, tags, force):
    secret = Secret(
        str(uuid.uuid4()),
        name,
        value,
        tags.split(",") if tags != "" else [],
        None,
        None,
    )

    return Secrets().init().add(secret, force)


# List secrets sub command
@secret.command(help="List all secrets")
@click.option("-t", "--tag", "tag", type=click.STRING, default="", help="Secret tag")
@click.option(
    "-o", "--output", "output", type=click.STRING, default="", help="Output format"
)
def list(tag, output):
    return Secrets().init().list(tag, output)


# Get secret sub command
@secret.command(help="Get a secret")
@click.argument("name")
@click.option(
    "-o", "--output", "output", type=click.STRING, default="", help="Output format"
)
def get(name, output):
    return Secrets().init().get(name, output)


# Delete secret sub command
@secret.command(help="Delete a secret")
@click.argument("name")
def delete(name):
    return Secrets().init().delete(name)


# Random data command
@click.group(help="Generate random data")
def random():
    pass


# Init random sub command
@random.command(help="Generate a password")
@click.argument("length")
def password(length):
    return Random().password(int(length))


# Register Commands
main.add_command(host)
main.add_command(recipe)
main.add_command(config)
main.add_command(secret)
main.add_command(random)


if __name__ == "__main__":
    main()
