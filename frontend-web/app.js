/* ═══════════════════════════════════════════════════════
   Wealify Scout — UI interactivity (vanilla JS)
   ═══════════════════════════════════════════════════════ */

// ─── i18n dictionary ───────────────────────────────

const I18N = {
    en: {
        brand_sub: 'AI financial review',
        profile_card: 'Card 4218 · 7734',

        panel_command: 'Command Center',
        panel_hint_live: 'Live review',
        block_reconciliation: 'Reconciliation',
        flow_bank: 'Bank account',
        flow_wallet: 'Wealify wallet',
        flow_card: 'Card statement',
        alert_mismatch: '$50.05 unaccounted for',
        alert_mismatch_sub: 'Left the account, not yet on the card',

        block_urgent: 'Urgent flags',
        flag_duplicate: 'Duplicate charges',
        flag_duplicate_sub: '3 transactions',
        flag_unrecognized: 'Unrecognized',
        flag_unrecognized_sub: '5 transactions',
        flag_audit: 'Audit required',
        flag_audit_sub: '5 transactions',

        flag_email_audit: 'Email reconciliation needed',
        flag_email_audit_sub: '8 emails',

        action_add_whitelist: 'Add to whitelist',
        action_draft_appeal: 'Draft appeal email',
        label_days_remaining: (days) => `${days} days left`,

        section_whitelist_not_found: 'Emails not yet in whitelist',
        section_whitelist_found: 'Whitelisted emails without a matching transaction',

        section_active_subs: 'Currently active',
        section_pending_cancel: 'Awaiting cancellation',
        action_want_cancel: 'Want to cancel renewal',
        action_pending_cancel: 'Cancellation pending',
        action_forgot_cancel: 'Forgot to cancel',
        label_marked_ago: (days) => `Marked ${days} day${days === 1 ? '' : 's'} ago`,
        label_marked_overdue: (days) => `${days} days since cancellation request`,

        block_radar: 'Subscriptions',
        sub_price: 'Price increased',
        sub_active: 'Active subscriptions',
        sub_trial: 'Trials ending soon',
        sub_unused: 'Unused 60+ days',

        panel_chat: 'AI Chat Assistant',
        status_online: 'Online',
        chat_greeting: "Hi TienNX, I've cross-checked your card statements, wallet, and emails. Where should we start?",
        chip_top3: 'Top 3 expenses?',
        chip_duplicate: 'Any duplicate charges?',
        chip_subs: 'Which subscriptions increased?',
        chip_report: 'Draft monthly report',
        chat_placeholder: 'Ask about your transactions',
        readonly_note: 'Read-only access mode',
        ai_reply:
            'Reviewing that against your card statement, wallet and receipt emails now. Results are for reference ' +
            'only, so please confirm anything unusual with support.',

        panel_detail: 'Detail view',
        empty_title: 'Nothing selected',
        empty_sub: 'Pick a flag in the Command Center to inspect the underlying transactions.',
        detail_duplicate: 'Duplicate charges',
        detail_unrecognized: 'Unrecognized',
        detail_audit: 'Audit required',
        detail_price_hike: 'Price increased',
        detail_active_subs: 'Active subscriptions',
        detail_trial: 'Trials ending soon',
        detail_unused: 'Unused 60+ days',
        label_txn_id: 'Transaction ID',
        label_merchant: 'Merchant',
        label_time: 'Time',
        label_status: 'Status',
        label_reason: 'Reason',
        label_email: 'Email',
        count_items: (n) => `${n} item${n === 1 ? '' : 's'}`,
        action_draft_email: 'Draft support email',
        // Single line on purpose: a text input strips newlines.
        prompt_draft_email: (item) =>
            `Draft a support email asking Wealify to review this transaction — ` +
            `merchant: ${item.details.name} (${item.merchant}); ` +
            `amount: ${item.amount}; ` +
            `date: ${loc(item.date)}; ` +
            `transaction ID: ${item.details.id}; ` +
            `reason for review: ${item.reason.en}. ` +
            `Keep it factual and polite, ask for a written response, and mention that the US dispute window is ` +
            `60 days from the statement date. Do not accuse anyone of fraud.`,

        disclaimer_label: 'Disclaimer',
        disclaimer_text:
            'This tool only assists in financial review. Results are for reference only. If you see strange ' +
            'transactions, contact support immediately. US dispute timeframe is 60 days from the statement date.',
    },

    vi: {
        brand_sub: 'Rà soát tài chính bằng AI',
        profile_card: 'Thẻ 4218 · 7734',

        panel_command: 'Trung tâm điều khiển',
        panel_hint_live: 'Rà soát trực tiếp',
        block_reconciliation: 'Đối soát',
        flow_bank: 'Tài khoản ngân hàng',
        flow_wallet: 'Ví Wealify',
        flow_card: 'Sao kê thẻ',
        alert_mismatch: 'Chưa khớp $50.05',
        alert_mismatch_sub: 'Đã rời tài khoản nhưng chưa lên thẻ',

        block_urgent: 'Cảnh báo giao dịch bất thường',
        flag_duplicate: 'Giao dịch trùng lặp',
        flag_duplicate_sub: '3 giao dịch',
        flag_unrecognized: 'Chưa có email biên lai',
        flag_unrecognized_sub: '5 giao dịch',
        flag_audit: 'Cần kiểm tra thủ công',
        flag_audit_sub: '5 giao dịch',

        flag_email_audit: 'Cần đối soát email',
        flag_email_audit_sub: '8 email',

        action_add_whitelist: 'Thêm vào whitelist',
        action_draft_appeal: 'Soạn email khiếu nại',
        label_days_remaining: (days) => `${days} ngày còn lại`,

        section_whitelist_not_found: 'Email chưa có trong whitelist',
        section_whitelist_found: 'Email trong whitelist nhưng chưa có giao dịch',

        section_active_subs: 'Đang hoạt động',
        section_pending_cancel: 'Đang chờ hủy',
        action_want_cancel: 'Muốn dừng gia hạn',
        action_pending_cancel: 'Đang chờ hủy',
        action_forgot_cancel: 'Quên hủy đăng ký',
        label_marked_ago: (days) => `Đã đánh dấu ${days} ngày trước`,
        label_marked_overdue: (days) => `${days} ngày từ lúc yêu cầu hủy`,

        block_radar: 'Các gói đăng ký',
        sub_price: 'Gói tăng giá',
        sub_active: 'Gói đang hoạt động',
        sub_trial: 'Bản dùng thử sắp hết hạn',
        sub_unused: 'Không dùng 60+ ngày',

        panel_chat: 'Trợ lý AI',
        status_online: 'Trực tuyến',
        chat_greeting: 'Chào TienNX, mình đã đối chiếu sao kê thẻ, ví và email của bạn. Bạn muốn bắt đầu từ đâu?',
        chip_top3: '3 khoản chi lớn nhất?',
        chip_duplicate: 'Có giao dịch trùng không?',
        chip_subs: 'Gói nào vừa tăng giá?',
        chip_report: 'Soạn báo cáo tháng',
        chat_placeholder: 'Hỏi về giao dịch của bạn',
        readonly_note: 'Chế độ chỉ đọc',
        ai_reply:
            'Mình đang đối chiếu với sao kê thẻ, ví và email biên lai của bạn. Kết quả chỉ để tham khảo, bạn nên ' +
            'xác nhận lại với bộ phận hỗ trợ nếu thấy điểm bất thường.',

        panel_detail: 'Chi tiết',
        empty_title: 'Chưa chọn mục nào',
        empty_sub: 'Chọn một cảnh báo ở Trung tâm điều khiển để xem chi tiết giao dịch.',
        detail_duplicate: 'Giao dịch trùng lặp',
        detail_unrecognized: 'Chưa nhận diện',
        detail_audit: 'Cần kiểm tra thủ công',
        detail_price_hike: 'Gói tăng giá',
        detail_active_subs: 'Gói đang hoạt động',
        detail_trial: 'Bản dùng thử sắp hết hạn',
        detail_unused: 'Không dùng 60+ ngày',
        label_txn_id: 'Mã giao dịch',
        label_merchant: 'Đơn vị bán',
        label_time: 'Thời gian',
        label_status: 'Trạng thái',
        label_reason: 'Lý do',
        label_email: 'Email',
        count_items: (n) => `${n} mục`,
        action_draft_email: 'Soạn email hỗ trợ',
        // Một dòng duy nhất vì ô input sẽ bỏ ký tự xuống dòng.
        prompt_draft_email: (item) =>
            `Soạn mẫu email gửi bộ phận hỗ trợ Wealify để yêu cầu kiểm tra giao dịch này — ` +
            `đơn vị bán: ${item.details.name} (${item.merchant}); ` +
            `số tiền: ${item.amount}; ` +
            `ngày: ${loc(item.date)}; ` +
            `mã giao dịch: ${item.details.id}; ` +
            `lý do cần kiểm tra: ${item.reason.vi}. ` +
            `Viết tiếng Việt, giọng lịch sự và bám sát dữ kiện, đề nghị phản hồi bằng văn bản, nhắc thời hạn ` +
            `khiếu nại 60 ngày kể từ ngày sao kê. Không quy kết ai gian lận.`,

        disclaimer_label: 'Lưu ý',
        disclaimer_text:
            'Công cụ này chỉ hỗ trợ rà soát tài chính. Kết quả chỉ để tham khảo. Nếu thấy giao dịch lạ, hãy liên hệ ' +
            'hỗ trợ ngay. Ở Mỹ, thời hạn khiếu nại là 60 ngày kể từ ngày sao kê.',
    },
};

