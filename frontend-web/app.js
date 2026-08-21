/* ═══════════════════════════════════════════════════════
   Wealify Smart Finance — Frontend App Logic
   ═══════════════════════════════════════════════════════ */

const API = 'http://localhost:8000';
let lang = 'vi';
let dashboardData = {};

// ─── i18n ──────────────────────────────────────────
const i18n = {
  vi: {
    nav_overview: 'Tổng quan', nav_reconcile: 'Đối chiếu', nav_safety: 'An toàn',
    nav_findings: 'Findings', btn_scan: 'Rà soát định kỳ', btn_export: 'Xuất nhật ký',
    btn_refresh: 'Làm mới dữ liệu', btn_send: 'Gửi',
    hero_subtitle: 'AI Dashboard soi sao kê · Quản lý chi tiêu & An toàn giao dịch cho Seller Cross-Border',
    metric_income: 'HOÀN TIỀN', metric_spending: 'TỔNG CHI TIÊU', metric_fees: 'TỔNG PHÍ',
    metric_wallet: 'SỐ DƯ VÍ (WEALIFY)',
    disclaimer: '⚠️ Công cụ này chỉ hỗ trợ bạn rà soát tài chính. Kết quả để tham khảo, không phải kết luận chính thức của Wealify và không thay cho việc bạn tự kiểm tra. Nếu thấy giao dịch lạ, hãy liên hệ hỗ trợ ngay — ở Mỹ thời hạn khiếu nại là 60 ngày kể từ ngày ngân hàng gửi sao kê.',
    chat_placeholder: 'Nhập câu hỏi...',
    quick_btns: [
      ['📊 Tổng chi tháng này', 'Tháng này tôi chi bao nhiêu, phí bao nhiêu, 3 khoản lớn nhất là gì?'],
      ['📧 Đối soát email', 'Đối soát giao dịch với email biên lai'],
      ['🔍 Đối chiếu 3 nguồn', 'Có tiền nào rời tài khoản mà chưa thấy lên thẻ không?'],
      ['📋 Gói đăng ký', 'Mình đang có những gói đăng ký định kỳ nào, gói nào vừa tăng giá?'],
      ['🔁 Khoản trùng', 'Có khoản nào bị tính hai lần / phí kép không?'],
      ['⏰ Nhắc hạn 60 ngày', 'Khoản nào sắp hết hạn khiếu nại 60 ngày?'],
      ['🔍 Rà soát toàn bộ', 'Chạy kiểm tra toàn bộ tài khoản'],
    ],
  },
  en: {
    nav_overview: 'Overview', nav_reconcile: 'Reconciliation', nav_safety: 'Safety',
    nav_findings: 'Findings', btn_scan: 'Scheduled Scan', btn_export: 'Export Audit Log',
    btn_refresh: 'Refresh Data', btn_send: 'Send',
    hero_subtitle: 'AI Statement Scanner · Expense Management & Transaction Safety for Cross-Border Sellers',
    metric_income: 'REFUNDS', metric_spending: 'TOTAL SPENDING', metric_fees: 'TOTAL FEES',
    metric_wallet: 'WALLET BALANCE (WEALIFY)',
    disclaimer: '⚠️ This tool assists you in reviewing finances. Results are for reference only, not official Wealify conclusions. If you spot suspicious transactions, contact support — in the US, the dispute deadline is 60 days from statement date.',
    chat_placeholder: 'Ask a question...',
    quick_btns: [
      ['📊 Monthly overview', 'How much did I spend this month? Top 3 charges?'],
      ['📧 Email cross-check', 'Cross-check transactions with email receipts'],
      ['🔍 3-source reconcile', 'Any money left the account but hasn\'t reached the card?'],
      ['📋 Subscriptions', 'What subscriptions do I have? Any price increases?'],
      ['🔁 Duplicates', 'Are there any duplicate charges or double fees?'],
      ['⏰ Dispute deadlines', 'Any items approaching the 60-day dispute deadline?'],
      ['🔍 Full scan', 'Run a complete check on my account'],
    ],
  }
};

// ─── API Helpers ───────────────────────────────────
async function apiGet(endpoint) {
  try {
    const res = await fetch(`${API}${endpoint}`);
    return await res.json();
  } catch { return null; }
}

