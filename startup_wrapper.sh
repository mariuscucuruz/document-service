#!/bin/bash

# import env variables
source .env

# server configuration
appName="service_api"
appHost="0.0.0.0"
appPort="8089"
serviceName="document_service"
app_debug=${app_debug:-true}

# little helper methods:
COLOR_RESET='\033[0m'
printError() {
  COLOUR_RED='\033[0;31m'
  echo -e "\n${COLOUR_RED}Wrapper ERROR${COLOR_RESET}: $1${COLOR_RESET}.\n"
}
printMessage() {
  COLOUR_BLUE='\033[0;34m'
  echo -e "\n${COLOUR_BLUE}Wrapper INFO${COLOR_RESET}: $1${COLOR_RESET}.\n"
}
printDebug() {
  COLOUR_GREEN='\033[0;34m'
  echo -e "\n${COLOUR_GREEN}Wrapper DEBUG${COLOR_RESET}: $1${COLOR_RESET}.\n"
}
printSeparator() {
  echo -e "${COLOR_RESET}=================================================================="
}

uvicorn ${appName}:app --host ${appHost} --port ${appPort} &

status=$?
if [[ ${status} -ne 0 ]]; then
  printError "Failed to start ${appName}: $status"
  exit ${status}
fi


printSeparator
printMessage "The ${appName} is now running on ${appHost}:${appPort}"


python3 -u ${serviceName}.py &
if [[ ${status} -ne 0 ]]; then
  printSeparator
  printError "Failed to start ${serviceName}: ${status}"
  exit ${status}
fi


printSeparator
printMessage "Monitoring ${serviceName} service health every 60 seconds..."


while sleep 60; do
  ps aux | grep ${serviceName}.py | grep -q -v grep

  PROCESS_1_STATUS=$?
  if [[ ${PROCESS_1_STATUS} -ne 0 ]]; then
    printError "The ${serviceName} process has failed. Throwing exit status 1 in an attempt to notify the container."
    exit 1
  fi

  if [[ "${app_debug}" = true ]] ; then
    printDebug "${app_name} Healthy!"
    printDebug "API ${serviceName} for ${app_name} is running on ${appHost}:${appPort}..."
  fi

  printSeparator
done
