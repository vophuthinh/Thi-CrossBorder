/* ═══════════════════════════════════════════════════════
   Wealify Scout — UI interactivity (vanilla JS)
   Wired to the real backend (no mock data) — every number here comes from
   GET /findings, /dashboard/wallet, /dashboard/wealify-accounts, and
   POST /chat, all fetched live from the running FastAPI backend.
   ═══════════════════════════════════════════════════════ */

const API = '';

// ─── i18n dictionary (UI chrome text only — live data is rendered
// directly from bilingual fields the backend already provides, e.g.
// finding.title_vi / finding.title_en) ───────────────────────────
const I18N = {
    en: {
        brand_sub: 'AI financial review',

        panel_command: 'Command Center',
        panel_hint_live: 'Live review',
        export_audit: 'Export log',
        export_done: 'Audit log exported to',
        export_failed: 'Export failed — check the backend is running.',
        reminder_settings: 'Reminders',
        run_check: 'Run check',
        run_check_running: 'Running...',
        run_check_done: (n, already) => `Done! ${n} new flags, ${already} already reported.`,
        run_check_failed: 'Check failed — the backend may be restarting.',
        block_reconciliation: 'Reconciliation',
        flow_wallet: 'Wealify wallet',
        flow_transferred: 'Transferred to card',
        flow_card: 'Card spending',
        mismatch_ok: 'No transfer-to-card mismatch found',
        mismatch_ok_sub: 'Every wallet-to-card transfer is accounted for',

        block_urgent: 'Urgent flags',
        flag_duplicate: 'Duplicate charges',
        flag_unrecognized: 'Unrecognized / no receipt',
        flag_audit: 'Needs your confirmation',
        flag_email_audit: 'Email reconciliation needed',

        block_radar: 'Subscription radar',
        block_report: 'Report',
        create_report: 'Create report',
        sub_price: 'Price increased',
        sub_active: 'Active subscriptions',
        sub_trial: 'Trials ending soon',
        sub_unused: 'Unused 60+ days',
        not_tracked: 'Not tracked by this build — out of scope for the current detection rules.',

        panel_chat: 'AI Chat Assistant',
        status_online: 'Online',
        status_offline: 'Offline',
        chat_greeting: 'Hi! Ask me anything about your statements, subscriptions, or email cross-checks.',
        chip_top3: 'Top 3 expenses this month?',
        chip_duplicate: 'Any duplicate charges?',
        chip_subs: 'Which subscriptions increased?',
        chip_report: 'Send me the monthly report',
        chip_deadline: 'Anything nearing the 60-day deadline?',
        chat_placeholder: 'Ask about your transactions',
        readonly_note: 'Read-only access mode',
        thinking: 'Analyzing...',
        chat_error: 'Connection error — the backend may be restarting. Try again in a moment.',

        panel_detail: 'Detail view',
        panel_report: 'Report detail',
        report_nav_month: 'Month',
        report_nav_quarter: 'Quarter',
        report_nav_year: 'Year',
        report_pick_month: 'Select month',
        report_pick_quarter: 'Select quarter',
        report_year_summary: 'Yearly report',
        report_send_email: 'Send to my email',
        report_send_success: (to) => `✅ Report email sent to ${to}`,
        report_send_failed: '⚠️ Could not send report email. Check SMTP configuration.',
        empty_title: 'Nothing selected',
        empty_sub: 'Pick a flag in the Command Center to inspect the underlying transactions.',
        empty_none_title: 'Nothing to show',
        empty_none_sub: 'No items currently match this category.',
        label_finding_id: 'Finding ID',
        label_status: 'Status',
        label_deadline: 'Dispute deadline',
        label_days_left: 'days left',
        label_confidence: 'Confidence',
        label_evidence: 'Evidence',
        count_items: (n) => `${n} item${n === 1 ? '' : 's'}`,
        action_draft_email: 'Draft note for chat',

        disclaimer_label: 'Disclaimer',
        disclaimer_text:
            '⚠️ This tool only assists you in reviewing your finances. Results are for reference only, not ' +
            'official Wealify conclusions, and do not replace your own verification. If you notice suspicious ' +
            'transactions, contact support immediately — in the US, the dispute deadline is 60 days from the ' +
            'statement date.',
    },

    vi: {
        brand_sub: 'Rà soát tài chính bằng AI',

        panel_command: 'Trung tâm điều khiển',
        panel_hint_live: 'Rà soát trực tiếp',
        export_audit: 'Xuất nhật ký',
        export_done: 'Đã xuất nhật ký cảnh báo ra',
        export_failed: 'Xuất thất bại — kiểm tra backend có đang chạy không.',
        reminder_settings: 'Nhắc hạn',
        run_check: 'Rà soát định kỳ',
        run_check_running: 'Đang rà soát...',
        run_check_done: (n, already) => `Hoàn tất! ${n} cảnh báo mới, ${already} đã báo trước.`,
        run_check_failed: 'Rà soát thất bại — backend có thể đang khởi động lại.',
        block_reconciliation: 'Đối soát',
        flow_wallet: 'Ví Wealify',
        flow_transferred: 'Đã chuyển sang thẻ',
        flow_card: 'Chi tiêu trên thẻ',
        mismatch_ok: 'Không phát hiện lệch chuyển tiền sang thẻ',
        mismatch_ok_sub: 'Mọi khoản chuyển từ ví sang thẻ đều đã được đối chiếu khớp',

        block_urgent: 'Cảnh báo giao dịch bất thường',
        flag_duplicate: 'Giao dịch trùng lặp',
        flag_unrecognized: 'Chưa nhận diện / không có biên lai',
        flag_audit: 'Cần bạn tự xác nhận',
        flag_email_audit: 'Cần đối soát email',

        block_radar: 'Radar gói đăng ký',
        block_report: 'Báo cáo',
        create_report: 'Tạo report',
        sub_price: 'Gói tăng giá',
        sub_active: 'Gói đang hoạt động',
        sub_trial: 'Bản dùng thử sắp hết hạn',
        sub_unused: 'Không dùng 60+ ngày',
        not_tracked: 'Bản build này chưa theo dõi mục này — nằm ngoài phạm vi các luật phát hiện hiện có.',

        panel_chat: 'Trợ lý AI',
        status_online: 'Trực tuyến',
        status_offline: 'Mất kết nối',
        chat_greeting: 'Xin chào! Hỏi mình bất kỳ điều gì về sao kê, gói đăng ký, hay đối chiếu email của bạn.',
        chip_top3: '3 khoản chi lớn nhất tháng này?',
        chip_duplicate: 'Có giao dịch trùng không?',
        chip_subs: 'Gói nào vừa tăng giá?',
        chip_report: 'Gửi báo cáo tháng cho tôi',
        chip_deadline: 'Khoản nào sắp hết hạn khiếu nại 60 ngày?',
        chat_placeholder: 'Hỏi về giao dịch của bạn',
        readonly_note: 'Chế độ chỉ đọc',
        thinking: 'Đang phân tích...',
        chat_error: 'Lỗi kết nối — backend có thể đang khởi động lại. Thử lại sau giây lát.',

        panel_detail: 'Chi tiết',
        panel_report: 'Chi tiết báo cáo',
        report_nav_month: 'Tháng',
        report_nav_quarter: 'Quý',
        report_nav_year: 'Năm',
        report_pick_month: 'Chọn tháng',
        report_pick_quarter: 'Chọn quý',
        report_year_summary: 'Báo cáo theo năm',
        report_send_email: 'Gửi vào email của tôi',
        report_send_success: (to) => `✅ Đã gửi email báo cáo tới ${to}`,
        report_send_failed: '⚠️ Chưa gửi được email báo cáo. Kiểm tra cấu hình SMTP.',
        empty_title: 'Chưa chọn mục nào',
        empty_sub: 'Chọn một cảnh báo ở Trung tâm điều khiển để xem chi tiết giao dịch.',
        empty_none_title: 'Không có mục nào',
        empty_none_sub: 'Hiện chưa có giao dịch nào khớp mục này.',
        label_finding_id: 'Mã cảnh báo',
        label_status: 'Nhãn',
        label_deadline: 'Hạn khiếu nại',
        label_days_left: 'ngày còn lại',
        label_confidence: 'Độ tin cậy',
        label_evidence: 'Bằng chứng',
        count_items: (n) => `${n} mục`,
        action_draft_email: 'Soạn ghi chú vào khung chat',

        disclaimer_label: 'Lưu ý',
        disclaimer_text:
            '⚠️ Công cụ này chỉ hỗ trợ bạn rà soát tài chính. Kết quả để tham khảo, không phải kết luận chính ' +
            'thức của Wealify và không thay cho việc bạn tự kiểm tra. Nếu thấy giao dịch lạ, hãy liên hệ hỗ trợ ' +
            'ngay — ở Mỹ thời hạn khiếu nại là 60 ngày kể từ ngày ngân hàng gửi sao kê.',
    },
};

