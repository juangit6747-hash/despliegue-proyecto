/* ══════════════════════════════════════════════════════════════
   reporte.js — Charts compactos, light minimalista premium
   Requiere: window.CHART_DATA (inyectado desde el template)
   ══════════════════════════════════════════════════════════════ */

// ── Tab switcher ────────────────────────────────────────────────
function switchTab(id, btn) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  btn.classList.add('active');
}

// ── Paleta ──────────────────────────────────────────────────────
const C = {
  blue:   '#2563eb',
  green:  '#16a34a',
  yellow: '#ca8a04',
  red:    '#dc2626',
  purple: '#7c3aed',
  cyan:   '#0891b2',
  slate:  '#64748b',
};

const PALETTE = [C.blue, C.green, C.yellow, C.red, C.purple, C.cyan, C.slate];

// ── Helpers ─────────────────────────────────────────────────────

/** Filtra labels "None" / null / undefined y sus valores asociados */
function cleanSeries(labels, values) {
  const out = { labels: [], values: [] };
  (labels || []).forEach((l, i) => {
    if (l != null && l !== 'None' && l !== '') {
      out.labels.push(l);
      out.values.push((values || [])[i] ?? 0);
    }
  });
  return out;
}

/** Gradiente vertical de área para gráficas de línea */
function areaGrad(ctx, hex, a0 = 0.14, a1 = 0.01) {
  const g = ctx.createLinearGradient(0, 0, 0, 160);
  g.addColorStop(0, hex + Math.round(a0 * 255).toString(16).padStart(2, '0'));
  g.addColorStop(1, hex + Math.round(a1 * 255).toString(16).padStart(2, '0'));
  return g;
}

// ── Estilos base compartidos ─────────────────────────────────────
const FONT = { family: "'DM Sans', sans-serif", size: 11 };

const GRID = {
  color: 'rgba(148,163,184,.12)',
  drawBorder: false,
};

const TOOLTIP = {
  backgroundColor: '#1e293b',
  titleColor: '#f1f5f9',
  bodyColor: '#94a3b8',
  padding: 10,
  cornerRadius: 6,
  titleFont: { ...FONT, weight: '600' },
  bodyFont:  { ...FONT },
  displayColors: true,
  boxWidth: 7, boxHeight: 7, boxPadding: 3,
  caretSize: 5,
};

const LEGEND = {
  position: 'bottom',
  labels: {
    font: FONT,
    color: '#94a3b8',
    padding: 14,
    boxWidth: 8,
    boxHeight: 8,
    usePointStyle: true,
    pointStyleWidth: 8,
  }
};

const SCALE_Y = {
  beginAtZero: true,
  grid: GRID,
  border: { display: false },
  ticks: { font: FONT, color: '#94a3b8', maxTicksLimit: 5 },
};

const SCALE_X = {
  grid: { display: false },
  border: { display: false },
  ticks: { font: FONT, color: '#94a3b8', maxRotation: 0 },
};

// ── Plugin dona: texto central ───────────────────────────────────
Chart.register({
  id: 'centerText',
  beforeDraw(chart) {
    if (chart.config.type !== 'doughnut') return;
    const { ctx, data, chartArea: { top, bottom, left, right } } = chart;
    const cx = (left + right) / 2;
    const cy = (top + bottom) / 2;
    const total = data.datasets[0].data.reduce((a, b) => a + (b || 0), 0);
    ctx.save();
    ctx.font = `700 1.1rem 'DM Sans', sans-serif`;
    ctx.fillStyle = '#0f172a';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total, cx, cy - 6);
    ctx.font = `400 0.6rem 'DM Sans', sans-serif`;
    ctx.fillStyle = '#94a3b8';
    ctx.fillText('total', cx, cy + 8);
    ctx.restore();
  }
});

// ══ PRODUCTOS: stock por producto ════════════════════════════════
(function () {
  const d = window.CHART_DATA;
  const { labels, values } = cleanSeries(d.graf_productos_labels, d.graf_productos_stock);
  const colors = values.map(v => v === 0 ? C.red : v <= 10 ? C.yellow : C.blue);

  new Chart(document.getElementById('chartProductosStock'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Stock',
        data: values,
        backgroundColor: colors.map(c => c + '22'),
        borderColor: colors,
        borderWidth: 1.5,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: { ...TOOLTIP, callbacks: { label: c => ` ${c.parsed.y} uds` } }
      },
      scales: { y: SCALE_Y, x: SCALE_X }
    }
  });
})();

