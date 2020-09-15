# avito_backend_test (Сокращатель ссылок)

## Как запустить

- docker-compose up --build

## Методы API
- http://0.0.0.0:5000/ (открывает простейший UI, куда нужно ввести логин, пароль, url, короткую ссылку (опционально, если кастомная ссылка не была введена то при пустом поле сгенерирует случайную)
- http://0.0.0.0:5000/authentication? (аналогично UI, но только через запрос)
    - Пример: http://0.0.0.0:5000/authentication?nickname=User&password=12345&url=https://github.com/avito-tech/auto-backend-trainee-assignment&short=avito_assignment
    - Ответ: {"nickname": "User", "long_url": "https://github.com/avito-tech/auto-backend-trainee-assignment", "short_url": "http://0.0.0.0:5000/avito_assignment"}
- http://0.0.0.0:5000/redirecting? (Проверяет короткую ссылку и пользователя и редиректит на сайт изначального url)

    - Пример: (после вызова метода /authentication из примера выше)
        
        - http://0.0.0.0:5000/redirecting?nickname=User&password=12345&short=http://0.0.0.0:5000/avito_assignment
        - Ответ: Переход на https://github.com/avito-tech/auto-backend-trainee-assignment
- http://0.0.0.0:5000/<short_link> (аналогично /redirecting), только с таким методом это бы работало в Интернете наподобие bit.ly, если задеплоить на хостинг
    
    - Пример: http://0.0.0.0:5000/avito_assignment
    - Ответ: Переход на https://github.com/avito-tech/auto-backend-trainee-assignment

## Что поддерживает
- Валидация длинного и короткого url
- Кастомные ссылки

## Устойчивость
Не успел написать тесты, но обработал поведение пользователя на большинство случаев: неверный пароль, невведение данных, некорректный url и т.д.

## Что можно исправить

- Схема БД: User -> Long (One-To-Many), Long -> Short (One-To-One) (не совсем корректная реализация, так как в этом случае если разные пользователи введут одинаковый длинный url, то им будет выдаваться одинаковый короткий url, тут должно быть One-To-Many отношение, тогда пользователи смогут создавать различные короткие url на одинаковые длинные url)

- Переписать поиск элемента через SQL-запрос, реализовано некорректно за время O(n)
