#!/usr/bin/bash

docker build -t web .

# heroku container:push web --app dsc2-sw-food-delivery

# heroku container:release web --app dsc2-sw-food-delivery
