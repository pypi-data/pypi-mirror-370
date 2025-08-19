
## Установка библиотеки
```
pip install safesubs
```


## Пример использования
```python
from safesubs import checksubs

isSubs = checksubs(api_token="********")

async def my_handler(message):
    user_id = message.from_user.id
    if not await isSubs(user_id):
        return 
    # Ваш код для обработки сообщения, если пользователь подписан

```


Интеграция так же доступна через [API](https://subs.sxve.it/docs)