const STATUS = {
    posted: { en: 'Posted', vi: 'Đã ghi nhận' },
    pending: { en: 'Pending', vi: 'Đang chờ' },
    recurring: { en: 'Recurring', vi: 'Định kỳ' },
};

// Mock review data. Swap for a fetch() against the backend when wiring live.
// `alert: true` is what turns an amount red — it is not a default.
const DETAIL_DATA = {
    duplicate: {
        titleKey: 'detail_duplicate',
        items: [
            {
                merchant: 'Apple.com/bill',
                amount: '-$9.99',
                date: 'Oct 12',
                alert: true,
                details: { id: 'TXN-99123', name: 'Apple Services', time: '14:32 EST', status: STATUS.posted },
            },
            {
                merchant: 'Apple.com/bill',
                amount: '-$9.99',
                date: 'Oct 12',
                alert: true,
                details: { id: 'TXN-99124', name: 'Apple Services', time: '14:33 EST', status: STATUS.posted },
            },
            {
                merchant: 'Uber*Trip',
                amount: '-$24.50',
                date: 'Oct 10',
                alert: true,
                warning: { en: 'Matches a charge on Oct 9', vi: 'Trùng với giao dịch ngày 9 Thg 10' },
                details: { id: 'TXN-98871', name: 'Uber Technologies', time: '09:14 EST', status: STATUS.posted },
            },
        ],
    },
    unrecognized: {
        titleKey: 'detail_unrecognized',
        items: [
            {
                merchant: 'BLINKIST*SUB',
                amount: '-$89.99',
                date: 'Oct 14',
                alert: true,
                warning: { en: 'No matching receipt email', vi: 'Không có email biên lai tương ứng' },
                details: { id: 'TXN-99450', name: 'Blinkist GmbH', time: '03:07 EST', status: STATUS.posted },
            },
            {
                merchant: 'DIGITALOCEAN',
                amount: '-$41.86',
                date: 'Oct 13',
                details: { id: 'TXN-99312', name: 'DigitalOcean LLC', time: '00:11 EST', status: STATUS.posted },
            },
            {
                merchant: 'PAYPAL *STEAM',
                amount: '-$59.99',
                date: 'Oct 11',
                details: { id: 'TXN-99205', name: 'Valve Corp. via PayPal', time: '21:48 EST', status: STATUS.posted },
            },
            {
                merchant: 'SP GLOBALSTORE',
                amount: '-$132.40',
                date: 'Oct 08',
                alert: true,
                warning: { en: 'First time seeing this merchant', vi: 'Lần đầu xuất hiện đơn vị bán này' },
                details: { id: 'TXN-98740', name: 'Global Store Ltd.', time: '11:06 EST', status: STATUS.pending },
            },
            {
                merchant: 'AWS EMEA',
                amount: '-$18.22',
                date: 'Oct 05',
                details: { id: 'TXN-98501', name: 'Amazon Web Services', time: '06:02 EST', status: STATUS.posted },
            },
        ],
    },
    // Email-audit: two categories — not yet in whitelist / already whitelisted with transactions
    'email-audit': {
        titleKey: 'flag_email_audit',
        items: [
            // --- Type 1: Emails not in whitelist ---
            {
                merchant: 'SP GLOBALSTORE',
                amount: '-$132.40',
                date: 'Oct 08',
                alert: true,
                warning: { en: 'Merchant never seen before', vi: 'Lần đầu xuất hiện đơn vị bán này' },
                email: 'billing@globalstore.com',
                type: 'whitelist-not-found',
                details: { id: 'TXN-98740', name: 'Global Store Ltd.', time: '11:06 EST', status: STATUS.pending },
            },
            {
                merchant: 'BLINKIST*SUB',
                amount: '-$89.99',
                date: 'Oct 14',
                alert: true,
                warning: { en: 'No matching receipt email', vi: 'Không có email biên lai tương ứng' },
                email: 'receipts@blinkist.com',
                type: 'whitelist-not-found',
                details: { id: 'TXN-99450', name: 'Blinkist GmbH', time: '03:07 EST', status: STATUS.posted },
            },
            {
                merchant: 'AWS EMEA',
                amount: '-$18.22',
                date: 'Oct 05',
                email: 'accounting@aws.amazon.com',
                type: 'whitelist-not-found',
                details: { id: 'TXN-98501', name: 'Amazon Web Services', time: '06:02 EST', status: STATUS.posted },
            },
            {
                merchant: 'PAYPAL *STEAM',
                amount: '-$59.99',
                date: 'Oct 11',
                email: 'invoice@valve.com',
                type: 'whitelist-not-found',
                details: { id: 'TXN-99205', name: 'Valve Corp. via PayPal', time: '21:48 EST', status: STATUS.posted },
            },
            {
                merchant: 'DIGITALOCEAN',
                amount: '-$41.86',
                date: 'Oct 13',
                email: 'billing@digitalocean.com',
                type: 'whitelist-not-found',
                details: { id: 'TXN-99312', name: 'DigitalOcean LLC', time: '00:11 EST', status: STATUS.posted },
            },
            // --- Type 2: Whitelisted emails with matching transactions ---
            {
                merchant: 'WEALIFY TOPUP',
                amount: '-$50.05',
                date: 'Oct 09',
                alert: true,
                warning: { en: 'Left the account, never reached the card', vi: 'Đã rời tài khoản nhưng chưa lên thẻ' },
                email: 'support@wealify.com',
                statementDate: 'Oct 15',
                type: 'whitelist-found',
                details: { id: 'TXN-98655', name: 'Wealify Wallet', time: '16:41 EST', status: STATUS.pending },
            },
            {
                merchant: 'Apple.com/bill',
                amount: '-$9.99',
                date: 'Oct 12',
                alert: true,
                warning: { en: 'Charged twice within 61 seconds', vi: 'Bị thu hai lần cách nhau 61 giây' },
                email: 'itunes-apple@invoice.apple.com',
                statementDate: 'Oct 20',
                type: 'whitelist-found',
                details: { id: 'TXN-99124', name: 'Apple Services', time: '14:33 EST', status: STATUS.posted },
            },
            {
                merchant: 'Netflix Premium',
                amount: '-$22.99',
                date: 'Oct 07',
                warning: { en: 'Price changed without notice', vi: 'Tăng giá không báo trước' },
                email: 'membership@netflix.com',
                statementDate: 'Oct 12',
                type: 'whitelist-found',
                details: { id: 'TXN-98620', name: 'Netflix Inc.', time: '02:17 EST', status: STATUS.recurring },
            },
        ],
    },
    'price-hike': {
        titleKey: 'detail_price_hike',
        items: [
            {
                merchant: 'Netflix Premium',
                amount: '-$22.99',
                date: 'Oct 07',
                alert: true,
                warning: { en: 'Was $19.99 last month, up 15%', vi: 'Tháng trước là $19.99, tăng 15%' },
                details: { id: 'TXN-98620', name: 'Netflix Inc.', time: '02:17 EST', status: STATUS.recurring },
            },
            {
                merchant: 'Adobe Creative Cloud',
                amount: '-$59.99',
                date: 'Oct 03',
                alert: true,
                warning: { en: 'Was $54.99 last month, up 9.1%', vi: 'Tháng trước là $54.99, tăng 9,1%' },
                details: { id: 'TXN-98390', name: 'Adobe Systems', time: '08:41 EST', status: STATUS.recurring },
            },
        ],
    },
    'active-subs': {
        titleKey: 'detail_active_subs',
        items: [
            {
                merchant: 'Netflix Premium',
                amount: '-$22.99',
                date: { en: 'Monthly', vi: 'Hàng tháng' },
                details: { id: 'SUB-1001', name: 'Netflix Inc.', time: '02:17 EST', status: STATUS.recurring },
            },
            {
                merchant: 'Adobe Creative Cloud',
                amount: '-$59.99',
                date: { en: 'Monthly', vi: 'Hàng tháng' },
                details: { id: 'SUB-1002', name: 'Adobe Systems', time: '08:41 EST', status: STATUS.recurring },
            },
            {
                merchant: 'Spotify Family',
                amount: '-$16.99',
                date: { en: 'Monthly', vi: 'Hàng tháng' },
                details: { id: 'SUB-1003', name: 'Spotify AB', time: '19:23 EST', status: STATUS.recurring },
            },
            {
                merchant: 'iCloud+ 2TB',
                amount: '-$9.99',
                date: { en: 'Monthly', vi: 'Hàng tháng' },
                details: { id: 'SUB-1005', name: 'Apple Services', time: '14:32 EST', status: STATUS.recurring },
            },
            // Marked for cancellation — recent (< 30 days): neutral pending state
            {
                merchant: 'Canva Pro',
                amount: '-$12.99',
                date: { en: 'Monthly', vi: 'Hàng tháng' },
                details: { id: 'SUB-1004', name: 'Canva Pty Ltd', time: '05:34 EST', status: STATUS.recurring },
                markedForCancel: true,
                markedAt: '2026-08-01',
            },
            {
                merchant: 'Blinkist Premium',
                amount: '-$89.99',
                date: { en: 'Yearly', vi: 'Hàng năm' },
                details: { id: 'SUB-1006', name: 'Blinkist GmbH', time: '03:07 EST', status: STATUS.recurring },
                markedForCancel: true,
                markedAt: '2026-08-15',
            },
            // Marked for cancellation — overdue (> 30 days): red "Forgot to cancel" state
            {
                merchant: 'DigitalOcean',
                amount: '-$41.86',
                date: { en: 'Monthly', vi: 'Hàng tháng' },
                details: { id: 'SUB-1007', name: 'DigitalOcean LLC', time: '00:11 EST', status: STATUS.recurring },
                markedForCancel: true,
                markedAt: '2026-07-01',
            },
        ],
    },
    trial: {
        titleKey: 'detail_trial',
        items: [
            {
                merchant: 'Notion AI',
                amount: '$0.00',
                date: { en: 'Ends Oct 22', vi: 'Hết hạn 22 Thg 10' },
                warning: {
                    en: 'Converts to $10.00 a month after the trial',
                    vi: 'Sẽ tự thu $10.00 mỗi tháng sau khi hết dùng thử',
                },
                details: { id: 'SUB-1008', name: 'Notion Labs Inc.', time: '10:03 EST', status: STATUS.pending },
            },
        ],
    },
    unused: {
        titleKey: 'detail_unused',
        items: [
            {
                merchant: 'Canva Pro',
                amount: '-$12.99',
                date: { en: 'Last used Aug 04', vi: 'Dùng lần cuối 04 Thg 8' },
                details: { id: 'SUB-1004', name: 'Canva Pty Ltd', time: '05:34 EST', status: STATUS.recurring },
            },
            {
                merchant: 'Blinkist Premium',
                amount: '-$89.99',
                date: { en: 'Last used Jul 19', vi: 'Dùng lần cuối 19 Thg 7' },
                details: { id: 'SUB-1006', name: 'Blinkist GmbH', time: '03:07 EST', status: STATUS.recurring },
            },
            {
                merchant: 'iCloud+ 2TB',
                amount: '-$9.99',
                date: { en: 'Last used Aug 01', vi: 'Dùng lần cuối 01 Thg 8' },
                details: { id: 'SUB-1005', name: 'Apple Services', time: '14:32 EST', status: STATUS.recurring },
            },
        ],
    },
};

