# WebGameFlask

Запустить сервер:

python app.py

Как пользоваться:

Сначала нужно зарегистрировать пользователя, с подтверждением на почту. 
![mail_screen](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/mail_screen.png)

(для сервера не обязательно можно посмотреть код подтверждения в папке temp_profiles в файле напротив secret_invite_code)
![secret_invite_code](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/secret_invite_code.png)


Потом, если вы вошли в свой аккаунт, то можно встать в очередь ожидания игроков. 
![get_in_queue](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/get_in_queue.png)
![in_queue_waiting](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/in_queue_waiting.png)

Если набирается два игрока то они отправляются в одну комнату на дуэлью Дуэль происходит так: каждый раунд, каждый игрок выбирает действие, которое совершит через 10 секунд, действия игроков происходят одновременно, любой выстрел, если не защититься смертельный, супер высрел в любом случае смертельный.

(это можно сымитировать с одного компьютера используя режим инкогнито )
![two_players](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/two_players.png)

по истечении времени (таймер справа ) будет выполнено действие которое обведено красной точечной рамкой и начнется следующий раунд
![before_death](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/before_death.png)

произошла смэрть
![death](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/death.png)

( возможна смерть обоих )
![before_death](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/before_death.png)
![all_death](https://github.com/SlippySleppers/WebGameFlask/raw/dev/readme_pictures/all_death.png)
