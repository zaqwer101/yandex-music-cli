# Yandex Music CLI

CLI плеер для сервиса Яндекс.Музыка, написан на библиотеке [MarshalX/yandex-music-api](https://github.com/MarshalX/yandex-music-api)

Единственный на данный момент поддерживаемый плеер - **MPV** (потому что он поддерживает сокеты)

## Использование

0. Получить токен для Яндекс Музыки и прописать его в переменную `TOKEN` файла `config.py`
    - Вариант получения: 
        1. Установить на ПК эмулятор Android (я использовал Genymotion)
        2. Установить на ПК сниффер HTTP-трафика (я использовал HTTP Toolkit)
        3. Подключить сниффер к эмулятору, пробросить его сертификат (Genymotion + HTTP Toolkit пробрасывают сертификат автоматически)
        4. Установить приложение Яндекс Музыки, начать сниффинг, залогиниться
        5. Поискать в ответах `token`

1. Установить pip-пакеты
    ```
    pip install -r requirements.txt
    ```

2. Запустить приложение
    ```
    ./ymp.py
    ```
    или
    ```
    python3 ymp.py
    ```

3. Писать в сокет `/tmp/ymp.sock`
    - Для паузы/воспроизведения
        ```bash
        $ echo PLAY_PAUSE | socat - /tmp/ymp.sock
        ```
    - Играть следующий трек
        ```bash
        $ echo NEXT_TRACK | socat - /tmp/ymp.sock
        ```
    - Играть предыдущий трек
        ```bash
        $ echo PREV_TRACK | socat - /tmp/ymp.sock
        ```
    - Завершить программу
        ```bash
        $ echo STOP | socat - /tmp/ymp.sock
        ```