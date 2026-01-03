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
        const select = card.querySelector(".turno-select");
        const button = card.querySelector(".btn-inscrever");

        if (!select || !button) return;

        button.addEventListener("click", (e) => {
            e.preventDefault();  // não submeter já

            const option = select.selectedOptions[0];

            if (!option || !option.value) {
                alert("Escolhe um turno primeiro!");
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

            // depois de desenhar no horário, submeter o form
            card.querySelector("form").submit();
        });
    });
});
