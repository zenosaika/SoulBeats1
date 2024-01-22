FROM python:alpine3.19

WORKDIR /app

COPY server.py .

EXPOSE 8080

CMD ["python", "server.py"]