document.addEventListener("DOMContentLoaded", () => {
  const botoes = document.querySelectorAll(".btn-inscrever");
  const mensagem = document.getElementById("mensagem");

  botoes.forEach(btn => {
    btn.addEventListener("click", () => {
      const select = btn.parentElement.querySelector(".turno-select");
      const escolha = select.value;

      if (!escolha || escolha === "Escolhe um turno...") {
        alert("Por favor, seleciona um turno antes de inscrever.");
        return;
      }

      // Simulação de inscrição
      mensagem.classList.remove("hidden");
      setTimeout(() => mensagem.classList.add("hidden"), 2500);
    });
  });
});
