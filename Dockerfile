FROM python:3.10.4-alpine

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENV TZ=Europe/Bucharest

ENTRYPOINT [ "python" ]

CMD ["-u", "mc-control.py" ]
