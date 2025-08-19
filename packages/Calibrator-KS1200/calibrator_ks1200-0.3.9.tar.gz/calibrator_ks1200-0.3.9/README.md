![Компания Эталон](https://omsketalon.ru/sites/default/files/logo_s_0.png)

<br>
<h1>Калибратор КС-1200С</h1>

Данный пакет предназначен для рабооты калибратора сухоблочного КС-1200С компании Эталон.
<br><br><br>
1. <h2>Установка</h2>

    1.1. Пошаговая установка на чистую систему.<br>
    1.1.1. Загружаем чистую систему с сайта [Armbian](https://www.armbian.com/orange-pi-plus-2e/) или с [Яндекс диска](https://disk.yandex.ru/d/d5oLR2isGOukiw).  
    1.1.2. Загружаем программу для записи образа на flash накопитель, например [Rufus](https://disk.yandex.ru/d/1JKf5sK0ytQStw) или с [официального сайта Rufus](https://rufus.ie/ru/).<br>
    1.1.3. Записываем образ системы на microSD карту, для этого запускаем Rufus, в поле Устройство выбираем microSD карту, затем нажимает кнопку Выбрать и  указываем за загруженный в п.п. 1.1.1. образ системы. Далее нажимаем Старт и ждём окончания.<br>
    1.1.4. Вставляем microSD карту в Orange PI и устанавливаем систему<br>
    1.1.4.1. Create root password: try123!<br>
    1.1.4.2. Repeat root password: try123!<br>
    1.1.4.3. 1) bash 1<br>
    1.1.4.4. Please prowide a user name (eg. your first name): user<br>
    1.1.4.5. Create user (user) passeword: try123!<br>
    1.1.4.6. Repeat user (user) passeword: try123!<br>
    1.1.4.7. Please provide your real name: User<br>
    1.1.4.8. Set user language based on your location? [Y/n] y<br>
    1.1.4.9. Please enter your choice: 7 (ru_RU.UTF-8)<br>
    1.1.5. Открываем терминал и обновляем систему:<br>
            sudo apt update && sudo apt upgrade -y<br>
    1.1.6. Устанавливаем необходимые пакеты:<br>
            sudo apt install python3-pyqt5 python-is-python3 python3-pip python3-dev libxml2-dev qtdeclarative5-dev libqt5svg5-dev qtbase5-private-dev qml-module-qtquick-controls2 qml-module-qtquick-controls qml-module-qt-labs-folderlistmodel '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev python3-docx -y<br>
    1.1.7. Если нужна виртуальная клавиатура, то загружаем её исходники, собираем её с нужными языками и устанавливаем:<br>
            git clone -b 5.11 https://github.com/qt/qtvirtualkeyboard.git<br>
            cd qtvirtualkeyboard<br>
            qmake "CONFIG += lang-en lang-ru"<br>
            sudo make<br>
            sudo make install<br>
    1.1.8. Устанавливаем данный пакет калибратора:<br>
            pip config set global.break-system-packages true<br>
            pip install Calibrator-KS1200<br><br>

    1.2. Утановка готовой системы с предустановленной на неё ПО Калибратора.<br>
    1.2.1. Загрузить готовый образ системы с установленным на неё ПО  Калибратора по [ссылке](https://disk.yandex.ru/d/Ea4wLmxjT-6JfA).<br>
    1.2.2. Загружаем программу для записи образа на flash накопитель, например [Rufus](https://disk.yandex.ru/d/1JKf5sK0ytQStw)  или с [официального сайта Rufus](https://rufus.ie/ru/).<br>
    1.2.3. Записываем образ системы на microSD карту, для этого запускаем Rufus, в поле "Устройство" выбираем microSD карту, затем нажимает кнопку "Выбрать" и  указываем за загруженный в п.п.          1.2.1. образ системы. Далее нажимаем Старт и ждём окончания.<br>
    1.2.4. После загрузки Armbian необходимо войти в систему введя пароль по-умолчанию try123!<br>
    1.2.5. Для того, чтобы убедиться, что мы используем последнюю версию ПО калибратора, необходимо открыть терминал и выполнить следующую команду:<br>
        pip install --upgrade Calibrator-KS1200<br>
    1.2.6. Система готова к работе.<br>

2. <h2>Обновление</h2>

    2.1. Автоматическое обновление<br>
    2.1.1. Для автоматического обновления ПО Калибратора, необходимо подключить Orange к сети Интернет и выполнить следующую команду:<br>
        pip install --upgrade Calibrator-KS1200<br>
    2.2. Ручное обновление<br>
    2.2.1. Для ручного обновления необходимо перейти на сайт [Git Hub](https://github.com/psih0/KS1200)<br>
    2.2.2. Нажать в правой верхней части сайта на зеленую кнопку "<> Code" и в открывшемся меню выбрать Download ZIP.<br>
    2.2.3. Извлеч из загруженного файла KS1200-master папку Calibrator_KS1200 на USB Flash накопитель.<br>
    2.2.4. Подключить USB Flash накопитель к Orange и перенести папку Calibrator_KS1200 в папку /home/user/.local/lib/python3.12/site-packages/
           Если система скажет, что данный файл уже существует, необходимо подтвердить перезапись.<br>

<br><br><br>
<h2> Ссылки </h2>   

- [Компания эталон](http://www.omsketalon.ru/)
- [GitHUB](https://github.com/psih0/KS1200)
<br><br><br>
## Лицензия

Лицензия MIT
