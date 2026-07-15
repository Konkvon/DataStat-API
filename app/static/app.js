/* ============================================================
   DataStat API — frontend vanilla
   ============================================================ */

function parseNumbers(text) {
  if (!text) return [];
  return text
    .replace(/,/g, ' ')
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map(Number)
    .filter(n => !Number.isNaN(n));
}

async function postJson(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return res.json();
}

async function getJson(path) {
  const res = await fetch(path, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return res.json();
}

const LOADING = '<span class="loading"><span class="spinner"></span>Carregando...</span>';
const STAT_LABELS = {
  Count: 'Contagem',
  Mean: 'Média',
  Median: 'Mediana',
  STD: 'Desvio-padrão',
  Variance: 'Variância',
  Min: 'Mínimo',
  Max: 'Máximo',
  p25: 'Percentil 25%',
  p50: 'Percentil 50%',
  p75: 'Percentil 75%'
};

/* ---------- Abas ---------- */
const tabs = Array.from(document.querySelectorAll('.tab'));
const panels = {
  calc: document.getElementById('panel-calc'),
  hist: document.getElementById('panel-hist'),
  cmp: document.getElementById('panel-cmp')
};

function activateTab(name) {
  tabs.forEach(tab => {
    const selected = tab.dataset.tab === name;
    tab.setAttribute('aria-selected', selected ? 'true' : 'false');
    tab.tabIndex = selected ? 0 : -1;
  });
  Object.entries(panels).forEach(([key, panel]) => {
    panel.hidden = key !== name;
  });
}

tabs.forEach(tab => {
  tab.addEventListener('click', () => activateTab(tab.dataset.tab));
});

/* ---------- Renderização ---------- */
function chartHtml(grafico, alt) {
  if (!grafico) return '';
  return `<div class="chart"><img src="${grafico}" alt="${alt}" /></div>`;
}

function statsTable(stats) {
  let html = '<div class="table-wrap"><table class="data"><thead>';
  html += '<tr><th>Métrica</th><th>Valor</th></tr></thead><tbody>';
  for (const [key, label] of Object.entries(STAT_LABELS)) {
    html += `<tr><td class="label">${label}</td><td class="value">${stats[key]}</td></tr>`;
  }
  html += '</tbody></table></div>';
  return html;
}

function formatEstatisticas(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;
  return statsTable(data.Estatisticas);
}

function formatHistograma(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;

  const hist = data.Histograma;
  const intervalos = hist.Intervalos;
  const frequencia = hist.Frequencia;

  let html = chartHtml(data.Grafico, 'Histograma de frequência');
  html += '<div class="table-wrap"><table class="data"><thead>';
  html += '<tr><th>Intervalo</th><th>Frequência</th></tr></thead><tbody>';
  for (let i = 0; i < frequencia.length; i++) {
    const inicio = intervalos[i].toFixed(2);
    const fim = intervalos[i + 1].toFixed(2);
    html += `<tr><td>${inicio} – ${fim}</td><td class="value">${frequencia[i]}</td></tr>`;
  }
  html += '</tbody></table></div>';
  return html;
}

function formatComparacao(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;

  const comp = data.Comparacao;
  let html = '<div class="table-wrap"><table class="data"><thead>';
  html += '<tr><th>Métrica</th><th>Conjunto 1</th><th>Conjunto 2</th></tr></thead><tbody>';
  for (const [chave, valores] of Object.entries(comp)) {
    const label = STAT_LABELS[chave] || chave;
    html += `<tr><td class="label">${label}</td><td class="value">${valores[0]}</td><td class="value">${valores[1]}</td></tr>`;
  }
  html += '</tbody></table></div>';
  return html;
}

/* ---------- Ações ---------- */
document.getElementById('calcBtn').addEventListener('click', async () => {
  const nums = parseNumbers(document.getElementById('nums').value);
  const out = document.getElementById('calcResult');
  if (nums.length === 0) { out.innerHTML = '<p class="muted">Informe números.</p>'; return; }
  out.innerHTML = LOADING;
  const data = await postJson('/calculate', { numeros: nums });
  out.innerHTML = formatEstatisticas(data);
  loadHistory();
});

document.getElementById('histBtn').addEventListener('click', async () => {
  const nums = parseNumbers(document.getElementById('histNums').value);
  const bins = parseInt(document.getElementById('bins').value || '0', 10);
  const out = document.getElementById('histResult');
  if (nums.length === 0 || !bins) { out.innerHTML = '<p class="muted">Informe números e bins válidos.</p>'; return; }
  out.innerHTML = LOADING;
  const data = await postJson('/histogram', { numeros: nums, bins });
  out.innerHTML = formatHistograma(data);
  loadHistory();
});

document.getElementById('cmpBtn').addEventListener('click', async () => {
  const n1 = parseNumbers(document.getElementById('nums1').value);
  const n2 = parseNumbers(document.getElementById('nums2').value);
  const out = document.getElementById('cmpResult');
  if (n1.length === 0 || n2.length === 0) { out.innerHTML = '<p class="muted">Informe os dois conjuntos.</p>'; return; }
  out.innerHTML = LOADING;
  const data = await postJson('/compare', { numeros1: n1, numeros2: n2 });
  out.innerHTML = formatComparacao(data);
  loadHistory();
});

/* ---------- Histórico ---------- */
function formatHistorEntry(entry) {
  const timestamp = new Date(entry.timestamp).toLocaleString('pt-BR');
  const typeLabel = {
    calculate: 'Estatísticas',
    histogram: 'Histograma',
    compare: 'Comparação'
  }[entry.type] || entry.type;

  let result = '';
  if (entry.type === 'calculate') {
    result = formatEstatisticas({ Estatisticas: entry.result });
  } else if (entry.type === 'histogram') {
    // Sem gráfico: imagens não são persistidas no histórico.
    result = formatHistograma({ Histograma: entry.result });
  } else if (entry.type === 'compare') {
    result = formatComparacao({ Comparacao: entry.result });
  }

  let html = '<div class="history-entry">';
  html += `<div class="history-top"><span class="badge">${typeLabel}</span><span class="history-time">${timestamp}</span></div>`;
  html += `<small class="history-input">Entrada: ${JSON.stringify(entry.input)}</small>`;
  html += `<div class="history-result">${result}</div></div>`;
  return html;
}

function formatHistory(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;
  if (!data.Historico || data.Historico.length === 0) return '<p class="muted">Nenhum histórico disponível.</p>';

  let html = '<div class="history-list">';
  for (const entry of data.Historico.slice().reverse()) {
    html += formatHistorEntry(entry);
  }
  html += '</div>';
  return html;
}

async function loadHistory() {
  const out = document.getElementById('historyResult');
  out.innerHTML = LOADING;
  const data = await getJson('/history');
  out.innerHTML = formatHistory(data);
}

document.getElementById('loadHistBtn').addEventListener('click', loadHistory);

document.getElementById('clearHistBtn').addEventListener('click', async () => {
  if (!confirm('Tem certeza que deseja limpar o histórico?')) return;
  const res = await fetch('/history/clear', { method: 'DELETE' });
  const data = await res.json();
  if (data.Sucesso) {
    loadHistory();
  } else {
    document.getElementById('historyResult').innerHTML = `<div class="error">Erro: ${data.Erro}</div>`;
  }
});

window.addEventListener('load', loadHistory);
