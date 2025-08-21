# Django CMS QE

Django CMS Quick & Easy provides all important modules to run new page
without a lot of coding. Aims to do it very easily and securely.

For more information please read [documentation](<https://websites.pages.nic.cz/django-cms-qe>) or [GitLab](https://gitlab.nic.cz/websites/django-cms-qe).

## Development

To prepare your dev environment run this command:

    make prepare-dev  (run with apt get update)
    make prepare-env

Caution! It is allowed only Python >= 3.9 due to typing:

    VENV_PYTHON=/usr/bin/python3.9 make prepare-venv

To prepare the explicit python version into the explicit folder:

    VENV_PATH=/home/username/venv VENV_PYTHON=/usr/bin/python3.9 make prepare-venv
    export VENV_PATH=/home/username/venv

To run tests or lint use this commands:

    make test
    make lint

To run only particular test:

    make test=cms_qe_table/tests/test_utils.py::test_get_model_by_table test

To run example use this command:

    make run-example


To call other Django commands:

    make cmd  (List django commands, same like --help)
    make cmd=dbshell cmd
    make cmd='createsuperuser --username=dave --email=dave@rd.foo' cmd

To find more useful commands, run just `make`.

## Upgrade

To upgrade from version `2.2` to version >= `3.0.0`, you can use the [DjangoCMS upgrade plugins](https://gitlab.nic.cz/utils/djangocms-upgrade-plugins) tool.
