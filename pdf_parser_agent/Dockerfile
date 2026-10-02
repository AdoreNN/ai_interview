FROM python:3.12-slim

WORKDIR /app

COPY pdf_parser_agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pdf_parser_agent ./pdf_parser_agent

EXPOSE 8000
CMD ["uvicorn", "pdf_parser_agent.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
