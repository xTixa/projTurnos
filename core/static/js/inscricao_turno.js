function adicionarAula(dia, hora, uc) {
    const cellId = `${dia}-${hora}`;  // ex.: "Segunda-09:00"
    const cell = document.getElementById(cellId);
    if (!cell) {
        console.warn("Célula não encontrada:", cellId);
        return;
    }
    cell.textContent = uc;
}

document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".uc-card");

    cards.forEach((card) => {
        const form = card.querySelector("form");
        const select = card.querySelector(".turno-select");

        if (!select || !form) return;

        // Quando mudar o select, atualizar o horário
        select.addEventListener("change", (e) => {
            const option = e.target.selectedOptions[0];

            if (!option || !option.value) {
                return;
            }

            const dia = option.dataset.dia;
            const hora = option.dataset.hora;
            const uc = card.querySelector("h3").innerText;

            if (!dia || !hora) {
                console.warn("Falta dia ou hora no option selecionado", option);
                return;
            }

            adicionarAula(dia, hora, uc);
        });
    });
});