// ─── Currency formatting — statement mixes VND/USD/EUR, each rendered in
// its own real unit rather than converted with a fabricated FX rate. ────
const CURRENCY_SYMBOLS = { USD: '$', EUR: '€' };
const fmtCur = (n, currency) => {
    const v = Number(n) || 0;
    if (currency === 'VND') return `${Math.round(Math.abs(v)).toLocaleString('en-US')} VND`;
    const sym = CURRENCY_SYMBOLS[currency] || (currency ? currency + ' ' : '$');
    return `${sym}${Math.abs(v).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

// ─── Tiny markdown renderer for chat bubbles ────────────────────────
// /chat responses use **bold**, `code`, and "- " bullet lines — plain
// textContent would show the raw asterisks/backticks, so this converts
// the small subset of markdown chat.py actually emits into safe HTML
// (escaping user/model text first, then re-introducing only these tags).
function renderMarkdown(text) {
    const escape = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const paragraphs = text.split('\n\n');
    return paragraphs
        .map((para) => {
            const lines = para.split('\n').filter((l) => l.trim() !== '');
            if (lines.length === 0) return '';
            const isList = lines.every((l) => /^[-•]\s/.test(l.trim()));
            const inline = (s) =>
                escape(s)
                    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                    .replace(/`(.+?)`/g, '<code>$1</code>')
                    .replace(/_(.+?)_/g, '<em>$1</em>');
            if (isList) {
                const items = lines.map((l) => `<li>${inline(l.trim().replace(/^[-•]\s/, ''))}</li>`).join('');
                return `<ul>${items}</ul>`;
            }
            return `<p>${lines.map(inline).join('<br>')}</p>`;
        })
        .join('');
}

// ─── Live data, fetched once per load/refresh ───────────────────────
let allFindings = [];
let walletData = null;
let emailAuditItems = [];

async function apiGet(path) {
    try {
        const res = await fetch(`${API}${path}`);
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

async function apiPost(path, body = null) {
    try {
        const res = await fetch(`${API}${path}`, {
            method: 'POST',
            headers: body ? { 'Content-Type': 'application/json' } : undefined,
            body: body ? JSON.stringify(body) : undefined,
        });
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

async function apiPostChat(message) {
    try {
        const res = await fetch(`${API}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

// A finding is bucketed into one or more Command Center flags by its real
// type/label — nothing here is invented, it's the same taxonomy
// finding_engine.py already assigns (R-01..R-15).
const FLAG_FILTERS = {
    duplicate: (f) => ['DUPLICATE_CHARGE', 'DUPLICATE_PAYIN', 'DOUBLE_FEE'].includes(f.type),
    unrecognized: (f) => ['NO_MATCHING_EMAIL', 'UNKNOWN_MERCHANT', 'SUSPICIOUS_EMAIL'].includes(f.type),
    audit: (f) => f.label === 'CAN_BAN_TU_XAC_NHAN',
    'price-hike': (f) => f.type === 'SILENT_PRICE_INCREASE',
    'active-subs': (f) => f.type === 'RECURRING_SUBSCRIPTION',
    // No trial/unused-subscription detector exists server-side (out of
    // spec scope) — always empty rather than inventing placeholder data.
    trial: () => false,
    unused: () => false,
};

const FLAG_TITLE_KEY = {
    duplicate: 'flag_duplicate',
    unrecognized: 'flag_unrecognized',
    audit: 'flag_audit',
    'price-hike': 'sub_price',
    'active-subs': 'sub_active',
    trial: 'sub_trial',
    unused: 'sub_unused',
};

// Email reconciliation needed — two real sources, normalized into the same
// finding-like shape buildDetailItem already renders: (1) phishing/lookalike
// sender domains (check_suspicious_domains), (2) receipt emails that
// matched a Wealify transaction but not cleanly (match_outbound_emails,
// excluding "matched_success" — those are fine, nothing to review).
function normalizeEmailAuditItems(suspiciousRes, outboundRes) {
    const items = [];
    for (const it of (suspiciousRes && suspiciousRes.items) || []) {
        items.push({
            finding_id: `SUSPICIOUS-${it.email_from}`,
            title_vi: it.email_subject || it.email_from,
            title_en: it.email_subject || it.email_from,
            explanation_vi: it.detail,
            explanation_en: it.detail,
            label: 'CAN_BAN_TU_XAC_NHAN',
            label_vi: it.label,
            label_en: it.label,
            amount_cents: 0,
            currency: 'USD',
            occurred_at: (it.email_date || '').split(' ')[0],
        });
    }
    for (const it of (outboundRes && outboundRes.items) || []) {
        if (it.category === 'matched_success') continue;
        items.push({
            finding_id: `OUTBOUND-${it.email_ref}`,
            title_vi: it.email_subject || it.email_ref,
            title_en: it.email_subject || it.email_ref,
            explanation_vi: it.detail,
            explanation_en: it.detail,
            label: 'CAN_BAN_TU_XAC_NHAN',
            label_vi: it.label,
            label_en: it.label,
            amount_cents: Math.round((it.wealify_amount ?? it.email_amount ?? 0) * 100),
            currency: 'USD',
            occurred_at: (it.email_date || '').split(' ')[0],
        });
    }
    return items;
}

async function loadAll() {
    const [findingsRes, wallet, suspiciousRes, outboundRes] = await Promise.all([
        apiGet('/findings'),
        apiGet('/dashboard/wallet'),
        apiGet('/dashboard/suspicious-domains'),
        apiGet('/dashboard/outbound-reconciliation'),
    ]);
    allFindings = (findingsRes && findingsRes.findings) || [];
    walletData = wallet;
    emailAuditItems = normalizeEmailAuditItems(suspiciousRes, outboundRes);

    renderReconciliation();
    renderCommandCenterCounts();
    if (activeFlag) renderDetails(activeFlag, { instant: true });

    const dot = document.querySelector('.dot');
    const statusLabel = document.querySelector('.status-chip span[data-i18n]');
    const ok = Boolean(findingsRes);
    if (dot) dot.classList.toggle('is-offline', !ok);
    if (statusLabel) statusLabel.textContent = ok ? t('status_online') : t('status_offline');
}

// ─── Left panel: reconciliation flow + Command Center counts ────────

function renderReconciliation() {
    const walletEl = document.querySelector('[data-flow="wallet"] .flow-value');
    const transferredEl = document.querySelector('[data-flow="transferred"] .flow-value');
    const cardEl = document.querySelector('[data-flow="card"] .flow-value');

    // Cards can be in more than one currency (USD/EUR here) — stack each
    // on its own line rather than picking one and hiding the rest, or
    // joining them as if they were the same unit.
    const stackCurrencies = (el, byCurrency, pick) => {
        if (!el) return;
        const entries = Object.entries(byCurrency || {}).filter(
            ([, v]) => pick(v) !== 0 || Object.keys(byCurrency).length === 1,
        );
        if (!entries.length) {
            el.textContent = '—';
            return;
        }
        el.innerHTML = entries.map(([cur, v]) => `<span class="cur-line">${fmtCur(pick(v), cur)}</span>`).join('');
    };

    if (walletData) {
        if (walletEl) walletEl.textContent = fmtCur(walletData.wallet_balance, walletData.currency || 'VND');
        const byCurrency = walletData.card_totals_by_currency || {};
        stackCurrencies(transferredEl, byCurrency, (v) => v.total_transferred_to_card);
        stackCurrencies(cardEl, byCurrency, (v) => v.total_card_spending);
    }

    const mismatchFindings = allFindings.filter((f) =>
        ['IN_TRANSIT_NOT_ON_CARD', 'WALLET_BALANCE_MISMATCH'].includes(f.type),
    );
    const noteEl = document.querySelector('.note');
    if (!noteEl) return;

    const titleEl = noteEl.querySelector('strong');
    const subEl = noteEl.querySelector('.note-sub');
    const iconEl = noteEl.querySelector('i');

    if (mismatchFindings.length === 0) {
        noteEl.classList.remove('note-caution');
        noteEl.classList.add('note-ok');
        if (iconEl) iconEl.className = 'ph ph-check-circle';
        if (titleEl) titleEl.textContent = t('mismatch_ok');
        if (subEl) subEl.textContent = t('mismatch_ok_sub');
    } else {
        noteEl.classList.add('note-caution');
        noteEl.classList.remove('note-ok');
        if (iconEl) iconEl.className = 'ph ph-warning-circle';
        // Group by currency instead of summing amount_cents across
        // findings that might not share a currency into one fabricated total.
        const byCurrency = {};
        for (const f of mismatchFindings) {
            const cur = f.currency || 'USD';
            byCurrency[cur] = (byCurrency[cur] || 0) + (f.amount_cents || 0);
        }
        const totalText = Object.entries(byCurrency)
            .map(([cur, cents]) => fmtCur(cents / 100, cur))
            .join(' · ');
        const suffix = lang === 'vi' ? 'chưa khớp' : 'unaccounted for';
        if (titleEl) titleEl.textContent = `${totalText} ${suffix}`;
        if (subEl) subEl.textContent = findingTitle(mismatchFindings[0]);
    }
}

function renderCommandCenterCounts() {
    document.querySelectorAll('[data-flag]').forEach((el) => {
        const flag = el.dataset.flag;
        const count = flag === 'email-audit' ? emailAuditItems.length : allFindings.filter(FLAG_FILTERS[flag]).length;
        const badge = el.querySelector('.badge, .pill');
        if (badge) badge.textContent = String(count);
        const sub = el.querySelector('.flag-sub');
        if (sub) sub.textContent = t('count_items')(count);
    });
}

// ─── Right panel: detail view, sourced directly from finding objects ─

function findingTitle(f) {
    return lang === 'vi' ? f.title_vi : f.title_en;
}
function findingExplanation(f) {
    return lang === 'vi' ? f.explanation_vi : f.explanation_en;
}
function findingLabel(f) {
    return lang === 'vi' ? f.label_vi : f.label_en;
}

const detailTitle = document.getElementById('detailTitle');
const detailCount = document.getElementById('detailCount');
const detailBody = document.getElementById('detailBody');
const chatHistory = document.getElementById('chatHistory');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const langSwitch = document.getElementById('langSwitch');
const createReportBtn = document.getElementById('createReportBtn');

let lang = localStorage.getItem('wealify_lang') === 'en' ? 'en' : 'vi';
let activeFlag = null;
let openIndex = null;
let loadTimer = null;
let rightPanelMode = 'detail';
let reportYear = new Date().getFullYear();
let reportType = 'month';
let selectedMonth = new Date().getMonth() + 1;
let selectedQuarter = Math.floor(new Date().getMonth() / 3) + 1;
let selectedCurrency = null;
let reportChart = null;

const t = (key) => I18N[lang][key];

function icon(name, extraClass) {
    const i = document.createElement('i');
    i.className = `ph ph-${name}${extraClass ? ' ' + extraClass : ''}`;
    i.setAttribute('aria-hidden', 'true');
    return i;
}

function buildMetaRow(list, label, value) {
    const dt = document.createElement('dt');
    dt.textContent = label;
    const dd = document.createElement('dd');
    dd.textContent = value;
    list.append(dt, dd);
}

function buildDetailItem(f, index) {
    const row = document.createElement('article');
    row.className = 'detail-item';
    if (openIndex === index) row.classList.add('is-open');
    row.style.setProperty('--i', String(index));

    const head = document.createElement('button');
    head.type = 'button';
    head.className = 'detail-head';
    head.setAttribute('aria-expanded', String(openIndex === index));

    const main = document.createElement('div');
    main.className = 'detail-main';

    const line = document.createElement('div');
    line.className = 'detail-row';

    const title = document.createElement('span');
    title.className = 'detail-merchant';
    title.textContent = findingTitle(f);

    const amount = document.createElement('span');
    const isAlert = f.label === 'CAN_BAN_TU_XAC_NHAN';
    amount.className = 'detail-amount num' + (isAlert ? ' is-alert' : '');
    amount.textContent = fmtCur((f.amount_cents || 0) / 100, f.currency || 'USD');

    line.append(title, amount);

    const date = document.createElement('div');
    date.className = 'detail-date';
    date.textContent = f.occurred_at || '';

    main.append(line, date);

    const explanation = findingExplanation(f);
    if (explanation) {
        const warn = document.createElement('div');
        warn.className = 'detail-warning';
        const label = document.createElement('span');
        label.textContent = explanation;
        warn.append(icon('warning-circle'), label);
        main.appendChild(warn);
    }

    head.append(main, icon('caret-down', 'detail-chevron'));

    const extra = document.createElement('div');
    extra.className = 'detail-extra';

    const inner = document.createElement('div');
    inner.className = 'detail-extra-inner';

    const meta = document.createElement('dl');
    meta.className = 'detail-meta';
    buildMetaRow(meta, t('label_finding_id'), f.finding_id || '');
    buildMetaRow(meta, t('label_status'), findingLabel(f));
    if (f.dispute_deadline) {
        buildMetaRow(
            meta,
            t('label_deadline'),
            `${f.dispute_deadline} (${f.days_left ?? '?'} ${t('label_days_left')})`,
        );
    }
    if (typeof f.confidence === 'number') {
        buildMetaRow(meta, t('label_confidence'), `${Math.round(f.confidence * 100)}%`);
    }
    if (Array.isArray(f.evidence_refs) && f.evidence_refs.length) {
        buildMetaRow(meta, t('label_evidence'), f.evidence_refs.join(', '));
    }

    inner.appendChild(meta);

    if (isAlert) {
        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'detail-action';
        const label = document.createElement('span');
        label.textContent = t('action_draft_email');
        action.append(icon('envelope-simple'), label);
        action.addEventListener('click', () => draftNote(f));
        inner.appendChild(action);
    }

    extra.appendChild(inner);
    row.append(head, extra);

    head.addEventListener('click', () => toggleItem(row, index));

    return row;
}

function toggleItem(row, index) {
    const willOpen = openIndex !== index;
    openIndex = willOpen ? index : null;

    detailBody.querySelectorAll('.detail-item').forEach((el) => {
        el.classList.remove('is-open');
        el.querySelector('.detail-head').setAttribute('aria-expanded', 'false');
    });

    if (willOpen) {
        row.classList.add('is-open');
        row.querySelector('.detail-head').setAttribute('aria-expanded', 'true');
    }
}

function showSkeleton(count) {
    const list = document.createElement('div');
    list.className = 'detail-list';

    for (let n = 0; n < count; n += 1) {
        const row = document.createElement('div');
        row.className = 'skeleton-row';
        const wide = document.createElement('div');
        wide.className = 'skeleton-bar w-60';
        const narrow = document.createElement('div');
        narrow.className = 'skeleton-bar w-34';
        row.append(wide, narrow);
        list.appendChild(row);
    }

    detailBody.replaceChildren(list);
}

function paintEmpty() {
    const wrap = document.createElement('div');
    wrap.className = 'empty-state';
    const iconEl = icon('tray', 'empty-icon');
    const title = document.createElement('p');
    title.className = 'empty-title';
    title.textContent = t('empty_none_title');
    const sub = document.createElement('p');
    sub.className = 'empty-sub';
    sub.textContent = activeFlag === 'trial' || activeFlag === 'unused' ? t('not_tracked') : t('empty_none_sub');
    wrap.append(iconEl, title, sub);
    detailBody.replaceChildren(wrap);
}

function paintDetails(items) {
    if (items.length === 0) {
        paintEmpty();
        return;
    }
    const list = document.createElement('div');
    list.className = 'detail-list';
    list.append(...items.map(buildDetailItem));
    detailBody.replaceChildren(list);
    detailBody.scrollTop = 0;
}

function renderDetails(flag, { instant = false } = {}) {
    rightPanelMode = 'detail';
    destroyReportChart();
    const isEmailAudit = flag === 'email-audit';
    if (!isEmailAudit && !FLAG_FILTERS[flag]) return;

    if (flag !== activeFlag) openIndex = null;
    activeFlag = flag;

    const items = isEmailAudit ? emailAuditItems : allFindings.filter(FLAG_FILTERS[flag]);

    detailTitle.textContent = t(isEmailAudit ? 'flag_email_audit' : FLAG_TITLE_KEY[flag]);
    detailCount.textContent = t('count_items')(items.length);

    document.querySelectorAll('[data-flag]').forEach((el) => {
        el.classList.toggle('is-active', el.dataset.flag === flag);
    });

    window.clearTimeout(loadTimer);

    if (instant) {
        paintDetails(items);
        return;
    }

    showSkeleton(Math.min(items.length, 4) || 2);
    loadTimer = window.setTimeout(() => paintDetails(items), 220);
}

function destroyReportChart() {
    if (reportChart) {
        reportChart.destroy();
        reportChart = null;
    }
}

function buildReportShell() {
    const wrap = document.createElement('div');
    wrap.className = 'report-shell';
    wrap.innerHTML = `
        <div class="report-nav" id="reportNav">
            <button type="button" class="report-nav-btn" data-report-type="month">${t('report_nav_month')}</button>
            <button type="button" class="report-nav-btn" data-report-type="quarter">${t('report_nav_quarter')}</button>
            <button type="button" class="report-nav-btn" data-report-type="year">${t('report_nav_year')}</button>
        </div>
        <div class="report-picker-title" id="reportPickerTitle"></div>
        <div class="report-picker" id="reportPicker"></div>
        <div class="report-currency-picker" id="reportCurrencyPicker"></div>
        <div class="report-chart-wrap">
            <canvas id="reportChartCanvas"></canvas>
        </div>
        <div class="report-text" id="reportText"></div>
        <button type="button" class="report-send-btn" id="reportSendBtn">${t('report_send_email')}</button>
    `;
    return wrap;
}

function renderReportPicker() {
    const titleEl = document.getElementById('reportPickerTitle');
    const pickerEl = document.getElementById('reportPicker');
    if (!titleEl || !pickerEl) return;

    pickerEl.innerHTML = '';
    if (reportType === 'month') {
        titleEl.textContent = t('report_pick_month');
        for (let m = 1; m <= 12; m += 1) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `report-pick-btn${m === selectedMonth ? ' is-active' : ''}`;
            btn.textContent = String(m);
            btn.addEventListener('click', () => {
                selectedMonth = m;
                loadAndRenderReport();
            });
            pickerEl.appendChild(btn);
        }
        return;
    }

    if (reportType === 'quarter') {
        titleEl.textContent = t('report_pick_quarter');
        for (let q = 1; q <= 4; q += 1) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = `report-pick-btn${q === selectedQuarter ? ' is-active' : ''}`;
            btn.textContent = `Q${q}`;
            btn.addEventListener('click', () => {
                selectedQuarter = q;
                loadAndRenderReport();
            });
            pickerEl.appendChild(btn);
        }
        return;
    }

    titleEl.textContent = t('report_year_summary');
}