async function apiPost(endpoint, body = {}) {
  try {
    const res = await fetch(`${API}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return await res.json();
  } catch { return null; }
}

// ─── Tab Navigation ───────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelector(`.nav-item[data-tab="${tab}"]`).classList.add('active');
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.getElementById(`tab-${tab}`).classList.add('active');
}

// ─── Language ─────────────────────────────────────
function setLang(l) {
  lang = l;
  document.querySelectorAll('.lang-toggle button').forEach(b => b.classList.remove('active'));
  document.querySelector(`.lang-toggle button:${l === 'vi' ? 'first-child' : 'last-child'}`).classList.add('active');
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (i18n[l][key]) el.textContent = i18n[l][key];
  });
  document.getElementById('disclaimerBar').textContent = i18n[l].disclaimer;
  document.getElementById('chatInput').placeholder = i18n[l].chat_placeholder;
  renderQuickBtns();
  loadAll();
}

// ─── Format Helpers ───────────────────────────────
const fmt = (n) => `$${Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
// Live statement mixes currencies (VND payin, USD/EUR card spend) — the
// backend groups summary/top3/monthly by currency instead of summing them
// together (which would be meaningless without a fake conversion rate).
const CURRENCY_SYMBOLS = { USD: '$', EUR: '€' };
// VND on Wealify's own site reads "274,436,000 VND" — no decimals, code as
// a suffix, not a symbol prefix — matched exactly so this number is
// directly comparable to what's on the real page.
const fmtCur = (n, currency) => currency === 'VND'
  ? `${Math.round(Math.abs(n)).toLocaleString('en-US')} VND`
  : `${CURRENCY_SYMBOLS[currency] || currency + ' '}${Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

function labelBadge(label) {
  const map = {
    'DINH_KY_DA_XAC_DINH': ['badge-confirmed', lang === 'vi' ? 'Định kỳ đã xác định' : 'Confirmed recurring'],
    'CAN_BAN_TU_XAC_NHAN': ['badge-review', lang === 'vi' ? 'Cần bạn tự xác nhận' : 'Needs confirmation'],
    'CHUA_DU_DU_LIEU': ['badge-insufficient', lang === 'vi' ? 'Chưa đủ dữ liệu' : 'Insufficient data'],
  };
  const [cls, text] = map[label] || ['badge-insufficient', label];
  return `<span class="finding-badge ${cls}">${text}</span>`;
}

function severityClass(rank) {
  return rank === 1 ? 'critical' : rank === 2 ? 'warning' : 'info';
}

// ─── Load Dashboard Data ──────────────────────────
async function loadAll() {
  const [health, overview, risk, anomalies, recon, emailsData, report, findings, txns, wallet] = await Promise.all([
    apiGet('/health'),
    apiGet('/dashboard/overview'),
    apiGet('/dashboard/risk-score'),
    apiGet('/dashboard/anomalies'),
    apiGet('/dashboard/reconciliation'),
    apiGet('/dashboard/email-matches'),
    apiGet('/dashboard/report'),
    apiGet('/findings'),
    apiGet('/dashboard/transactions'),
    apiGet('/dashboard/wallet'),
  ]);
  const emails = emailsData ? emailsData.matches : [];
  dashboardData = { health, overview, risk, anomalies, recon, emails, report, findings, txns, wallet };

  // Update status dot
  const dot = document.querySelector('.status-dot');
  dot.className = `status-dot ${health ? 'online' : 'offline'}`;

  renderMetrics(overview, risk, report, wallet);
  renderOverview(overview, report, anomalies);
  renderReconcile(recon, emails);
  renderSafety(anomalies);
  renderFindings(findings);
}

// ─── Render Metrics ───────────────────────────────
function renderMetrics(overview, risk, report, wallet) {
  if (!overview) return;
  // overview.summary is {currency: {label: value}} — each currency gets its
  // own line (never summed together, which would need a fake FX rate).
  const summaryByCurrency = overview.summary || {};
  const pick = (group, viKey, enKey) => (group[viKey] ?? group[enKey] ?? 0);
  const stackAcrossCurrencies = (viKey, enKey) => {
    const entries = Object.entries(summaryByCurrency);
    if (!entries.length) return fmt(0);
    return entries
      .map(([currency, group]) => {
        const amount = fmtCur(pick(group, viKey, enKey), currency);
        // Wealify web format: "$12,555.56" / "€1,421.39" / "274,436,000 VND"
        // — no redundant ISO prefix when symbol is already present.
        return `<span class="cur-line">${amount}</span>`;
      })
      .join('');
  };

  document.getElementById('metricIncome').innerHTML = stackAcrossCurrencies('Tổng tiền vào', 'Total Income');
  document.getElementById('metricSpending').innerHTML = stackAcrossCurrencies('Tổng chi tiêu', 'Total Spending');
  document.getElementById('metricFees').innerHTML = stackAcrossCurrencies('Tổng phí', 'Total Fees');
  // The one figure that's directly verifiable against the real Wealify
  // site (confirmed against a live screenshot) is the wallet balance —
  // show it plainly so there's always a number on this dashboard that
  // matches Wealify's own page.
  const walletEl = document.getElementById('metricWallet');
  if (walletEl) {
    if (wallet && typeof wallet.wallet_balance === 'number') {
      walletEl.textContent = fmtCur(wallet.wallet_balance, wallet.currency || 'VND');
    } else {
      walletEl.textContent = '—';
    }
  }

  if (risk) {
    const score = risk.total_score || 0;
    document.getElementById('metricRisk').textContent = `${score}/100`;
    document.getElementById('metricRiskLevel').innerHTML =
      `<span style="color:${risk.color || '#ef4444'}">${lang === 'vi' ? risk.level_vi : risk.level}</span>`;
  }
}

// ─── Render Overview Tab ──────────────────────────
function renderOverview(overview, report, anomalies) {
  if (!overview) return;
  const el = document.getElementById('tab-overview');

  // Top 3 — per currency (top3_largest is {currency: [...]})
  const top3ByCurrency = overview.top3_largest || {};
  const medals = ['🥇', '🥈', '🥉'];
  let top3Html = '<div class="section"><div class="section-header"><span class="section-icon">🏆</span>' +
    (lang === 'vi' ? 'Top 3 khoản lớn nhất' : 'Top 3 Largest Charges') + '</div>';
  for (const [currency, top3] of Object.entries(top3ByCurrency)) {
    if (!top3.length) continue;
    top3Html += `<div class="finding-meta" style="margin:8px 0 4px">[${currency}]</div><div class="grid-3">`;
    top3.forEach((t, i) => {
      top3Html += `<div class="top3-card">
        <div class="top3-medal">${medals[i]}</div>
        <div class="top3-desc">${t.description}</div>
        <div class="top3-amount">${fmtCur(t.amount, currency)}</div>
        <div class="top3-date">📅 ${t.date}</div>
      </div>`;
    });
    top3Html += '</div>';
  }
  top3Html += '</div>';

  // Monthly Breakdown Chart — per currency (monthly_breakdown is {currency: {month: {...}}})
  const monthlyByCurrency = overview.monthly_breakdown || {};
  let chartHtml = '<div class="section"><div class="section-header"><span class="section-icon">📅</span>' +
    (lang === 'vi' ? 'Chi tiêu theo tháng' : 'Monthly Spending') + '</div>';
  for (const [currency, monthly] of Object.entries(monthlyByCurrency)) {
    const maxSpend = Math.max(...Object.values(monthly).map(m => m.spending || 0), 1);
    chartHtml += `<div class="card"><div class="finding-meta" style="margin-bottom:4px">[${currency}]</div><div class="risk-breakdown">`;
    for (const [month, data] of Object.entries(monthly).sort()) {
      const pct = ((data.spending || 0) / maxSpend * 100).toFixed(0);
      chartHtml += `<div class="risk-bar-container">
        <span class="risk-bar-label">${month}</span>
        <div class="risk-bar-track"><div class="risk-bar-fill warning" style="width:${pct}%"></div></div>
        <span class="risk-bar-value">${fmtCur(data.spending || 0, currency)}</span>
      </div>`;
    }
    chartHtml += '</div></div>';
  }
  chartHtml += '</div>';

  // Quarterly & Yearly — per currency (quarterly_breakdown/yearly_breakdown are {currency: {period: {...}}})
  let qyHtml = '';
  if (report) {
    const quarterlyByCurrency = report.quarterly_breakdown || {};
    const yearlyByCurrency = report.yearly_breakdown || {};
    qyHtml = '<div class="grid-2">';

    // Quarterly
    qyHtml += '<div class="section"><div class="section-header"><span class="section-icon">📅</span>' +
      (lang === 'vi' ? 'Báo cáo quý' : 'Quarterly Report') + '</div>';
    for (const [currency, quarterly] of Object.entries(quarterlyByCurrency)) {
      qyHtml += `<div class="finding-meta" style="margin:6px 0 4px">[${currency}]</div>`;
      for (const [q, d] of Object.entries(quarterly).sort()) {
        const netColor = d.net >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
        qyHtml += `<div class="finding-item info" style="margin-bottom:8px">
          <div class="finding-title">${q}</div>
          <div class="finding-detail" style="display:flex;gap:14px;margin-top:6px">
            <span style="color:var(--accent-green)">Thu: ${fmtCur(d.income, currency)}</span>
            <span style="color:var(--accent-red)">Chi: ${fmtCur(d.spending, currency)}</span>
            <span style="color:var(--accent-yellow)">Phí: ${fmtCur(d.fees, currency)}</span>
            <span style="color:${netColor};font-weight:700">Ròng: ${fmtCur(d.net, currency)}</span>
          </div>
        </div>`;
      }
    }
    qyHtml += '</div>';

    // Yearly
    qyHtml += '<div class="section"><div class="section-header"><span class="section-icon">📆</span>' +
      (lang === 'vi' ? 'Báo cáo năm' : 'Yearly Report') + '</div>';
    for (const [currency, yearly] of Object.entries(yearlyByCurrency)) {
      qyHtml += `<div class="finding-meta" style="margin:6px 0 4px">[${currency}]</div>`;
      for (const [y, d] of Object.entries(yearly).sort()) {
        const netColor = d.net >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
        qyHtml += `<div class="finding-item info" style="margin-bottom:8px">
          <div class="finding-title">${y}</div>
          <div class="finding-detail" style="display:flex;gap:14px;margin-top:6px">
            <span style="color:var(--accent-green)">Thu: ${fmtCur(d.income, currency)}</span>
            <span style="color:var(--accent-red)">Chi: ${fmtCur(d.spending, currency)}</span>
            <span style="color:var(--accent-yellow)">Phí: ${fmtCur(d.fees, currency)}</span>
            <span style="color:${netColor};font-weight:700">Ròng: ${fmtCur(d.net, currency)}</span>
          </div>
        </div>`;
      }
    }
    qyHtml += '</div></div>';
  }

  // Subscriptions
  let subsHtml = '';
  if (anomalies && anomalies.subscriptions) {
    subsHtml = '<div class="section"><div class="section-header"><span class="section-icon">📋</span>' +
      (lang === 'vi' ? 'Gói đăng ký định kỳ' : 'Active Subscriptions') + '</div><div class="finding-list">';
    anomalies.subscriptions.forEach(s => {
      subsHtml += `<div class="finding-item safe">
        <div class="finding-header">
          <div class="finding-title">${s.description}</div>
          <span style="color:var(--accent-blue);font-size:18px;font-weight:700">${fmt(s.current_price)}</span>
        </div>
        <div class="finding-detail">${s.explanation || ''}</div>
        <div class="finding-meta">
          <span>📅 ${lang === 'vi' ? 'Kỳ kế tiếp' : 'Next'}: ${s.next_charge_date}</span>
          <span>🔄 ${s.frequency}</span>
          <span>×${s.occurrences} ${lang === 'vi' ? 'lần' : 'times'}</span>
        </div>
      </div>`;
    });
    subsHtml += '</div></div>';
  }

  // Transaction Table
  let tableHtml = '';
  if (dashboardData.txns) {
    const txns = dashboardData.txns.account_transactions || [];
    tableHtml = '<div class="section"><div class="section-header"><span class="section-icon">📋</span>' +
      (lang === 'vi' ? 'Bảng giao dịch' : 'Transaction Table') + '</div>' +
      '<div class="card" style="overflow-x:auto;padding:0"><table class="data-table"><thead><tr>' +
      '<th>' + (lang === 'vi' ? 'Ngày' : 'Date') + '</th>' +
      '<th>' + (lang === 'vi' ? 'Mô tả' : 'Description') + '</th>' +
      '<th>' + (lang === 'vi' ? 'Loại' : 'Type') + '</th>' +
      '<th>' + (lang === 'vi' ? 'Số tiền' : 'Amount') + '</th>' +
      '<th>' + (lang === 'vi' ? 'Số dư' : 'Balance') + '</th>' +
      '</tr></thead><tbody>';
    txns.slice(0, 30).forEach(t => {
      const amtClass = t.amount >= 0 ? 'amount-positive' : 'amount-negative';
      tableHtml += `<tr>
        <td>${t.date}</td>
        <td>${t.description}</td>
        <td><span style="opacity:0.7">${t.type}</span></td>
        <td class="${amtClass}">${fmt(t.amount)}</td>
        <td>${fmt(t.balance || 0)}</td>
      </tr>`;
    });
    tableHtml += '</tbody></table></div></div>';
  }

  el.innerHTML = top3Html + chartHtml + qyHtml + subsHtml + tableHtml;
}

// ─── Render Reconcile Tab ─────────────────────────
function renderReconcile(recon, emails) {
  const el = document.getElementById('tab-reconcile');
  let html = '';

  if (recon) {
    const nDisc = recon.total_discrepancies || 0;
    html += `<div class="section"><div class="section-header"><span class="section-icon">🔍</span>
      ${lang === 'vi' ? `Đối chiếu 3 nguồn — ${nDisc} lệch` : `3-Source Reconciliation — ${nDisc} discrepancies`}</div>
      <div class="finding-list">`;
    (recon.discrepancies || []).forEach(d => {
      html += `<div class="finding-item warning">
        <div class="finding-title">${d.type || d.description || 'Discrepancy'}</div>
        <div class="finding-detail">${d.detail || d.explanation || ''}</div>
        <div class="finding-meta"><span>${labelBadge('CAN_BAN_TU_XAC_NHAN')}</span></div>
      </div>`;
    });
    html += '</div></div>';
  }

  if (emails) {
    html += `<div class="section"><div class="section-header"><span class="section-icon">📧</span>
      ${lang === 'vi' ? 'Đối soát email' : 'Email Cross-Check'}</div><div class="finding-list">`;
    (emails || []).forEach(m => {
      const statusIcon = m.match_status === 'matched' ? '✅' : m.match_status === 'suspicious_email' ? '🚨' : '❓';
      const cls = m.match_status === 'matched' ? 'safe' : m.match_status === 'suspicious_email' ? 'critical' : 'warning';
      html += `<div class="finding-item ${cls}">
        <div class="finding-header">
          <div class="finding-title">${statusIcon} ${m.description}</div>
          <span style="color:var(--accent-blue);font-weight:600">${fmt(m.amount)}</span>
        </div>
        <div class="finding-detail">${m.match_status === 'matched' ? (m.matched_email?.subject || 'Email khớp') :
          m.match_status === 'suspicious_email' ? (m.suspicious_reasons?.join('; ') || 'Email nghi giả') :
          (lang === 'vi' ? 'Không tìm thấy email khớp' : 'No matching email found')}</div>
        <div class="finding-meta"><span>📅 ${m.date}</span></div>
      </div>`;
    });
    html += '</div></div>';
  }

  el.innerHTML = html || '<div class="loading-overlay">No data</div>';
}

// ─── Render Safety Tab ────────────────────────────
function renderSafety(anomalies) {
  const el = document.getElementById('tab-safety');
  if (!anomalies) { el.innerHTML = '<div class="loading-overlay">No data</div>'; return; }
  let html = '';

  // Risk breakdown
  const risk = dashboardData.risk;
  if (risk && risk.breakdown) {
    html += `<div class="section"><div class="section-header"><span class="section-icon">⚠️</span>
      Risk Score: ${risk.total_score}/100 — <span style="color:${risk.color}">${lang === 'vi' ? risk.level_vi : risk.level}</span></div>
      <div class="card"><div class="risk-breakdown">`;
    for (const [key, val] of Object.entries(risk.breakdown)) {
      const pct = (val.score / val.max * 100).toFixed(0);
      const cls = pct >= 80 ? 'critical' : pct >= 50 ? 'warning' : 'safe';
      html += `<div class="risk-bar-container">
        <span class="risk-bar-label">${key}</span>
        <div class="risk-bar-track"><div class="risk-bar-fill ${cls}" style="width:${pct}%"></div></div>
        <span class="risk-bar-value">${val.score}/${val.max}</span>
      </div>`;
    }
    html += '</div></div></div>';
  }

  // Unknown merchants
  const unknown = anomalies.unknown_merchants || [];
  if (unknown.length) {
    html += `<div class="section"><div class="section-header"><span class="section-icon">❓</span>
      ${lang === 'vi' ? `Khoản lạ — ${unknown.length}` : `Unknown Merchants — ${unknown.length}`}</div><div class="finding-list">`;
    unknown.forEach(u => {
      html += `<div class="finding-item warning">
        <div class="finding-header">
          <div class="finding-title">${u.description}</div>
          <span style="color:var(--accent-red);font-weight:700">${fmt(u.amount)}</span>
        </div>
        <div class="finding-detail">${u.explanation || 'chưa xác định được'}</div>
        <div class="finding-meta">
          <span>📅 ${u.date}</span>
          <span>${labelBadge(u.label === 'Cần bạn tự xác nhận' ? 'CAN_BAN_TU_XAC_NHAN' : 'CHUA_DU_DU_LIEU')}</span>
        </div>
      </div>`;
    });
    html += '</div></div>';
  }

  // Duplicates
  const dupes = anomalies.duplicate_charges || [];
  if (dupes.length) {
    html += `<div class="section"><div class="section-header"><span class="section-icon">🔁</span>
      ${lang === 'vi' ? `Khoản trùng — ${dupes.length}` : `Duplicates — ${dupes.length}`}</div><div class="finding-list">`;
    dupes.forEach(d => {
      html += `<div class="finding-item critical">
        <div class="finding-header">
          <div class="finding-title">${d.description}</div>
          <span style="color:var(--accent-red);font-weight:700">${fmt(d.amount)}</span>
        </div>
        <div class="finding-detail">${lang === 'vi' ? 'Trùng với' : 'Duplicate of'}: ${d.duplicate_of}</div>
        <div class="finding-meta"><span>📅 ${d.date}</span> ${labelBadge('CAN_BAN_TU_XAC_NHAN')}</div>
      </div>`;
    });
    html += '</div></div>';
  }

  // Price hikes
  const hikes = anomalies.price_hikes || [];
  if (hikes.length) {
    html += `<div class="section"><div class="section-header"><span class="section-icon">📈</span>
      ${lang === 'vi' ? `Tăng giá âm thầm — ${hikes.length}` : `Silent Price Increases — ${hikes.length}`}</div><div class="finding-list">`;
    hikes.forEach(h => {
      html += `<div class="finding-item warning">
        <div class="finding-header">
          <div class="finding-title">⚠️ ${h.merchant}</div>
        </div>
        <div class="finding-detail" style="font-size:16px;margin:8px 0">
          ${fmt(h.old_price)} → ${fmt(h.new_price)}
          <span style="color:var(--accent-red);font-weight:600"> (+${fmt(h.increase)}, +${h.increase_pct}%)</span>
        </div>
        <div class="finding-detail">${h.explanation || ''}</div>
      </div>`;
    });
    html += '</div></div>';
  }

  el.innerHTML = html || '<div class="loading-overlay">No issues found</div>';
}

// ─── Render Findings Tab ──────────────────────────
function renderFindings(findingsData) {
  const el = document.getElementById('tab-findings');
  if (!findingsData || !findingsData.findings) {
    el.innerHTML = '<div class="loading-overlay"><div class="spinner"></div> Loading...</div>';
    return;
  }

  const findings = findingsData.findings;
  let html = `<div class="section"><div class="section-header"><span class="section-icon">🎯</span>
    ${lang === 'vi' ? `Findings chuẩn PDF — ${findings.length} mục` : `PDF-Compliant Findings — ${findings.length} items`}</div>
    <div class="finding-list">`;

  findings.forEach(f => {
    const cls = severityClass(f.severity_rank);
    const titleKey = lang === 'vi' ? 'title_vi' : 'title_en';
    const explKey = lang === 'vi' ? 'explanation_vi' : 'explanation_en';
    html += `<div class="finding-item ${cls}">
      <div class="finding-header">
        <div class="finding-title">${f[titleKey] || f.title_vi}</div>
        ${labelBadge(f.label)}
      </div>
      <div class="finding-detail">${f[explKey] || f.explanation_vi || ''}</div>
      <div class="finding-meta">
        <span>📅 ${f.occurred_at || ''}</span>
        <span>🏷️ ${f.label_rule_id || ''}</span>
        <span>📊 conf: ${f.confidence}</span>
        <span>⏰ ${lang === 'vi' ? 'Hạn' : 'Deadline'}: ${f.dispute_deadline || '—'} (${f.days_left != null ? f.days_left + (lang === 'vi' ? ' ngày' : ' days') : '—'})</span>
        <span>🔐 ${f.fingerprint?.substring(0, 20) || ''}</span>
      </div>
    </div>`;
  });

  html += '</div></div>';
  el.innerHTML = html;
}

// ─── Quick Buttons ────────────────────────────────
function renderQuickBtns() {
  const container = document.getElementById('chatQuickBtns');
  const btns = i18n[lang].quick_btns;
  container.innerHTML = btns.map(([label, q]) =>
    `<button class="quick-btn" onclick="sendChatMsg('${q.replace(/'/g, "\\'")}')">${label}</button>`
  ).join('');
}

// ─── Chat ─────────────────────────────────────────
function addChatMsg(text, type) {
  const el = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `chat-msg ${type}`;
  // Simple markdown-like rendering
  div.innerHTML = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code style="background:rgba(255,255,255,0.08);padding:1px 5px;border-radius:3px">$1</code>')
    .replace(/\n/g, '<br>');
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  addChatMsg(msg, 'user');

  // Show typing
  const typingId = 'typing-' + Date.now();
  const msgsEl = document.getElementById('chatMessages');
  const typing = document.createElement('div');
  typing.id = typingId;
  typing.className = 'chat-msg bot';
  // A "..." spinner for up to ~18s (real DeepSeek reasoning-model latency
  // for complex questions) reads as stuck — a short status line makes it
  // clear it's still actively working.
  const thinkingText = lang === 'vi' ? 'Đang phân tích...' : 'Analyzing...';
  typing.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px"></div> ${thinkingText}`;
  msgsEl.appendChild(typing);
  msgsEl.scrollTop = msgsEl.scrollHeight;

  const res = await apiPost('/chat', { message: msg });
  typing.remove();

  if (res && res.response) {
    addChatMsg(res.response, 'bot');
  } else {
    addChatMsg('❌ ' + (lang === 'vi' ? 'Lỗi kết nối backend' : 'Backend connection error'), 'bot');
  }
}

function sendChatMsg(msg) {
  document.getElementById('chatInput').value = msg;
  sendChat();
}

// ─── Sidebar Actions ──────────────────────────────
async function runScheduledCheck() {
  const btn = event.target.closest('.sidebar-btn');
  btn.innerHTML = '<div class="spinner" style="width:14px;height:14px;border-width:2px"></div> ...';
  const res = await apiPost('/scheduled-check', {});
  if (res) {
    const msg = lang === 'vi'
      ? `✅ Hoàn tất! ${res.new_flags} cảnh báo mới, ${res.already_reported} đã báo trước.`
      : `✅ Done! ${res.new_flags} new flags, ${res.already_reported} already reported.`;
    alert(msg);
    loadAll();
  }
  btn.innerHTML = `🔍 <span>${i18n[lang].btn_scan}</span>`;
}

async function exportAuditLog() {
  const res = await apiGet('/audit-log/export');
  if (res) {
    alert(lang === 'vi' ? `✅ Đã xuất: ${res.exported_to}` : `✅ Exported: ${res.exported_to}`);
  }
}

async function refreshData() {
  await apiPost('/reset', {});
  loadAll();
}

// ─── Init ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setLang('vi');
  renderQuickBtns();
  loadAll();
});
