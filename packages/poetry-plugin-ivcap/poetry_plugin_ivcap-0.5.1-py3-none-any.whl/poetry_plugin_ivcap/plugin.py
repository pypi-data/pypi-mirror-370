#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#
import os
from poetry.plugins.application_plugin import ApplicationPlugin
from cleo.commands.command import Command
from cleo.helpers import argument, option
import subprocess
from importlib.metadata import version

from poetry_plugin_ivcap.constants import DEF_IVCAP_BASE_URL, DOCKER_BUILD_TEMPLATE_OPT, DOCKER_RUN_TEMPLATE_OPT, PLUGIN_CMD, PLUGIN_NAME
from poetry_plugin_ivcap.constants import PORT_OPT, SERVICE_FILE_OPT, SERVICE_ID_OPT, SERVICE_TYPE_OPT, POLICY_OPT
from poetry_plugin_ivcap.util import get_version

from .ivcap import create_service_id, exec_job, get_service_id, service_register, tool_register
from .docker import docker_build, docker_run
from .ivcap import docker_publish

class IvcapCommand(Command):
    name = "ivcap"
    description = f"IVCAP plugin `poetry {PLUGIN_CMD} <subcommand>`"
    help = f"""\

IVCAP plugin

Supporting the development of services and tools for the IVCAP platform

Available subcommands:
    run                 Run the service locally
    docker-build        Build the docker image for this service
    docker-run          Run the service's docker image locally for testing
    deploy              Deploy the service to IVCAP (calls docker-publish, service-register and tool-register)
    job-exec file_name  Execute a job defined in 'file_name'
    docker-publish      Publish the service's docker image to IVCAP
    service-register    Register the service with IVCAP
    create-service-id   Create a unique service ID for the service
    get-service-id      Return the service ID for the service
    tool-register       Register the service as an AI Tool with IVCAP
    version             Print the version of this plugin

Example:
  poetry {PLUGIN_CMD} run -- --port 8080
  poetry {PLUGIN_CMD} job-exec request.json -- --timeout 0 # don't wait for result

Configurable options in pyproject.toml:

  [tool.{PLUGIN_NAME}]
  {SERVICE_FILE_OPT} = "service.py"  # The Python file that implements the service
  {SERVICE_ID_OPT} = "urn:ivcap:service:ac158a1f-dfb4-5dac-bf2e-00000000000" # A unique identifier for the service
  {SERVICE_TYPE_OPT} = "lambda

  # Optional
  {POLICY_OPT} = "urn:ivcap:policy:ivcap.open.metadata"
  {DOCKER_BUILD_TEMPLATE_OPT} = "docker buildx build -t #DOCKER_NAME#  ."
  {DOCKER_RUN_TEMPLATE_OPT} = "docker run --rm -p #PORT#:#PORT# #DOCKER_NAME#"
"""
    arguments = [
        argument("subcommand", optional=True, description="Subcommand: run, deploy, etc."),
        argument("args", optional=True, multiple=True, description="Additional arguments for subcommand"),
    ]
    options = [
        option("silent", None, "Run silently (no output)", flag=True),
    ]

    allow_extra_args = True
    ignore_validation_errors = True

    def handle(self):

        sub = self.argument("subcommand")
        if sub == "version":
            #v = poetry.get_plugin('ivcap').version
            v = version(PLUGIN_NAME)
            print(f"IVCAP plugin (version {v})")
            return

        poetry = self.application.poetry
        data = poetry.pyproject.data

        args = self.argument("args")
        is_silent = self.option("silent")

        if sub == "run":
            self.run_service(data, args, self.line)
        elif sub == "docker-build":
            docker_build(data, self.line)
        elif sub == "docker-run":
            docker_run(data, args, self.line)
        elif sub == "deploy" or sub == "publish":
            docker_publish(data, self.line)
            service_register(data, self.line)
            tool_register(data, self.line)
        elif sub == "exec-job" or sub == "job-exec":
            exec_job(data, args, is_silent, self.line)
        elif sub == "docker-publish":
            docker_publish(data, self.line)
        elif sub == "service-register":
            service_register(data, self.line)
        elif sub == "create-service-id":
            sid = create_service_id(data, is_silent, self.line)
            print(sid)
        elif sub == "get-service-id":
            sid = get_service_id(data, is_silent, self.line)
            print(sid)
        elif sub == "tool-register":
            tool_register(data, self.line)

        else:
            if not (sub == None or sub == "help"):
                self.line(f"<error>Unknown subcommand: {sub}</error>")
            print(self.help)

    def run_service(self, data, args, line):
        config = data.get("tool", {}).get(PLUGIN_NAME, {})

        service = config.get(SERVICE_FILE_OPT)
        if not service:
            self.line(f"<error>Missing '{SERVICE_FILE_OPT}' in [tool.{PLUGIN_NAME}]</error>")
            return

        if not '--port' in args:
            port = config.get(PORT_OPT)
            if port:
                args.extend(["--port", str(port)])

        env = os.environ.copy()
        env["VERSION"] = get_version(data, None, line)
        env.setdefault("IVCAP_BASE_URL", DEF_IVCAP_BASE_URL)

        cmd = ["poetry", "run", "python", service]
        cmd.extend(args)
        self.line(f"<info>Running: {' '.join(cmd)}</info>")
        subprocess.run(cmd, env=env)

class IvcapPlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory(PLUGIN_CMD, lambda: IvcapCommand())
