# steam-common-game-finder
A simple flask application and uWGSI Docker deployment.

Requires a steam web api key environment variable, vailable here - https://steamcommunity.com/dev/apikey.

Debug server - export STEAM_WEB_API_KEY="<your key>" and run app.py.

Deploy with Docker using uWGSI - requires uwgsi frontend - see https://github.com/rdkr/docker for example implementation with Nginx. This repo is built automatically here - https://hub.docker.com/r/rdkr/steam-common-game-finder/.
