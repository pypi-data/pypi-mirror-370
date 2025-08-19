# TTClient

Клиент для АПИ чата


## INSTALL

Достаточно установить библиотеку ttclient

```
$ pip install ttclient
```


## USAGE

```python
from ttclient import TTClient

client = TTClient('...', host='example.com')
data = await client.get_chat_data([123])
```
