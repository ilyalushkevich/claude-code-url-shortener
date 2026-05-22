FROM python:3.12

WORKDIR /app

ENV DATABASE_URL=postgresql+asyncpg://url_shortener:password@localhost:5432/url_shortener
ENV BASE_URL=http://localhost:8000
ENV SECRET_KEY=changeme

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app"]
