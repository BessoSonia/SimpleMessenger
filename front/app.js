const ws = new WebSocket("ws://localhost:8888/websocket");

ws.onmessage = function(event) {
    let message;
    
    try {
        message = JSON.parse(event.data);
    } catch (e) {
        message = event.data;
    }

    if (message.event === "update_clients") {
        const usersList = document.getElementById("users-list");
        usersList.innerHTML = "";

        message.clients.forEach(client => {
            const li = document.createElement("li");
            li.textContent = client;
            usersList.appendChild(li);
        });
    } else {
        const chatWindow = document.getElementById("chat");
        const msgDiv = document.createElement("div");
        msgDiv.textContent = message;
        chatWindow.appendChild(msgDiv);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }
};



function sendMessage() {
    const input = document.getElementById("message");
    const text = input.value.trim();
    
    if (text !== "") {
        const message = JSON.stringify({ text: text });
        ws.send(message);
        input.value = "";
    }
}
