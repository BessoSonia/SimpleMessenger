const ws = new WebSocket("ws://localhost:8888/websocket");

ws.onmessage = function(event) {
    let message;
    
    try {
        message = JSON.parse(event.data); // Попытка распарсить как JSON
    } catch (e) {
        message = event.data; // Если не получилось, просто берем текст
    }

    // Если сообщение содержит событие "update_clients", то обновляем список пользователей
    if (message.event === "update_clients") {
        const usersList = document.getElementById("users-list");
        usersList.innerHTML = "";  // Очищаем текущий список

        message.clients.forEach(client => {
            const li = document.createElement("li");
            li.textContent = client;
            usersList.appendChild(li);
        });
    } else {
        // В другом случае, это обычное текстовое сообщение
        const chatWindow = document.getElementById("chat");
        const msgDiv = document.createElement("div");
        msgDiv.textContent = message; // Добавляем текст сообщения
        chatWindow.appendChild(msgDiv);

        // Прокручиваем чат вниз, чтобы увидеть последнее сообщение
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
};



function sendMessage() {
    const input = document.getElementById("message");
    const text = input.value.trim();
    
    if (text !== "") {
        const message = JSON.stringify({ text: text });  // Создаем объект сообщения
        ws.send(message);  // Отправляем сообщение на сервер
        input.value = "";  // Очищаем поле ввода
    }
}
