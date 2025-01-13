# Guesthouse Booking Project

Этот проект представляет собой систему бронирования гостевых домов, разработанную на Django. Проект настроен для работы
в Docker с использованием SQLite в качестве базы данных.

## Оглавление

- Требования
- Установка и запуск
- Использование Docker
- Структура проекта
- Лицензия

## Требования

Для запуска проекта вам потребуется:

- Docker
- Docker Compose
- Скачать тут (https://www.docker.com/products/docker-desktop/)

## 1. Клонирование репозитория

Склонируйте репозиторий на ваш локальный компьютер:

```bash
https://github.com/MICROWAVE-web/guesthouse_booking.git
cd guesthouse_booking
```

### Запуск проекта с использованием Docker

```bash
docker-compose up --build
```

После запуска контейнеров, Django приложение будет доступно по адресу:

```bash
http://localhost:8000
```

Примените миграции для создания таблиц в базе данных:

```bash
docker-compose exec web python manage.py migrate
```

### Запуск проекта без Docker
Создание виртуального окружения

```bash
python -m venv venv
```
Активируйте виртуальное окружение:

Windows:

```bash
venv\Scripts\activate
```
macOS/Linux:

```bash
source venv/bin/activate
```
Установка зависимостей

   
```bash
pip install -r requirements.txt
```
Примените миграции для создания таблиц в базе данных
   

```bash
python manage.py migrate
```


   Запустите сервер разработки Django:
```bash
python manage.py runserver
```
После запуска сервера, ваше приложение будет доступно по адресу:

```bash
http://127.0.0.1:8000/
```