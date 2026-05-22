FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY tools/ ./tools/
# PORT 環境変数は Foundry プラットフォーム側で自動管理されるため、
# Dockerfile では明示しない。ローカル動作確認のみで上書きしたい場合は
# `docker run -e PORT=8088 -p 8088:8088 ...` のように渡すこと。
EXPOSE 8088
CMD ["python", "src/agent.py"]

