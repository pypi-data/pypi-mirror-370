#
# Copyright (c) 2025 Commonwealth Scientific and Industrial Research Organisation (CSIRO). All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file. See the AUTHORS file for names of contributors.
#

PLUGIN_NAME = "poetry-plugin-ivcap"
PLUGIN_CMD = "ivcap"

SERVICE_ID_OPT = "service-id"
SERVICE_FILE_OPT = "service-file"
SERVICE_TYPE_OPT = "service-type"
PORT_OPT = "port"
POLICY_OPT = "policy"

DOCKER_RUN_TEMPLATE_OPT = "docker-run-template"
DOCKER_RUN_OPT = "docker-run-opts"
DOCKER_BUILD_TEMPLATE_OPT = "docker-build-template"

DEF_POLICY = "urn:ivcap:policy:ivcap.base.metadata"
DEF_PORT = 8000
DEF_IVCAP_BASE_URL = "https://develop.ivcap.net"

DOCKER_BUILD_TEMPLATE = """
docker buildx build
    -t #DOCKER_NAME#
    --platform linux/#ARCH#
    --build-arg VERSION=#VERSION#
    --build-arg BUILD_PLATFORM=linux/#ARCH#
    -f #PROJECT_DIR#/#DOCKERFILE#
    --load #PROJECT_DIR#
"""

DOCKER_LAMBDA_RUN_TEMPLATE = """
	docker run -it
        -p #PORT#:#PORT#
        -e IVCAP_BASE_URL=#IVCAP_BASE_URL#
		--platform=linux/#ARCH#
		--rm \
		#NAME#_#ARCH#:#TAG#
"""

DOCKER_BATCH_RUN_TEMPLATE = """
	docker run -it
        -e IVCAP_BASE_URL=#IVCAP_BASE_URL#
		--platform=linux/#ARCH#
        -v #PROJECT_DIR#:/data
		--rm \
		#NAME#_#ARCH#:#TAG#
"""