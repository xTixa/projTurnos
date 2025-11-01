document.addEventListener("DOMContentLoaded", () => {
  const data = window.planoData || [];
  const container = document.getElementById("planoContainer");
  const buttons = document.querySelectorAll(".tab-btn");
  const modal = document.getElementById("ucModal");
  const closeBtn = modal.querySelector(".close");

  // Função que renderiza as UCs
  function render(ano, sem) {
    container.innerHTML = "";
    const bloco = data.find(p => p.ano === ano && p.semestre === sem);

    if (!bloco) {
      container.innerHTML = "<p class='placeholder'>Sem dados para este semestre.</p>";
      return;
    }

    bloco.ucs.forEach(uc => {
      const card = document.createElement("div");
      card.className = "uc-card animate";
      card.innerHTML = `
        <h3>${uc.nome}</h3>
        <p class="uc-type">${uc.tipo}</p>
        <span class="ects">${uc.ects} ECTS</span>
      `;
      card.addEventListener("click", () => openModal(uc));
      container.appendChild(card);
    });
  }

  // Abre o modal com detalhes
  function openModal(uc) {
    modal.classList.remove("hidden");
    document.getElementById("ucNome").textContent = uc.nome;
    document.getElementById("ucDesc").textContent = uc.descricao;
    document.getElementById("ucEcts").textContent = uc.ects;
    document.getElementById("ucTipo").textContent = uc.tipo;
    document.getElementById("ucDocente").textContent = uc.docente;
  }

  // Fecha modal
  closeBtn.addEventListener("click", () => modal.classList.add("hidden"));
  modal.addEventListener("click", e => {
    if (e.target === modal) modal.classList.add("hidden");
  });

  // Tabs — muda o semestre
  buttons.forEach(btn => btn.addEventListener("click", () => {
    buttons.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    render(parseInt(btn.dataset.ano), parseInt(btn.dataset.sem));
  }));

  // Ativa automaticamente o primeiro
  if (buttons.length > 0) {
    buttons[0].classList.add("active");
    const { ano, sem } = buttons[0].dataset;
    render(parseInt(ano), parseInt(sem));
  }
});