// ══ PRODUCTOS: estado inventario (dona) ══════════════════════════
new Chart(document.getElementById('chartProductosEstado'), {
  type: 'doughnut',
  data: {
    labels: ['Normal', 'Stock bajo', 'Sin stock'],
    datasets: [{
      data: window.CHART_DATA.productos_estado,
      backgroundColor: [C.green + '22', C.yellow + '22', C.red + '22'],
      borderColor:      [C.green,        C.yellow,        C.red],
      borderWidth: 1.5,
      hoverOffset: 5,
    }]
  },
  options: {
    responsive: true,
    cutout: '72%',
    plugins: {
      legend: LEGEND,
      tooltip: { ...TOOLTIP, callbacks: { label: c => ` ${c.label}: ${c.parsed}` } }
    }
  }
});

// ══ CLIENTES: top por compras (barras horizontales) ══════════════
(function () {
  const d = window.CHART_DATA;
  const { labels, values } = cleanSeries(d.graf_clientes_labels, d.graf_clientes_valores);

  new Chart(document.getElementById('chartClientesTop'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Total ($)',
        data: values,
        backgroundColor: C.blue + '18',
        borderColor: C.blue,
        borderWidth: 1.5,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { ...TOOLTIP, callbacks: { label: c => ` $${c.parsed.x.toLocaleString('es-CO')}` } }
      },
      scales: {
        x: { ...SCALE_Y, ticks: { ...SCALE_Y.ticks, callback: v => '$' + (v >= 1000 ? (v / 1000) + 'K' : v) } },
        y: SCALE_X
      }
    }
  });
})();

// ══ CLIENTES: activos vs inactivos (dona) ════════════════════════
new Chart(document.getElementById('chartClientesEstado'), {
  type: 'doughnut',
  data: {
    labels: ['Activos', 'Inactivos'],
    datasets: [{
      data: [window.CHART_DATA.clientes_activos, window.CHART_DATA.clientes_inactivos],
      backgroundColor: [C.green + '22', C.red + '22'],
      borderColor:     [C.green,        C.red],
      borderWidth: 1.5,
      hoverOffset: 5,
    }]
  },
  options: {
    responsive: true,
    cutout: '72%',
    plugins: { legend: LEGEND, tooltip: { ...TOOLTIP } }
  }
});

// ══ VENTAS: por día (línea) ══════════════════════════════════════
let ventasChart;
(function () {
  const d = window.CHART_DATA;
  const { labels, values } = cleanSeries(d.graf_ventas_labels, d.graf_ventas_valores);
  const canvas = document.getElementById('chartVentasDia');
  const ctx = canvas.getContext('2d');

  ventasChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Ventas ($)',
        data: values,
        borderColor: C.blue,
        backgroundColor: areaGrad(ctx, '#2563eb'),
        borderWidth: 2,
        pointBackgroundColor: '#fff',
        pointBorderColor: C.blue,
        pointBorderWidth: 1.5,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.4,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { ...TOOLTIP, callbacks: { label: c => ` $${c.parsed.y.toLocaleString('es-CO')}` } }
      },
      scales: {
        y: { ...SCALE_Y, ticks: { ...SCALE_Y.ticks, callback: v => '$' + (v >= 1000 ? (v / 1000) + 'K' : v) } },
        x: SCALE_X
      }
    }
  });
})();

// ══ VENTAS: estado (dona) ════════════════════════════════════════
new Chart(document.getElementById('chartVentasEstado'), {
  type: 'doughnut',
  data: {
    labels: ['Completadas', 'Pendientes'],
    datasets: [{
      data: [window.CHART_DATA.ventas_completadas, window.CHART_DATA.ventas_pendientes],
      backgroundColor: [C.green + '22', C.yellow + '22'],
      borderColor:     [C.green,        C.yellow],
      borderWidth: 1.5,
      hoverOffset: 5,
    }]
  },
  options: {
    responsive: true,
    cutout: '72%',
    plugins: { legend: LEGEND, tooltip: { ...TOOLTIP } }
  }
});

// ══ PROVEEDORES: compras por proveedor ═══════════════════════════
(function () {
  const d = window.CHART_DATA;
  const { labels, values } = cleanSeries(d.graf_proveedores_labels, d.graf_proveedores_valores);

  new Chart(document.getElementById('chartProveedores'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Compras',
        data: values,
        backgroundColor: PALETTE.map(c => c + '1e'),
        borderColor:     PALETTE,
        borderWidth: 1.5,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { ...TOOLTIP, callbacks: { label: c => ` ${c.parsed.y} compras` } }
      },
      scales: { y: { ...SCALE_Y, ticks: { ...SCALE_Y.ticks, stepSize: 1 } }, x: SCALE_X }
    }
  });
})();

