#!/bin/bash
DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4" docker build -t elifesciences/lax-develop .
