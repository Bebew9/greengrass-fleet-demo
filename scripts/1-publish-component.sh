#!/usr/bin/env bash
# Publish the example component: upload the artifact to S3, then register the
# component version in Greengrass. Run 2-deploy-to-fleet.sh afterwards — publishing
# a component does NOT install it on any device.
set -euo pipefail

: "${BUCKET:?set BUCKET to your S3 bucket name}"
: "${REGION:=eu-west-1}"

NAME="com.example.hello-fleet"
VERSION="1.0.0"
ARTIFACT="components/${NAME}/artifacts/${NAME}/${VERSION}/hello_fleet.py"

echo "1/2 uploading artifact to s3://${BUCKET}/components/${NAME}/${VERSION}/"
aws s3 cp "${ARTIFACT}" "s3://${BUCKET}/components/${NAME}/${VERSION}/hello_fleet.py" --region "${REGION}"

echo "2/2 creating component version ${NAME} ${VERSION}"
# Point the recipe URI at the real bucket just-in-time, then register it.
sed "s|s3://BUCKET/|s3://${BUCKET}/|" "components/${NAME}/recipe.yaml" > /tmp/recipe.yaml
aws greengrassv2 create-component-version \
  --inline-recipe fileb:///tmp/recipe.yaml \
  --region "${REGION}"

echo "done. component ${NAME} ${VERSION} is published (not yet deployed)."