function renderCurrencyPicker(currencies) {
    const wrap = document.getElementById('reportCurrencyPicker');
    if (!wrap) return;
    wrap.innerHTML = '';
    if (!Array.isArray(currencies) || currencies.length <= 1) return;

    if (!selectedCurrency || !currencies.includes(selectedCurrency)) {
        selectedCurrency = currencies[0];
    }

    for (const cur of currencies) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = `report-currency-btn${cur === selectedCurrency ? ' is-active' : ''}`;
        btn.textContent = cur;
        btn.addEventListener('click', () => {
            selectedCurrency = cur;
            loadAndRenderReport();
        });
        wrap.appendChild(btn);
    }
}

function renderReportChart(data) {
    const canvas = document.getElementById('reportChartCanvas');
    if (!canvas || !window.Chart) return;
    destroyReportChart();

    const type = data.period_type;
    const currencies = data.currencies || [];
    const currency = selectedCurrency && currencies.includes(selectedCurrency) ? selectedCurrency : currencies[0];
    selectedCurrency = currency || null;

    if (!currency) return;

    if (type === 'month') {
        const rows = (data.categories_by_currency && data.categories_by_currency[currency]) || [];
        const labels = rows.map((r) => r.category_label);
        const totals = rows.map((r) => r.total_amount);
        reportChart = new window.Chart(canvas, {
            type: 'pie',
            data: {
                labels,
                datasets: [
                    {
                        data: totals,
                        backgroundColor: ['#355070', '#6d597a', '#b56576', '#e56b6f', '#eaac8b', '#5f6f52', '#8ab17d'],
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom' } },
            },
        });
        return;
    }

    const rows = (data.comparison_by_currency && data.comparison_by_currency[currency]) || [];
    const labels = rows.map((r) => r.month);
    reportChart = new window.Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                { label: 'Tiền vào', data: rows.map((r) => r.money_in), backgroundColor: '#5f6f52' },
                { label: 'Tiền ra', data: rows.map((r) => r.money_out), backgroundColor: '#355070' },
            ],
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } },
            plugins: { legend: { position: 'bottom' } },
        },
    });
}

