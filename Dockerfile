FROM python:3.10

WORKDIR /app

COPY requirements.txt requirements.txt
COPY requirements-web.txt requirements-web.txt

RUN pip3 install \
    -rrequirements.txt \
    -rrequirements-web.txt

COPY transpiler transpiler
COPY web web

EXPOSE 8000

CMD ["python3", "-m" , "web"]
