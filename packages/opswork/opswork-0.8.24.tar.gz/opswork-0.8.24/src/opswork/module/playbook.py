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

import yaml
import ansible_runner

from opswork.module.file_system import FileSystem


class Playbook:
    """Playbook Class"""

    def __init__(self, id, cache, hosts, recipe, var):
        """Class Constructor"""
        self._id = id
        self._cache = cache
        self._hosts = hosts
        self._recipe = recipe
        self._var = var
        self._file_system = FileSystem()

    def build(self):
        """Build Playbook"""
        self._file_system.create_dirs("{}/{}".format(self._cache, self._id))
        self._file_system.create_dirs("{}/{}/cache".format(self._cache, self._id))

        hosts = "[remote]\n"

        for host in self._hosts:
            if host.connection == "local":
                hosts = (
                    hosts
                    + f"{host.ip} ansible_connection={host.connection} ansible_python_interpreter=python3"
                )

            elif host.password != "":
                hosts = (
                    hosts
                    + f"{host.ip} ansible_port={host.port} ansible_connection={host.connection} ansible_user={host.user} ansible_password={host.password} ansible_python_interpreter=python3"
                )
            else:
                hosts = (
                    hosts
                    + f"{host.ip} ansible_port={host.port} ansible_connection={host.connection} ansible_user={host.user} ansible_ssh_private_key_file={self._cache}/{self._id}/{host.id}.pem ansible_python_interpreter=python3"
                )
                self._file_system.write_file(
                    "{}/{}/{}.pem".format(self._cache, self._id, host.id),
                    host.ssh_private_key,
                )
                self._file_system.change_permission(
                    "{}/{}/{}.pem".format(self._cache, self._id, host.id), 0o400
                )

            hosts = hosts + "\n"

        self._file_system.write_file("{}/{}/hosts".format(self._cache, self._id), hosts)

        data = yaml.load(self._recipe.recipe, Loader=yaml.Loader)

        if "templates" in data.keys():
            for item in self._recipe.templates:
                for key in item.keys():
                    self._file_system.write_file(
                        "{}/{}/{}".format(self._cache, self._id, key), item[key]
                    )

            del data["templates"]

        # Override vars
        if "vars" in data.keys():
            data["vars"].update(self._var)

        base = {
            "hosts": "remote",
        }

        base.update(data)
        playbook = [base]
        self._file_system.write_file(
            "{}/{}/playbook.yml".format(self._cache, self._id), yaml.dump(playbook)
        )

    def run(self):
        """Run Ansible Playbook"""
        out = ansible_runner.run(
            private_data_dir="{}/{}/cache".format(self._cache, self._id),
            playbook="{}/{}/playbook.yml".format(self._cache, self._id),
            inventory="{}/{}/hosts".format(self._cache, self._id),
        )

        if out.status.lower() == "failed":
            return False

        elif out.status.lower() == "successful":
            return True

        return False

    def cleanup(self):
        """Cleanup Playbook Directory"""
        try:
            self._file_system.delete_directory("{}/{}".format(self._cache, self._id))
        except Exception:
            pass