function renderReportText(data) {
    const textEl = document.getElementById('reportText');
    if (!textEl) return;
    const currencies = data.currencies || [];
    const currency = selectedCurrency && currencies.includes(selectedCurrency) ? selectedCurrency : currencies[0];
    if (!currency) {
        textEl.textContent = data.text_summary || '';
        return;
    }

    if (data.period_type === 'month') {
        const rows = (data.categories_by_currency && data.categories_by_currency[currency]) || [];
        const money = (data.money_summary_by_currency && data.money_summary_by_currency[currency]) || {};
        const lines = rows.map((r) => `• ${r.category_label}: ${fmtCur(r.total_amount, currency)} · ${r.transaction_count} giao dịch`);
        textEl.textContent =
            `${data.text_summary}\n\n[${currency}]\n${lines.join('\n')}\n\n` +
            `• Tổng tiền vào: ${fmtCur(money.money_in || 0, currency)}\n` +
            `• Tổng tiền ra: ${fmtCur(money.money_out || 0, currency)}`;
        return;
    }

    const rows = (data.comparison_by_currency && data.comparison_by_currency[currency]) || [];
    const lines = rows.map(
        (r) =>
            `• ${r.month}: Tiền vào ${fmtCur(r.money_in, currency)} | Tiền ra ${fmtCur(r.money_out, currency)}`,
    );
    textEl.textContent = `${data.text_summary}\n\n[${currency}]\n${lines.join('\n')}`;
}

