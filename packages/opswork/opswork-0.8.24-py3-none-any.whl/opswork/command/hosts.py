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

import click
import subprocess

from opswork.model.host import Host
from opswork.module.logger import Logger
from opswork.module.output import Output
from opswork.module.config import Config
from opswork.module.encrypt import Encrypt
from opswork.module.database import Database
from opswork.module.file_system import FileSystem


class Hosts:
    """Hosts Class"""

    def __init__(self):
        self.output = Output()
        self.database = Database()
        self.config = Config()
        self.encrypt = Encrypt()
        self.file_system = FileSystem()
        self.logger = Logger().get_logger(__name__)

    def init(self):
        """Init database and configs"""
        self.configs = self.config.load()
        self.database.connect(self.configs["database"]["path"])
        self.database.migrate()

        return self

    def add(self, host, force):
        """Add a new host"""
        if force:
            self.database.delete_host(host.name)

        if self.database.get_host(host.name) is not None:
            raise click.ClickException(f"Host with name {host.name} exists")

        # Encrypt the user
        if host.user != "":
            host.user = self.encrypt.encrypt(
                self.configs["database"]["token"], host.user
            )

        # Encrypt the password
        if host.password != "":
            host.password = self.encrypt.encrypt(
                self.configs["database"]["token"], host.password
            )

        # Encrypt the private key
        if host.ssh_private_key != "":
            host.ssh_private_key = self.encrypt.encrypt(
                self.configs["database"]["token"], host.ssh_private_key
            )

        self.database.insert_host(host)

        click.echo(f"Host with name {host.name} got created")

    def list(self, tag, output):
        """List hosts"""
        data = []
        hosts = self.database.list_hosts()

        for host in hosts:
            if tag != "" and tag not in host.tags:
                continue

            data.append(
                {
                    "ID": host.id,
                    "Name": host.name,
                    "IP": host.ip,
                    "Connection": host.connection.upper(),
                    "Tags": ", ".join(host.tags) if len(host.tags) > 0 else "-",
                    "Created at": host.created_at,
                    "Updated at": host.updated_at,
                }
            )

        if len(data) == 0:
            raise click.ClickException(f"No hosts found!")

        print(
            self.output.render(
                data, Output.JSON if output.lower() == "json" else Output.DEFAULT
            )
        )

    def get(self, name, output):
        """Get a host"""
        host = self.database.get_host(name)

        if host is None:
            raise click.ClickException(f"Host with name {name} not found")

        data = [
            {
                "ID": host.id,
                "Name": host.name,
                "IP": host.ip,
                "Connection": host.connection.upper(),
                "Tags": ", ".join(host.tags) if len(host.tags) > 0 else "-",
                "Created at": host.created_at,
                "Updated at": host.updated_at,
            }
        ]

        print(
            self.output.render(
                data, Output.JSON if output.lower() == "json" else Output.DEFAULT
            )
        )

    def ssh(self, name):
        """SSH to a host"""
        host = self.database.get_host(name)

        if host is None:
            raise click.ClickException(f"Host with name {name} not found")

        if host.ssh_private_key == "":
            raise click.ClickException(
                f"SSH feature is only for hosts with private keys"
            )

        tmp_path = self.configs["cache"]["path"]

        if self.file_system.file_exists(f"{tmp_path}/{host.id}.pem"):
            self.file_system.delete_file(f"{tmp_path}/{host.id}.pem")

        # Decrypt the ssh key
        if host.ssh_private_key != "":
            host.ssh_private_key = self.encrypt.decrypt(
                self.configs["database"]["token"], host.ssh_private_key
            )

        # Decrypt the password
        if host.password != "":
            host.password = self.encrypt.decrypt(
                self.configs["database"]["token"], host.password
            )

        # Decrypt the username
        if host.user != "":
            host.user = self.encrypt.decrypt(
                self.configs["database"]["token"], host.user
            )

        self.file_system.write_file(
            f"{tmp_path}/{host.id}.pem",
            host.ssh_private_key,
        )

        self.file_system.change_permission(f"{tmp_path}/{host.id}.pem", 0o400)

        cmd = f"ssh -o StrictHostKeyChecking=no -i {tmp_path}/{host.id}.pem -p {host.port} {host.user}@{host.ip}"

        subprocess.run(cmd.split(" "))

    def delete(self, name):
        """Delete a host"""
        self.database.delete_host(name)

        click.echo(f"Host with name {name} got deleted")
