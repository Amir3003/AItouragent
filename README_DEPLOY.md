# Zari Travel - Production Deployment Guide

Руководство по развертыванию автономной тревел-платформы **Zari Travel** на выделенном сервере (Ubuntu 22.04 / 24.04 LTS) с кастомным доменом `zaritravel.com` и SSL-сертификатом.

---

## 1. Системные требования и окружение

- **ОС**: Linux Ubuntu 22.04 LTS или новее
- **Python**: 3.11+
- **Веб-сервер / Reverse Proxy**: Nginx 1.20+
- **Сертификаты**: Let's Encrypt Certbot
- **Менеджер процессов**: Systemd / Gunicorn + Uvicorn Workers

---

## 2. Клонирование и настройка проекта

```bash
# Переход в рабочую директорию
cd /var/www/
git clone <your-repo-url> zaritravel
cd zaritravel

# Создание виртуального окружения
python3 -m venv .venv
source .venv/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn uvicorn

# Настройка переменных окружения
cp .env.example .env
nano .env
```

---

## 3. Systemd служба (Gunicorn + Uvicorn)

Создайте файл службы: `/etc/systemd/system/zaritravel.service`

```ini
[Unit]
Description=Zari Travel Autonomous Concierge Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/zaritravel
EnvironmentFile=/var/www/zaritravel/.env
ExecStart=/var/www/zaritravel/.venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/zaritravel/access.log \
    --error-logfile /var/log/zaritravel/error.log

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Активация и запуск службы:
```bash
sudo mkdir -p /var/log/zaritravel
sudo chown -R www-data:www-data /var/log/zaritravel /var/www/zaritravel
sudo systemctl daemon-reload
sudo systemctl enable zaritravel
sudo systemctl start zaritravel
sudo systemctl status zaritravel
```

---

## 4. Конфигурация Nginx и подключение домена `zaritravel.com`

Создайте конфигурационный файл: `/etc/nginx/sites-available/zaritravel.conf`

```nginx
server {
    server_name zaritravel.com www.zaritravel.com;

    # Gzip сжатие статики
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml image/svg+xml;

    location /static/ {
        alias /var/www/zaritravel/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        proxy_connect_timeout 60s;
    }

    client_max_body_size 10M;
}
```

Активация сайта в Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/zaritravel.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 5. Выпуск бесплатного SSL-сертификата (Let's Encrypt)

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d zaritravel.com -d www.zaritravel.com
```

Certbot автоматически настроит HTTPS, редирект с HTTP и автопродление сертификата.

---

## 6. Проверка работоспособности (Healthcheck)

```bash
curl -I https://zaritravel.com/health
```

Ожидаемый ответ:
```http
HTTP/2 200 
content-type: application/json
```

