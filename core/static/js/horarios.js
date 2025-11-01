document.addEventListener("DOMContentLoaded", () => {
  const eventosRaw = window.__EVENTOS__ || [];
  const cal = document.getElementById("calendar");
  const filtroAno = document.getElementById("filtroAno");
  const filtroTurma = document.getElementById("filtroTurma");

  // Modal
  const openBtn = document.getElementById("openInscricao");
  const modal = document.getElementById("inscricaoModal");
  const closeBtn = document.getElementById("closeInscricao");
  const form = document.getElementById("formInscricao");
  const msg = document.getElementById("inscricaoMsg");

  // grid helpers
  const START_MIN = 8 * 60;   // 08:00
  const END_MIN   = 20 * 60;  // 20:00
  const STEP = 30;            // 30 min
  const totalRows = (END_MIN - START_MIN) / STEP; // 24

  // Converte "HH:MM" -> minutos
  const toMin = t => {
    const [h,m]=t.split(":").map(Number);
    return h*60+m;
  };

  // limpa eventos existentes
  function clearEvents(){
    cal.querySelectorAll(".evento").forEach(e => e.remove());
  }

  // deteta sobreposição simples (intervalos)
  function overlap(a,b){
    return a.inicioMin < b.fimMin && b.inicioMin < a.fimMin;
  }

  // calcula índice de sobreposição para deslocar horizontalmente
  function computeOverlaps(list){
    // por dia: ordena por início e atribui “layer” (1..3)
    const byDay = {1:[],2:[],3:[],4:[],5:[]};
    list.forEach(e => byDay[e.dia].push(e));
    Object.values(byDay).forEach(arr=>{
      arr.sort((x,y)=>x.inicioMin-y.inicioMin);
      arr.forEach((e,i)=>{
        e.layer = 1;
        for (let k=0;k<i;k++){
          if (overlap(e, arr[k])) e.layer = Math.max(e.layer, (arr[k].layer||1)+1);
        }
        e.layer = Math.min(e.layer, 3); // até 3 deslocamentos
      });
    });
  }

  // renderiza eventos para ano/turma
  function render(){
    clearEvents();

    const anoSel = parseInt(filtroAno.value);
    const turmaSel = filtroTurma.value;

    // filtra
    const data = eventosRaw
      .filter(e => e.ano === anoSel && e.turma === turmaSel)
      .map(e => ({
        ...e,
        inicioMin: toMin(e.inicio),
        fimMin: toMin(e.fim),
      }));

    computeOverlaps(data);

    // marca conflitos (mesmo dia com sobreposição)
    data.forEach((e,i)=>{
      e.conflict = data.some((o,j)=> j!==i && e.dia===o.dia && overlap(e,o));
    });

    // cria blocos
    data.forEach(e=>{
      // coluna: day -> precisamos do elemento day-cell desse dia para posicionar absolute nele
      // vamos usar o primeiro .day-cell com data-day=dia como âncora de medida
      const dayCell = cal.querySelector(`.day-cell[data-day="${e.dia}"]`);
      if(!dayCell) return;

      // container real é a coluna do dia (todas as day-cell do mesmo day partilham offset);
      // calculamos altura total (cal) e posição relativa:
      const allDayCells = [...cal.querySelectorAll(`.day-cell[data-day="${e.dia}"]`)];
      const first = allDayCells[0];
      const last  = allDayCells[allDayCells.length-1];
      const topBase = first.getBoundingClientRect().top;
      const bottomBase = last.getBoundingClientRect().bottom;
      const height = bottomBase - topBase;

      const totalMin = END_MIN - START_MIN;
      const topPct = (e.inicioMin - START_MIN) / totalMin;
      const bottomPct = (e.fimMin - START_MIN) / totalMin;
      const y = topPct * height;
      const h = (bottomPct - topPct) * height;

      // cria elemento
      const ev = document.createElement("div");
      ev.className = `evento overlap-${e.layer} ${e.conflict ? "conflict":""}`;
      ev.style.top = `${y}px`;
      ev.style.height = `${Math.max(h, 24)}px`;

      // posicionar dentro da coluna do dia (usamos o parent grid; absolute relativo ao calendar)
      // truque: append ao cal e alinhar horizontalmente usando a coluna do dia:
      const dayIndex = e.dia; // 1..5
      // calcular left/right a partir da coluna (grid): usamos getBoundingClientRect do primeiro dayCell dessa coluna
      const dayRect = first.getBoundingClientRect();
      const calRect = cal.getBoundingClientRect();
      const colLeft = dayRect.left - calRect.left;
      const colRight = calRect.right - (calRect.right - dayRect.right);
      const width = colRight - colLeft;

      const shift = (e.layer-1) * 0.08 * width; // 8% por layer
      ev.style.left = `${colLeft + 6 + shift}px`;
      ev.style.width = `${width - 12 - shift}px`;
      ev.style.position = "absolute";

      ev.innerHTML = `
        <span class="tit">${e.uc} <small>(${e.turno} · ${e.tipo})</small>${e.conflict ? '<span class="badge">Conflito</span>':''}</span>
        <span class="sub">${e.inicio}–${e.fim} · ${e.sala}</span>
      `;

      cal.appendChild(ev);
    });
  }

  // eventos UI
  filtroAno.addEventListener("change", render);
  filtroTurma.addEventListener("change", render);

  // Modal inscrição
  openBtn.addEventListener("click", ()=> modal.classList.remove("hidden"));
  closeBtn.addEventListener("click", ()=> modal.classList.add("hidden"));
  modal.addEventListener("click", e => { if(e.target===modal) modal.classList.add("hidden"); });

  // valida inscrição sem colisões
  form.addEventListener("submit", (e)=>{
    e.preventDefault();
    const escolhas = [...form.querySelectorAll("select")].map(s => s.value).filter(Boolean);
    if (escolhas.length === 0){
      feedback("Seleciona pelo menos um turno.", false); return;
    }

    // transformar "UC||Turno||Seg 08:30–10:00" -> comparar por dia/hora
    const toSlot = txt => {
      const [, , when] = txt.split("||");
      // ex "Seg 08:30–10:00"
      const map = { "Seg":1, "Ter":2, "Qua":3, "Qui":4, "Sex":5 };
      const [diaTxt, horas] = when.split(" ");
      const [ini, fim] = horas.split("–");
      return { dia: map[diaTxt], ini: toMin(ini), fim: toMin(fim) };
    };

    const slots = escolhas.map(toSlot);
    // colisão entre escolhas do utilizador
    const colisao = slots.some((s,i)=> slots.some((o,j)=> i<j && s.dia===o.dia && s.ini<o.fim && o.ini<s.fim));
    if (colisao){ feedback("Conflito entre turnos escolhidos. Ajusta a seleção.", false); return; }

    feedback("Inscrição efetuada com sucesso! ✅", true);
  });

  function feedback(text, ok){
    msg.textContent = text;
    msg.classList.remove("hidden","ok","err");
    msg.classList.add(ok ? "ok":"err");
  }

  // primeira renderização
  render();
});
