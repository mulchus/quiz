#!/bin/bash
set -e

echo "Обновляем код из github"
git pull origin master

echo "Запускаем Redis (должен быть предварительно установлен)"
redis-server --daemonize yes

echo "Создаем виртуальное окружение"
if ! [ -d /opt/quiz/venv ]; then
    python3 -m venv venv
fi

echo "Активируем виртуальное окружение"
source venv/bin/activate

echo "Устанавливаем зависимости"
pip install -r requirements.txt

echo "Подготавливаем в памяти Redis вопросы-ответы"
python3 main.py --path PPP --file 123.txt

echo "Копируем файлы демонов tg и vk, добавляем их в автозагрузку, запускаем"
cp quiz-tg.service /etc/systemd/system
cp quiz-vk.service /etc/systemd/system
systemctl enable quiz-tg.service
systemctl enable quiz-vk.service
systemctl start quiz-tg.service
systemctl start quiz-vk.service