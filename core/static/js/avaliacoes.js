document.addEventListener("DOMContentLoaded", () => {
  const data = window.avaliacoesData || [];
  const container = document.getElementById("avaliacoesContainer");
  const filtroAno = document.getElementById("filtroAno");
  const filtroTipo = document.getElementById("filtroTipo");
  const pesquisa = document.getElementById("pesquisaUC");

  function render(lista) {
    container.innerHTML = "";
    if (!lista.length) {
      container.innerHTML = "<p class='placeholder'>Nenhuma avaliação encontrada.</p>";
      return;
    }
    lista.forEach(av => {
      const card = document.createElement("div");
      card.className = "av-card animate";
      card.innerHTML = `
        <h3>${av.uc}</h3>
        <p><i class="fa-solid fa-calendar-days"></i> ${av.data}</p>
        <p><i class="fa-solid fa-location-dot"></i> ${av.sala}</p>
        <span class="tag">${av.tipo}</span>
      `;
      container.appendChild(card);
    });
  }

  function filtrar() {
    const ano = filtroAno.value;
    const tipo = filtroTipo.value;
    const termo = pesquisa.value.toLowerCase();
    const filtrados = data.filter(av =>
      (ano === "todos" || av.ano.toString() === ano) &&
      (tipo === "todos" || av.tipo === tipo) &&
      av.uc.toLowerCase().includes(termo)
    );
    render(filtrados);
  }

  filtroAno.addEventListener("change", filtrar);
  filtroTipo.addEventListener("change", filtrar);
  pesquisa.addEventListener("input", filtrar);

  render(data);
});
