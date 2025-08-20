#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#
from datetime import datetime, timezone
import os
import re
import sys
import tempfile
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import subprocess

from .constants import DEF_IVCAP_BASE_URL, DEF_PORT, DOCKER_BATCH_RUN_TEMPLATE, DOCKER_BUILD_TEMPLATE, DOCKER_BUILD_TEMPLATE_OPT, DOCKER_LAMBDA_RUN_TEMPLATE, DOCKER_RUN_OPT, DOCKER_RUN_TEMPLATE_OPT, PLUGIN_NAME, SERVICE_TYPE_OPT
from .util import command_exists, get_name, get_version

class DockerConfig(BaseModel):
    name: Optional[str] = Field(None)
    tag: Optional[str] = Field(None)
    arch: Optional[str] = Field(None)
    version: Optional[str] = Field(None)
    dockerfile: Optional[str] = Field("Dockerfile")
    project_dir: Optional[str] = Field(os.getcwd())

    @property
    def docker_name(self) -> str:
        return f"{self.name}_{self.arch}:{self.tag}"

    def from_build_template(self, data: dict) -> str:
        pdata = data.get("tool", {}).get(PLUGIN_NAME, {})
        template = pdata.get(DOCKER_BUILD_TEMPLATE_OPT, DOCKER_BUILD_TEMPLATE).strip()
        t = template.strip()\
            .replace("#DOCKER_NAME#", self.docker_name)\
            .replace("#NAME#", self.name)\
            .replace("#TAG#", self.tag)\
            .replace("#ARCH#", self.arch)\
            .replace("#VERSION#", self.version)\
            .replace("#DOCKERFILE#", self.dockerfile)\
            .replace("#PROJECT_DIR#", self.project_dir)\
            .split()
        return t

    def from_run_template(self, data, args, line) -> List[any]:
        pdata = data.get("tool", {}).get(PLUGIN_NAME, {})
        template = pdata.get(DOCKER_RUN_TEMPLATE_OPT)
        smode = pdata.get(SERVICE_TYPE_OPT)
        if smode is None:
            line(f"<error>ERROR: 'service-type' is not defined in [{PLUGIN_NAME}]</error>")
            sys.exit(1)
        if template is None:
            if smode == "lambda":
                template = DOCKER_LAMBDA_RUN_TEMPLATE
            elif smode == "batch":
                template = DOCKER_BATCH_RUN_TEMPLATE
            else:
                line(f"<error>ERROR: Unknown service type '{smode}' in [{PLUGIN_NAME}]</error>")
                sys.exit(1)

        opts = pdata.get(DOCKER_RUN_OPT, [])
        port = get_port_value(args)
        port_in_args = True
        if not port:
            port = get_port_value(opts)
        if not port:
            port_in_args = False
            port = str(pdata.get("port", DEF_PORT))

        base_url = os.environ.get("IVCAP_BASE_URL", DEF_IVCAP_BASE_URL)
        t = template.strip()\
            .replace("#DOCKER_NAME#", self.docker_name)\
            .replace("#IVCAP_BASE_URL#", base_url)\
            .replace("#NAME#", self.name)\
            .replace("#TAG#", self.tag)\
            .replace("#PORT#", port)\
            .replace("#ARCH#", self.arch)\
            .replace("#VERSION#", self.version)\
            .replace("#PROJECT_DIR#", self.project_dir)

        cmd = t.split()
        cmd.extend(opts)
        cmd.extend(args)
        if smode == "lambda" and not port_in_args:
            cmd.extend(["--port", port])
        return cmd


def docker_build(data: dict, line, arch = None) -> None:
    check_docker_cmd(line)
    config = docker_cfg(data, line, arch)
    build_cmd = config.from_build_template(data)
    line(f"<info>INFO: {' '.join(build_cmd)}</info>")
    process = subprocess.Popen(build_cmd, stdout=sys.stdout, stderr=sys.stderr)
    exit_code = process.wait()
    if exit_code != 0:
        line(f"<error>ERROR: Docker build failed with exit code {exit_code}</error>")
    else:
        line("<info>INFO: Docker build completed successfully</info>")
    return config.docker_name

def docker_run(data: dict, args, line) -> None:
    check_docker_cmd(line)
    config = docker_cfg(data, line)
    build_run = config.from_run_template(data, args, line)
    line(f"<info>INFO: {' '.join(build_run)}</info>")
    process = subprocess.Popen(build_run, stdout=sys.stdout, stderr=sys.stderr)
    exit_code = process.wait()
    if exit_code != 0:
        line(f"<error>ERROR: Docker run failed with exit code {exit_code}</error>")
    else:
        line("<info>INFO: Docker run completed successfully</info>")

def docker_cfg(data: dict, line, arch = None) -> DockerConfig:
    name = get_name(data)

    pdata = data.get("tool", {}).get(PLUGIN_NAME, {})
    config = DockerConfig(name=name, **pdata.get("docker", {}))
    if arch:
        # override architecture if provided
        config.arch = arch

    if not config.tag:
        try:
            config.tag = subprocess.check_output(['git', 'rev-parse', "--short", 'HEAD']).decode().strip()
        except Exception as e:
            line(f"<warning>WARN: retrieving commit hash: {e}</warning>")
            config.tag = "latest"

    if not config.version:
        config.version = get_version(data, config.tag, line)

    if not config.arch:
        try:
            config.arch = subprocess.check_output(['uname', '-m']).decode().strip()
        except Exception as e:
            line(f"<error>ERROR: cannot obtain build architecture: {e}</error>")
            os.exit(1)

    return config

def docker_push(docker_img, line):
    push_cmd = ["ivcap", "package", "push", "--force", "--local", docker_img]
    line(f"<debug>Running: {' '.join(push_cmd)} </debug>")
    p1 = subprocess.Popen(push_cmd, stdout=subprocess.PIPE, stderr=sys.stderr)

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Pipe its output to tee (or to the screen via /dev/tty)
        p2 = subprocess.Popen(
            ["tee", tmp_path],
            stdin=p1.stdout,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        p1.stdout.close()
        # Wait for both to finish
        p2.communicate()
        exit_code = p1.wait()
        if exit_code != 0:
            line(f"<error>ERROR: package push failed with exit code {exit_code}</error>")
            sys.exit(1)

        # Lookginf for "45a06508-5c3a-4678-8e6d-e6399bf27538/gene_onology_term_mapper_amd64:9a9a7cc pushed\n"
        pattern = re.compile(
            r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/[^\s]+) pushed'
        )
        package_name = None
        with open(tmp_path, 'r') as f:
            for l in f:
                match = pattern.search(l)
                if match:
                    package_name = match.group(1)
                    break

        if not package_name:
            line("<error>ERROR: No package name found in output</error>")
            sys.exit(1)

        line("<info>INFO: package push completed successfully</info>")
        return package_name
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def check_docker_cmd(line):
    if not command_exists("docker"):
        line("<error>'docker' command not found. Please install it first.</error>")
        sys.exit(1)

def get_port_value(arr):
    try:
        index = arr.index('--port')
        return arr[index + 1]
    except ValueError:
        return None
    except IndexError:
        return None