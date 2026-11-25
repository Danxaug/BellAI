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

    // 3. Formulario de Lead (WhatsApp Inteligente)
    const form = document.getElementById("leadForm");
    const servicioSelect = document.getElementById("servicio"); 
    
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById("submitBtn");
            const formStatus = document.getElementById("formStatus");
            
            if(submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.dataset.originalHtml = originalText;
                submitBtn.innerHTML = `<span>Enviando...</span>`;
            }
            if(formStatus) formStatus.textContent = "";

            const fd = new FormData(form);
            const servicioElegido = servicioSelect ? servicioSelect.value : "BellAI Flow"; 

            const body = { 
                nombre: fd.get("nombre"), 
                empresa: fd.get("empresa") || "", 
                whatsapp: fd.get("whatsapp"), 
                servicio: servicioElegido 
            };

            try {
                const res = await fetch("/procesar_lead", { 
                    method: "POST", 
                    headers: { "Content-Type": "application/json" }, 
                    body: JSON.stringify(body) 
                });

                if (!res.ok) throw new Error("Error en el servidor");
                const data = await res.json();

                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    if(formStatus) formStatus.textContent = "¡Gracias! Redirigiendo a WhatsApp...";
                    const phone = "573174827958"; 
                    const msg = encodeURIComponent(`Hola BellAI, quiero agendar mi diagnóstico gratuito para el servicio: ${servicioElegido}. Mi nombre es ${body.nombre}.`);
                    
                    setTimeout(() => {
                         window.open(`https://wa.me/${phone}?text=${msg}`, '_blank');
                         if(submitBtn && submitBtn.dataset.originalHtml) {
                             submitBtn.disabled = false;
                             submitBtn.innerHTML = submitBtn.dataset.originalHtml;
                         }
                    }, 1000);
                }

            } catch (err) {
                console.error(err);
                if(formStatus) formStatus.textContent = "⚠️ Hubo un error al conectar. Por favor intenta de nuevo o escríbenos directo.";
                if(submitBtn) {
                    submitBtn.disabled = false;
                    if(submitBtn.dataset.originalHtml) submitBtn.innerHTML = submitBtn.dataset.originalHtml;
                }
            }
        });
    }
});

// =========================================
// WIDGET CHAT ASESOR IA (CORREGIDO)
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

                // 🔥 CORRECCIÓN CRÍTICA: Generación Automática de Link WhatsApp Seguro
                // Detectamos si el usuario acaba de enviar un número de teléfono en su mensaje
                const phoneRegex = /(\+?\d{7,15})/; 
                const userPhoneMatch = message.match(phoneRegex);

                // Si el usuario envió un número O si la respuesta de la IA menciona "agendar" o "diagnóstico"
                if (userPhoneMatch || (responseText.toLowerCase().includes('agendar') && responseText.toLowerCase().includes('whatsapp'))) {
                    let cleanPhone = "";
                    
                    // Prioridad 1: Usar el número que el usuario acaba de escribir
                    if (userPhoneMatch) {
                        cleanPhone = userPhoneMatch[0].replace(/\D/g, ''); // Limpiar símbolos
                    } 
                    // Prioridad 2: Si no hay número en el mensaje actual, buscar en el historial reciente
                    else {
                        const lastUserMsg = [...chatHistory].reverse().find(m => m.role === 'user');
                        if (lastUserMsg) {
                            const histMatch = lastUserMsg.content.match(phoneRegex);
                            if (histMatch) cleanPhone = histMatch[0].replace(/\D/g, '');
                        }
                    }

                    // Si encontramos un número válido, generamos el link correcto manualmente
                    if (cleanPhone.length >= 7) {
                        if (!cleanPhone.startsWith('57')) {
                            cleanPhone = '57' + cleanPhone;
                        }
                        
                        const whatsappLink = `https://wa.me/${cleanPhone}?text=${encodeURIComponent('Hola BellAI, confirmo mi interés en el diagnóstico gratuito.')}`;
                        
                        // Agregamos un botón profesional al final de la respuesta
                        responseText += `<br><br>👉 <a href="${whatsappLink}" target="_blank" style="display: inline-block; background-color: #25D366; color: white; padding: 12px 20px; text-decoration: none; border-radius: 8px; font-weight: bold; font-family: sans-serif; margin-top: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);"> Abrir WhatsApp para Agendar</a>`;
                    }
                }

                botMsg.innerHTML = responseText; // Usamos innerHTML para renderizar el botón
                chatMessages.appendChild(botMsg);

                chatHistory.push({ role: 'user', content: message });
                chatHistory.push({ role: 'assistant', content: data.response }); // Guardamos la respuesta original sin el botón extra
                chatMessages.scrollTop = chatMessages.scrollHeight;

            } catch (error) {
                console.error(error);
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