const detailTitle = document.getElementById('detailTitle');
const detailCount = document.getElementById('detailCount');
const detailBody = document.getElementById('detailBody');
const chatHistory = document.getElementById('chatHistory');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const langSwitch = document.getElementById('langSwitch');

let lang = localStorage.getItem('wealify_lang') === 'vi' ? 'vi' : 'en';
let activeFlag = null;
let openIndex = null;
let loadTimer = null;

const t = (key) => I18N[lang][key];
// Data values are either a plain string or an { en, vi } pair
const loc = (value) => (value && typeof value === 'object' ? value[lang] : value);

function icon(name, extraClass) {
    const i = document.createElement('i');
    i.className = `ph ph-${name}${extraClass ? ' ' + extraClass : ''}`;
    i.setAttribute('aria-hidden', 'true');
    return i;
}

// ─── Right panel rendering ─────────────────────────

function buildMetaRow(list, labelKey, value) {
    const dt = document.createElement('dt');
    dt.textContent = t(labelKey);
    const dd = document.createElement('dd');
    dd.textContent = value;
    list.append(dt, dd);
}

function buildDetailItem(item, index) {
    const row = document.createElement('article');
    row.className = 'detail-item';

    // Overdue: marked-for-cancel + more than 30 days ago
    const isOverdue = item.markedForCancel && daysSinceMarked(item.markedAt) > 30;
    if (isOverdue) row.classList.add('is-overdue');

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

    const merchant = document.createElement('span');
    merchant.className = 'detail-merchant';
    merchant.textContent = item.merchant;

    const amount = document.createElement('span');
    amount.className = 'detail-amount num' + (item.alert ? ' is-alert' : '');
    amount.textContent = item.amount;

    line.append(merchant, amount);

    const date = document.createElement('div');
    date.className = 'detail-date';
    date.textContent = loc(item.date);

    main.append(line, date);

    if (item.warning) {
        const warn = document.createElement('div');
        warn.className = 'detail-warning';
        const label = document.createElement('span');
        label.textContent = loc(item.warning);
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
    buildMetaRow(meta, 'label_txn_id', item.details.id);
    buildMetaRow(meta, 'label_merchant', item.details.name);
    buildMetaRow(meta, 'label_time', item.details.time);
    buildMetaRow(meta, 'label_status', loc(item.details.status));
    if (item.reason) buildMetaRow(meta, 'label_reason', loc(item.reason));
    if (item.email) buildMetaRow(meta, 'label_email', item.email);

    inner.appendChild(meta);

    if (item.reason) {
        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'detail-action';
        const label = document.createElement('span');
        label.textContent = t('action_draft_email');
        action.append(icon('envelope-simple'), label);
        action.addEventListener('click', () => draftSupportEmail(item));
        inner.appendChild(action);
    } else if (item.type === 'whitelist-not-found') {
        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'detail-action';
        const label = document.createElement('span');
        label.textContent = t('action_add_whitelist');
        action.append(icon('check-circle'), label);
        action.addEventListener('click', () => addToWhitelist(item));
        inner.appendChild(action);
    } else if (item.type === 'whitelist-found') {
        const countDown = document.createElement('div');
        countDown.className = 'email-countdown';
        const days = getDaysRemaining(item.date, item.statementDate);
        const countBadge = document.createElement('span');
        countBadge.className = 'email-countdown-badge' + (days <= 15 ? ' is-expiring' : '');
        countBadge.textContent = t('label_days_remaining')(days);
        countDown.append(icon('hourglass-half'), countBadge);

        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'detail-action';
        const label = document.createElement('span');
        label.textContent = t('action_draft_appeal');
        action.append(icon('envelope-simple'), label);
        action.addEventListener('click', () => draftAppealEmail(item));
        inner.append(countDown, action);
    } else if (item.markedForCancel) {
        const days = daysSinceMarked(item.markedAt);
        const status = document.createElement('div');
        status.className = 'cancel-status' + (isOverdue ? ' is-overdue' : '');

        const badge = document.createElement('span');
        badge.className = 'cancel-status-badge';
        badge.textContent = isOverdue ? t('action_forgot_cancel') : t('action_pending_cancel');

        const meta = document.createElement('span');
        meta.className = 'cancel-status-days';
        meta.textContent = isOverdue
            ? t('label_marked_overdue')(days)
            : t('label_marked_ago')(days);

        status.append(badge, meta);
        inner.appendChild(status);
    } else {
        const action = document.createElement('button');
        action.type = 'button';
        action.className = 'detail-action';
        const label = document.createElement('span');
        label.textContent = t('action_want_cancel');
        action.append(icon('x-circle'), label);
        action.addEventListener('click', () => markForCancellation(item));
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

function paintDetails(data) {
    const list = document.createElement('div');
    list.className = 'detail-list';
    list.append(...data.items.map(buildDetailItem));
    detailBody.replaceChildren(list);
    detailBody.scrollTop = 0;
}

function renderDetails(flag, { instant = false } = {}) {
    const data = DETAIL_DATA[flag];
    if (!data) return;

    if (flag !== activeFlag) openIndex = null;
    activeFlag = flag;

    detailTitle.textContent = t(data.titleKey);
    detailCount.textContent = t('count_items')(data.items.length);

    document.querySelectorAll('[data-flag]').forEach((el) => {
        el.classList.toggle('is-active', el.dataset.flag === flag);
    });

    window.clearTimeout(loadTimer);

    if (instant) {
        if (flag === 'email-audit') {
            renderEmailAudit(data);
        } else if (flag === 'active-subs') {
            renderActiveSubs(data);
        } else {
            paintDetails(data);
        }
        return;
    }

    showSkeleton(Math.min(data.items.length, 4));
    loadTimer = window.setTimeout(() => {
        if (flag === 'email-audit') {
            renderEmailAudit(data);
        } else if (flag === 'active-subs') {
            renderActiveSubs(data);
        } else {
            paintDetails(data);
        }
    }, 220);
}

// ─── Email-audit renderer ──────────────────────────

function renderEmailAudit(data) {
    const notFound = data.items.filter((i) => i.type === 'whitelist-not-found');
    const found = data.items.filter((i) => i.type === 'whitelist-found');
    const wrap = document.createElement('div');
    wrap.className = 'detail-split';

    if (notFound.length) {
        wrap.appendChild(buildSplitSection(t('section_whitelist_not_found'), notFound));
    }

    if (found.length) {
        wrap.appendChild(buildSplitSection(t('section_whitelist_found'), found));
    }

    detailBody.replaceChildren(wrap);
}

function buildSplitSection(title, items) {
    const section = document.createElement('section');
    section.className = 'detail-split-section';

    const header = document.createElement('div');
    header.className = 'section-header';
    header.textContent = title;
    section.appendChild(header);

    const body = document.createElement('div');
    body.className = 'detail-split-body';
    items.forEach((item, idx) => body.appendChild(buildDetailItem(item, idx)));
    section.appendChild(body);

    return section;
}

// ─── Active-subs renderer (70/30 split) ────────────

function renderActiveSubs(data) {
    const active = data.items.filter((i) => !i.markedForCancel);
    const pending = data.items.filter((i) => i.markedForCancel);
    const wrap = document.createElement('div');
    wrap.className = 'detail-split subs-split';

    if (active.length) {
        wrap.appendChild(buildSubSplitSection(t('section_active_subs'), active, 'top'));
    }

    if (pending.length) {
        wrap.appendChild(buildSubSplitSection(t('section_pending_cancel'), pending, 'bottom'));
    }

    detailBody.replaceChildren(wrap);
}

function buildSubSplitSection(title, items, position) {
    const section = document.createElement('section');
    section.className = `detail-split-section subs-split-section subs-split-${position}`;

    const header = document.createElement('div');
    header.className = 'section-header';
    header.textContent = title;
    section.appendChild(header);

    const body = document.createElement('div');
    body.className = 'detail-split-body';
    items.forEach((item, idx) => body.appendChild(buildDetailItem(item, idx)));
    section.appendChild(body);

    return section;
}

function markForCancellation(item) {
    // TODO: wire to backend — locally toggle and re-render
    item.markedForCancel = true;
    item.markedAt = new Date().toISOString().slice(0, 10);
    openIndex = null;
    if (activeFlag === 'active-subs') {
        renderActiveSubs(DETAIL_DATA['active-subs']);
    }
}

// ─── Helper: count down days from 60-day window ─────

function getDaysRemaining(txnDateStr, statementDateStr) {
    const statement = parseMonthDate(statementDateStr);
    const txn = parseMonthDate(txnDateStr);
    const windowEnd = new Date(statement);
    windowEnd.setDate(windowEnd.getDate() + 60);
    const diff = windowEnd - txn;
    return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
}

function daysSinceMarked(isoDateStr) {
    const marked = new Date(isoDateStr);
    if (isNaN(marked)) return 0;
    const now = new Date();
    const diff = now - marked;
    return Math.max(0, Math.floor(diff / (1000 * 60 * 60 * 24)));
}

function parseMonthDate(str) {
    const months = {
        jan: 0,
        feb: 1,
        mar: 2,
        apr: 3,
        may: 4,
        jun: 5,
        jul: 6,
        aug: 7,
        aug: 7,
        sep: 8,
        oct: 9,
        nov: 10,
        dec: 11,
    };
    const match = str.match(/^([A-Za-z]+)\s+(\d{1,2})$/);
    if (!match) return new Date();
    const m = months[match[1].toLowerCase()];
    if (m === undefined) return new Date();
    return new Date(2025, m, parseInt(match[2], 10));
}

// ─── Email-audit actions ───────────────────────────

function addToWhitelist(item) {
    // TODO: call backend API to add email to whitelist
    // For now, show a quick confirmation in the chat
    appendMessage(`Đã thêm ${item.email} vào whitelist.`, 'user');
    window.setTimeout(() => appendMessage('Email đã được thêm thành công.', 'ai'), 450);
}

function draftAppealEmail(item) {
    const prompt =
        `Tôi có một giao dịch với email ${item.email} (${item.merchant}, ${item.amount}, ngày ${item.date}, ` +
        `mã ${item.details.id}), nhưng bên Wealify chưa có giao dịch tương ứng. ` +
        `Đề nghị đội support hỗ trợ làm rõ.`;
    askAssistant(prompt);
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

// ─── Chat ──────────────────────────────────────────

function appendMessage(text, sender) {
    const wrap = document.createElement('div');
    wrap.className = `msg msg-${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = sender === 'ai' ? 'AI' : 'TN';

    const bubble = document.createElement('div');
    bubble.className = `bubble bubble-${sender}`;
    bubble.textContent = text;

    wrap.append(avatar, bubble);
    chatHistory.appendChild(wrap);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function askAssistant(text) {
    const question = text.trim();
    if (!question) return;

    appendMessage(question, 'user');
    chatInput.value = '';

    window.setTimeout(() => appendMessage(t('ai_reply'), 'ai'), 450);
}

// Sends the draft prompt directly to the chatbot.
function draftSupportEmail(item) {
    askAssistant(t('prompt_draft_email')(item));
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    askAssistant(chatInput.value);
});

document.getElementById('suggestionChips').addEventListener('click', (e) => {
    const chip = e.target.closest('.chip');
    if (chip) askAssistant(chip.textContent);
});

// ─── Initial state ─────────────────────────────────

applyLang(lang);
renderDetails('duplicate', { instant: true });
