from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])

# Проверка подключения
if es.ping():
    print("Connected to Elasticsearch")
else:
    print("Connection failed")