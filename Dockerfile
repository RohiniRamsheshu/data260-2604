FROM python:3.11-slim
WORKDIR /app
COPY . .
EXPOSE 8804
CMD ["python3", "-m", "http.server", "8804"]