// ══ COMPRAS: por día (línea) ═════════════════════════════════════
(function () {
  const d = window.CHART_DATA;
  const { labels, values } = cleanSeries(d.graf_compras_labels, d.graf_compras_valores);
  const canvas = document.getElementById('chartComprasDia');
  const ctx = canvas.getContext('2d');

  new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Compras',
        data: values,
        borderColor: C.purple,
        backgroundColor: areaGrad(ctx, '#7c3aed'),
        borderWidth: 2,
        pointBackgroundColor: '#fff',
        pointBorderColor: C.purple,
        pointBorderWidth: 1.5,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.4,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: { ...TOOLTIP, callbacks: { label: c => ` ${c.parsed.y} compras` } }
      },
      scales: { y: { ...SCALE_Y, ticks: { ...SCALE_Y.ticks, stepSize: 1 } }, x: SCALE_X }
    }
  });
})();

// ══ COMPRAS: estado (dona) ═══════════════════════════════════════
new Chart(document.getElementById('chartComprasEstado'), {
  type: 'doughnut',
  data: {
    labels: ['Completadas', 'Pendientes'],
    datasets: [{
      data: [window.CHART_DATA.compras_completadas, window.CHART_DATA.compras_pendientes],
      backgroundColor: [C.green + '22', C.yellow + '22'],
      borderColor:     [C.green,        C.yellow],
      borderWidth: 1.5,
      hoverOffset: 5,
    }]
  },
  options: {
    responsive: true,
    cutout: '72%',
    plugins: { legend: LEGEND, tooltip: { ...TOOLTIP } }
  }
});

// ══ TODO: Ventas vs Compras ══════════════════════════════════════
let todoChart;
(function () {
  const d = window.CHART_DATA;
  const ventas  = cleanSeries(d.graf_todo_labels, d.graf_todo_ventas);
  const compras = cleanSeries(d.graf_todo_labels, d.graf_todo_compras);
  const labels  = ventas.labels.length >= compras.labels.length ? ventas.labels : compras.labels;

  todoChart = new Chart(document.getElementById('chartTodo'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Ventas ($)',
          data: ventas.values,
          backgroundColor: C.blue + '22',
          borderColor: C.blue,
          borderWidth: 1.5,
          borderRadius: 5,
          borderSkipped: false,
        },
        {
          label: 'Compras',
          data: compras.values,
          backgroundColor: C.purple + '22',
          borderColor: C.purple,
          borderWidth: 1.5,
          borderRadius: 5,
          borderSkipped: false,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: LEGEND, tooltip: { ...TOOLTIP } },
      scales: { y: SCALE_Y, x: SCALE_X }
    }
  });
})();

// ══ Polling 30s ══════════════════════════════════════════════════
function actualizarDatos() {
  fetch('/reportes/data/')
    .then(r => r.json())
    .then(data => {
      document.getElementById('kpi-ventas-mes').textContent    = '$ ' + Math.round(data.total_ventas_mes).toLocaleString('es-CO');
      document.getElementById('kpi-transacciones').textContent = data.transacciones_mes + ' transacciones';
      document.getElementById('kpi-ingreso-total').textContent = '$ ' + Math.round(data.ingreso_total).toLocaleString('es-CO');
      document.getElementById('kpi-stock-bajo').textContent    = data.stock_bajo + ' con stock bajo';

      const v = cleanSeries(data.grafica_labels, data.grafica_valores);
      ventasChart.data.labels = v.labels;
      ventasChart.data.datasets[0].data = v.values;
      ventasChart.update('active');

      const t = cleanSeries(data.grafica_labels, data.grafica_valores);
      todoChart.data.labels = t.labels;
      todoChart.data.datasets[0].data = t.values;
      todoChart.update('active');

      const c = document.getElementById('alertas-container');
      if (c && data.alertas?.length)
        c.innerHTML = data.alertas.map(a =>
          `<div class="alerta-item alerta-${a.estado}">
             <span class="alerta-dot dot-${a.estado}"></span>
             ${a.nombre} — ${a.estado === 'out' ? 'Sin stock' : a.stock + ' uds'}
           </div>`
        ).join('');
    })
    .catch(e => console.warn('[reportes] Error al actualizar:', e));
}

setInterval(actualizarDatos, 30000);