#!/bin/bash
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                    	     Shell script for Docker/Linux (x64)                                 %     
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Bash script for creating a custom interface to Jenkins CI.
# Created on 13.06.2021
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - 
#
# -------------------------------------------------------------------------------------------------
JOB_NAME=$1
JENKINS_HOST="https://jenkins.fa-services.intra.dlr.de"
JENKINS_BUILD=${GIT_JENKINS:-build}
USER_NAME=${CI_USER}
USER_TOKEN=${CI_TOKEN}
QUEUE_URL="${JENKINS_HOST}/job/${JOB_NAME}/api/json"
BUILD_URL='null'; RESULT=0; UPDATE='';
# Make sure all dependencies are actually installed
apt-get update && apt-get install -y curl jq
# Activate the given job
curl --silent "${JENKINS_HOST}/job/${JOB_NAME}/${JENKINS_BUILD}" -X POST -L --user "${USER_NAME}:${USER_TOKEN}" --insecure
# Let the job start
sleep 10
# Fetch latest job identifier
while [ "$BUILD_URL" == "null" ]
do
  BUILD_URL=$(curl --silent "${QUEUE_URL}" --user "${USER_NAME}:${USER_TOKEN}" --insecure | jq -r '.builds[0].url')
done
# Echo console output
OUTPUT=$(curl --silent "${BUILD_URL}/consoleText" --user "${USER_NAME}:${USER_TOKEN}" --insecure )
echo "Intermediate results from ${BUILD_URL}:"
echo "${OUTPUT}"
# Wait for job to complete.
while [ "$RESULT" == 0 ]
do
  RESULT=$(curl --silent "${BUILD_URL}api/json" --user "${USER_NAME}:${USER_TOKEN}" --insecure | jq -r '.duration')
  UPDATE=$(curl --silent "${BUILD_URL}/consoleText" --user "${USER_NAME}:${USER_TOKEN}" --insecure )
  [ -n "${UPDATE#"$OUTPUT"}" ] && echo ${UPDATE#"$OUTPUT"}
  OUTPUT=$UPDATE
  sleep 0.1
  RESULT=$(curl --silent "${BUILD_URL}api/json" --user "${USER_NAME}:${USER_TOKEN}" --insecure | jq -r '.duration')
  if [ "$RESULT" != 0 ]; then break; fi
done <<< "$OUTPUT"
exit 0