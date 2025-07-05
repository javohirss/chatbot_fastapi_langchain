document.addEventListener("DOMContentLoaded", () => {
    // ---- Элементы UI ----
    const authContainer = document.getElementById("auth-container");
    const chatContainer = document.getElementById("chat-container");
    const modeSelectionContainer = document.getElementById("mode-selection-container");
    const adminPanelContainer = document.getElementById("admin-panel-container");

    // Формы авторизации
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const showRegisterLink = document.getElementById("show-register");
    const showLoginLink = document.getElementById("show-login");
    const loginError = document.getElementById("login-error");
    const registerError = document.getElementById("register-error");

    // Элементы чата
    const messageForm = document.getElementById("message-form");
    const messageInput = document.getElementById("message-input");
    const messageList = document.getElementById("message-list");
    const modelSelect = document.getElementById("model-select");
    const newChatBtn = document.getElementById("new-chat-btn");
    const loadingIndicator = document.getElementById("loading-indicator");

    // Элементы админ-панели
    const gotoChatBtn = document.getElementById("goto-chat-btn");
    const gotoAdminPanelBtn = document.getElementById("goto-admin-panel-btn");
    const userList = document.getElementById("user-list");
    const historyContent = document.getElementById("history-content");
    const historyPanelTitle = document.getElementById("history-panel-title");
    const backToSelectionBtn = document.getElementById("back-to-selection-btn");

    // ---- Состояние приложения ----
    let conversationId = null;

    // ---- Константы ----
    const API_BASE_URL = "http://127.0.0.1:8000";

    // ---- Функции ----

    // Универсальная функция для отправки запросов
    async function apiRequest(endpoint, options = {}) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: { 'Content-Type': 'application/json', ...options.headers },
            credentials: 'include'
        });
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { detail: "Произошла неизвестная ошибка сервера." };
            }
            throw new Error(errorData.detail || `Ошибка ${response.status}`);
        }
        if (response.status === 204) return null;
        return response.json();
    }

    // Функции переключения экранов
    function showChat() {
        authContainer.style.display = "none";
        modeSelectionContainer.style.display = "none";
        adminPanelContainer.style.display = "none";
        chatContainer.style.display = "flex";
        if (messageList.children.length === 0) {
            addMessageToUI("Здравствуйте! Какой у вас вопрос?", "bot");
        }
    }

    function showModeSelection() {
        authContainer.style.display = "none";
        chatContainer.style.display = "none";
        adminPanelContainer.style.display = "none";
        modeSelectionContainer.style.display = "flex";
    }

    function showAdminPanel() {
        modeSelectionContainer.style.display = "none";
        adminPanelContainer.style.display = "flex";
        fetchAndDisplayUsers();
    }

    // Функционал чата
    function addMessageToUI(text, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", `${sender}-message`);
        messageElement.textContent = text;
        messageList.appendChild(messageElement);
        messageList.scrollTop = messageList.scrollHeight;
    }
    
    function setLoading(isLoading) {
        const sendButton = messageForm.querySelector("button");
        loadingIndicator.style.display = isLoading ? "flex" : "none";
        messageInput.disabled = isLoading;
        sendButton.disabled = isLoading;
        if (!isLoading) messageInput.focus();
    }

    // Функционал админ-панели
    async function fetchAndDisplayUsers() {
        try {
            // Убедитесь, что ваш эндпоинт /admin/users возвращает {id, email}
            const users = await apiRequest("/admin/users", { method: "GET" });
            userList.innerHTML = "";
            users.forEach(user => {
                const li = document.createElement("li");
                li.textContent = user.email;
                li.dataset.userId = user.id;
                li.addEventListener("click", () => {
                    document.querySelectorAll("#user-list li").forEach(item => item.classList.remove("active"));
                    li.classList.add("active");
                    fetchAndDisplayHistory(user.id, user.email);
                });
                userList.appendChild(li);
            });
        } catch (error) {
            console.error("Failed to fetch users:", error);
            userList.innerHTML = `<li>${error.message}</li>`;
        }
    }

    // ======================================================================
    // === ОБНОВЛЕННАЯ ФУНКЦИЯ ДЛЯ РАБОТЫ С ВАШИМ ФОРМАТОМ API ===
    // ======================================================================
    async function fetchAndDisplayHistory(userId, userEmail) {
        historyPanelTitle.textContent = `История сообщений: ${userEmail}`;
        historyContent.innerHTML = "<p>Загрузка...</p>";
        try {
            // Ваш API возвращает плоский массив сообщений: [{id, content, ...}]
            const messages = await apiRequest(`/admin/${userId}`, { method: "GET" });
            historyContent.innerHTML = "";
            console.log(messages)
            if (!messages || messages.length === 0) {
                historyContent.innerHTML = "<p>У этого пользователя нет истории чатов.</p>";
                return;
            }

            // Группируем сообщения по conversation_id на стороне клиента
            const conversations = messages.reduce((acc, msg) => {
                // Если для этого conversation_id еще нет группы, создаем ее
                if (!acc[msg.conversation_id]) {
                    acc[msg.conversation_id] = {
                        messages: [],
                        // Запоминаем время первого сообщения для заголовка диалога
                        timestamp: msg.timestamp 
                    };
                }
                // Добавляем сообщение в соответствующую группу
                acc[msg.conversation_id].messages.push(msg);
                return acc;
            }, {});

            // Преобразуем объект в массив и сортируем диалоги по дате (от старых к новым)
            const sortedConversations = Object.values(conversations).sort(
                (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
            );

            // Отображаем каждый сгруппированный диалог
            sortedConversations.forEach((conv, index) => {
                const convDiv = document.createElement("div");
                convDiv.className = "conversation";
                const convDate = new Date(conv.timestamp).toLocaleString();
                convDiv.innerHTML = `<div class="conversation-title">Диалог #${index + 1} (начался ${convDate})</div>`;
                
                // Внутри диалога сообщения уже отсортированы, так как API их так отдает
                conv.messages.forEach(msg => {
                    const msgElement = document.createElement("div");
                    msgElement.classList.add("message", `${msg.sender_type}-message`);
                    msgElement.textContent = msg.content;
                    convDiv.appendChild(msgElement);
                });
                historyContent.appendChild(convDiv);
            });

        } catch (error) {
            console.error("Failed to fetch history:", error);
            historyContent.innerHTML = `<p>Не удалось загрузить историю: ${error.message}</p>`;
        }
    }


    // ---- Обработчики событий ----

    // Переключение форм авторизации
    showRegisterLink.addEventListener("click", (e) => { e.preventDefault(); registerForm.style.display="block"; loginForm.style.display="none"; });
    showLoginLink.addEventListener("click", (e) => { e.preventDefault(); loginForm.style.display="block"; registerForm.style.display="none"; });

    // Логин
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        loginError.textContent = "";

        try {
            const data = await apiRequest("/auth/login", {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });
            if (data.role.toLowerCase() === "admin") {
                showModeSelection();
            } else {
                showChat();
            }
        } catch (error) {
            loginError.textContent = "Ошибка входа. Проверьте email и пароль.";
            console.error("Login failed:", error);
        }
    });

    // Регистрация
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;
        registerError.textContent = "";
        try {
            await apiRequest("/auth/register", {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });
            loginForm.style.display="block"; 
            registerForm.style.display="none";
            alert("Регистрация успешна! Теперь вы можете войти.");
        } catch (error) {
            registerError.textContent = "Ошибка регистрации. Возможно, пользователь с таким email уже существует.";
            console.error("Registration failed:", error);
        }
    });

    // Отправка сообщения в чате
    messageForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const question = messageInput.value.trim();
        if (!question) return;
        
        const model_version = modelSelect.value;
        addMessageToUI(question, "user");
        messageInput.value = "";
        setLoading(true);

        try {
            const endpoint = conversationId ? `/chat/${conversationId}` : "/chat/";
            const payload = { model_version, question };
            const data = await apiRequest(endpoint, { method: "POST", body: JSON.stringify(payload) });
            
            if (!conversationId) {
                conversationId = "active";
            }
            addMessageToUI(data.model_response, "bot");
        } catch (error) {
            addMessageToUI(`Ошибка: ${error.message}`, "bot");
            console.error("Chat error:", error);
        } finally {
            setLoading(false);
        }
    });

    // Новый чат
    newChatBtn.addEventListener("click", () => {
        conversationId = null;
        messageList.innerHTML = "";
        addMessageToUI("Здравствуйте! Какой у вас вопрос?", "bot");
    });
    
    // Кнопки админа
    gotoChatBtn.addEventListener("click", showChat);
    gotoAdminPanelBtn.addEventListener("click", showAdminPanel);
    backToSelectionBtn.addEventListener("click", showModeSelection);
});