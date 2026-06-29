# Stage 1: Build React frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install --silent
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend + built frontend
FROM python:3.12-slim
WORKDIR /app

COPY pyproject.toml ./
COPY backend/ ./backend/
RUN pip install --no-cache-dir .

# Copy built frontend assets
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Persistent data volume for SQLite DB
VOLUME ["/app/data"]

EXPOSE 9001

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "9001"]