async function loadAndRenderReport() {
    const nav = document.getElementById('reportNav');
    if (nav) {
        nav.querySelectorAll('.report-nav-btn').forEach((btn) => {
            btn.classList.toggle('is-active', btn.dataset.reportType === reportType);
        });
    }

    let data = null;
    if (reportType === 'month') data = await apiGet(`/dashboard/reporting/month/${selectedMonth}`);
    else if (reportType === 'quarter') data = await apiGet(`/dashboard/reporting/quarter/${selectedQuarter}`);
    else data = await apiGet('/dashboard/reporting/year');
    if (!data || data.status?.startsWith('invalid')) return;

    reportYear = data.year || reportYear;
    renderReportPicker();
    renderCurrencyPicker(data.currencies || []);
    renderReportChart(data);
    renderReportText(data);

    const sendBtn = document.getElementById('reportSendBtn');
    if (sendBtn) {
        sendBtn.onclick = async () => {
            const payload = {
                period_type: reportType,
                period_value: reportType === 'year' ? null : reportType === 'month' ? selectedMonth : selectedQuarter,
            };
            const res = await apiPost('/dashboard/reporting/send-email', payload);
            if (res && res.status === 'sent') {
                appendMessage(t('report_send_success')(res.to), 'ai');
            } else {
                appendMessage(t('report_send_failed'), 'ai');
            }
        };
    }
}

