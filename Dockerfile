# Container configuration
FROM library/python:3.13.0-slim-bullseye
WORKDIR /app
COPY . .

# Python index URL
ARG PYTHON_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple

# Set environment variables
RUN pip config set global.index-url ${PYTHON_INDEX}
ENV UV_INDEX_URL=${PYTHON_INDEX}

# Build
RUN pip install uv
RUN uv venv
RUN uv sync

EXPOSE 8501

# Run
CMD ["uv", "run", "streamlit", "run", "src/main.py"]