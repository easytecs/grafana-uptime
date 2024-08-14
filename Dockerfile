FROM python:alpine
RUN pip install prometheus_client requests pyyaml python-dotenv

WORKDIR /app

RUN mkdir .data

COPY . .

EXPOSE 8000

CMD ["python", "-u", "service.py"]