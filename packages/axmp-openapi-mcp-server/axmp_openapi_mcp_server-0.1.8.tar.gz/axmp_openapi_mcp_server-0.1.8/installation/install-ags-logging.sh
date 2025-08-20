#!/bin/bash
set -e

. env.properties
. env-logging.properties

# helm upgrade -i ${RELEASE_NAME} cloudzcp/axmp-openapi-mcp-server --version ${CHART_VERSION} \
helm upgrade -i ${RELEASE_NAME} ../charts/axmp-openapi-mcp-server \
--namespace ${TARGET_NAMESPACE} \
--set image.repository=${IMAGE_REGISTRY}/cloudzcp/axmp-openapi-mcp-server \
--set imagePullSecrets[0].name="${IMAGE_PULL_SECRETS}" \
--set fullnameOverride="${RELEASE_NAME}" \
--set image.tag="${CONTANINER_IMAGE_TAG}" \
--set service.port=${AXMP_MCP_PORT} \
--set livenessProbe.tcpSocket.port=${AXMP_MCP_PORT} \
--set readinessProbe.tcpSocket.port=${AXMP_MCP_PORT} \
--set startupProbe.tcpSocket.port=${AXMP_MCP_PORT} \
--set configmap.data.AXMP_MCP_PORT=${AXMP_MCP_PORT} \
--set configmap.data.AXMP_MCP_TRANSPORT_TYPE="${AXMP_MCP_TRANSPORT_TYPE}" \
--set configmap.data.AXMP_MCP_SERVER_NAME="${AXMP_MCP_SERVER_NAME}" \
--set configmap.data.AXMP_MCP_PROFILE_BASE_PATH="${AXMP_MCP_PROFILE_BASE_PATH}" \
--set configmap.data.AXMP_MCP_PROFILE_ID="${AXMP_MCP_PROFILE_ID}" \
# --set secret.data.SECRET_KEY="${SECRET_KEY}" \
# --dry-run 