async function openReportPanel() {
    rightPanelMode = 'report';
    activeFlag = null;
    detailTitle.textContent = t('panel_report');
    detailCount.textContent = '';
    detailBody.replaceChildren(buildReportShell());

    const nav = document.getElementById('reportNav');
    if (nav) {
        nav.querySelectorAll('.report-nav-btn').forEach((btn) => {
            btn.classList.toggle('is-active', btn.dataset.reportType === reportType);
            btn.addEventListener('click', () => {
                reportType = btn.dataset.reportType;
                loadAndRenderReport();
            });
        });
    }

    await loadAndRenderReport();
}

// ─── Language switching ────────────────────────────

function applyLang(next) {
    lang = next;
    localStorage.setItem('wealify_lang', lang);
    document.documentElement.lang = lang;

    document.querySelectorAll('[data-i18n]').forEach((el) => {
        const value = I18N[lang][el.dataset.i18n];
        if (typeof value === 'string') el.textContent = value;
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
        el.placeholder = I18N[lang][el.dataset.i18nPlaceholder];
    });

    langSwitch.querySelectorAll('.lang-btn').forEach((btn) => {
        btn.classList.toggle('is-active', btn.dataset.lang === lang);
    });

    renderReconciliation();
    renderCommandCenterCounts();
    if (rightPanelMode === 'report') {
        openReportPanel();
    } else if (activeFlag) {
        renderDetails(activeFlag, { instant: true });
    } else {
        detailTitle.textContent = t('panel_detail');
    }
}

