import tornado.ioloop
import tornado.web
import tornado.websocket
import redis
import threading
import json


class ChatWebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = {}  # Словарь для хранения всех подключенных клиентов по их id

    def open(self):
        self.client_id = f"client{len(self.clients) + 1}"  # Генерация уникального clientid
        self.clients[self.client_id] = self  # Добавляем клиента в словарь
        print(f"Client {self.client_id} connected. Total clients: {len(self.clients)}")
        self.update_clients_list()

    def on_message(self, message):
        # Сообщение приходит в формате JSON
        try:
            msg_data = json.loads(message)
            text = msg_data.get("text")
            if text:
                formatted_message = f"{self.client_id}: {text}"  # Форматируем сообщение с clientid

                for client in self.clients.values():
                    client.write_message(formatted_message)

                # Публикуем сообщение в Redis
                redis_client.publish("chat", formatted_message)
            else:
                print("Received empty message")

        except json.JSONDecodeError:
            print("Received invalid message format")

    def on_close(self):
        # Удаляем клиента из списка при отключении
        del self.clients[self.client_id]
        print(f"Client {self.client_id} disconnected. Total clients: {len(self.clients)}")
        self.update_clients_list()

    def update_clients_list(self):
        # Обновляем список онлайн-клиентов и передаем его всем
        online_clients = list(self.clients.keys())
        for client in self.clients.values():
            client.write_message(json.dumps({"event": "update_clients", "clients": online_clients}))


# Функция для работы с Redis Pub/Sub
def redis_subscriber(client, callback):
    pubsub = client.pubsub()
    pubsub.subscribe("chat")
    print("Subscribed to Redis channel 'chat'")
    for message in pubsub.listen():
        if message["type"] == "message":
            callback(message["data"])


def make_app():
    return tornado.web.Application([
        (r"/websocket", ChatWebSocketHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "front", "default_filename": "index.html"})
    ])


if __name__ == "__main__":
    # Подключение к Redis
    redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

    # Функция-обработчик для сообщений, полученных через Redis Pub/Sub
    def redis_callback(message):
        loop = tornado.ioloop.IOLoop.current()
        loop.add_callback(lambda: send_message_to_clients(message))

    def send_message_to_clients(message):
        for client in ChatWebSocketHandler.clients.values():
            client.write_message(message)

    # Запуск подписки на Redis в отдельном потоке
    threading.Thread(target=lambda: redis_subscriber(redis_client, redis_callback), daemon=True).start()

    # Запуск Tornado сервера
    app = make_app()
    app.listen(8888)
    print("Server running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
