#!/bin/bash

IS_PODMAN=$(ls -l $(which docker) | grep -q "podman" && echo true || echo false)
if [[ "$IS_PODMAN" == false ]]; then
    DOCKER_VERSION=$(docker --version | awk '{printf("%s\n", $3);}')
    DOCKER_VERSION_MAJOR=$(echo ${DOCKER_VERSION} | awk -F'.' '{printf("%d\n", $1);}')
    DOCKER_VERSION_MINOR=$(echo ${DOCKER_VERSION} | awk -F'.' '{printf("%d\n", $2);}')
    if [[ ${DOCKER_VERSION_MAJOR} -ge 18 ]]; then
        if [[ ${DOCKER_VERSION_MINOR} -ge 9 ]]; then
            export DOCKER_BUILDKIT=1
        fi
    else
        echo "This version's docker does not support buildkit.(>=18.09)"
        exit
    fi
fi

local MOUNT_OPTIONS=""
if [[ "$IS_PODMAN" == true ]]; then
    MOUNT_OPTIONS=",bind-propagation=rshared,z"
fi

DOCKER_BUILDKIT=1 docker buildx build --platform linux/amd64 -t easymaker-sdk:latest \
    --build-arg MOUNT_OPTIONS="${MOUNT_OPTIONS}" .
