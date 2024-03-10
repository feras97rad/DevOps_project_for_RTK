# docker-compose.yml

version: '3'
services:
  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    volumes:
      - ./redis-data:/data
    networks:
      - my_network

  mysql-master1:
    image: mysql:latest
    ports:
      - "33061:3306"
    volumes:
      - ./mysql-master1-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: my_pw
      MYSQL_DATABASE: my_database
      MYSQL_USER: my_user
      MYSQL_PASSWORD: my_password
    networks:
      - my_network

  mysql-master2:
    image: mysql:latest
    ports:
      - "33062:3306"
    volumes:
      - ./mysql-master2-data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: my_pw
      MYSQL_DATABASE: my_database
      MYSQL_USER: my_user
      MYSQL_PASSWORD: my_password
    networks:
      - my_network

  mysql-proxy:
    image: docker.io/mysql/mysql-proxy:latest
    ports:
      - "3306:3306"
    volumes:
      - ./mysql-proxy-config:/etc/mysql-proxy
    command: "--proxy-backend-addresses=mysql-master1:3306 --proxy-backend-addresses=mysql-master2:3306"
    networks:
      - my_network

  apache:
    image: httpd:latest
    ports:
      - "80:80"
    networks:
      - my_network

  nginx:
    image: nginx:latest
    ports:
      - "443:443"
    volumes:
      - ./nginx-config:/etc/nginx
    networks:
      - my_network

networks:
  my_network:
    driver: bridge



 # Dockerfile для каждого контейнера

# Redis
FROM redis:latest

# MySQL master (пароль - my_pw)
mysql-master1:
  image: mysql:latest
  ports:
   - "33061:3306"
  volumes:
   - ./mysql-master1-data:/var/lib/mysql
  environment:
   MYSQL_ROOT_PASSWORD: my_pw
   MYSQL_DATABASE: my_database
   MYSQL_USER: my_user
   MYSQL_PASSWORD: my_password
  networks:
   - my_network

# MySQL Proxy
FROM docker.io/mysql/mysql-proxy:latest
COPY ./mysql-proxy-config /etc/mysql-proxy
CMD ["--proxy-backend-addresses=mysql-master1:3306","--proxy-backend-addresses=mysql-master2:3306"]


# Apache
FROM httpd:latest

# Nginx
FROM nginx:latest
ENV NGINX_CONFIG=/etc/nginx

# Сеть (назовем my_network)
docker network create my_network

# Тут используем встроенную в Docker фичу (volume),
# Но лучше использовать Kafka (брокер сообщений)
docker volume create redis-data
docker volume create mysql-master-data
docker volume create mysql-slave-data
docker volume create mysql-proxy-config
docker volume create nginx-config

# Также можно использовать K8s (Kubernetes)
# Но в задачу это не входило ))

'''
Для решения этой задачи, мы будем использовать следующие технологии:

Docker: для создания и управления контейнерами.
Docker Compose: для определения и запуска многоконтейнерных приложений.

Описание образов необходимых контейнеров:
Python 2.7: для работы сервиса.
Redis: для хранения временных данных.
MySQL: для хранения основных данных (master-master) (необходима репликация).
MySQL Proxy: для балансировки нагрузки между мастерами MySQL.
Apache: для обработки HTTP-запросов.
Nginx: для обработки HTTPS-запросов.

Компонентная схема контейнеров:
Все указанные выше образы будут запущены в отдельных контейнерах для повышения отказоустойчивости

'''


""""
Описание процесса развертывания на новом хосте:

1: Подготовка нового хоста
Установим Docker на новый хост. 
Это может быть выполнено через официальный репозиторий (Docker hub) или установочный пакет дистрибутива Linux.
Проверяем, что Docker запущен и работает.

2: Подготовим контейнеры для сервисов
Создаем Docker образы для каждого сервиса.
Для этого понадобятся Dockerfile для каждого сервиса, описывающие, как собрать образ.
В Dockerfile каждого сервиса укажем зависимости, такие как Python 2.7, Redis, MySQL, MySQL Proxy, Apache, Nginx.
Собераем Docker образы для каждого сервиса, используя команду docker build.

3: Создаем Docker сеть и volumes для резервного хранения данных
Создаем Docker сеть для внутреннего взаимодействия между контейнерами.
Можно использовать команду docker network create.
Создаем Docker volumes для хранения данных MySQL и Redis в постоянном хранилище.
Это обеспечит сохранность данных даже при перезапуске контейнеров.

4: Запуск контейнеров
Запускаем контейнеры для каждого сервиса с использованием созданных ранее образов, указав необходимые опции,
такие как сети, объемы данных, зависимости и переменные окружения.

5: Настройка взаимодействия между сервисами
Настроим контейнеры для взаимодействия друг с другом.
Например, настраиваем приложения Python 2,7 для подключения к Redis и MySQL, учитывая их адреса и порты в Docker сети.

Шаг 6: Мониторинг и обслуживание
Выбираем тул для миониторинга
Настраиваем мониторинг для контейнеров и их служб.
Проверяем работоспособность приложения, убедившись, что оно может получать доступ к необходимым службам, таким как базы данных и прокси-серверы.
Проверяем, что контейнеры работают корректно и доступны друг другу в созданных Docker сетях средствами мониторинга (zabbix, grafana, prometeus).

""""