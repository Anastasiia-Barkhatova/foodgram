
[![Main Foodgram workflow](https://github.com/Anastasiia-Barkhatova/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/Anastasiia-Barkhatova/foodgram/actions/workflows/main.yml)

### **Описание проекта Foodgram**

> Foodgram - сервис для публикации веганских рецептов, на котором пользователи могут делиться своими рецептами, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.Зарегистрированным пользователям доступна функция «Список покупок». Она позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### **Cтек технологий**

- Python 3.9
- Django 3.2.16
- Django Rest Framework 3.12.4
- PostgreSQL 13
- Node.js
- React

### **Запуск backend проекта**

Клонировать проект:

```bash
git clone https://github.com/Anastasiia-Barkhatova/foodgram
```

Создать файл .env и заполнить его данными:

- POSTGRES_DB=<имя_базы_данных>
- POSTGRES_USER=<имя_пользователя_базы_данных>
- POSTGRES_PASSWORD=<пароль_пользователя_базы_данных>
- DB_HOST=db
- DB_PORT=5432


Перейти в репозиторий backend:

```bash
cd backend
```

Cоздать и активировать виртуальное окружение:

```bash
python -m venv env
```

```bash
source env/scripts/activate
```

Обновить pip:

```bash
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python manage.py migrate
```

Запустить проект:

```bash
python manage.py runserver
```


### **Запуск проекта в контейнерах локально**

В корневой директории проекта запустить файл docker-compose.production.yml:

```bash
docker compose -f docker-compose.production.yml up
```
Собрать статику:

```bash
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

Выполнить миграции:

```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

Добавить ингредиенты в базу данных:

- посмотреть имя контейнера

```bash
docker ps
```

- перейти в Git Bash

```bash
docker exec -it <имя_контейнера> bash
```

- находясь в папке app запустить команду:

```bash
python manage.py import_ingredients_csv
```


### **Запуск проекта на удаленном сервере**

Подключиться к удаленному серверу:

```bash
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера 
```

Создать на сервере директорию foodgram:

```bash
mkdir foodgram
```

Установить на сервере Docker Compose:

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

Скопировать файлы docker-compose.production.yml и .env в директорию foodgram/ на сервере.

```bash
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
```
Где:
- path_to_SSH — путь к файлу с SSH-ключом;
- SSH_name — имя файла с SSH-ключом (без расширения);
- username — ваше имя пользователя на сервере;
- server_ip — IP вашего сервера.

Запустить Docker Compose в режиме демона:

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

Выполнить миграции, собрать статические файлы бэкенда и скопировать их в /backend_static/static/:

```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Перенаправить все запросы в докер, для этого необходимо открыть конфигурационный файл Nginx в редакторе nano и изменить настройки location в секции server:

```bash
sudo nano /etc/nginx/sites-enabled/default
```
```bash
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:9090;
    }
```

Убедиться, что в конфигурационном файле Nginx нет ошибок, выполнить команду проверки конфигурации:

```bash
sudo nginx -t
```

Перезагрузить конфигурационный файл Nginx:

```bash
sudo service nginx reload
```

### **Настройка CI/CD**

Файл workflow расположен в директории foodgram/.github/workflows/main.yml

Для работы с ним на своем ервере необходимо добавить секреты в GitHub Actions:

- DOCKER_USERNAME - имя пользователя в DockerHub
- DOCKER_PASSWORD - пароль пользователя в DockerHub
- HOST - IP-адрес сервера
- USER - имя пользователя
- SSH_KEY - содержимое приватного SSH-ключа
- SSH_PASSPHRASE - пароль для SSH-ключа
- TELEGRAM_TO - ID телеграм-аккаунта (его можно узнать через @userinfobot, команда /start)
- TELEGRAM_TOKEN - токен вашего бота (его можно узнать через @BotFather, команда /token, имя бота)

Авторы: [команда Яндекс.Практикума](https://github.com/yandex-praktikum), [Бархатова Анастасия](https://github.com/Anastasiia-Barkhatova)
