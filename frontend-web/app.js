/* ═══════════════════════════════════════════════════════
   Wealez — UI interactivity (vanilla JS)
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
        flow_wallet: 'Wealez wallet',
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
        back: 'Back',
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

        context_kind_finding: 'Finding',
        context_kind_email_audit: 'Email',
        context_kind_subscription: 'Subscription',
        context_chip_dismiss: 'Dismiss context',
        detail_ask_ai: 'Ask AI about this',
        context_chip_prefix: (kind, title) => `Asking about ${kind}: ${title}`,

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

        block_report: 'Report',
        create_report: 'Create report',
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

        disclaimer_label: 'Disclaimer',
        disclaimer_text:
            '⚠️ This tool only assists you in reviewing your finances. Results are for reference only, not ' +
            'official Wealez conclusions, and do not replace your own verification. If you notice suspicious ' +
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
        flow_wallet: 'Ví Wealez',
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
        back: 'Quay lại',
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

        context_kind_finding: 'Khoản giao dịch',
        context_kind_email_audit: 'Email',
        context_kind_subscription: 'Gói đăng ký',
        context_chip_dismiss: 'Bỏ ngữ cảnh',
        detail_ask_ai: 'Hỏi AI về item này',
        context_chip_prefix: (kind, title) => `Đang hỏi về ${kind}: ${title}`,

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

        block_report: 'Báo cáo',
        create_report: 'Tạo report',
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

        disclaimer_label: 'Lưu ý',
        disclaimer_text:
            '⚠️ Công cụ này chỉ hỗ trợ bạn rà soát tài chính. Kết quả để tham khảo, không phải kết luận chính ' +
            'thức của Wealez và không thay cho việc bạn tự kiểm tra. Nếu thấy giao dịch lạ, hãy liên hệ hỗ trợ ' +
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

async function apiPostChat(message, context = null) {
    try {
        const body = { message };
        if (context) body.context = context;
        const res = await fetch(`${API}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
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
    const [findingsRes, wallet, suspiciousRes, outboundRes, anomaliesRes] = await Promise.all([
        apiGet('/findings'),
        apiGet('/dashboard/wallet'),
        apiGet('/dashboard/suspicious-domains'),
        apiGet('/dashboard/outbound-reconciliation'),
        apiGet('/dashboard/anomalies'),
    ]);
    allFindings = (findingsRes && findingsRes.findings) || [];
    walletData = wallet;
    emailAuditItems = normalizeEmailAuditItems(suspiciousRes, outboundRes);
    ACTIVE_SUBS = buildActiveSubsFromAnomalies(anomaliesRes);

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
    flagEls.forEach((el) => {
        const flag = el.dataset.flag;
        let count;
        if (flag === 'email-audit') count = emailAuditItems.length;
        else if (flag === 'active-subs') count = ACTIVE_SUBS.length;
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
const detailBackBtn = document.getElementById('detailBackBtn');
const chatContextChip = document.getElementById('chatContextChip');
const chatContextChipText = document.getElementById('chatContextChipText');
const chatContextChipClear = document.getElementById('chatContextChipClear');
// Cached at module load — the set of flag cards in the left panel never
// changes after page load, so re-running querySelectorAll on every
// renderDetails (and every language switch) is wasted work.
const flagEls = document.querySelectorAll('[data-flag]');
const chatHistory = document.getElementById('chatHistory');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const langSwitch = document.getElementById('langSwitch');
const createReportBtn = document.getElementById('createReportBtn');

let lang = localStorage.getItem('wealify_lang') === 'en' ? 'en' : 'vi';
let activeFlag = null;
let rightPanelMode = 'detail'; // 'detail' | 'report'
let reportYear = new Date().getFullYear();
let reportType = 'month';
let selectedMonth = new Date().getMonth() + 1;
let selectedQuarter = Math.floor(new Date().getMonth() / 3) + 1;
let selectedCurrency = null;
let reportChart = null;
// Index of the item currently opened in the detail view, scoped to the
// items list rendered for `activeFlag`. null = show the list of items
// for the active flag (the previous accordion behaviour let users peek
// inside one row inline; we now replace the list entirely with that
// item's detail until the user clicks Back).
let openItem = null;
// Snapshot of the item the user is currently inspecting in the detail
// view + its kind ('finding' | 'email-audit' | 'subscription'). Used to
// attach the item's full data to every chat message so the LLM can
// answer questions about the specific transaction / email / subscription
// without the user having to spell out the details. Mirrored visually
// in the chat-context-chip in the chat footer; clicking the chip's ×
// button (or the Back button in the right panel) clears it.
let currentDetailItem = null;
let currentDetailKind = null;
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

// Pastel warning block — shared by finding-detail and email-detail
// pages; the optional `stack` class turns it into a wider card on the
// detail view vs the inline list-row variant.
function buildExplanationWarning(text, { stack = false } = {}) {
    const warn = document.createElement('div');
    warn.className = 'detail-warning' + (stack ? ' detail-page-warning' : '');
    const label = document.createElement('span');
    label.textContent = text;
    warn.append(icon('warning-circle'), label);
    return warn;
}

// Buckets a "days until deadline" value into one of three visual tiers
// so the compact email-row pill and the wide email-detail block agree
// on what counts as urgent vs clear vs normal.
function computeDeadlineUrgency(days) {
    if (days <= 0) return 'urgent';
    if (days <= 14) return 'urgent';
    if (days > 30) return 'clear';
    return 'normal';
}

// Renders a deadline badge in either the compact list-row shape or the
// wide detail-page shape — both sites used to spell the urgency math
// and class names inline.
function buildDeadlineBadge(days, { tag = 'span', baseClass = 'deadline-pill' } = {}) {
    const urgency = computeDeadlineUrgency(days);
    const elNode = document.createElement(tag);
    elNode.className = baseClass + (urgency === 'urgent' ? ' is-urgent' : urgency === 'clear' ? ' is-clear' : '');
    elNode.append(icon('hourglass-medium'), document.createTextNode(t('email_deadline_urgent')(days)));
    return elNode;
}

// ─── Chat context chip ──────────────────────────────────────────────
// Visual mirror of currentDetailItem / currentDetailKind. When the user
// is in a detail view the chip appears above the chat input so they
// always know the next message will carry the item's data to the LLM.
// The × button clears the context (right panel keeps showing the item)
// without forcing the user to leave the detail view first.

const KIND_LABEL_KEY = {
    finding: 'context_kind_finding',
    'email-audit': 'context_kind_email_audit',
    subscription: 'context_kind_subscription',
};
function kindLabelKey(kind) {
    return KIND_LABEL_KEY[kind] || null;
}

function renderChatContextChip() {
    if (currentDetailItem && currentDetailKind) {
        const key = kindLabelKey(currentDetailKind);
        const kindLabel = key ? t(key) : currentDetailKind;
        const title = detailTitleFor(currentDetailItem);
        chatContextChipText.textContent = t('context_chip_prefix')(kindLabel, title);
        chatContextChip.hidden = false;
    } else {
        chatContextChip.hidden = true;
        chatContextChipText.textContent = '';
    }
}

function buildDetailItem(f, index) {
    // List-row summary — click opens the full detail view for this item
    // (replaces the old inline accordion expand).
    const row = document.createElement('article');
    row.className = 'detail-item';
    row.style.setProperty('--i', String(index));

    const head = document.createElement('button');
    head.type = 'button';
    head.className = 'detail-head';

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

    head.append(main, icon('caret-right', 'detail-chevron'));

    row.appendChild(head);
    head.addEventListener('click', () => openItemFromList(index));

    return row;
}

// Builds the meta block (ID/status/deadline/confidence/evidence) and
// the optional draft-note action. Reused both by the (now-removed) inline
// accordion and by paintFindingDetail below.
function buildFindingMeta(f) {
    const isAlert = f.label === 'CAN_BAN_TU_XAC_NHAN';

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

    const wrapper = document.createElement('div');
    wrapper.className = 'detail-page-body';

    if (isAlert) {
        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'detail-action';
        const label = document.createElement('span');
        label.textContent = t('action_draft_email');
        action.append(icon('envelope-simple'), label);
        action.addEventListener('click', () => draftNote(f));
        wrapper.append(action);
    }

    wrapper.prepend(meta);
    return wrapper;
}

// Full-page detail for a single finding — fills the entire right panel
// body. Same content the old accordion .detail-extra showed, but as the
// only thing on screen so the user can read it without scrolling past
// every other row in the list.
function paintFindingDetail(f) {
    const page = document.createElement('article');
    page.className = 'detail-page';

    const head = document.createElement('header');
    head.className = 'detail-page-head';

    const title = document.createElement('h3');
    title.className = 'detail-page-title';
    title.textContent = findingTitle(f);

    const sub = document.createElement('div');
    sub.className = 'detail-page-sub';

    const isAlert = f.label === 'CAN_BAN_TU_XAC_NHAN';
    const amount = document.createElement('span');
    amount.className = 'detail-page-amount num' + (isAlert ? ' is-alert' : '');
    amount.textContent = fmtCur((f.amount_cents || 0) / 100, f.currency || 'USD');
    sub.appendChild(amount);

    if (f.occurred_at) {
        const date = document.createElement('span');
        date.className = 'detail-page-date';
        date.textContent = f.occurred_at;
        sub.appendChild(date);
    }

    head.append(title, sub);
    page.appendChild(head);

    const explanation = findingExplanation(f);
    if (explanation) {
        page.appendChild(buildExplanationWarning(explanation, { stack: true }));
    }

    page.appendChild(buildFindingMeta(f));
    page.appendChild(buildAskAiButton(f, 'finding'));

    detailBody.replaceChildren(page);
    detailBody.scrollTop = 0;
}

function openItemFromList(index) {
    openItem = index;
    renderDetails(activeFlag, { instant: true });
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

function buildEmailRow(item, flatIndex) {
    // `flatIndex` is the position in the unified emailAuditItems array
    // (the list the right panel would render as a flat list), not the
    // position within this pane — keeps openItem stable across both panes.
    const row = document.createElement('div');
    row.className = 'email-row';
    row.style.setProperty('--i', String(flatIndex));

    const main = document.createElement('button');
    main.type = 'button';
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

    main.addEventListener('click', () => openItemFromList(flatIndex));

    const side = document.createElement('div');
    side.className = 'email-row-side';

    if (item.email_group === 'in_wlist_no_tx') {
        const days = daysUntilDeadline(item.email_date);
        if (days !== null) {
            side.appendChild(buildDeadlineBadge(days));
        }

        const complaint = document.createElement('button');
        complaint.type = 'button';
        complaint.className = 'email-action';
        complaint.append(icon('envelope-simple'), document.createTextNode(t('email_action_draft_complaint')));
        // The action button is inside .email-row-side (separate from
        // .email-row-main) so clicking it never bubbles to "open detail".
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

function buildEmailPane(titleKey, paneItems, itemsRef) {
    const pane = document.createElement('section');
    pane.className = 'detail-pane';

    const head = document.createElement('header');
    head.className = 'detail-pane-head';
    const title = document.createElement('h3');
    title.className = 'detail-pane-title';
    title.textContent = t(titleKey);
    const count = document.createElement('span');
    count.className = 'detail-pane-count num';
    count.textContent = String(paneItems.length);
    head.append(title, count);
    pane.appendChild(head);

    const body = document.createElement('div');
    body.className = 'detail-pane-body';
    if (paneItems.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'email-pane-empty';
        empty.textContent = t('email_pane_empty');
        body.appendChild(empty);
    } else {
        // O(1) lookup map built once per pane-render — the old
        // `emailAuditItems.indexOf(it)` was O(m) per row, making a
        // 60-item list render 1800 comparisons on every paint.
        const flatIndexByItem = new Map(itemsRef.map((it, i) => [it, i]));
        paneItems.forEach((it) => {
            body.appendChild(buildEmailRow(it, flatIndexByItem.get(it)));
        });
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
    split.append(
        buildEmailPane('email_pane_not_in_wlist', top, items),
        buildEmailPane('email_pane_in_wlist_no_tx', bottom, items),
    );
    detailBody.replaceChildren(split);
}

// Full-page detail for one email-audit item — replaces the list of two
// panes with a single article showing everything we know about the
// sender, subject, full date, Ref, explanation, deadline, and the same
// action button that used to live in the compact row.
function paintEmailDetail(item) {
    const page = document.createElement('article');
    page.className = 'detail-page';

    const head = document.createElement('header');
    head.className = 'detail-page-head';

    const title = document.createElement('h3');
    title.className = 'detail-page-title';
    title.textContent = item.email_from || item.email_ref || findingTitle(item);
    head.appendChild(title);

    const sub = document.createElement('div');
    sub.className = 'detail-page-sub detail-page-sub-stack';

    const subject = document.createElement('div');
    subject.className = 'detail-page-subject';
    subject.textContent = item.email_subject || findingExplanation(item) || '';
    sub.appendChild(subject);

    if (item.email_ref) {
        const ref = document.createElement('div');
        ref.className = 'detail-page-ref';
        ref.textContent = `Ref ${item.email_ref}`;
        sub.appendChild(ref);
    }

    if (item.email_date) {
        const date = document.createElement('div');
        date.className = 'detail-page-date';
        date.textContent = item.email_date;
        sub.appendChild(date);
    }

    head.appendChild(sub);
    page.appendChild(head);

    const explanation = findingExplanation(item);
    if (explanation) {
        page.appendChild(buildExplanationWarning(explanation, { stack: true }));
    }

    if (item.email_group === 'in_wlist_no_tx') {
        const days = daysUntilDeadline(item.email_date);
        if (days !== null) {
            page.appendChild(buildDeadlineBadge(days, { tag: 'div', baseClass: 'deadline-block' }));
        }
    }

    const actions = document.createElement('div');
    actions.className = 'detail-page-actions';
    if (item.email_group === 'in_wlist_no_tx') {
        const complaint = document.createElement('button');
        complaint.type = 'button';
        complaint.className = 'detail-action';
        complaint.append(icon('envelope-simple'), document.createTextNode(t('email_action_draft_complaint')));
        complaint.addEventListener('click', () => draftComplaintEmail(item));
        actions.appendChild(complaint);
    } else {
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'detail-action';
        addBtn.append(icon('plus-circle'), document.createTextNode(t('email_action_add_wlist')));
        addBtn.addEventListener('click', () => addSenderToWhitelist(item, addBtn));
        actions.appendChild(addBtn);
    }
    page.appendChild(actions);
    page.appendChild(buildAskAiButton(item, 'email-audit'));

    detailBody.replaceChildren(page);
    detailBody.scrollTop = 0;
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
            ? `Giúp tôi soạn một email cho đội hỗ trợ: tôi có một giao dịch như email này${refPart}${senderPart} nhưng bên Wealez chưa có giao dịch tương ứng — đề nghị đội support hỗ trợ làm rõ.${deadlinePart}`
            : `Please draft a complaint email to support: I have a transaction receipt in this email${refPart}${senderPart} but no matching transaction on the Wealez side — please investigate.${deadlinePart}`;
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

// ─── Active subscriptions — 60/40 split ──────────────────
// Wired to /dashboard/anomalies' real subscriptions list (populated below
// in loadAll, see buildActiveSubsFromAnomalies) instead of the mock
// placeholder this started as — no fabricated subscription names/prices.
//
// Two panes, top 60% / bottom 40%:
//   - Top:    "Currently active" — each row has a "Stop renewal" button.
//             Clicking it moves the row to the bottom pane with the
//             current timestamp recorded, so we can later tell whether
//             the user actually went and cancelled at the merchant. This
//             is a local note-to-self only (localStorage) — the app never
//             calls Wealify to actually cancel anything.
//   - Bottom: "Pending cancellation" — each row shows how many days the
//             cancellation has been pending. After 30 days the row picks
//             up a red ring + "Forgot to cancel?" flag. Buttons on each
//             row let the user confirm they cancelled at the merchant
//             (drop the row entirely) or restore the sub to active.

let ACTIVE_SUBS = [];

// Maps /dashboard/anomalies' real subscriptions (anomaly_detector.py —
// merchant_code, description, current_price, frequency, next_charge_date)
// into the row shape this section's renderer already expects. No currency
// field there (anomaly_detector.py doesn't track it) — defaults to USD,
// which every real subscription found in this account's live data is.
function buildActiveSubsFromAnomalies(anomalies) {
    const subs = (anomalies && anomalies.subscriptions) || [];
    return subs.map((s) => ({
        id: s.merchant_code || s.description,
        name: s.description,
        amount_cents: Math.round((s.current_price || 0) * 100),
        currency: 'USD',
        cycle: s.frequency || '',
        renewal_date: s.next_charge_date || '',
    }));
}

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

function buildSubRow(sub, kind, flatIndex) {
    // `flatIndex` is the position of `sub` in the unified ACTIVE_SUBS
    // list — kept stable so openItem can be re-resolved when the user
    // returns from the detail view.
    const row = document.createElement('div');
    row.className = 'sub-row';
    if (kind === 'top') {
        // Top pane = "currently active" — gets the green status dot.
        row.classList.add('is-active');
    } else {
        const days = daysPending(sub.cancelled_at);
        if (days > SUB_OVERDUE_DAYS) row.classList.add('is-overdue');
    }
    row.style.setProperty('--i', String(flatIndex));

    // Top line: subscription name (wraps freely) + price on the right.
    // The whole head is a button so clicking anywhere on it (name or
    // price) opens the detail view — the action buttons below are
    // siblings, not nested, so they never bubble up to open detail.
    const head = document.createElement('button');
    head.type = 'button';
    head.className = 'sub-row-head';

    const name = document.createElement('span');
    name.className = 'sub-row-name';
    name.textContent = sub.name;
    head.appendChild(name);

    const amount = document.createElement('span');
    amount.className = 'sub-row-amount';
    amount.textContent = fmtCur((sub.amount_cents || 0) / 100, sub.currency || 'USD');
    head.appendChild(amount);

    head.addEventListener('click', () => openItemFromList(flatIndex));
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

function buildSubPane(titleKey, items, kind, itemsRef) {
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
        // O(1) lookup map built once per pane-render. ACTIVE_SUBS
        // is the canonical list of subscriptions (split into top/bottom
        // panes below by cancellation status), so the flat index is the
        // same as this row's position in it.
        const flatIndexById = new Map(itemsRef.map((s, i) => [s.id, i]));
        items.forEach((it) => {
            body.appendChild(buildSubRow(it, kind, flatIndexById.get(it.id)));
        });
    }
    pane.appendChild(body);

    return pane;
}

// Full-page detail for one subscription — replaces the 60/40 split panes
// with a single article showing the name, full price, cycle, renewal
// date, pending days (if applicable), and the same action buttons that
// used to live at the bottom of the row.
function paintSubDetail(sub) {
    const pending = loadPendingCancellations();
    const kind = pending[sub.id] ? 'bottom' : 'top';
    const cancelledAt = pending[sub.id];
    const days = cancelledAt ? daysPending(cancelledAt) : 0;

    const page = document.createElement('article');
    page.className = 'detail-page';

    const head = document.createElement('header');
    head.className = 'detail-page-head';

    const title = document.createElement('h3');
    title.className = 'detail-page-title';
    title.textContent = sub.name;
    head.appendChild(title);

    const sub_ = document.createElement('div');
    sub_.className = 'detail-page-sub detail-page-sub-stack';

    const amount = document.createElement('div');
    amount.className = 'detail-page-amount num';
    amount.textContent = fmtCur((sub.amount_cents || 0) / 100, sub.currency || 'USD');
    sub_.appendChild(amount);

    const metaParts = [];
    if (sub.cycle) metaParts.push(sub.cycle.charAt(0).toUpperCase() + sub.cycle.slice(1));
    if (sub.renewal_date) metaParts.push(`renews ${sub.renewal_date}`);
    if (kind === 'bottom') metaParts.push(t('sub_pending_sub')(days));
    if (metaParts.length) {
        const meta = document.createElement('div');
        meta.className = 'detail-page-date';
        meta.textContent = metaParts.join(' · ');
        sub_.appendChild(meta);
    }

    head.appendChild(sub_);
    page.appendChild(head);

    if (kind === 'bottom' && days > SUB_OVERDUE_DAYS) {
        const overdue = document.createElement('div');
        overdue.className = 'deadline-block is-urgent';
        overdue.append(icon('warning-circle'), document.createTextNode(t('sub_overdue_label')));
        overdue.title = t('sub_overdue_sub')(days);
        page.appendChild(overdue);
    }

    const actions = document.createElement('div');
    actions.className = 'detail-page-actions';

    if (kind === 'top') {
        const stopBtn = document.createElement('button');
        stopBtn.type = 'button';
        stopBtn.className = 'detail-action';
        stopBtn.append(icon('prohibit'), document.createTextNode(t('sub_action_stop_renewal')));
        stopBtn.addEventListener('click', () => moveSubToPending(sub, stopBtn));
        actions.appendChild(stopBtn);
    } else {
        const restoreBtn = document.createElement('button');
        restoreBtn.type = 'button';
        restoreBtn.className = 'detail-action';
        restoreBtn.append(icon('arrow-counter-clockwise'), document.createTextNode(t('sub_action_restore')));
        restoreBtn.addEventListener('click', () => restoreSub(sub, restoreBtn));
        actions.appendChild(restoreBtn);

        const doneBtn = document.createElement('button');
        doneBtn.type = 'button';
        doneBtn.className = 'detail-action';
        doneBtn.append(icon('check-circle'), document.createTextNode(t('sub_action_confirmed_cancelled')));
        doneBtn.addEventListener('click', () => confirmCancelled(sub, doneBtn));
        actions.appendChild(doneBtn);
    }
    page.appendChild(actions);
    page.appendChild(buildAskAiButton(sub, 'subscription'));

    detailBody.replaceChildren(page);
    detailBody.scrollTop = 0;
}

function paintActiveSubsDetails() {
    const pending = loadPendingCancellations();
    const active = ACTIVE_SUBS.filter((s) => !pending[s.id]);
    const pendingList = ACTIVE_SUBS.filter((s) => pending[s.id]).map((s) => ({
        ...s,
        cancelled_at: pending[s.id],
    }));

    const split = document.createElement('div');
    split.className = 'detail-split-60-40';
    split.append(
        buildSubPane('sub_active_top', active, 'top', ACTIVE_SUBS),
        buildSubPane('sub_active_bottom', pendingList, 'bottom', ACTIVE_SUBS),
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
    rightPanelMode = 'detail';
    const isEmailAudit = flag === 'email-audit';
    const isActiveSubs = flag === 'active-subs';
    if (!isEmailAudit && !isActiveSubs && !FLAG_FILTERS[flag]) return;

    // Switching flags always drops back to the list view — the openItem
    // belongs to the previous flag's items list and would otherwise
    // land on the wrong row (or no row at all) under the new flag.
    if (flag !== activeFlag) openItem = null;
    activeFlag = flag;

    const items = isEmailAudit
        ? emailAuditItems
        : isActiveSubs
          ? ACTIVE_SUBS
          : allFindings.filter(FLAG_FILTERS[flag]);

    const inDetail = openItem !== null && openItem >= 0 && openItem < items.length;

    // Mirror the detail view into the chat-context state so the next
    // message the user sends from the chat composer carries the item's
    // full data as context for the LLM. Cleared on flag switch / Back.
    if (inDetail) {
        currentDetailItem = items[openItem];
        currentDetailKind = isEmailAudit ? 'email-audit' : isActiveSubs ? 'subscription' : 'finding';
    } else {
        currentDetailItem = null;
        currentDetailKind = null;
    }
    renderChatContextChip();
    // Hide the back button + count and show the item title when the
    // user is inside a single-item detail view; the count only makes
    // sense for the list view it now replaces.
    detailBackBtn.hidden = !inDetail;
    detailCount.hidden = inDetail;
    detailTitle.textContent = inDetail
        ? detailTitleFor(items[openItem])
        : t(isEmailAudit ? 'flag_email_audit' : FLAG_TITLE_KEY[flag]);
    if (!inDetail) detailCount.textContent = t('count_items')(items.length);

    flagEls.forEach((el) => {
        el.classList.toggle('is-active', el.dataset.flag === flag);
    });

    window.clearTimeout(loadTimer);

    // Detail-view branch — render exactly one item filling the body, no
    // skeleton loader (same reason as the email-audit list view: no
    // network flash to soften, the data is already in memory).
    if (inDetail) {
        const item = items[openItem];
        if (isEmailAudit) paintEmailDetail(item);
        else if (isActiveSubs) paintSubDetail(item);
        else paintFindingDetail(item);
        return;
    }

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
        // ACTIVE_SUBS is already in memory by the time this can be
        // clicked (populated in loadAll before first paint) — no
        // network round-trip here, so the skeleton loader would just
        // flash for no reason. Render immediately.
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

// Title for the panel-head when the right side is showing a single
// item. Falls back to a generic label if the item has no obvious name.
function detailTitleFor(item) {
    if (activeFlag === 'email-audit') return item.email_from || item.email_ref || findingTitle(item);
    if (activeFlag === 'active-subs') return item.name || findingTitle(item);
    return findingTitle(item);
}

// ─── Report builder (month/quarter/year, Chart.js, self-notify send) ──

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
        // Two-step send: this button only requests the draft (confirmed
        // omitted/false) and shows it in chat for the user to read before
        // a second, explicit click actually sends — spec requires "xác
        // nhận trước khi gửi", not sending straight from one click.
        sendBtn.onclick = async () => {
            const payload = {
                period_type: reportType,
                period_value: reportType === 'year' ? null : reportType === 'month' ? selectedMonth : selectedQuarter,
            };
            const draft = await apiPost('/dashboard/reporting/send-email', payload);
            if (!draft || draft.status !== 'draft') {
                appendMessage(t('report_send_failed'), 'ai');
                return;
            }
            appendMessage(
                `📧 <strong>${draft.subject}</strong><br>${t('report_send_email')}: ${draft.to}` +
                    `<br><br><button type="button" class="report-send-confirm-btn" id="reportSendConfirmBtn">${t('report_send_email')}</button>`,
                'ai',
            );
            const confirmBtn = document.getElementById('reportSendConfirmBtn');
            if (confirmBtn) {
                confirmBtn.onclick = async () => {
                    confirmBtn.disabled = true;
                    const res = await apiPost('/dashboard/reporting/send-email', { ...payload, confirmed: true });
                    if (res && res.status === 'sent') {
                        appendMessage(t('report_send_success')(res.to), 'ai');
                    } else {
                        appendMessage(t('report_send_failed'), 'ai');
                    }
                };
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

if (createReportBtn) {
    createReportBtn.addEventListener('click', () => {
        openReportPanel();
    });
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

    document.querySelectorAll('[data-i18n-aria-label]').forEach((el) => {
        const value = I18N[lang][el.dataset.i18nAriaLabel];
        if (typeof value === 'string') el.setAttribute('aria-label', value);
    });

    langSwitch.querySelectorAll('.lang-btn').forEach((btn) => {
        btn.classList.toggle('is-active', btn.dataset.lang === lang);
    });

    renderReconciliation();
    renderCommandCenterCounts();
    if (rightPanelMode === 'report') openReportPanel();
    else if (activeFlag) renderDetails(activeFlag, { instant: true });
    else detailTitle.textContent = t('panel_detail');
    renderChatContextChip();
}

langSwitch.addEventListener('click', (e) => {
    const btn = e.target.closest('.lang-btn');
    if (btn && btn.dataset.lang !== lang) applyLang(btn.dataset.lang);
});

// ─── Command Center clicks ─────────────────────────

document.querySelectorAll('[data-flag]').forEach((el) => {
    el.addEventListener('click', () => renderDetails(el.dataset.flag));
});

// Back button — collapses the current single-item detail view back to
// the list of items for the active flag. No-op if the user somehow
// triggers it from the list view (the button is hidden there). The
// chat-context-chip is cleared by renderDetails itself, so we don't
// need to call renderChatContextChip here.
detailBackBtn.addEventListener('click', () => {
    if (!activeFlag) return;
    openItem = null;
    currentDetailItem = null;
    currentDetailKind = null;
    renderDetails(activeFlag, { instant: true });
});

// × on the chat-context-chip clears the active context without leaving
// the detail view — the right panel keeps showing the same item, but
// the next chat message will go to the LLM without the item context.
chatContextChipClear.addEventListener('click', () => {
    currentDetailItem = null;
    currentDetailKind = null;
    renderChatContextChip();
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

    // Attach the currently-open detail item as context if the chip is
    // active. The backend prepends a structured summary to the user
    // message so the LLM can answer questions about this specific item.
    // Only `type` + `data` are needed — the backend doesn't read the
    // active flag, and shipping extras wastes payload bytes on every
    // chat request.
    const contextPayload = currentDetailItem && currentDetailKind
        ? { type: currentDetailKind, data: currentDetailItem }
        : null;

    const res = await apiPostChat(question, contextPayload);
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
// Pre-fills the chat composer with a starter question about the given
// item. Covers all three item kinds so the "Ask AI about this" button
// inside each detail view (and the per-finding "Draft note for chat"
// inline action) can share the same generator.
function draftAskForItem(item, kind) {
    let body;
    if (kind === 'finding') {
        const deadlinePart = item.dispute_deadline
            ? lang === 'vi'
                ? ` Hạn khiếu nại: ${item.dispute_deadline} (còn ${item.days_left} ngày).`
                : ` Dispute deadline: ${item.dispute_deadline} (${item.days_left} days left).`
            : '';
        body = lang === 'vi'
            ? `Giải thích giúp mình khoản này: ${findingTitle(item)} — ${findingExplanation(item)}${deadlinePart}`
            : `Explain this to me: ${findingTitle(item)} — ${findingExplanation(item)}${deadlinePart}`;
    } else if (kind === 'email-audit') {
        const subj = item.email_subject || findingTitle(item) || '';
        const sender = item.email_from || '';
        const refPart = item.email_ref ? ` (Ref: ${item.email_ref})` : '';
        body = lang === 'vi'
            ? `Email này có đáng lo không? "${subj}" từ ${sender}${refPart}`
            : `Should I be concerned about this email? "${subj}" from ${sender}${refPart}`;
    } else if (kind === 'subscription') {
        const price = fmtCur((item.amount_cents || 0) / 100, item.currency || 'USD');
        body = lang === 'vi'
            ? `Tôi có nên giữ gói "${item.name}" này không? (${price}, gia hạn ${item.renewal_date || '—'})`
            : `Should I keep this "${item.name}" subscription? (${price}, renews ${item.renewal_date || '—'})`;
    } else {
        body = lang === 'vi' ? `Giải thích giúp mình mục này.` : `Tell me about this item.`;
    }
    chatInput.value = body;
    chatInput.focus();
    chatInput.setSelectionRange(chatInput.value.length, chatInput.value.length);
}

// Back-compat shim — the "Draft note for chat" inline action in the
// finding meta block used to call this directly; it now shares the
// generic draftAskForItem so all three detail views go through one
// place.
function draftNote(f) {
    draftAskForItem(f, 'finding');
}

// Builds the "Ask AI about this" CTA used at the bottom of every
// detail-page. Clicking pre-fills the chat composer with a starter
// question AND ensures the chat-context-chip is showing so the user
// sees the message will carry this item's data to the LLM.
function buildAskAiButton(item, kind) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'detail-page-ask-ai';
    btn.append(icon('chat-circle-dots'), document.createTextNode(t('detail_ask_ai')));
    btn.addEventListener('click', () => {
        // Make sure the context chip reflects this item even if the
        // user previously cleared it (or came back from list view).
        if (currentDetailItem !== item || currentDetailKind !== kind) {
            currentDetailItem = item;
            currentDetailKind = kind;
            renderChatContextChip();
        }
        draftAskForItem(item, kind);
    });
    return btn;
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
