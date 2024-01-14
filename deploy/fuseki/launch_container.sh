#!/usr/bin/bash
docker run -e PORT=3030 -p "3030:3030" --name jen-fuseki -v ./fuseki-base/db:/fuseki-base/databases web