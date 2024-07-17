
This `document-service` includes:

 - RabbitMq consumer and producer
 - CRUD operations on hasura db
 - Test suite
 - FastApi endpoint "/health"

**Adjustments**

To make the FastApi endpoint work, letsencrypt will need to be added to the uvicorn app in `starup_wrapper.sh`.


## Description

### ENV, interfaces, and ports

Because the service runs in a Docker container, the network port and interface should be static (i.e. hardcoded in `startup_wrapper.sh`) and only mapped on the host in `docker-compose.yml` file which is where the values from `.env` are implemented.

**startup_wrapper.sh**
```
appName="service_api"
appHost="0.0.0.0"
appPort="8089"
serviceName="Document Service"
```

**docker-compose.yml**
```
 document-service:
  image: mariux/document-service:staging
  container_name: document-service-app
  restart: unless-stopped
  ports:
  - 127.0.0.1:${app_port:-8089}:8089
```

### Starting the service

To start the microService on a given environment you can run `./docker-start.sh` shell and type `local`, `staging` or `prod` at the prompt:


### Build and / or Push Docker Image

To build / push the Docker image run the shell script `./build_push.sh` and type the environment you wish to build (i.e. `local`, `staging` or `prod`) for at the prompt.

***Example:***

1. Run shell script `./docker-build-push.sh` and type ***`"staging"`*** for instance:
  - if the unit tests fail, you’re prompted to abort or continue the build

2. When the build has completed, you’re prompted to ***`push`*** to Docker hub:
  - the default is **no**, so if you don’t type `"y"` and `ENTER` your built is not pushed.


#### Testing

Export OpenAPI configuration from the HOST (after starting the container_:

```
docker exec -it document-service-app bash -c "python3 extract-openapi.py --app-dir /app/ service_api:app"
```

or from inside the container:

```
python3 extract-openapi.py --app-dir /app/ service_api:app
```
