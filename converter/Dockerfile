FROM python:3.11-slim
WORKDIR /app
COPY convert.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "convert.py"] 