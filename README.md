# Боты викторины в Telegram и VK


## Переменные окружения
Часть настроек проекта берётся из переменных окружения.  
Чтобы их определить, создайте файл `.env` в корневой папке `quiz` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`:    
- `TELEGRAM_TOKEN` - токен бота Телеграмм. [Инструкция, как создать бота.](https://core.telegram.org/bots/features#botfather)  
- `VK_TOKEN`- Инструкция по Implicit Flow для получения [ключа доступа пользователя ВК](https://vk.com/dev/implicit_flow_user)  


## Установка и настройка
Для запуска у вас уже должен быть установлен Python не ниже 3-й версии.  
В командной строке:  
- Скачайте код: `git clone https://github.com/mulchus/quiz.git`
- Создайте файл с переменными окружения, активируйте виртуальное окружение: 
    `python -m venv venv`  
    - Windows: `.\venv\Scripts\activate`  
    - MacOS/Linux: `source venv/bin/activate`  
- Установите зависимости: `pip install -r requirements.txt`  


#### Установка Redis
- Установите Redis - хранилище структур данных в памяти с открытым исходным кодом (лицензия BSD), 
используемое в качестве базы данных, кэша, посредника сообщений  
[Инструкция для Linux](https://redis.io/docs/getting-started/installation/install-redis-on-linux/)  
[Инструкция для Windows 10 и выше](https://redis.io/docs/getting-started/installation/install-redis-on-windows/)  
[Инструкция для Windows 8.1 и ниже](https://dzone.com/articles/running-redis-on-windows-81-and-prior)  
Проверка установки:
```commandline
root@......:/opt/quiz# redis-cli
127.0.0.1:6379> ping
PONG
127.0.0.1:6379>
```

#### Подготовка викторины  

- Запустите скрипт `python main.py [--path PATH] [--file FILES]`  
  --path [PATH] - имя папки в корне проекта с файлами вопросов-ответов (по умолчанию - quiz-questions)  
  --files [FILES ...]  имена файлов вопросов-ответов для викторины (по умолчанию - questions-answers.txt)    
    

#### Запуск ботов  

- Запуск бота в Telegram - `python tg.py` (в отдельном окне командной строки)
- Запуск бота в VK - `python vk.py` (в отдельном окне командной строки)  
  
  Результат викторины с [ботом в Telegram](https://t.me/mulchusbot)  
![tg_bot](https://github.com/mulchus/quiz/assets/111083714/ce34b7e5-033d-4e87-b95a-bcf3a47ca4aa)  
  
  Результат викторины с [ботом в VK](https://vk.com/club219033181)  
![vk_bot](https://github.com/mulchus/quiz/assets/111083714/ee7d2111-3203-4877-8f0a-02daefabd054)  
  

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
