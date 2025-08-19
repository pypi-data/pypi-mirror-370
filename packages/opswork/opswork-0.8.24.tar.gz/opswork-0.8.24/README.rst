.. image:: https://img.shields.io/pypi/v/opswork.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/opswork/
.. image:: https://github.com/clivern/opswork/actions/workflows/ci.yml/badge.svg
    :alt: Build Status
    :target: https://github.com/clivern/opswork/actions/workflows/ci.yml
.. image:: https://static.pepy.tech/badge/opswork
    :alt: Downloads
    :target: https://pepy.tech/projects/opswork

|

=======
OpsWork
=======

To use opswork, follow the following steps:

1. Create a python virtual environment or use system wide environment

.. code-block::

    $ python3 -m venv venv
    $ source venv/bin/activate


2. Install opswork package with pip.

.. code-block::

    $ pip install opswork


3. Get opswork command line help

.. code-block::

    $ opswork --help


4. Init the config file and the sqlite database

.. code-block::

    $ opswork config init


5. To edit configs

.. code-block::

    $ opswork config init


6. Add a recipe

.. code-block::

    $ opswork recipe add <recipe_name> -p <recipe_relative_path>

    # Some examples
    $ opswork recipe add clivern/ping -p recipe/ping -f
    $ opswork recipe add clivern/nginx -p recipe/nginx -f
    $ opswork recipe add clivern/motd -p recipe/motd -f
    $ opswork recipe add clivern/cmd -p recipe/cmd -f
    # From remote git
    $ opswork recipe add clivern/dotfiles/update -p git@github.com:clivern/dotfiles.git -s brew/update -t dotfiles -f


7. To list recipes

.. code-block::

    $ opswork recipe list

    # Get recipes as a JSON
    $ opswork recipe list -o json | jq .


8. To get a recipe

.. code-block::

    $ opswork recipe get <recipe_name>


9. To delete a recipe

.. code-block::

    $ opswork recipe delete <recipe_name>


10. Add a host

.. code-block::

    $ opswork host add <host_name> -i <host_ip> -p <ssh_port> -u <ssh_username> -s <ssh_key_path>

    # Add a remote host
    $ opswork host add example.com -i 127.0.0.1 -p 22 -u root -s /Users/root/.ssh/id_rsa.pem

    # Add the localhost
    $ opswork host add localhost -i localhost -c local


11. To list hosts

.. code-block::

    $ opswork host list

    # Get hosts as a JSON
    $ opswork host list -o json | jq .


12. To get a host

.. code-block::

    $ opswork host get <host_name>


13. To SSH into a host

.. code-block::

    $ opswork host ssh <host_name>


14. To delete a host

.. code-block::

    $ opswork host delete <host_name>


15. Run a recipe towards a host

.. code-block::

    $ opswork recipe run <recipe_name> -h <host_name> -v key=value

    # Some examples
    $ opswork recipe run clivern/nginx -h example.com
    $ opswork recipe run clivern/ping -h localhost


16. To generate a random password

.. code-block::

    $ opswork random password 8


17. To add a secret

.. code-block::

    $ opswork secret add <secret/name> <secret_value> -t <tag>

    $ opswork secret add clivern/cloud_provider/api_key xxxx-xxxx-xxxx-xxxx -t cloud_provider


18. To list secrets

.. code-block::

    $ opswork secret list -o json


19. To get a secret

.. code-block::

    $ opswork secret get <secret_name>

    # For example
    $ opswork secret get clivern/cloud_provider/api_key


20. To delete a secret

.. code-block::

    $ opswork secret delete <secret_name>

    # For example
    $ opswork secret delete clivern/cloud_provider/api_key
