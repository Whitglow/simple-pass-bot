# simple-pass-bot
This project is a Telegram bot that helps users keep their passwords secure. It uses data encryption with the cryptography library and stores user data in JSON format<br/>

Проект Telegram-бота, который помогает хранить пароли. Бот использует шифрование данных с помощью библиотеки cryptography и сохраняет данные пользователя в формате JSON.
***
## Installation and Setup / Установка и запуск

<br/> 1. Clone the repository / Клонируйте репозиторий:
```sh
git clone https://github.com/Whitglow/simple-pass-bot.git
``` 
<br/> 2. Install the dependencies / Установите зависимости:
```sh
pip install -r requirements.txt
```
<br/> 3. In the `.env` file, enter your Telegram bot token / В файле `.env` укажите токен своего Telegram-бота:
```sh
TOKEN=<ваш_токен>
```
<br/> 4. Run the bot / Запустите бота:
```sh
python app.py
```

## Функции

| Command / Команда | Description / Описание |  |
| ------ | ------ | ------ |
| /set | Adding a new service<br/> Добавление нового сервиса | Отправьте боту команду `/set`, затем введите название сервиса, логин и пароль через символ `:`|
| /get | Getting the login and password for a service<br/>Получение логина и пароля для сервиса | Отправьте боту команду `/get`, затем введите название сервиса, для которого нужно получить логин и пароль |
| /del | Deleting a service<br/>Удаление логина и пароля для сервиса | Отправьте боту команду `/del`, затем введите название сервиса, данные для которого нужно удалить|

