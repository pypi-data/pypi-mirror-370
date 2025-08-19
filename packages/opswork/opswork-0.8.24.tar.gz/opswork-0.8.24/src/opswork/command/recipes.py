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
import yaml
import click
import git

from opswork.model.recipe import Recipe
from opswork.module.logger import Logger
from opswork.module.output import Output
from opswork.module.config import Config
from opswork.module.encrypt import Encrypt
from opswork.module.database import Database
from opswork.module.playbook import Playbook
from opswork.module.file_system import FileSystem


class Recipes:
    """Recipes Class"""

    def __init__(self):
        self.output = Output()
        self.config = Config()
        self.encrypt = Encrypt()
        self.database = Database()
        self.file_system = FileSystem()
        self.logger = Logger().get_logger(__name__)

    def init(self):
        """Init database and configs"""
        self.configs = self.config.load()
        self.database.connect(self.configs["database"]["path"])
        self.database.migrate()
        return self

    def add(self, name, configs, force):
        """Add a Recipe"""
        recipe = ""
        templates = []

        if force:
            self.database.delete_recipe(name)

        if self.database.get_recipe(name) is not None:
            raise click.ClickException(f"Recipe with name {name} exists")

        # If path start with http or git
        clone_path = None

        if (
            configs["path"].startswith("http") or configs["path"].startswith("git")
        ) and configs["path"].endswith(".git"):
            uid = str(uuid.uuid4())
            clone_path = "{}/{}".format(self.configs["cache"]["path"].rstrip("/"), uid)

            recipe_path = "{}/{}/{}".format(
                self.configs["cache"]["path"].rstrip("/"),
                uid,
                configs["sub"].strip("/"),
            )

            git.Repo.clone_from(configs["path"], clone_path)
            # Override the path
            configs["path"] = recipe_path.rstrip("/")

        if self.file_system.file_exists("{}/recipe.yml".format(configs["path"])):
            recipe = self.file_system.read_file("{}/recipe.yml".format(configs["path"]))

        if self.file_system.file_exists("{}/recipe.yaml".format(configs["path"])):
            recipe = self.file_system.read_file(
                "{}/recipe.yaml".format(configs["path"])
            )

        data = yaml.load(recipe, Loader=yaml.Loader)

        if data and "templates" in data.keys():
            for k, v in data["templates"].items():
                if self.file_system.file_exists("{}/{}".format(configs["path"], v)):
                    templates.append(
                        {
                            k: self.file_system.read_file(
                                "{}/{}".format(configs["path"], v)
                            )
                        }
                    )

        recipe = Recipe(
            str(uuid.uuid4()), name, recipe, templates, configs["tags"], None, None
        )

        self.database.insert_recipe(recipe)

        if not clone_path is None:
            self.file_system.delete_directory(clone_path)

        click.echo(f"Recipe with name {name} got created")

    def list(self, tag, output):
        """List Recipes"""
        data = []
        recipes = self.database.list_recipes()

        for recipe in recipes:
            if tag != "" and tag not in recipe.tags:
                continue

            data.append(
                {
                    "ID": recipe.id,
                    "Name": recipe.name,
                    "Tags": ", ".join(recipe.tags) if len(recipe.tags) > 0 else "-",
                    "Created at": recipe.created_at,
                    "Updated at": recipe.updated_at,
                }
            )

        if len(data) == 0:
            raise click.ClickException(f"No recipes found!")

        print(
            self.output.render(
                data, Output.JSON if output.lower() == "json" else Output.DEFAULT
            )
        )

    def get(self, name, output):
        """Get Recipe"""
        recipe = self.database.get_recipe(name)

        if recipe is None:
            raise click.ClickException(f"Recipe with name {name} not found")

        data = [
            {
                "ID": recipe.id,
                "Name": recipe.name,
                "Tags": ", ".join(recipe.tags) if len(recipe.tags) > 0 else "-",
                "Created at": recipe.created_at,
                "Updated at": recipe.updated_at,
            }
        ]

        print(
            self.output.render(
                data, Output.JSON if output.lower() == "json" else Output.DEFAULT
            )
        )

    def delete(self, name):
        """Delete a Recipe"""
        self.database.delete_recipe(name)

        click.echo(f"Recipe with name {name} got deleted")

    def run(self, name, host_name, tag, var):
        """Run a Recipe towards a host"""
        hosts = []
        found = ""
        recipe = self.database.get_recipe(name)

        if recipe is None:
            raise click.ClickException(f"Recipe with name {name} not found")

        if host_name != "":
            host = self.database.get_host(host_name)

            if host is None:
                raise click.ClickException(f"Host with name {name} not found")

            found = host.id

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

            hosts.append(host)

        if tag != "":
            items = self.database.list_hosts()
            for item in items:
                if tag not in item.tags or found == item.id:
                    continue

                # Decrypt the ssh key
                if item.ssh_private_key != "":
                    item.ssh_private_key = self.encrypt.decrypt(
                        self.configs["database"]["token"], item.ssh_private_key
                    )

                # Decrypt the password
                if item.password != "":
                    item.password = self.encrypt.decrypt(
                        self.configs["database"]["token"], item.password
                    )

                # Decrypt the username
                if item.user != "":
                    item.user = self.encrypt.decrypt(
                        self.configs["database"]["token"], item.user
                    )

                hosts.append(item)

        if len(hosts) == 0:
            raise click.ClickException(f"No hosts matching!")

        var_override = {}

        for item in var:
            if "=" not in item:
                continue
            data = item.split("=")
            var_override[data[0]] = data[1]

        playbook = Playbook(
            str(uuid.uuid4()),
            self.configs["cache"]["path"].rstrip("/"),
            hosts,
            recipe,
            var_override,
        )

        playbook.build()
        playbook.run()
        playbook.cleanup()
