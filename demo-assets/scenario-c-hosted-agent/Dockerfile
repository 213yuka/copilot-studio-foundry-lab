FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY tools/ ./tools/
ENV PORT=8088
EXPOSE 8088
CMD ["python", "src/agent.py"]
