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

        block_radar: 'Subscriptions',
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

        email_pane_not_in_wlist: 'Not in whitelist',
        email_pane_in_wlist_no_tx: 'In whitelist, no matching transaction',
        email_pane_empty: 'No items in this group.',
        email_action_add_wlist: 'Add to whitelist',
        email_action_draft_complaint: 'Draft complaint email',
        email_added_to_wlist: (sender) => `Added ${sender} to whitelist.`,
        email_deadline_urgent: (days) => `${days}d left`,
        email_deadline_clear: (days) => `${days}d left`,

        sub_active_top: 'Currently active',
        sub_active_bottom: 'Pending cancellation',
        sub_action_stop_renewal: 'Stop renewal',
        sub_action_confirmed_cancelled: 'Confirmed cancelled',
        sub_action_restore: 'Restore',
        sub_overdue_label: 'Forgot to cancel?',
        sub_overdue_sub: (days) => `${days} days pending`,
        sub_pending_sub: (days) => `Pending for ${days} day${days === 1 ? '' : 's'}`,
        sub_empty_top: 'No active subscriptions.',
        sub_empty_bottom: 'No subscriptions pending cancellation.',
        sub_moved_pending: 'Moved to pending cancellation.',
        sub_restored: 'Restored to active list.',
        sub_confirmed_done: 'Marked as cancelled.',

        toast_close: 'Dismiss',

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
        flag_unrecognized: 'Không có biên lai',
        flag_audit: 'Cần bạn tự xác nhận',
        flag_email_audit: 'Cần đối soát email',

        block_radar: 'Các gói đã đăng ký',
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

        email_pane_not_in_wlist: 'Chưa có trong whitelist',
        email_pane_in_wlist_no_tx: 'Có trong whitelist nhưng chưa có giao dịch',
        email_pane_empty: 'Chưa có mục nào trong nhóm này.',
        email_action_add_wlist: 'Thêm vào whitelist',
        email_action_draft_complaint: 'Soạn email khiếu nại',
        email_added_to_wlist: (sender) => `Đã thêm ${sender} vào whitelist.`,
        email_deadline_urgent: (days) => `còn ${days} ngày`,
        email_deadline_clear: (days) => `còn ${days} ngày`,

        sub_active_top: 'Đang hoạt động',
        sub_active_bottom: 'Đang chờ hủy',
        sub_action_stop_renewal: 'Muốn dừng gia hạn',
        sub_action_confirmed_cancelled: 'Đã hủy xong',
        sub_action_restore: 'Khôi phục',
        sub_overdue_label: 'Quên hủy đăng ký',
        sub_overdue_sub: (days) => `Chờ ${days} ngày`,
        sub_pending_sub: (days) => `Chờ ${days} ngày`,
        sub_empty_top: 'Chưa có gói đang hoạt động.',
        sub_empty_bottom: 'Không có gói chờ hủy.',
        sub_moved_pending: 'Đã chuyển vào danh sách chờ hủy.',
        sub_restored: 'Đã khôi phục gói.',
        sub_confirmed_done: 'Đã đánh dấu hủy.',

        toast_close: 'Đóng',

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

