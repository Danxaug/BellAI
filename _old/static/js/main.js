document.addEventListener("DOMContentLoaded", () => {
    // AOS (si existe)
    if (window.AOS) AOS.init({ duration: 800, once: true, easing: "ease-out-cubic" });

    // Calculadora
    const leadsIn = document.getElementById("leadsInput");
    const ticketIn = document.getElementById("ticketInput");
    const leadsVal = document.getElementById("leadsVal");
    const ticketVal = document.getElementById("ticketVal");
    const roiResult = document.getElementById("roiResult");

    const fmt = new Intl.NumberFormat("es-CO");

    function calcROI() {
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

    // Formulario
    const form = document.getElementById("leadForm");
    const status = document.getElementById("formStatus");
    const submitBtn = document.getElementById("submitBtn");

    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            status.textContent = "";
            submitBtn.disabled = true;
            submitBtn.textContent = "Procesando...";

            const fd = new FormData(form);
            const body = {
                nombre: fd.get("nombre"),
                empresa: fd.get("empresa") || "",
                whatsapp: fd.get("whatsapp"),
                servicio: fd.get("servicio") || "General",
            };

            try {
                const res = await fetch("/procesar_lead", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(body),
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    throw new Error(err.detail || "Error al enviar");
                }
                const data = await res.json();
                status.textContent = "Redirigiendo a WhatsApp...";
                status.className = "text-xs text-center text-green-400 min-h-[1rem]";
                window.location.href = data.redirect_url;
            } catch (err) {
                status.textContent = err.message || "Error al enviar. Intenta de nuevo.";
                status.className = "text-xs text-center text-red-400 min-h-[1rem]";
                submitBtn.disabled = false;
                submitBtn.textContent = "Solicitar Diagnóstico por WhatsApp 🚀";
            }
        });
    }
});