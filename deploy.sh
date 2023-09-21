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
python3 quiz-data-upload.py

echo "Копируем файлы демонов ata-upload, tg и vk, добавляем их в автозагрузку, запускаем"
cp quiz-data-upload.service /etc/systemd/system
systemctl enable quiz-data-upload.service
systemctl start quiz-data-upload.service
echo "waiting..."
for i in {1..3}; do
  sleep 1s
  echo "waiting..."
done
echo "done"

cp quiz-tg.service /etc/systemd/system
cp quiz-vk.service /etc/systemd/system
systemctl enable quiz-tg.service
systemctl enable quiz-vk.service
systemctl start quiz-tg.service
systemctl start quiz-vk.service

echo "all deploy done"