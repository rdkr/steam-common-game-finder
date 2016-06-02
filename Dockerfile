FROM python:3.5.1

RUN git clone --recursive https://github.com/rdkr/steam-common-game-finder.git

WORKDIR steam-common-game-finder

RUN pip3 install -r requirements.txt

RUN pip3 install uwsgi

CMD uwsgi --master --http 0.0.0.0:3031 --manage-script-name --mount /=app:app