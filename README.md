# steam-common-game-finder
A simple flask application with uWSGI Docker deployment.

Requires a steam web api key as environment variable, available here - https://steamcommunity.com/dev/apikey.

Debug server - export STEAM_WEB_API_KEY="<your key>" and run app.py.

Deploy with Docker using uWSGI - requires uwsgi frontend - see https://github.com/rdkr/docker for example implementation with Nginx. This repo is built automatically here - https://hub.docker.com/r/rdkr/steam-common-game-finder/.
