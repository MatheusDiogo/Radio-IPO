FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# Instalar FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

EXPOSE 2000

CMD ["python", "app.py"]
