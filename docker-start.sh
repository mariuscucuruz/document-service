#!/bin/bash
python -m venv .venv && \
  source .venv/bin/activate && \
  .venv/bin/pip3 install --no-cache-dir --upgrade pip && \
  .venv/bin/pip3 install --no-cache-dir --upgrade -r requirements.txt

echo "Please specify an environment: local, staging, prod."
read -p 'Confirm ENV [local,staging,prod]: ' confirmEnv
case $confirmEnv in
  [staging]* ) TagName='staging';;
  [prod]* ) TagName='prod';;
  [local]* ) TagName='local';;
  *) TagName='local';;
esac

imageName="mariux/document-service"
newImageNameTag="${imageName}:${TagName}"

docker pull ${newImageNameTag}

sed -i "s|${imageName}:[^ ]*|${newImageNameTag}|g" docker-compose.yml

docker compose pull
docker compose up -d --force-recreate --build --remove-orphans
docker ps

echo "Service ${newImageNameTag} is up."

black *.py
