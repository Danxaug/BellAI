document.addEventListener("DOMContentLoaded", () => {
    // 1. Animaciones AOS
    if (window.AOS) AOS.init({ duration: 800, once: true, easing: "ease-out-cubic" });

    // 2. Calculadora ROI
    const leadsIn = document.getElementById("leadsInput");
    const ticketIn = document.getElementById("ticketInput");
    const leadsVal = document.getElementById("leadsVal");
    const ticketVal = document.getElementById("ticketVal");
    const roiResult = document.getElementById("roiResult");
    const fmt = new Intl.NumberFormat("es-CO");

    function calcROI() {
        if(!leadsIn || !ticketIn) return;
        const leads = parseInt(leadsIn.value, 10);
        const ticket = parseInt(ticketIn.value, 10);
        leadsVal.textContent = leads;
        ticketVal.textContent = "$" + fmt.format(ticket);
        roiResult.textContent = "$" + fmt.format(Math.round(leads * 0.25 * ticket)) + " COP / mes";
    }
    if (leadsIn && ticketIn) {
        leadsIn.addEventListener("input", calcROI);
        ticketIn.addEventListener("input", calcROI);
    }

    // 3. Formulario de Lead (WhatsApp)
    const form = document.getElementById("leadForm");
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const fd = new FormData(form);
            const body = { nombre: fd.get("nombre"), empresa: fd.get("empresa") || "", whatsapp: fd.get("whatsapp"), servicio: "General" };
            try {
                const res = await fetch("/procesar_lead", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
                const data = await res.json();
                if(data.redirect_url) window.location.href = data.redirect_url;
            } catch (err) { alert("Error al enviar. Intenta de nuevo."); }
        });
    }
});

// =========================================
// WIDGET CHAT ASESOR IA
// =========================================
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-chat-btn');
    const closeBtn = document.getElementById('close-chat-btn');
    const chatWindow = document.getElementById('ai-chat-window');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    let chatHistory = [];
    let isOpen = false;

    if (toggleBtn && chatWindow) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            isOpen = !isOpen;
            chatWindow.style.display = isOpen ? 'flex' : 'none';
            if (isOpen && chatInput) setTimeout(() => chatInput.focus(), 100);
        });

        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                isOpen = false;
                chatWindow.style.display = 'none';
            });
        }

        document.addEventListener('click', function(e) {
            if (isOpen && !chatWindow.contains(e.target) && !toggleBtn.contains(e.target)) {
                isOpen = false;
                chatWindow.style.display = 'none';
            }
        });
    }

    if (chatForm && chatInput) {
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;

            const userMsg = document.createElement('div');
            userMsg.className = 'msg-user';
            userMsg.textContent = message;
            chatMessages.appendChild(userMsg);
            chatInput.value = '';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            const loader = document.createElement('div');
            loader.className = 'msg-loading';
            loader.textContent = '⏳ BellAI está analizando...';
            chatMessages.appendChild(loader);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, history: chatHistory })
                });
                if (!res.ok) throw new Error('HTTP ' + res.status);
                const data = await res.json();
                loader.remove();

                const botMsg = document.createElement('div');
                botMsg.className = 'msg-bot';
                botMsg.innerHTML = data.response || 'Lo siento, no pude procesar tu mensaje.';
                chatMessages.appendChild(botMsg);

                chatHistory.push({ role: 'user', content: message });
                chatHistory.push({ role: 'assistant', content: data.response });
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } catch (error) {
                loader.remove();
                const errorMsg = document.createElement('div');
                errorMsg.className = 'msg-error';
                errorMsg.textContent = '⚠️ Error de conexión. Intenta de nuevo.';
                chatMessages.appendChild(errorMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });
    }
});