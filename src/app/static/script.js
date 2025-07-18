document.addEventListener("DOMContentLoaded", () => {
    // ---- Элементы UI ----
    const authContainer = document.getElementById("auth-container");
    const chatContainer = document.getElementById("chat-container");

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

    // ---- Состояние приложения ----
    let conversationId = null;

    // ---- Константы ----
    const API_BASE_URL = "http://127.0.0.1:8000"; // ВАЖНО: Укажите правильный адрес вашего бэкенда

    // ---- Функции ----

    // Функция для переключения между формами входа и регистрации
    function toggleAuthForms() {
        loginForm.style.display = loginForm.style.display === "none" ? "block" : "none";
        registerForm.style.display = registerForm.style.display === "none" ? "block" : "none";
        loginError.textContent = "";
        registerError.textContent = "";
    }

    // Показывает чат и скрывает авторизацию
    function showChat() {
        authContainer.style.display = "none";
        chatContainer.style.display = "flex";
    }

    // Добавляет сообщение в UI
    function addMessageToUI(text, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message", `${sender}-message`);
        messageElement.textContent = text;
        messageList.appendChild(messageElement);
        // Автоматически прокручиваем вниз
        messageList.scrollTop = messageList.scrollHeight;
    }
    
    // Управляет индикатором загрузки и блокировкой формы
    function setLoading(isLoading) {
        const sendButton = messageForm.querySelector("button");
        if (isLoading) {
            loadingIndicator.style.display = "flex";
            messageInput.disabled = true;
            sendButton.disabled = true;
        } else {
            loadingIndicator.style.display = "none";
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    // Универсальная функция для отправки запросов
    async function apiRequest(endpoint, options) {
        // 'credentials: "include"' заставляет браузер отправлять cookie (наш access_token)
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: { 'Content-Type': 'application/json', ...options.headers },
            credentials: 'include'
        });

        if (!response.ok) {
            // Если ошибка, пытаемся прочитать тело ошибки от FastAPI
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { detail: "Произошла неизвестная ошибка сервера." };
            }
            throw new Error(errorData.detail || `Ошибка ${response.status}`);
        }
        // Если ответ 204 No Content или другой без тела
        if (response.status === 204) return null;
        
        return response.json();
    }


    // ---- Обработчики событий ----

    showRegisterLink.addEventListener("click", (e) => {
        e.preventDefault();
        toggleAuthForms();
    });

    showLoginLink.addEventListener("click", (e) => {
        e.preventDefault();
        toggleAuthForms();
    });

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;
        loginError.textContent = "";

        try {
            await apiRequest("/auth/login", {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });
            showChat();
        } catch (error) {
            loginError.textContent = "Ошибка входа. Проверьте email и пароль.";
            console.error("Login failed:", error);
        }
    });

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
            // После успешной регистрации переключаем на форму входа
            toggleAuthForms();
            alert("Регистрация успешна! Теперь вы можете войти.");
        } catch (error) {
            registerError.textContent = "Ошибка регистрации. Возможно, пользователь с таким email уже существует.";
            console.error("Registration failed:", error);
        }
    });

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
            const payload = {
                model_version,
                question
            };

            const data = await apiRequest(endpoint, {
                method: "POST",
                body: JSON.stringify(payload)
            });

            // Если это был первый запрос, сохраняем ID диалога из cookie (хотя он и не нужен на фронте, но бэку нужен)
            // Бэкенд установит conversation_id в cookie, но мы также будем управлять им в JS для отправки запросов.
            // Ваш бэкенд возвращает ID диалога в ответе, что удобнее, чем парсить cookie.
            // Но в вашем коде ID возвращается только для нового чата, и устанавливается в cookie.
            // Давайте для надежности просто запомним, что чат начат.
            if (!conversationId) {
                // После первого успешного ответа, мы знаем, что чат начался
                // и браузер сохранил cookie. Следующие запросы пойдут на /chat/{id},
                // который бэкэнд будет читать из cookie. Но для фронта это прозрачно.
                // Чтобы различать запросы, нам нужен ID.
                // Ваш бэкэнд не возвращает ID в ответе, он ставит cookie.
                // Это проблема. Давайте модифицируем бэкэнд.
                // ВРЕМЕННОЕ РЕШЕНИЕ: Будем считать, что после первого ответа чат существует
                // и просто будем посылать на `/chat/some_id` чтобы попасть на нужный роут.
                // Ваш бэкенд читает ID из кук, так что это сработает.
                conversationId = "active"; // Просто маркер, что чат начат.
            }

            addMessageToUI(data.model_response, "bot");

        } catch (error) {
            addMessageToUI(`Ошибка: ${error.message}`, "bot");
            console.error("Chat error:", error);
        } finally {
            setLoading(false);
        }
    });

    newChatBtn.addEventListener("click", () => {
        conversationId = null;
        messageList.innerHTML = ""; // Очищаем поле сообщений
        addMessageToUI("Здравствуйте! Какой у вас вопрос?", "bot");
        // Примечание: нужно также очистить cookie `conversation_id` на стороне бэкенда,
        // но простого способа сделать это с фронта нет.
        // Бэкенд должен сам это обрабатывать при старте нового чата.
        // Ваш код так и делает: `/chat/` создает новый чат.
    });
    
    // Начальное приветствие при загрузке чата
    addMessageToUI("Здравствуйте! Какой у вас вопрос?", "bot");
});