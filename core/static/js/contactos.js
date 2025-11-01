document.addEventListener("DOMContentLoaded", () => {
  const contacts = [
    { nome: "Filipe Caldeira", funcao: "Diretor Departamento de Informática", email: "caldeira@estgv.ipv.pt", grupo: "direcao" },
    { nome: "Steven Abrantes", funcao: "Diretor de Curso", email: "steven@estgv.ipv.pt", grupo: "direcao" },

    { nome: "Nuno Costa", funcao: "Técnico Superior", email: "ncosta@estgv.ipv.pt", grupo: "tecnicos" },
    { nome: "Silvia Moreira", funcao: "Técnica Superior", email: "smoreira@estgv.ipv.pt", grupo: "tecnicos" },

    { nome: "Ana Cristina Wanzeller Guedes de Lacerda", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Ana Raquel Ferreira de Almeida Sebastião", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Artur Jorge Afonso de Sousa", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Carlos Alberto Tomás Simões", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Carlos Augusto da Silva Cunha", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Francisco Ferreira Francisco", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "João Pedro Menoita Henriques", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Paulo Costa", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },
    { nome: "Paulo Rogério Perfeito Tomé", funcao: "Docente", email: "@estgv.ipv.pt", grupo: "docentes" },

    { nome: "XXXXXXXX", funcao: "Delegado 1.º ano", email: "xxxxxxx@alunos.estgv.ipv.pt", grupo: "delegados" },
    { nome: "XXXXXXXX", funcao: "Delegado 1.º ano", email: "xxxxxxx@alunos.estgv.ipv.pt", grupo: "delegados" },
    { nome: "XXXXXXXX", funcao: "Delegado 2.º ano", email: "xxxxxxx@alunos.estgv.ipv.pt", grupo: "delegados" },
    { nome: "XXXXXXXX", funcao: "Delegado 3.º ano", email: "xxxxxxx@alunos.estgv.ipv.pt", grupo: "delegados" },
    { nome: "Rodrigo Pereira", funcao: "Delegado 3.º ano", email: "xxxxxxx@alunos.estgv.ipv.pt", grupo: "delegados" },
    { nome: "Francisco Pereira", funcao: "Delegado 3.º ano", email: "xxxxxxx@alunos.estgv.ipv.pt", grupo: "delegados" },
  ];

  const container = document.getElementById("contactsContainer");
  const search = document.getElementById("searchInput");
  const filters = document.querySelectorAll(".filter-btn");

  function render(list) {
    container.innerHTML = "";
    list.forEach(c => {
      const card = document.createElement("div");
      card.className = "contact-card";
      card.dataset.group = c.grupo;
      card.innerHTML = `
        <h3>${c.nome}</h3>
        <p>${c.funcao}</p>
        <p><i class="fa-solid fa-envelope"></i> ${c.email}</p>
        <div class="actions">
          <a href="mailto:${c.email}" class="btn-icon" title="Enviar email"><i class="fa-regular fa-envelope"></i></a>
          <button class="btn-icon copy" data-email="${c.email}" title="Copiar email"><i class="fa-regular fa-copy"></i></button>
        </div>
      `;
      container.appendChild(card);
    });
  }

  function filter() {
    const term = search.value.toLowerCase();
    const active = document.querySelector(".filter-btn.active").dataset.group;
    const filtered = contacts.filter(c =>
      (active === "all" || c.grupo === active) &&
      (c.nome.toLowerCase().includes(term) || c.funcao.toLowerCase().includes(term) || c.email.toLowerCase().includes(term))
    );
    render(filtered);
  }

  filters.forEach(btn => btn.addEventListener("click", () => {
    filters.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filter();
  }));

  search.addEventListener("input", filter);

  document.addEventListener("click", e => {
    if (e.target.closest(".copy")) {
      const email = e.target.closest(".copy").dataset.email;
      navigator.clipboard.writeText(email);
      const icon = e.target.closest(".copy").querySelector("i");
      icon.className = "fa-solid fa-circle-check";
      setTimeout(() => icon.className = "fa-regular fa-copy", 1200);
    }
  });

  render(contacts);
});
