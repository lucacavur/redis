FROM python:3.10

ADD docker.py .

RUN pip install beautifulsoup4 requests pymongo redis

CMD [ "python", "./docker.py" ]
