#!/usr/bin/bash
docker run -p '80:3030' --name jen-fuseki -v ./fuseki-base/db:/fuseki-base/databases sw