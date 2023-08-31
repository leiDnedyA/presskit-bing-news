FROM python:3.12.0rc1-bookworm

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]