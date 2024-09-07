


### **Описание проекта Foodgram**

> Foodgram - это сервис для публикации веганских рецептов, на котором пользователи могут делиться своими рецептами, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.Зарегистрированным пользователям доступна функция «Список покупок». Она позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

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
- SECRET_KEY='django-insecure-e68r(-kl9upv$tm)dmfm6644m#ye%c+vk(=+1965@605ec#8@u'
- ALLOWED_HOSTS='158.160.76.66,127.0.0.1,localhost,mykittygram.zapto.org'
- DEBUG='True'

Перейти в репозиторию backend:

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

### **Запуск frontend проекта**

Перейти в репозиторий infra:

```bash
cd frontend
```

Установить зависимости:

```bash
npm i
```

Запустить проект:

```bash
npm run start
```

### **Запуск проекта в контейнерах**

Собрать образы foodgram_frontend, foodgram_backend и foodgram_gateway:

```bash
cd frontend
docker build -t username/foodgram_frontend
```

```bash
cd backend
docker build -t username/foodgram_backend
```

```bash
cd nginx
docker build -t username/foodgram_gateway
```
- необходимо заменить username на свой логин на DockerHub.

Загрузить образы на DockerHub:

```bash
docker push username/foodgram_frontend
docker push username/foodgram_backend
docker push username/foodgram_gateway
```

Запустить проект из корневой папки проекта - foodgram:

```bash
docker-compose up --build
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
