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

function formatEstatisticas(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;
  
  const stats = data.Estatisticas;
  let html = '<div class="stats-container"><table class="stats-table"><thead>';
  html += '<tr><th>Métrica</th><th>Valor</th></tr></thead><tbody>';
  
  html += `<tr><td class="label">Count:</td><td class="value">${stats.Count}</td></tr>`;
  html += `<tr><td class="label">Mean:</td><td class="value">${stats.Mean}</td></tr>`;
  html += `<tr><td class="label">Median:</td><td class="value">${stats.Median}</td></tr>`;
  html += `<tr><td class="label">Standard Deviation:</td><td class="value">${stats.STD}</td></tr>`;
  html += `<tr><td class="label">Variance:</td><td class="value">${stats.Variance}</td></tr>`;
  html += `<tr><td class="label">Minimum:</td><td class="value">${stats.Min}</td></tr>`;
  html += `<tr><td class="label">Maximum:</td><td class="value">${stats.Max}</td></tr>`;
  html += `<tr><td class="label">Percentile 25%:</td><td class="value">${stats.p25}</td></tr>`;
  html += `<tr><td class="label">Percentile 50%:</td><td class="value">${stats.p50}</td></tr>`;
  html += `<tr><td class="label">Percentile 75%:</td><td class="value">${stats.p75}</td></tr>`;
  
  html += '</tbody></table></div>';
  return html;
}

function formatHistograma(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;
  
  const hist = data.Histograma;
  const intervalos = hist.Intervalos;
  const frequencia = hist.Frequencia;
  
  let html = '<div class="histogram-container"><table class="histogram-table"><thead>';
  html += '<tr><th>Intervalo</th><th>Frequência</th></tr></thead><tbody>';
  
  for (let i = 0; i < frequencia.length; i++) {
    const inicio = intervalos[i].toFixed(2);
    const fim = intervalos[i + 1].toFixed(2);
    html += `<tr><td>${inicio} - ${fim}</td><td>${frequencia[i]}</td></tr>`;
  }
  
  html += '</tbody></table></div>';
  return html;
}

function formatComparacao(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;
  
  const comp = data.Comparacao;
  let html = '<div class="comparison-container"><table class="comparison-table"><thead>';
  html += '<tr><th>Métrica</th><th>Conjunto 1</th><th>Conjunto 2</th></tr></thead><tbody>';
  
  for (const [chave, valores] of Object.entries(comp)) {
    html += `<tr><td class="label">${chave}</td><td>${valores[0]}</td><td>${valores[1]}</td></tr>`;
  }
  
  html += '</tbody></table></div>';
  return html;
}

document.getElementById('calcBtn').addEventListener('click', async () => {
  const nums = parseNumbers(document.getElementById('nums').value);
  const out = document.getElementById('calcResult');
  if (nums.length === 0) { out.textContent = 'Informe números.'; return; }
  out.innerHTML = '<p>Carregando...</p>';
  const data = await postJson('/calculate', { numeros: nums });
  out.innerHTML = formatEstatisticas(data);
});

document.getElementById('histBtn').addEventListener('click', async () => {
  const nums = parseNumbers(document.getElementById('histNums').value);
  const bins = parseInt(document.getElementById('bins').value || '0', 10);
  const out = document.getElementById('histResult');
  if (nums.length === 0 || !bins) { out.textContent = 'Informe números e bins válidos.'; return; }
  out.innerHTML = '<p>Carregando...</p>';
  const data = await postJson('/histogram', { numeros: nums, bins });
  out.innerHTML = formatHistograma(data);
});

document.getElementById('cmpBtn').addEventListener('click', async () => {
  const n1 = parseNumbers(document.getElementById('nums1').value);
  const n2 = parseNumbers(document.getElementById('nums2').value);
  const out = document.getElementById('cmpResult');
  if (n1.length === 0 || n2.length === 0) { out.textContent = 'Informe os dois conjuntos.'; return; }
  out.innerHTML = '<p>Carregando...</p>';
  const data = await postJson('/compare', { numeros1: n1, numeros2: n2 });
  out.innerHTML = formatComparacao(data);
});

async function getJson(path) {
  const res = await fetch(path, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return res.json();
}

function formatHistorEntry(entry) {
  const timestamp = new Date(entry.timestamp).toLocaleString('pt-BR');
  const typeLabel = {
    'calculate': 'Estatísticas',
    'histogram': 'Histograma',
    'compare': 'Comparação'
  }[entry.type] || entry.type;
  
  let html = `<div class="history-entry"><strong>${typeLabel}</strong> - ${timestamp}<br/>`;
  html += `<small>Entrada: ${JSON.stringify(entry.input)}</small>`;
  
  // Formatar resultado baseado no tipo de operação
  let formattedResult = '';
  if (entry.type === 'calculate') {
    const fakeData = { Estatisticas: entry.result };
    formattedResult = formatEstatisticas(fakeData);
  } else if (entry.type === 'histogram') {
    const fakeData = { Histograma: entry.result };
    formattedResult = formatHistograma(fakeData);
  } else if (entry.type === 'compare') {
    const fakeData = { Comparacao: entry.result };
    formattedResult = formatComparacao(fakeData);
  }
  
  html += `<div class="history-result">${formattedResult}</div></div>`;
  return html;
}

function formatHistory(data) {
  if (data.Erro) return `<div class="error">Erro: ${data.Erro}</div>`;
  if (!data.Historico || data.Historico.length === 0) return '<p>Nenhum histórico disponível.</p>';
  
  let html = '<div class="history-container">';
  for (const entry of data.Historico.reverse()) {
    html += formatHistorEntry(entry);
  }
  html += '</div>';
  return html;
}

document.getElementById('loadHistBtn').addEventListener('click', async () => {
  const out = document.getElementById('historyResult');
  out.innerHTML = '<p>Carregando...</p>';
  const data = await getJson('/history');
  out.innerHTML = formatHistory(data);
});

document.getElementById('clearHistBtn').addEventListener('click', async () => {
  if (confirm('Tem certeza que deseja limpar o histórico?')) {
    const res = await fetch('/history/clear', { method: 'DELETE' });
    const data = await res.json();
    if (data.Sucesso) {
      document.getElementById('historyResult').innerHTML = '<p>Histórico limpo.</p>';
    } else {
      document.getElementById('historyResult').innerHTML = `<div class="error">Erro: ${data.Erro}</div>`;
    }
  }
});

window.addEventListener('load', async () => {
  const out = document.getElementById('historyResult');
  const data = await getJson('/history');
  out.innerHTML = formatHistory(data);
});
