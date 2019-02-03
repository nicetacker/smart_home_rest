# Use Alpine python 
FROM python:3.7

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt && rm -rf /root/.cache

COPY . /app

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

CMD ["api_server"]
