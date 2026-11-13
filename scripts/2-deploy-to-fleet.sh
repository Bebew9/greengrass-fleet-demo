#!/usr/bin/env bash
# Deploy the published component to a whole thing group. Every device in the group
# picks up the deployment over MQTT and installs it — no per-device action.
set -euo pipefail

: "${REGION:=eu-west-1}"
: "${ACCOUNT_ID:?set ACCOUNT_ID to your AWS account id}"
: "${THING_GROUP:=fleet-a}"

NAME="com.example.hello-fleet"
VERSION="1.0.0"
TARGET="arn:aws:iot:${REGION}:${ACCOUNT_ID}:thinggroup/${THING_GROUP}"

echo "deploying ${NAME} ${VERSION} -> ${THING_GROUP}"
aws greengrassv2 create-deployment \
  --target-arn "${TARGET}" \
  --components "{\"${NAME}\":{\"componentVersion\":\"${VERSION}\"}}" \
  --region "${REGION}"

echo "deployment created. connected devices in ${THING_GROUP} will install it."
