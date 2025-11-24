document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".uc-card");

    cards.forEach((card) => {
        const select = card.querySelector(".turno-select");
        const button = card.querySelector(".btn-inscrever");

        button.addEventListener("click", () => {
            const valorEscolhido = select.value;

            if (!valorEscolhido || valorEscolhido.startsWith("Escolhe")) {
                alert("Escolhe um turno primeiro!");
                return;
            }

            // "T1 — Segunda 09:00 (25 vagas)"
            const [turnoNome, resto] = valorEscolhido.split("—");
            const [dia, horaRaw] = resto.trim().split(" ");
            const hora = horaRaw.replace("(", "").trim();

            const uc = card.querySelector("h3").innerText;

            // Preenche a célula correspondente
            adicionarAula(dia, hora, uc);

            // Mostra mensagem de sucesso
            const mensagem = document.getElementById("mensagem");
            mensagem.classList.remove("hidden");
            setTimeout(() => mensagem.classList.add("hidden"), 2000);
        });
    });
});
