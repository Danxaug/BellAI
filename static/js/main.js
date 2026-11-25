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

    // 3. Formulario de Lead (WhatsApp Inteligente - CORREGIDO PARA PRODUCCIÓN)
    const form = document.getElementById("leadForm");
    const servicioSelect = document.getElementById("servicio"); 
    
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById("submitBtn");
            const formStatus = document.getElementById("formStatus");
            
            // Datos del formulario
            const fd = new FormData(form);
            const nombre = fd.get("nombre");
            const empresa = fd.get("empresa") || "";
            const whatsappUser = fd.get("whatsapp");
            const servicioElegido = servicioSelect ? servicioSelect.value : "BellAI Flow"; 

            // Feedback visual
            if(submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.dataset.originalHtml = originalText;
                submitBtn.innerHTML = `<span>Enviando...</span>`;
            }
            if(formStatus) formStatus.textContent = "";

            // TU NÚMERO DE BELLAI (Asegurado con 57)
            const YOUR_PHONE = "573174827958"; 
            const msg = encodeURIComponent(`Hola BellAI, soy ${nombre} de ${empresa}. Quiero agendar mi diagnóstico gratuito para: ${servicioElegido}. Mi WhatsApp es ${whatsappUser}.`);
            const directWhatsAppLink = `https://wa.me/${YOUR_PHONE}?text=${msg}`;

            try {
                // Intentamos llamar al backend (solo si existe la ruta en producción)
                const res = await fetch("/procesar_lead", { 
                    method: "POST", 
                    headers: { "Content-Type": "application/json" }, 
                    body: JSON.stringify({ nombre, empresa, whatsapp: whatsappUser, servicio: servicioElegido }) 
                });

                // Si el backend responde OK y tiene una URL de redirección, la usamos
                if (res.ok) {
                    const data = await res.json();
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                        return; // Salimos aquí si funcionó el backend
                    }
                }
                
                // SI LLEGAMOS AQUÍ: El backend no dio URL válida O dio error 404/500
                // FALLBACK AUTOMÁTICO: Redirigir directo a WhatsApp
                throw new Error("Backend no respondió correctamente, usando fallback directo.");

            } catch (err) {
                console.warn("Error en backend o fallback activado:", err);
                
                // Mensaje opcional al usuario
                if(formStatus) formStatus.textContent = "️ Conectando directamente con WhatsApp...";
                
                // Abrir WhatsApp inmediatamente
                setTimeout(() => {
                     window.open(directWhatsAppLink, '_blank');
                     
                     // Restaurar botón
                     if(submitBtn && submitBtn.dataset.originalHtml) {
                         submitBtn.disabled = false;
                         submitBtn.innerHTML = submitBtn.dataset.originalHtml;
                     }
                }, 800); // Pequeña pausa para que el usuario vea el mensaje
            }
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
                
                let responseText = data.response || 'Lo siento, no pude procesar tu mensaje.';

                //  Lógica de Botón WhatsApp en Chat
                const phoneRegex = /(\+?\d{7,15})/; 
                const userPhoneMatch = message.match(phoneRegex);

                if (userPhoneMatch || (responseText.toLowerCase().includes('agendar') && responseText.toLowerCase().includes('whatsapp'))) {
                    let cleanPhone = "";
                    
                    if (userPhoneMatch) {
                        cleanPhone = userPhoneMatch[0].replace(/\D/g, '');
                    } else {
                        const lastUserMsg = [...chatHistory].reverse().find(m => m.role === 'user');
                        if (lastUserMsg) {
                            const histMatch = lastUserMsg.content.match(phoneRegex);
                            if (histMatch) cleanPhone = histMatch[0].replace(/\D/g, '');
                        }
                    }

                    if (cleanPhone.length >= 7) {
                        if (!cleanPhone.startsWith('57')) {
                            cleanPhone = '57' + cleanPhone;
                        }
                        
                        const whatsappLink = `https://wa.me/${cleanPhone}?text=${encodeURIComponent('Hola BellAI, confirmo mi interés en el diagnóstico gratuito.')}`;
                        responseText += `<br><br>👉 <a href="${whatsappLink}" target="_blank" style="display: inline-block; background-color: #25D366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; font-family: sans-serif; margin-top: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"> Abrir WhatsApp para Agendar</a>`;
                    }
                }

                botMsg.innerHTML = responseText;
                chatMessages.appendChild(botMsg);

                chatHistory.push({ role: 'user', content: message });
                chatHistory.push({ role: 'assistant', content: data.response });
                chatMessages.scrollTop = chatMessages.scrollHeight;

            } catch (error) {
                console.error(error);
                loader.remove();
                const errorMsg = document.createElement('div');
                errorMsg.className = 'msg-error';
                errorMsg.textContent = '⚠️ Error de conexión con la IA. Por favor escríbenos directo al WhatsApp.';
                chatMessages.appendChild(errorMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });
    }
});