version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql+psycopg2://usuario:senha@db:5432/meubanco

  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: usuario
      POSTGRES_PASSWORD: senha
      POSTGRES_DB: meubanco
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
