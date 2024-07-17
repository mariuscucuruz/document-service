#!/bin/bash
python -m venv .venv && \
  source .venv/bin/activate && \
  .venv/bin/pip3 install --no-cache-dir --upgrade pip && \
  .venv/bin/pip3 install --no-cache-dir --upgrade -r requirements.txt

ImageName='document-service'
TagName='local'

echo "Please specify an environment: local, staging, prod."
read -p 'Confirm ENV [local,staging,prod]: ' confirmEnv
case $confirmEnv in
  [staging]* ) TagName='staging';;
  [prod]* ) TagName='prod';;
  *) TagName='local';;
esac


black *.py


if python3 tests/*.py; then
    echo "Tests passed! Continuing with tag:${TagName} build."
else
    echo "TESTS FAILED! Are you sure you want to continue to build tag:${TagName}?"
    read -p "Confirm [y/N]: " confirmYN
    case $confirmYN in
      [Yy]* ) ;;
      *) exit;;
    esac
fi


echo "Building ${ImageName} image with tag ${TagName}.";
echo "Press CTRL+C within 2 seconds to stop building."
sleep 3;


# Call respective build_push_${TagName}.sh for docker configs
. ./docker/build_push_${TagName}.sh


if [ -z "${DockerFile}" ]; then
  echo "DockerFile not set. Program will now exit.";
  exit;
fi

if [ -z "${DockerImage}" ]; then
  echo "DockerImage will now default to 'latest'.";
fi

cp docker/${DockerFile} ./${DockerFile}
docker build --no-cache -t ${DockerImage} . -f ${DockerFile}
rm ${DockerFile}

read -p "Push image to Docker Hub? [y/N]: " confirmYN
case $confirmYN in
  [Yy]* ) docker push ${DockerImage};;
  *) exit 0;;
esac
