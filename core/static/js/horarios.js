document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".tab-btn");
  const tables = document.querySelectorAll(".horario-table");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      buttons.forEach(b => b.classList.remove("active"));
      tables.forEach(t => t.classList.remove("active"));

      btn.classList.add("active");
      document.getElementById("ano" + btn.dataset.ano).classList.add("active");
    });
  });
});