async function apiPost(path) {
    try {
        const res = await fetch(`${API}${path}`, { method: 'POST' });
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
//
// Each normalized item also carries an `email_group` so the right panel can
// split the list into two panes:
//   - "not_in_wlist"   — sender domain isn't on the trusted list (every
//                        suspicious-domain flag falls here by definition).
//   - "in_wlist_no_tx" — sender is trusted (an outbound Ref email) but
//                        Wealify has no matching transaction for the Ref
//                        printed in the receipt body (not_found_on_wealify).
function normalizeEmailAuditItems(suspiciousRes, outboundRes) {
    const items = [];
    for (const it of (suspiciousRes && suspiciousRes.items) || []) {
        items.push({
            finding_id: `SUSPICIOUS-${it.email_from}`,
            email_group: 'not_in_wlist',
            email_from: it.email_from,
            email_subject: it.email_subject,
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
            email_date: it.email_date,
        });
    }
    for (const it of (outboundRes && outboundRes.items) || []) {
        if (it.category === 'matched_success') continue;
        // Only "no matching Wealify transaction" emails belong in the
        // bottom pane — the other non-success buckets (matched_pending,
        // amount_mismatch, matched_failed_or_cancelled) all have a Wealify
        // record; they're surfaced elsewhere as findings, not as missing
        // receipts.
        const group = it.category === 'not_found_on_wealify' ? 'in_wlist_no_tx' : null;
        if (!group) continue;
        items.push({
            finding_id: `OUTBOUND-${it.email_ref}`,
            email_group: group,
            email_from: it.email_from,
            email_ref: it.email_ref,
            email_subject: it.email_subject,
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
            email_date: it.email_date,
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
        let count;
        if (flag === 'email-audit') count = emailAuditItems.length;
        else if (flag === 'active-subs') count = MOCK_ACTIVE_SUBS.length;
        else count = allFindings.filter(FLAG_FILTERS[flag]).length;
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

let lang = localStorage.getItem('wealify_lang') === 'en' ? 'en' : 'vi';
let activeFlag = null;
let openIndex = null;
let loadTimer = null;

const t = (key) => I18N[lang][key];

function icon(name, extraClass) {
    const i = document.createElement('i');
    i.className = `ph ph-${name}${extraClass ? ' ' + extraClass : ''}`;
    i.setAttribute('aria-hidden', 'true');
    return i;
}

// ─── Toast notifications ────────────────────────────────────────────
// Replaces the browser alert() for non-blocking, in-app feedback. Same
// pastel semantic palette as the rest of the UI (success/warning/danger),
// stacks under the navbar on the right, self-dismisses, and can be closed
// by click. Hard-capped at 4 visible toasts — older ones fall off the stack
// instead of growing it indefinitely under heavy action bursts.

const TOAST_DEFAULT_MS = 4000;
const TOAST_MAX_VISIBLE = 4;
const TOAST_ICON = { info: 'info', success: 'check-circle', warning: 'warning-circle', danger: 'x-circle' };

function getToastStack() {
    let stack = document.getElementById('toastStack');
    if (!stack) {
        stack = document.createElement('div');
        stack.id = 'toastStack';
        stack.className = 'toast-stack';
        stack.setAttribute('role', 'status');
        stack.setAttribute('aria-live', 'polite');
        document.body.appendChild(stack);
    }
    return stack;
}

function showToast(message, type = 'info', duration = TOAST_DEFAULT_MS) {
    const stack = getToastStack();
    while (stack.children.length >= TOAST_MAX_VISIBLE) {
        stack.firstElementChild && stack.firstElementChild.remove();
    }

    const toast = document.createElement('div');
    toast.className = `toast is-${type}`;
    toast.setAttribute('role', type === 'danger' || type === 'warning' ? 'alert' : 'status');

    const iconEl = document.createElement('i');
    iconEl.className = `ph ph-${TOAST_ICON[type] || TOAST_ICON.info}`;
    iconEl.setAttribute('aria-hidden', 'true');

    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = String(message);

    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'toast-close';
    closeBtn.setAttribute('aria-label', t('toast_close'));
    const closeIcon = document.createElement('i');
    closeIcon.className = 'ph ph-x';
    closeIcon.setAttribute('aria-hidden', 'true');
    closeBtn.appendChild(closeIcon);

    toast.append(iconEl, body, closeBtn);
    stack.appendChild(toast);

    let timer = null;
    const dismiss = () => {
        if (toast.classList.contains('is-leaving')) return;
        toast.classList.add('is-leaving');
        window.clearTimeout(timer);
        window.setTimeout(() => toast.remove(), 240);
    };
    closeBtn.addEventListener('click', dismiss);
    timer = window.setTimeout(dismiss, duration);
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

// ─── Email-audit split view ──────────────────────────────────────────
// Two stacked panes (not-in-whitelist on top, in-whitelist-no-tx below),
// each with its own header and independently-scrollable body. The top
// pane lets the user add an unknown sender to the whitelist; the bottom
// pane shows the 60-day dispute countdown and drafts a complaint email
// straight into the chat composer (where the existing /chat pipeline —
// with its confirm-before-send flow — takes over).

const EMAIL_DISPUTE_WINDOW_DAYS = 60;

function daysUntilDeadline(emailDate) {
    const raw = (emailDate || '').split(' ')[0];
    if (!raw) return null;
    const sent = new Date(raw);
    if (Number.isNaN(sent.getTime())) return null;
    const deadline = new Date(sent.getTime());
    deadline.setDate(deadline.getDate() + EMAIL_DISPUTE_WINDOW_DAYS);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const msPerDay = 24 * 60 * 60 * 1000;
    return Math.round((deadline.getTime() - today.getTime()) / msPerDay);
}

function buildEmailRow(item, index) {
    const row = document.createElement('div');
    row.className = 'email-row';
    row.style.setProperty('--i', String(index));

    const main = document.createElement('div');
    main.className = 'email-row-main';

    const from = document.createElement('div');
    from.className = 'email-row-from';
    from.textContent = item.email_from || item.email_ref || findingTitle(item);
    main.appendChild(from);

    const sub = document.createElement('div');
    sub.className = 'email-row-sub';
    const subj = item.email_subject || '';
    const ref = item.email_ref ? `Ref ${item.email_ref}` : '';
    sub.textContent = [subj, ref].filter(Boolean).join(' · ') || findingExplanation(item);
    main.appendChild(sub);

    const side = document.createElement('div');
    side.className = 'email-row-side';

    if (item.email_group === 'in_wlist_no_tx') {
        const days = daysUntilDeadline(item.email_date);
        if (days !== null) {
            const pill = document.createElement('span');
            const isOverdue = days <= 0;
            const isUrgent = !isOverdue && days <= 14;
            pill.className = 'deadline-pill' + (isOverdue || isUrgent ? ' is-urgent' : days > 30 ? ' is-clear' : '');
            pill.append(icon('hourglass-medium'), document.createTextNode(t('email_deadline_urgent')(days)));
            side.appendChild(pill);
        }

        const complaint = document.createElement('button');
        complaint.type = 'button';
        complaint.className = 'email-action';
        complaint.append(icon('envelope-simple'), document.createTextNode(t('email_action_draft_complaint')));
        complaint.addEventListener('click', () => draftComplaintEmail(item));
        side.appendChild(complaint);
    } else {
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'email-action';
        addBtn.append(icon('plus-circle'), document.createTextNode(t('email_action_add_wlist')));
        addBtn.addEventListener('click', () => addSenderToWhitelist(item, addBtn));
        side.appendChild(addBtn);
    }

    row.append(main, side);
    return row;
}

function buildEmailPane(titleKey, items) {
    const pane = document.createElement('section');
    pane.className = 'detail-pane';

    const head = document.createElement('header');
    head.className = 'detail-pane-head';
    const title = document.createElement('h3');
    title.className = 'detail-pane-title';
    title.textContent = t(titleKey);
    const count = document.createElement('span');
    count.className = 'detail-pane-count num';
    count.textContent = String(items.length);
    head.append(title, count);
    pane.appendChild(head);

    const body = document.createElement('div');
    body.className = 'detail-pane-body';
    if (items.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'email-pane-empty';
        empty.textContent = t('email_pane_empty');
        body.appendChild(empty);
    } else {
        items.forEach((it, i) => body.appendChild(buildEmailRow(it, i)));
    }
    pane.appendChild(body);

    return pane;
}

function paintEmailAuditDetails(items) {
    if (items.length === 0) {
        paintEmpty();
        return;
    }
    const split = document.createElement('div');
    split.className = 'detail-split';
    const top = items.filter((it) => it.email_group === 'not_in_wlist');
    const bottom = items.filter((it) => it.email_group === 'in_wlist_no_tx');
    split.append(buildEmailPane('email_pane_not_in_wlist', top), buildEmailPane('email_pane_in_wlist_no_tx', bottom));
    detailBody.replaceChildren(split);
}

// Adds the sender's domain to the user's whitelist via the Setup Wizard's
// backend endpoint. UI-only feedback for now — no reload; the next
// scheduled re-scan picks the change up, and the row is removed from the
// "not in whitelist" pane immediately so the user sees the action land.
async function addSenderToWhitelist(item, btn) {
    const sender = item.email_from || '';
    const domain = sender.split('@').pop() || '';
    btn.disabled = true;
    try {
        await fetch(`${API}/setup/whitelist/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ domain }),
        });
    } catch {
        // Network failure is silent on purpose — the row still disappears
        // locally so the user can keep working; the next scan will re-add
        // it if the backend actually rejected the call.
    }
    showToast(t('email_added_to_wlist')(sender || domain), 'success');
    // Drop this item from the cached list and re-render so the top pane
    // shrinks immediately.
    emailAuditItems = emailAuditItems.filter((it) => it !== item);
    renderCommandCenterCounts();
    paintEmailAuditDetails(emailAuditItems);
}

// Stages a complaint-email draft in the chat composer (same pattern as
// draftNote for findings) — the user reviews/edits, then the existing
// /chat pipeline sends it. We never fire-and-forget an email on the
// user's behalf.
function draftComplaintEmail(item) {
    const days = daysUntilDeadline(item.email_date);
    const deadlinePart =
        days !== null
            ? lang === 'vi'
                ? ` Hạn khiếu nại: còn ${days} ngày.`
                : ` Dispute deadline: ${days} days left.`
            : '';
    const subject = item.email_subject || item.email_ref || findingTitle(item);
    const refPart = item.email_ref ? ` (Ref: ${item.email_ref})` : '';
    const senderPart = item.email_from ? ` từ ${item.email_from}` : '';
    const text =
        lang === 'vi'
            ? `Giúp tôi soạn một email cho đội hỗ trợ: tôi có một giao dịch như email này${refPart}${senderPart} nhưng bên Wealify chưa có giao dịch tương ứng — đề nghị đội support hỗ trợ làm rõ.${deadlinePart}`
            : `Please draft a complaint email to support: I have a transaction receipt in this email${refPart}${senderPart} but no matching transaction on the Wealify side — please investigate.${deadlinePart}`;
    chatInput.value = `${subject}\n\n${text}`;
    chatInput.focus();
    chatInput.setSelectionRange(chatInput.value.length, chatInput.value.length);
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

// ─── Active subscriptions — 60/40 split (mock data) ──────────────────
// The user has flagged this section as a "wire API later" placeholder, so
// the row list is a hard-coded mockup that demonstrates the layout. When
// the real /dashboard/active-subscriptions lands, the only thing that
// changes is how MOCK_ACTIVE_SUBS is populated — every renderer below
// reads it as a plain list.
//
// Two panes, top 60% / bottom 40%:
//   - Top:    "Currently active" — each row has a "Stop renewal" button.
//             Clicking it moves the row to the bottom pane with the
//             current timestamp recorded, so we can later tell whether
//             the user actually went and cancelled at the merchant.
//   - Bottom: "Pending cancellation" — each row shows how many days the
//             cancellation has been pending. After 30 days the row picks
//             up a red ring + "Forgot to cancel?" flag. Buttons on each
//             row let the user confirm they cancelled at the merchant
//             (drop the row entirely) or restore the sub to active.

const MOCK_ACTIVE_SUBS = [
    {
        id: 'sub-adobe-cc',
        name: 'Adobe Creative Cloud',
        amount_cents: 5999,
        currency: 'USD',
        cycle: 'monthly',
        renewal_date: '2026-09-15',
    },
    {
        id: 'sub-figma-pro',
        name: 'Figma Professional',
        amount_cents: 1500,
        currency: 'USD',
        cycle: 'monthly',
        renewal_date: '2026-09-03',
    },
    {
        id: 'sub-notion-plus',
        name: 'Notion Plus',
        amount_cents: 1000,
        currency: 'USD',
        cycle: 'monthly',
        renewal_date: '2026-09-10',
    },
    {
        id: 'sub-nordvpn-2y',
        name: 'NordVPN 2-Year Plan',
        amount_cents: 9900,
        currency: 'USD',
        cycle: 'biennial',
        renewal_date: '2027-03-22',
    },
    {
        id: 'sub-spotify-family',
        name: 'Spotify Family',
        amount_cents: 1699,
        currency: 'USD',
        cycle: 'monthly',
        renewal_date: '2026-09-01',
    },
    {
        id: 'sub-netflix-premium',
        name: 'Netflix Premium',
        amount_cents: 229900,
        currency: 'VND',
        cycle: 'monthly',
        renewal_date: '2026-08-30',
    },
];

const SUB_OVERDUE_DAYS = 30;
const PENDING_CANCEL_KEY = 'wealify_pending_cancellations';

function loadPendingCancellations() {
    try {
        const raw = localStorage.getItem(PENDING_CANCEL_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch {
        return {};
    }
}

function savePendingCancellations(map) {
    try {
        localStorage.setItem(PENDING_CANCEL_KEY, JSON.stringify(map));
    } catch {
        // localStorage unavailable (private window, quota) — the in-memory
        // state still drives the current render; the user just won't see
        // the queue survive a reload.
    }
}

function daysPending(isoTimestamp) {
    if (!isoTimestamp) return 0;
    const ts = new Date(isoTimestamp).getTime();
    if (Number.isNaN(ts)) return 0;
    const ms = Date.now() - ts;
    return Math.max(0, Math.floor(ms / (24 * 60 * 60 * 1000)));
}

function buildSubRow(sub, kind, index) {
    const row = document.createElement('div');
    row.className = 'sub-row';
    if (kind === 'top') {
        // Top pane = "currently active" — gets the green status dot.
        row.classList.add('is-active');
    } else {
        const days = daysPending(sub.cancelled_at);
        if (days > SUB_OVERDUE_DAYS) row.classList.add('is-overdue');
    }
    row.style.setProperty('--i', String(index));

    // Top line: subscription name (wraps freely) + price on the right.
    const head = document.createElement('div');
    head.className = 'sub-row-head';

    const name = document.createElement('span');
    name.className = 'sub-row-name';
    name.textContent = sub.name;
    head.appendChild(name);

    const amount = document.createElement('span');
    amount.className = 'sub-row-amount';
    amount.textContent = fmtCur((sub.amount_cents || 0) / 100, sub.currency || 'USD');
    head.appendChild(amount);

    row.appendChild(head);

    // Middle: meta (cycle · renewal date · pending days).
    const meta = document.createElement('div');
    meta.className = 'sub-row-meta';
    const cycleLabel = sub.cycle ? sub.cycle.charAt(0).toUpperCase() + sub.cycle.slice(1) : '';
    const parts = [];
    if (cycleLabel) parts.push(cycleLabel);
    if (sub.renewal_date) parts.push(`renews ${sub.renewal_date}`);
    if (kind === 'bottom') {
        const days = daysPending(sub.cancelled_at);
        parts.push(t('sub_pending_sub')(days));
    }
    meta.textContent = parts.join(' · ');
    row.appendChild(meta);

    // Bottom: action buttons sit on their own row so the label above is
    // never squeezed by them.
    const actions = document.createElement('div');
    actions.className = 'sub-row-actions';

    if (kind === 'top') {
        const stopBtn = document.createElement('button');
        stopBtn.type = 'button';
        stopBtn.className = 'email-action';
        stopBtn.append(icon('prohibit'), document.createTextNode(t('sub_action_stop_renewal')));
        stopBtn.addEventListener('click', () => moveSubToPending(sub, stopBtn));
        actions.appendChild(stopBtn);
    } else {
        const days = daysPending(sub.cancelled_at);
        if (days > SUB_OVERDUE_DAYS) {
            const flag = document.createElement('span');
            flag.className = 'overdue-flag';
            flag.append(icon('warning-circle'), document.createTextNode(t('sub_overdue_label')));
            flag.title = t('sub_overdue_sub')(days);
            actions.appendChild(flag);
        }
        const restoreBtn = document.createElement('button');
        restoreBtn.type = 'button';
        restoreBtn.className = 'email-action';
        restoreBtn.append(icon('arrow-counter-clockwise'), document.createTextNode(t('sub_action_restore')));
        restoreBtn.addEventListener('click', () => restoreSub(sub, restoreBtn));
        actions.appendChild(restoreBtn);

        const doneBtn = document.createElement('button');
        doneBtn.type = 'button';
        doneBtn.className = 'email-action';
        doneBtn.append(icon('check-circle'), document.createTextNode(t('sub_action_confirmed_cancelled')));
        doneBtn.addEventListener('click', () => confirmCancelled(sub, doneBtn));
        actions.appendChild(doneBtn);
    }

    row.appendChild(actions);
    return row;
}

function buildSubPane(titleKey, items, kind) {
    const pane = document.createElement('section');
    pane.className = 'detail-pane';

    const head = document.createElement('header');
    head.className = 'detail-pane-head';
    const title = document.createElement('h3');
    title.className = 'detail-pane-title';
    title.textContent = t(titleKey);
    const count = document.createElement('span');
    count.className = 'detail-pane-count num';
    count.textContent = String(items.length);
    head.append(title, count);
    pane.appendChild(head);

    const body = document.createElement('div');
    body.className = 'detail-pane-body';
    if (items.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'email-pane-empty';
        empty.textContent = t(kind === 'top' ? 'sub_empty_top' : 'sub_empty_bottom');
        body.appendChild(empty);
    } else {
        items.forEach((it, i) => body.appendChild(buildSubRow(it, kind, i)));
    }
    pane.appendChild(body);

    return pane;
}

function paintActiveSubsDetails() {
    const pending = loadPendingCancellations();
    const active = MOCK_ACTIVE_SUBS.filter((s) => !pending[s.id]);
    const pendingList = MOCK_ACTIVE_SUBS.filter((s) => pending[s.id]).map((s) => ({
        ...s,
        cancelled_at: pending[s.id],
    }));

    const split = document.createElement('div');
    split.className = 'detail-split-60-40';
    split.append(
        buildSubPane('sub_active_top', active, 'top'),
        buildSubPane('sub_active_bottom', pendingList, 'bottom'),
    );
    detailBody.replaceChildren(split);
}

function moveSubToPending(sub, btn) {
    const pending = loadPendingCancellations();
    pending[sub.id] = new Date().toISOString();
    savePendingCancellations(pending);
    btn.disabled = true;
    showToast(t('sub_moved_pending'), 'info');
    paintActiveSubsDetails();
}

function restoreSub(sub, btn) {
    const pending = loadPendingCancellations();
    delete pending[sub.id];
    savePendingCancellations(pending);
    btn.disabled = true;
    showToast(t('sub_restored'), 'success');
    paintActiveSubsDetails();
}

function confirmCancelled(sub, btn) {
    const pending = loadPendingCancellations();
    delete pending[sub.id];
    savePendingCancellations(pending);
    btn.disabled = true;
    showToast(t('sub_confirmed_done'), 'success');
    paintActiveSubsDetails();
}

function renderDetails(flag, { instant = false } = {}) {
    const isEmailAudit = flag === 'email-audit';
    const isActiveSubs = flag === 'active-subs';
    if (!isEmailAudit && !isActiveSubs && !FLAG_FILTERS[flag]) return;

    if (flag !== activeFlag) openIndex = null;
    activeFlag = flag;

    const items = isEmailAudit
        ? emailAuditItems
        : isActiveSubs
          ? MOCK_ACTIVE_SUBS
          : allFindings.filter(FLAG_FILTERS[flag]);

    detailTitle.textContent = t(isEmailAudit ? 'flag_email_audit' : FLAG_TITLE_KEY[flag]);
    detailCount.textContent = t('count_items')(items.length);

    document.querySelectorAll('[data-flag]').forEach((el) => {
        el.classList.toggle('is-active', el.dataset.flag === flag);
    });

    window.clearTimeout(loadTimer);

    if (isEmailAudit) {
        // The email-audit view never uses the skeleton loader — the two
        // panes either populate immediately or stay visibly empty, which is
        // more honest feedback than a couple of grey bars flashing on top
        // of a layout the user is still learning.
        if (instant) paintEmailAuditDetails(items);
        else loadTimer = window.setTimeout(() => paintEmailAuditDetails(items), 220);
        return;
    }

    if (isActiveSubs) {
        // Active-subs is mock data — no network delay, so the skeleton
        // loader would just flash for no reason. Render immediately.
        paintActiveSubsDetails();
        return;
    }

    if (instant) {
        paintDetails(items);
        return;
    }

    showSkeleton(Math.min(items.length, 4) || 2);
    loadTimer = window.setTimeout(() => paintDetails(items), 220);
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
    if (activeFlag) renderDetails(activeFlag, { instant: true });
    else detailTitle.textContent = t('panel_detail');
}

langSwitch.addEventListener('click', (e) => {
    const btn = e.target.closest('.lang-btn');
    if (btn && btn.dataset.lang !== lang) applyLang(btn.dataset.lang);
});

// ─── Command Center clicks ─────────────────────────

document.querySelectorAll('[data-flag]').forEach((el) => {
    el.addEventListener('click', () => renderDetails(el.dataset.flag));
});

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
        showToast(t('run_check_done')(res.new_flags, res.already_reported), 'success');
        await loadAll();
    } else {
        showToast(t('run_check_failed'), 'warning');
    }
});

// ─── Export audit log ──────────────────────────────

document.getElementById('exportAuditBtn').addEventListener('click', async () => {
    const res = await apiGet('/audit-log/export');
    if (res && res.status === 'exported') {
        showToast(`${t('export_done')} ${res.exported_to} (${res.total_flags})`, 'success', 6000);
    } else {
        showToast(t('export_failed'), 'warning');
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