langSwitch.addEventListener('click', (e) => {
    const btn = e.target.closest('.lang-btn');
    if (btn && btn.dataset.lang !== lang) applyLang(btn.dataset.lang);
});

// ─── Command Center clicks ─────────────────────────

document.querySelectorAll('[data-flag]').forEach((el) => {
    el.addEventListener('click', () => renderDetails(el.dataset.flag));
});

if (createReportBtn) {
    createReportBtn.addEventListener('click', () => {
        openReportPanel();
    });
}

// ─── Chat — wired to POST /chat (real backend, no canned replies) ───

function appendMessage(html, sender) {
    const wrap = document.createElement('div');
    wrap.className = `msg msg-${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = sender === 'ai' ? 'AI' : 'You';

    const bubble = document.createElement('div');
    bubble.className = `bubble bubble-${sender}`;
    if (sender === 'ai') bubble.innerHTML = html;
    else bubble.textContent = html;

    wrap.append(avatar, bubble);
    chatHistory.appendChild(wrap);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return wrap;
}

async function askAssistant(text) {
    const question = text.trim();
    if (!question) return;

    appendMessage(question, 'user');
    chatInput.value = '';

    const thinking = appendMessage(
        `<span class="thinking"><span class="spinner-dot"></span> ${t('thinking')}</span>`,
        'ai',
    );

    const res = await apiPostChat(question);
    thinking.remove();

    if (res && res.response) {
        appendMessage(renderMarkdown(res.response), 'ai');
    } else {
        appendMessage(t('chat_error'), 'ai');
    }
}

// Stages a note about a finding in the chat composer instead of sending
// anything itself — the user reviews/edits it, and only the existing
// /chat pipeline (with its own confirm-before-send flow) can act on it.
function draftNote(f) {
    const deadlinePart = f.dispute_deadline
        ? lang === 'vi'
            ? ` Hạn khiếu nại: ${f.dispute_deadline} (còn ${f.days_left} ngày).`
            : ` Dispute deadline: ${f.dispute_deadline} (${f.days_left} days left).`
        : '';
    const text =
        lang === 'vi'
            ? `Giải thích giúp mình khoản này: ${findingTitle(f)} — ${findingExplanation(f)}${deadlinePart}`
            : `Explain this to me: ${findingTitle(f)} — ${findingExplanation(f)}${deadlinePart}`;
    chatInput.value = text;
    chatInput.focus();
    chatInput.setSelectionRange(chatInput.value.length, chatInput.value.length);
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    askAssistant(chatInput.value);
});

document.getElementById('suggestionChips').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (chip) askAssistant(chip.textContent);
});

// ─── Profile — real account holder, not a placeholder name ─────────

async function loadProfile() {
    const accounts = await apiGet('/dashboard/wealify-accounts');
    const nameEl = document.querySelector('.profile-name');
    const cardEl = document.querySelector('.profile-card');
    const avatarEl = document.querySelector('.avatar');
    if (!accounts || accounts.status !== 'live') return;

    const fullName = accounts.user && accounts.user.full_name;
    const firstVa = accounts.va_accounts && accounts.va_accounts[0];

    if (fullName && nameEl) nameEl.textContent = fullName;
    if (firstVa && cardEl) cardEl.textContent = firstVa.account_number || '';
    if (fullName && avatarEl) {
        const initials = fullName
            .split(' ')
            .map((p) => p[0])
            .slice(-2)
            .join('')
            .toUpperCase();
        avatarEl.textContent = initials;
    }
}

// ─── Manual scheduled check — matches the same dedup logic the ─────
// background loop runs automatically every SCHEDULED_CHECK_INTERVAL_SECONDS.

document.getElementById('scheduledCheckBtn').addEventListener('click', async () => {
    const btn = document.getElementById('scheduledCheckBtn');
    const label = btn.querySelector('span');
    const originalText = label.textContent;
    label.textContent = t('run_check_running');
    btn.disabled = true;

    const res = await apiPost('/scheduled-check');

    btn.disabled = false;
    label.textContent = originalText;

    if (res && typeof res.new_flags === 'number') {
        alert(t('run_check_done')(res.new_flags, res.already_reported));
        await loadAll();
    } else {
        alert(t('run_check_failed'));
    }
});

// ─── Export audit log ──────────────────────────────

document.getElementById('exportAuditBtn').addEventListener('click', async () => {
    const res = await apiGet('/audit-log/export');
    if (res && res.status === 'exported') {
        alert(`${t('export_done')} ${res.exported_to} (${res.total_flags})`);
    } else {
        alert(t('export_failed'));
    }
});

// ─── Initial state ─────────────────────────────────

applyLang(lang);
loadAll();
loadProfile();
renderDetails('duplicate', { instant: true });

// Keep Command Center counts fresh without a manual refresh — matches the
// backend's own periodic re-scan (SCHEDULED_CHECK_INTERVAL_SECONDS).
setInterval(loadAll, 60000);
