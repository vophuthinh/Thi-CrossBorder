"""
Chat Orchestrator — Routes user messages to the right agents.
Handles intent detection, safety checks, and response formatting.

NOTE: All responses use double-newline (\\n\\n) for Streamlit markdown compatibility.
Streamlit's st.markdown() treats single \\n as same paragraph, so we need \\n\\n
for proper line breaks.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from data_loader import get_all_data
from safety import detect_trap_question, get_trap_response, validate_response, detect_language, get_disclaimer
from audit_log import audit_log

from agents.statement_parser import analyze_statement
from agents.email_matcher import match_transactions_to_emails, get_match_summary
from agents.reconciler import reconcile_three_sources
from agents.anomaly_detector import detect_anomalies
from agents.report_generator import generate_report
import report_cache
from agents.email_drafter import draft_report_email, draft_dispute_reminder_email
from agents.risk_scorer import calculate_risk_score

from config import (
    LABEL_CONFIRMED, LABEL_NEEDS_REVIEW, LABEL_INSUFFICIENT,
    LABEL_CONFIRMED_EN, LABEL_NEEDS_REVIEW_EN, LABEL_INSUFFICIENT_EN,
    BYTEPLUS_API_KEY, CURRENCY_SYMBOLS,
)

# anomaly_detector.py's finding dicts carry the label as a raw Vietnamese
# string (config.py's canonical value, used for internal comparisons like
# `s["label"] == LABEL_CONFIRMED`) — unlike finding_schema.py's findings,
# there's no separate label_vi/label_en pair here, so displaying it in
# English mode needs an explicit translation, not just printing it as-is.
_LABEL_EN = {
    LABEL_CONFIRMED: LABEL_CONFIRMED_EN,
    LABEL_NEEDS_REVIEW: LABEL_NEEDS_REVIEW_EN,
    LABEL_INSUFFICIENT: LABEL_INSUFFICIENT_EN,
}


def _label_text(label: str, lang: str) -> str:
    return _LABEL_EN.get(label, label) if lang == "en" else label


# Short, natural replies for greetings/small talk — kept separate from the
# capability-list fallback (below in _handle_general) so a plain "xin chào"
# doesn't get the exact same wall of bullet points as every other
# unmatched message. Only fires on short messages so it doesn't swallow a
# real question that happens to start with a greeting word.
_GREETING_KEYWORDS = ["chào", "hi", "hello", "hey", "alo"]
_THANKS_KEYWORDS = ["cảm ơn", "cám ơn", "thanks", "thank you"]
_IDENTITY_KEYWORDS = ["bạn tên gì", "bạn là ai", "who are you", "your name"]
_WELLBEING_KEYWORDS = ["khoẻ không", "khỏe không", "how are you"]


_VN_MONTH_RE = re.compile(r"th[aá]ng\s*(\d{1,2})\b", re.IGNORECASE)
_EN_MONTH_RE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
    re.IGNORECASE,
)
_EN_MONTH_NUM = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}


_THIS_MONTH_RE = re.compile(
    r"th[aá]ng\s*(n[aà]y|hi[eệ]n\s*t[aạ]i)|(this|current)\s*month", re.IGNORECASE
)


def _extract_month_key(message: str, year: int = 2026) -> str | None:
    """
    Detect a month reference — explicit ("tháng 2", "February") or relative
    ("tháng này", "this month") — so questions about one month get that
    month's real numbers instead of silently falling back to the
    full-period total. Two real bugs this fixes:
    - explicit: "617 transactions in February" (the full Jan-Aug count)
    - relative: sample scenario #1 ("Tháng này tôi chi bao nhiêu... 3 khoản
      lớn nhất?") answered with the whole period's top-3, not August's.
    "tháng này" resolves to the real current month (UTC, matching
    report_cache.py's own definition of "current month") rather than a
    hardcoded value, so it stays correct as the demo clock moves forward.
    Hardcodes the current data's year (2026) for explicit mentions rather
    than trying to detect one — there's only one year of data to ask about
    right now.
    """
    if _THIS_MONTH_RE.search(message):
        now = datetime.now(timezone.utc)
        return f"{now.year}-{now.month:02d}"
    m = _VN_MONTH_RE.search(message)
    if m:
        month = int(m.group(1))
        if 1 <= month <= 12:
            return f"{year}-{month:02d}"
    m2 = _EN_MONTH_RE.search(message)
    if m2:
        month = _EN_MONTH_NUM[m2.group(1).lower()]
        return f"{year}-{month:02d}"
    return None


def _has_any(patterns: list[str], text: str) -> bool:
    """Word-boundary match — plain substring would let "hi" match inside
    "this" and misfire the greeting reply on a real question."""
    return any(re.search(rf"\b{re.escape(p)}\b", text) for p in patterns)


def _greeting_reply(message: str, lang: str) -> str | None:
    lower = message.lower().strip()
    if len(lower) > 30:
        return None

    if _has_any(_IDENTITY_KEYWORDS, lower):
        return (
            "Mình là trợ lý rà soát tài chính Wealify — đọc sao kê, đối chiếu email, "
            "phát hiện bất thường trong tài khoản của bạn. Hỏi mình bất kỳ điều gì nhé!"
            if lang == "vi" else
            "I'm the Wealify financial review assistant — I read statements, cross-check "
            "emails, and flag anomalies on your account. Ask me anything!"
        )
    if _has_any(_WELLBEING_KEYWORDS, lower):
        return (
            "Mình ổn, cảm ơn bạn! Bạn muốn mình kiểm tra gì trên tài khoản không?"
            if lang == "vi" else
            "I'm doing well, thanks for asking! Anything you'd like me to check?"
        )
    if _has_any(_THANKS_KEYWORDS, lower):
        return (
            "Không có gì! Cần kiểm tra thêm gì cứ hỏi mình nhé." if lang == "vi"
            else "You're welcome! Let me know if there's anything else to check."
        )
    if _has_any(_GREETING_KEYWORDS, lower):
        return (
            "Chào bạn! Mình có thể giúp rà soát sao kê, đối chiếu email, gói đăng ký, "
            "khoản bất thường... Bạn muốn kiểm tra gì?"
            if lang == "vi" else
            "Hello! I can help review statements, cross-check emails, subscriptions, "
            "anomalies... What would you like to check?"
        )
    return None


# Use double newline for Streamlit markdown rendering
NL = "\n\n"


class ChatOrchestrator:
    """Main chat logic — routes intents, calls agents, formats responses."""

    def __init__(self):
        self.data = get_all_data()
        self.conversation_history: list[dict[str, str]] = []
        self._cache: dict[str, Any] = {}
        self.pending_email_draft: dict[str, Any] | None = None
        self.pending_email_lang: str = "vi"

    def process_message(self, message: str) -> dict[str, Any]:
        """Process a user message and return response."""
        lang = detect_language(message)

        # 1. Safety check — detect trap questions
        trap = detect_trap_question(message)
        if trap:
            response_text = get_trap_response(trap, lang)
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            return {
                "response": response_text,
                "type": "safety_rejection",
                "lang": lang,
                "disclaimer": get_disclaimer(lang),
            }

        # 2. Check for email confirmation
        # Use the language the draft was created in — a short confirmation
        # word ("ok", "có") often isn't enough signal for fresh detection.
        if self.pending_email_draft and _is_confirmation(message):
            draft = self.pending_email_draft
            draft_lang = self.pending_email_lang
            self.pending_email_draft = None
            return self._send_confirmed_email(draft, draft_lang)

        # 3. Detect intent and route to agents
        intent = self._detect_intent(message, lang)
        response = self._handle_intent(intent, message, lang)

        # 4. Validate response (no banned phrases)
        response["response"] = validate_response(response["response"])
        response["disclaimer"] = get_disclaimer(lang)
        response["lang"] = lang

        # 5. Update conversation history
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": response["response"]})

        return response

    def _send_confirmed_email(self, draft: dict[str, Any], lang: str) -> dict[str, Any]:
        """Actually send the confirmed draft via SMTP to the user's own address only."""
        from email_sender import send_email, is_configured, EmailSendError

        if is_configured():
            try:
                send_email(draft["to"], draft["subject"], draft["body"])
                confirm_msg = (
                    "✅ Email đã được gửi tới " + draft["to"] if lang == "vi"
                    else "✅ Email sent to " + draft["to"]
                )
                result_type = "email_sent"
            except EmailSendError as e:
                confirm_msg = self._email_failed_message(draft, lang, str(e))
                result_type = "email_send_failed"
        else:
            reason = "SMTP chưa được cấu hình" if lang == "vi" else "SMTP not configured"
            confirm_msg = self._email_failed_message(draft, lang, reason)
            result_type = "email_send_failed"

        return {
            "response": confirm_msg,
            "type": result_type,
            "email": draft,
            "lang": lang,
            "disclaimer": get_disclaimer(lang),
        }

    @staticmethod
    def _email_failed_message(draft: dict[str, Any], lang: str, reason: str) -> str:
        if lang == "vi":
            return NL.join([
                f"⚠️ Chưa gửi được email ({reason}).",
                "Đây là nội dung để bạn tự gửi:",
                f"**Tới:** {draft['to']}",
                f"**Tiêu đề:** {draft['subject']}",
                "---",
                draft["body"],
            ])
        return NL.join([
            f"⚠️ Could not send the email ({reason}).",
            "Here is the content for you to send yourself:",
            f"**To:** {draft['to']}",
            f"**Subject:** {draft['subject']}",
            "---",
            draft["body"],
        ])

    def _detect_intent(self, message: str, lang: str) -> str:
        """Detect user intent from message."""
        lower = message.lower()

        # A specific dollar amount + "what is this" phrasing is an
        # unambiguous single-transaction lookup — route straight there
        # instead of letting it compete with the generic email-match
        # keyword score (both often co-occur, e.g. "$9.99 này là gì —
        # có email khớp không?").
        has_amount = bool(re.search(r"\$\s?[\d,]+\.?\d*", message))
        asks_what_is = any(
            p in lower for p in ("này là gì", "what is", "giải thích", "explain")
        )
        if has_amount and asks_what_is:
            return "unknown_merchant"

        # A message naming a specific month ("tháng 2", "February") always
        # routes to _handle_overview's month-specific path — otherwise this
        # can lose the keyword-score competition and fall through to the
        # free-form LLM, which has no month-filtered data and guesses (seen
        # producing two different wrong transaction counts for the same
        # real question in testing).
        if _extract_month_key(message) is not None:
            return "overview"

        # A plain "what's my balance" question shares the word "số dư"
        # with reconcile's keyword list (meant for "số dư ví không khớp"
        # mismatch questions) and always lost to it outright — the
        # reconciliation discrepancy dump was never actually answering the
        # question asked. Route to a direct answer instead, unless the
        # message actually names a reconciliation-specific signal.
        has_balance_question = bool(
            re.search(r"số dư.*(hiện tại|bao nhiêu)|(hiện tại|bao nhiêu).*số dư", lower)
        ) or "wallet balance" in lower or "current balance" in lower
        has_reconcile_signal = _has_any(
            ["lệch", "chưa lên thẻ", "rời tài khoản", "3 nguồn", "mismatch", "discrepancy"],
            lower,
        )
        if has_balance_question and not has_reconcile_signal:
            return "wallet_balance"

        # "Tiền vào"/inbound wording ("nhận tiền", "báo có", "tiền vào") +
        # an email signal routes to the VA/wallet-side inbound cross-check
        # (check_inbound_emails) instead of email_match's card-charge-only
        # matching — the two check completely different data (VA deposits
        # vs card spending) and share the generic "email"/"khớp" keywords,
        # so this needs to win before the keyword-score competition.
        has_inbound_signal = _has_any(
            ["tiền vào", "nhận tiền", "báo có", "nạp tiền", "chuyển vào", "inbound"], lower,
        )
        has_email_signal = _has_any(
            ["email", "khớp", "biên lai", "receipt", "xác nhận", "match"], lower,
        )
        if has_inbound_signal and has_email_signal:
            return "inbound_match"

        intents = {
            "overview": [
                "chi bao nhiêu", "phí bao nhiêu", "tổng", "summary", "tổng hợp",
                "how much", "total", "3 khoản lớn", "overview", "tháng này",
                "spending", "tóm tắt", "quý", "năm", "quarter", "year",
            ],
            "email_match": [
                "email", "khớp", "biên lai", "receipt", "xác nhận",
                "match", "confirmation", "có email", "đối soát",
            ],
            "reconcile": [
                "lệch", "đối chiếu", "3 nguồn", "chưa lên thẻ", "rời tài khoản",
                "discrepancy", "reconcile", "mismatch", "card", "wallet",
                "chưa thấy", "số dư",
            ],
            "subscriptions": [
                "gói", "đăng ký", "định kỳ", "subscription", "recurring",
                "tăng giá", "price", "quên huỷ", "netflix", "spotify",
            ],
            "duplicates": [
                "trùng", "hai lần", "phí kép", "duplicate", "double",
                "charged twice", "tính 2 lần",
            ],
            "send_report": [
                "gửi báo cáo", "gửi email", "send report", "email report",
                "send to my email", "gửi vào email",
            ],
            "dispute_reminder": [
                "hạn khiếu nại", "dispute", "deadline", "sắp hết hạn",
                "60 ngày", "nhắc hạn", "reminder",
            ],
            "scheduled_check": [
                "rà soát", "kiểm tra toàn bộ", "full check", "scan",
                "chạy kiểm tra", "run check", "giám sát", "monitor",
            ],
            "unknown_merchant": [
                "này là gì", "what is", "khoản lạ", "không biết", "unknown",
                "giải thích", "explain", "$",
            ],
            "audit_log": [
                "nhật ký", "audit", "log", "lịch sử cảnh báo", "flag history",
            ],
        }

        # Weight by keyword word-count so a specific multi-word phrase
        # (e.g. "gửi báo cáo") outranks a shorter generic overlap (e.g. "tháng này").
        scores = {intent: 0 for intent in intents}
        for intent, keywords in intents.items():
            for kw in keywords:
                if kw in lower:
                    scores[intent] += len(kw.split())

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "general"
        return best

    def _handle_intent(self, intent: str, message: str, lang: str) -> dict[str, Any]:
        handlers = {
            "overview": self._handle_overview,
            "email_match": self._handle_email_match,
            "inbound_match": self._handle_inbound_match,
            "reconcile": self._handle_reconcile,
            "subscriptions": self._handle_subscriptions,
            "duplicates": self._handle_duplicates,
            "send_report": self._handle_send_report,
            "dispute_reminder": self._handle_dispute_reminder,
            "scheduled_check": self._handle_scheduled_check,
            "unknown_merchant": self._handle_unknown_merchant,
            "audit_log": self._handle_audit_log,
            "wallet_balance": self._handle_wallet_balance,
            "general": self._handle_general,
        }
        handler = handlers.get(intent, self._handle_general)
        return handler(message, lang)

    def _get_statement_analysis(self, lang: str) -> dict[str, Any]:
        cache_key = f"statement_{lang}"
        if cache_key not in self._cache:
            self._cache[cache_key] = analyze_statement(self.data["account_statement"], lang)
        return self._cache[cache_key]

    def _get_anomalies(self, lang: str) -> dict[str, Any]:
        cache_key = f"anomalies_{lang}"
        if cache_key not in self._cache:
            self._cache[cache_key] = detect_anomalies(self.data["account_statement"], lang)
        return self._cache[cache_key]

    def _get_reconciliation(self, lang: str) -> dict[str, Any]:
        cache_key = f"reconciliation_{lang}"
        if cache_key not in self._cache:
            self._cache[cache_key] = reconcile_three_sources(
                self.data["account_statement"],
                self.data["card_statement"],
                self.data["wallet_balance"],
                lang,
            )
        return self._cache[cache_key]

    def _get_email_matches(self, lang: str) -> list[dict[str, Any]]:
        cache_key = f"email_matches_{lang}"
        if cache_key not in self._cache:
            self._cache[cache_key] = match_transactions_to_emails(
                self.data["account_statement"],
                self.data["emails"],
                lang,
            )
        return self._cache[cache_key]

    # --- Intent handlers ---

    def _handle_wallet_balance(self, message: str, lang: str) -> dict[str, Any]:
        """Direct answer to "what's my current balance" — previously lost
        the intent-routing competition to "reconcile" (both match "số dư")
        and got a 3-source discrepancy dump instead of an actual balance."""
        wallet = self.data["wallet_balance"]
        currency = wallet.get("currency", "VND")
        sym = CURRENCY_SYMBOLS.get(currency, currency + " ")
        balance = wallet.get("wallet_balance", 0)
        balance_text = f"{balance:,.0f} {currency}" if currency == "VND" else f"{sym}{balance:,.2f}"

        if lang == "en":
            parts = [f"💰 **Current wallet balance:** {balance_text}"]
        else:
            parts = [f"💰 **Số dư ví hiện tại:** {balance_text}"]

        card_totals = wallet.get("card_totals_by_currency", {})
        if card_totals:
            parts.append("")
            parts.append("**Card balances:**" if lang == "en" else "**Số dư thẻ:**")
            for cur, v in card_totals.items():
                csym = CURRENCY_SYMBOLS.get(cur, cur + " ")
                parts.append(f"- {cur}: {csym}{v.get('balance', 0):,.2f}")

        return {"response": NL.join(parts), "type": "wallet_balance", "data": wallet}

    def _handle_month_overview(self, month_key: str, lang: str) -> dict[str, Any] | None:
        """Answer using report_cache's pre-generated per-month report (Nhiệm
        vụ 6) instead of the full-period totals — that's the fix for a
        month-specific question ("tháng 2 có bao nhiêu giao dịch") getting
        answered with the whole dataset's numbers."""
        cached = report_cache.get_cached_report(month_key)
        if cached is None:
            return None
        overview = cached["report"].get("overview", {})
        if not overview:
            return None

        header = f"📊 **Tổng quan tháng {month_key}**" if lang == "vi" else f"📊 **Overview for {month_key}**"
        parts = [header]
        for currency, group in overview.items():
            sym = CURRENCY_SYMBOLS.get(currency, currency + " ")
            parts.append(f"\n**[{currency}]**")
            for k, v in group.items():
                parts.append(f"- **{k}:** {sym}{v:,.2f}" if isinstance(v, float) else f"- **{k}:** {v}")

        return {"response": NL.join(parts), "type": "month_overview", "data": cached}

    def _handle_overview(self, message: str, lang: str) -> dict[str, Any]:
        month_key = _extract_month_key(message)
        if month_key:
            month_response = self._handle_month_overview(month_key, lang)
            if month_response:
                return month_response
            # Falls through to the full-period overview below if that
            # month isn't cached yet (e.g. a future month with no report
            # generated) — better to show something than nothing.

        analysis = self._get_statement_analysis(lang)
        anomalies = self._get_anomalies(lang)
        report = generate_report(analysis, anomalies, lang)
        # summary/top3/monthly are {currency: ...} — statement mixes VND/USD/EUR
        # with no conversion, so each currency is reported separately.
        summary_by_currency = analysis["summary"]
        top3_by_currency = analysis["top3_largest"]
        monthly_by_currency = analysis["monthly_breakdown"]
        quarterly_by_currency = report.get("quarterly_breakdown", {})
        yearly_by_currency = report.get("yearly_breakdown", {})
        currencies = summary_by_currency.keys()

        if lang == "en":
            parts = ["📊 **Account Overview**"]
            for currency in currencies:
                sym = CURRENCY_SYMBOLS.get(currency, currency + " ")
                parts.append(f"\n**[{currency}]**")
                for k, v in summary_by_currency[currency].items():
                    parts.append(f"- **{k}:** {sym}{v:,.2f}" if isinstance(v, float) else f"- **{k}:** {v}")
                top3 = top3_by_currency.get(currency, [])
                if top3:
                    parts.append("**Top 3 Largest Charges:**")
                    for i, t in enumerate(top3, 1):
                        parts.append(f"{i}. `{t['description']}` — `{sym}{abs(t['amount']):,.2f}` ({t['date']})")
                monthly = monthly_by_currency.get(currency, {})
                if monthly:
                    parts.append("**Monthly Breakdown:**")
                    for month, data in sorted(monthly.items()):
                        parts.append(f"- `{month}`: Income `{sym}{data['income']:,.2f}` · Spending `{sym}{data['spending']:,.2f}` · Fees `{sym}{data['fees']:,.2f}`")
                quarterly = quarterly_by_currency.get(currency, {})
                if quarterly:
                    parts.append("**Quarterly Breakdown:**")
                    for q, data in sorted(quarterly.items()):
                        parts.append(f"- `{q}`: Income `{sym}{data['income']:,.2f}` · Spending `{sym}{data['spending']:,.2f}` · Fees `{sym}{data['fees']:,.2f}` · Net `{sym}{data['net']:,.2f}`")
                yearly = yearly_by_currency.get(currency, {})
                if yearly:
                    parts.append("**Yearly Summary:**")
                    for y, data in sorted(yearly.items()):
                        parts.append(f"- `{y}`: Income `{sym}{data['income']:,.2f}` · Spending `{sym}{data['spending']:,.2f}` · Fees `{sym}{data['fees']:,.2f}` · Net `{sym}{data['net']:,.2f}`")
        else:
            parts = ["📊 **Tổng quan tài khoản**"]
            for currency in currencies:
                sym = CURRENCY_SYMBOLS.get(currency, currency + " ")
                parts.append(f"\n**[{currency}]**")
                for k, v in summary_by_currency[currency].items():
                    parts.append(f"- **{k}:** {sym}{v:,.2f}" if isinstance(v, float) else f"- **{k}:** {v}")
                top3 = top3_by_currency.get(currency, [])
                if top3:
                    parts.append("**3 khoản lớn nhất:**")
                    for i, t in enumerate(top3, 1):
                        parts.append(f"{i}. `{t['description']}` — `{sym}{abs(t['amount']):,.2f}` ({t['date']})")
                monthly = monthly_by_currency.get(currency, {})
                if monthly:
                    parts.append("**Chi tiết theo tháng:**")
                    for month, data in sorted(monthly.items()):
                        parts.append(f"- `{month}`: Thu `{sym}{data['income']:,.2f}` · Chi `{sym}{data['spending']:,.2f}` · Phí `{sym}{data['fees']:,.2f}`")
                quarterly = quarterly_by_currency.get(currency, {})
                if quarterly:
                    parts.append("**Theo quý:**")
                    for q, data in sorted(quarterly.items()):
                        parts.append(f"- `{q}`: Thu `{sym}{data['income']:,.2f}` · Chi `{sym}{data['spending']:,.2f}` · Phí `{sym}{data['fees']:,.2f}` · Ròng `{sym}{data['net']:,.2f}`")
                yearly = yearly_by_currency.get(currency, {})
                if yearly:
                    parts.append("**Theo năm:**")
                    for y, data in sorted(yearly.items()):
                        parts.append(f"- `{y}`: Thu `{sym}{data['income']:,.2f}` · Chi `{sym}{data['spending']:,.2f}` · Phí `{sym}{data['fees']:,.2f}` · Ròng `{sym}{data['net']:,.2f}`")

        income_note = report.get("income_note")
        if income_note:
            parts.append("")
            parts.append(f"ℹ️ {income_note}")

        return {"response": NL.join(parts), "type": "overview", "data": analysis}

    def _handle_email_match(self, message: str, lang: str) -> dict[str, Any]:
        matches = self._get_email_matches(lang)
        summary = get_match_summary(matches, lang)

        if lang == "en":
            parts = ["📧 **Transaction ↔ Email Cross-Check**"]
            for k, v in summary.items():
                parts.append(f"- **{k}:** {v}")
            parts.append("")
            parts.append("**Details:**")
        else:
            parts = ["📧 **Đối soát giao dịch ↔ email**"]
            for k, v in summary.items():
                parts.append(f"- **{k}:** {v}")
            parts.append("")
            parts.append("**Chi tiết:**")

        # Group by status for cleaner display
        suspicious_items = []
        no_email_items = []
        matched_items = []

        for m in matches:
            status_icon = {"matched": "✅", "no_email": "❌", "suspicious_email": "⚠️"}.get(m["match_status"], "❓")
            status_text = {
                "matched": "Có email khớp" if lang == "vi" else "Email matched",
                "no_email": "Không tìm thấy email" if lang == "vi" else "No matching email",
                "suspicious_email": "Email nghi giả" if lang == "vi" else "Suspicious email",
            }.get(m["match_status"], "")

            line = f"- {status_icon} `{m['description']}` — ${abs(m['amount']):,.2f} ({m['date']}) → **{status_text}**"

            if m["match_status"] == "matched":
                matched_items.append(line)
            elif m["match_status"] == "suspicious_email":
                suspicious_items.append(line)
                if m.get("suspicious_reasons"):
                    for reason in m["suspicious_reasons"]:
                        suspicious_items.append(f"  - ⚠️ _{reason}_")
            else:
                no_email_items.append(line)

        # Show suspicious first, then no email, then matched
        for line in suspicious_items + no_email_items + matched_items:
            parts.append(line)

        return {"response": NL.join(parts), "type": "email_match", "data": matches}

    def _handle_inbound_match(self, message: str, lang: str) -> dict[str, Any]:
        """Đối soát email tiền vào (VA/ví) ↔ giao dịch VA thật trên Wealify.
        Was backend-only (only /dashboard/inbound-reconciliation, no chat
        or UI surface) — check_inbound_emails' real matched_success/
        matched_pending/amount_mismatch/matched_failed/not_found_on_wealify
        results were invisible to anyone not reading the API directly."""
        from agents.inbound_reconciler import check_inbound_emails
        from config import WEALIFY_EMAIL

        cache_key = f"inbound_match_{lang}"
        if cache_key not in self._cache:
            emails = self.data.get("emails", [])
            if WEALIFY_EMAIL:
                emails = [e for e in emails if e.get("to") == WEALIFY_EMAIL]
            va_transactions = self.data.get("_wealify_raw", {}).get("va_transactions", [])
            self._cache[cache_key] = check_inbound_emails(emails, va_transactions, lang)
        result = self._cache[cache_key]
        items = result["items"]

        icon_by_cat = {
            "matched_success": "✅", "matched_pending": "⏳",
            "amount_mismatch": "⚠️", "matched_failed": "❌",
            "not_found_on_wealify": "❓",
        }

        if lang == "en":
            parts = [f"📥 **Inbound money ↔ email cross-check** — {result['total_checked']} email(s) checked"]
            for cat, count in result["by_category"].items():
                parts.append(f"- **{cat}:** {count}")
        else:
            parts = [f"📥 **Đối soát email tiền vào ↔ Wealify** — {result['total_checked']} email đã kiểm tra"]
            for cat, count in result["by_category"].items():
                parts.append(f"- **{cat}:** {count}")

        # Most actionable first: not found, then mismatch/failed, then pending, then success.
        order = ["not_found_on_wealify", "amount_mismatch", "matched_failed", "matched_pending", "matched_success"]
        for cat in order:
            cat_items = [it for it in items if it["category"] == cat]
            if not cat_items:
                continue
            parts.append("")
            for it in cat_items:
                icon = icon_by_cat.get(cat, "❓")
                amt = it.get("email_amount")
                amt_text = f"${amt:,.2f}" if amt is not None else "—"
                parts.append(f"{icon} `{it.get('email_ref') or it.get('email_subject', '')}` — {amt_text} → **{it.get('label', '')}**")
                parts.append(f"  > {it.get('detail', '')}")

        return {"response": NL.join(parts), "type": "inbound_match", "data": items}

    def _handle_reconcile(self, message: str, lang: str) -> dict[str, Any]:
        recon = self._get_reconciliation(lang)
        discs = recon["discrepancies"]

        if lang == "en":
            parts = [f"🔍 **3-Source Reconciliation** — Found **{len(discs)}** discrepancies"]
        else:
            parts = [f"🔍 **Đối chiếu 3 nguồn** — Phát hiện **{len(discs)}** khoản lệch"]

        for d in discs:
            dtype = d.get("type", "")
            icon = {"duplicate_charge": "🔁", "duplicate_fee": "🔁", "missing_on_card": "❗",
                    "missing_in_account": "❗", "wallet_card_mismatch": "💰"}.get(dtype, "⚠️")

            if "reference" in d:
                parts.append(f"---")
                parts.append(f"{icon} **{d.get('reference', '')}** — `{d.get('description', '')}` (${abs(d.get('amount', 0)):,.2f})")

            parts.append(f"> {d.get('detail', '')}")

            if d.get("source"):
                src_label = "Nguồn" if lang == "vi" else "Source"
                parts.append(f"📎 *{src_label}: {d['source']}*")

            # Log to audit
            if "reference" in d:
                audit_log.log_flag(
                    transaction_ref=d.get("reference", ""),
                    reason=dtype,
                    confidence="medium",
                    label=LABEL_NEEDS_REVIEW,
                    source=d.get("source", "reconciliation"),
                    details=d.get("detail", ""),
                )

        return {"response": NL.join(parts), "type": "reconciliation", "data": recon}

    def _handle_subscriptions(self, message: str, lang: str) -> dict[str, Any]:
        anomalies = self._get_anomalies(lang)
        subs = anomalies["subscriptions"]
        hikes = anomalies["price_hikes"]

        if lang == "en":
            parts = [f"📋 **Active Subscriptions** — {len(subs)} found"]
        else:
            parts = [f"📋 **Gói đăng ký đang hoạt động** — {len(subs)} gói"]

        for s in subs:
            label_icon = "✅" if s["label"] == LABEL_CONFIRMED else "⚠️"
            freq_vi = {"monthly": "Hàng tháng", "yearly": "Hàng năm", "quarterly": "Hàng quý"}.get(s["frequency"], s["frequency"])
            freq = freq_vi if lang == "vi" else s["frequency"]
            parts.append(f"{label_icon} **{s['description']}**")
            if lang == "en":
                parts.append(f"- Price: `${s['current_price']:.2f}` / {freq}")
                parts.append(f"- Next charge: {s['next_charge_date']}")
            else:
                parts.append(f"- Giá: `${s['current_price']:.2f}` / {freq}")
                parts.append(f"- Kỳ trừ tiếp: {s['next_charge_date']}")
            parts.append(f"- 🏷️ _{_label_text(s['label'], lang)}_")

        # Explanations
        parts.append("")
        explain_header = "**Giải thích tên dịch vụ:**" if lang == "vi" else "**Service Explanations:**"
        parts.append(explain_header)
        for s in subs:
            if s.get("explanation") and s["explanation"] != "chưa xác định được":
                parts.append(f"- `{s['description']}`: {s['explanation']}")

        # Price hikes
        if hikes:
            parts.append("")
            hike_header = "⚠️ **Phát hiện tăng giá âm thầm:**" if lang == "vi" else "⚠️ **Price Increases Detected:**"
            parts.append(hike_header)

            for h in hikes:
                parts.append(f"- 🔺 **{h['merchant']}**: `${h['old_price']:.2f}` → `${h['new_price']:.2f}` (+`${h['increase']:.2f}`, +{h['increase_pct']}%)")
                parts.append(f"  - 🏷️ *{_label_text(h['label'], lang)}*")

                audit_log.log_flag(
                    # Must match main.py's _run_scheduled_check ref format
                    # (merchant + old/new prices) — merchant alone would
                    # dedup a merchant's second, different price hike
                    # against its first instead of logging it as new.
                    transaction_ref=f"{h['merchant']}|{h['old_price']}->{h['new_price']}",
                    reason="price_hike",
                    confidence="high",
                    label=LABEL_NEEDS_REVIEW,
                    source="anomaly_detector",
                    details=f"Price increased from ${h['old_price']} to ${h['new_price']}",
                )

        return {"response": NL.join(parts), "type": "subscriptions", "data": anomalies}

    def _handle_duplicates(self, message: str, lang: str) -> dict[str, Any]:
        anomalies = self._get_anomalies(lang)
        dups = anomalies["duplicate_charges"]
        recon = self._get_reconciliation(lang)
        fee_dups = [d for d in recon["discrepancies"] if d.get("type") in ("duplicate_charge", "duplicate_fee")]

        all_dups = dups + fee_dups

        if lang == "en":
            parts = [f"🔁 **Duplicate/Double Charges** — {len(all_dups)} found"]
        else:
            parts = [f"🔁 **Khoản trùng / Phí kép** — {len(all_dups)} khoản"]

        if not all_dups:
            no_msg = "Không phát hiện khoản trùng nào." if lang == "vi" else "No duplicate charges found."
            parts.append(no_msg)
        else:
            # Deduplicate by reference
            seen_refs = set()
            for d in all_dups:
                ref = d.get("reference", "")
                if ref in seen_refs:
                    continue
                seen_refs.add(ref)

                desc = d.get("description", "")
                amount = d.get("amount", 0)
                date = d.get("date", "")
                deadline = d.get("dispute_deadline", "")
                dup_of = d.get("duplicate_of", "")

                parts.append("---")
                parts.append(f"⚠️ **{ref}** — `{desc}` — ${abs(amount):,.2f} ({date})")

                if dup_of:
                    dup_label = "Trùng với" if lang == "vi" else "Duplicate of"
                    parts.append(f"- 🔁 {dup_label}: `{dup_of}`")
                if deadline:
                    dl_label = "Hạn khiếu nại" if lang == "vi" else "Dispute deadline"
                    parts.append(f"- ⏰ {dl_label}: **{deadline}**")

                parts.append(f"- 🏷️ *{LABEL_NEEDS_REVIEW}*")

        return {"response": NL.join(parts), "type": "duplicates", "data": all_dups}

    def _handle_send_report(self, message: str, lang: str) -> dict[str, Any]:
        analysis = self._get_statement_analysis(lang)
        anomalies = self._get_anomalies(lang)
        recon = self._get_reconciliation(lang)
        report = generate_report(analysis, anomalies, lang)
        draft = draft_report_email(report, anomalies, recon, lang)

        self.pending_email_draft = draft
        self.pending_email_lang = lang

        if lang == "en":
            parts = [
                "📧 **Email Report Draft Ready**",
                f"**To:** {draft['to']}",
                f"**Subject:** {draft['subject']}",
                "---",
                draft["body"],
                "---",
                "⚠️ **This is a draft. Type 'yes' or 'confirm' to send.**",
            ]
        else:
            parts = [
                "📧 **Bản nháp email báo cáo đã sẵn sàng**",
                f"**Gửi tới:** {draft['to']}",
                f"**Tiêu đề:** {draft['subject']}",
                "---",
                draft["body"],
                "---",
                "⚠️ **Đây là bản nháp. Gõ 'có' hoặc 'xác nhận' để gửi.**",
            ]

        return {"response": NL.join(parts), "type": "email_draft", "data": draft}

    def _handle_unknown_merchant(self, message: str, lang: str) -> dict[str, Any]:
        anomalies = self._get_anomalies(lang)
        unknowns = anomalies["unknown_merchants"]

        # Check if user is asking about a specific amount
        amount_match = re.search(r'\$?([\d,]+\.?\d*)', message)

        if amount_match:
            target_amount = float(amount_match.group(1).replace(",", ""))
            for txn in self.data["account_statement"]:
                if abs(abs(txn["amount"]) - target_amount) < 0.01:
                    email_matches = self._get_email_matches(lang)
                    email_info = ""
                    for em in email_matches:
                        if em.get("reference") == txn.get("reference"):
                            if em["match_status"] == "matched":
                                email_info = NL + ("✅ **Có email biên lai khớp**: " if lang == "vi" else "✅ **Matching receipt email found**: ") + em["matched_email"]["subject"]
                            elif em["match_status"] == "suspicious_email":
                                email_info = NL + ("⚠️ **Email nghi giả**" if lang == "vi" else "⚠️ **Suspicious email found**")
                            else:
                                email_info = NL + ("❌ **Không tìm thấy email biên lai**" if lang == "vi" else "❌ **No matching receipt email**")
                            break

                    from agents.anomaly_detector import _explain_merchant
                    explanation = _explain_merchant(txn.get("merchant_code", ""), txn.get("description", ""))

                    if lang == "en":
                        resp = NL.join([
                            f"🔍 **Transaction: `{txn['description']}`**",
                            f"- **Amount:** ${abs(txn['amount']):,.2f}",
                            f"- **Date:** {txn['date']}",
                            f"- **Type:** {txn['type']}",
                            f"- **Explanation:** {explanation}",
                            f"- **Dispute deadline:** {txn.get('dispute_deadline', 'N/A')}",
                        ]) + email_info
                    else:
                        resp = NL.join([
                            f"🔍 **Giao dịch: `{txn['description']}`**",
                            f"- **Số tiền:** ${abs(txn['amount']):,.2f}",
                            f"- **Ngày:** {txn['date']}",
                            f"- **Loại:** {txn['type']}",
                            f"- **Giải thích:** {explanation}",
                            f"- **Hạn khiếu nại:** {txn.get('dispute_deadline', 'N/A')}",
                        ]) + email_info

                    return {"response": resp, "type": "transaction_lookup"}

        # General unknown merchants list
        if lang == "en":
            parts = [f"❓ **Unknown/Unclear Merchants** — {len(unknowns)} found"]
        else:
            parts = [f"❓ **Khoản lạ / Tên cửa hàng khó hiểu** — {len(unknowns)} khoản"]

        for u in unknowns:
            parts.append("---")
            parts.append(f"⚠️ **`{u['description']}`** — ${abs(u['amount']):,.2f} ({u['date']})")
            parts.append(f"- ℹ️ {u['explanation']}")
            dl_label = "Hạn khiếu nại" if lang == "vi" else "Dispute deadline"
            parts.append(f"- ⏰ {dl_label}: **{u.get('dispute_deadline', 'N/A')}**")
            parts.append(f"- 🏷️ *{_label_text(u['label'], lang)}*")

        return {"response": NL.join(parts), "type": "unknown_merchants", "data": unknowns}

    def _handle_dispute_reminder(self, message: str, lang: str) -> dict[str, Any]:
        """Show items approaching 60-day dispute deadline."""
        today = datetime.utcnow()
        approaching = []

        for txn in self.data["account_statement"]:
            if txn.get("type") not in ("charge", "fee"):
                continue
            deadline_str = txn.get("dispute_deadline", "")
            if not deadline_str or deadline_str == "Unknown":
                continue
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
                days_left = (deadline - today).days
                if 0 < days_left <= 30:
                    approaching.append({
                        **txn,
                        "days_left": days_left,
                    })
            except ValueError:
                continue

        approaching.sort(key=lambda x: x["days_left"])

        if lang == "en":
            parts = [f"⏰ **Dispute Deadline Reminders** — {len(approaching)} items within 30 days"]
        else:
            parts = [f"⏰ **Nhắc hạn khiếu nại** — {len(approaching)} khoản sắp hết hạn (trong 30 ngày)"]

        if not approaching:
            parts.append("✅ Không có khoản nào sắp hết hạn khiếu nại." if lang == "vi" else "✅ No items approaching dispute deadline.")
        else:
            for item in approaching:
                urgency = "🔴" if item["days_left"] <= 7 else ("🟡" if item["days_left"] <= 14 else "🟢")
                if lang == "en":
                    parts.append(f"{urgency} **{item['description']}** — ${abs(item['amount']):,.2f} ({item['date']})")
                    parts.append(f"- Deadline: **{item['dispute_deadline']}** ({item['days_left']} days left)")
                else:
                    parts.append(f"{urgency} **{item['description']}** — ${abs(item['amount']):,.2f} ({item['date']})")
                    parts.append(f"- Hạn: **{item['dispute_deadline']}** (còn {item['days_left']} ngày)")
                parts.append(f"- 🏷️ *{LABEL_NEEDS_REVIEW}*")

            # Offer to draft reminder email
            if approaching:
                draft = draft_dispute_reminder_email(approaching, lang)
                self.pending_email_draft = draft
                self.pending_email_lang = lang
                parts.append("")
                parts.append("📧 " + ("Mình đã soạn email nhắc hạn. Gõ 'xác nhận' để gửi vào email của bạn." if lang == "vi" else "I've drafted a reminder email. Type 'confirm' to send it to your email."))

        return {"response": NL.join(parts), "type": "dispute_reminder"}

    def _handle_scheduled_check(self, message: str, lang: str) -> dict[str, Any]:
        """Run a full scheduled check: all agents, compile results, don't re-report."""
        # Refresh from source and drop cached analysis so newly-appeared
        # transactions actually get picked up, not just re-analyzed stale data.
        self.data = get_all_data()
        self._cache = {}

        analysis = self._get_statement_analysis(lang)
        anomalies = self._get_anomalies(lang)
        recon = self._get_reconciliation(lang)
        email_matches = self._get_email_matches(lang)
        risk = calculate_risk_score(anomalies, recon, email_matches)

        new_flags = 0
        total_issues = 0

        # Flag anomalies (skip if already flagged)
        for u in anomalies.get("unknown_merchants", []):
            total_issues += 1
            if audit_log.log_flag(u["reference"], "unknown_merchant", "medium", LABEL_NEEDS_REVIEW, "anomaly_detector", u.get("explanation", "")):
                new_flags += 1

        for d in anomalies.get("duplicate_charges", []):
            total_issues += 1
            if audit_log.log_flag(d["reference"], "duplicate_charge", "high", LABEL_NEEDS_REVIEW, "anomaly_detector", f"Duplicate of {d.get('duplicate_of', '')}"):
                new_flags += 1

        for h in anomalies.get("price_hikes", []):
            total_issues += 1
            # Ref must match main.py's _run_scheduled_check and the other
            # price_hike logging site above — merchant alone would dedup a
            # merchant's second, different price hike against its first.
            ref = f"{h['merchant']}|{h['old_price']}->{h['new_price']}"
            if audit_log.log_flag(ref, "price_hike", "high", LABEL_NEEDS_REVIEW, "anomaly_detector", f"${h['old_price']} → ${h['new_price']}"):
                new_flags += 1

        for disc in recon.get("discrepancies", []):
            total_issues += 1
            ref = disc.get("reference", disc.get("type", "unknown"))
            if audit_log.log_flag(ref, disc.get("type", "discrepancy"), "medium", LABEL_NEEDS_REVIEW, "reconciler", disc.get("detail", "")):
                new_flags += 1

        for m in email_matches:
            if m.get("match_status") == "suspicious_email":
                total_issues += 1
                if audit_log.log_flag(m["reference"], "suspicious_email", "high", LABEL_NEEDS_REVIEW, "email_matcher", "; ".join(m.get("suspicious_reasons", []))):
                    new_flags += 1

        skipped = total_issues - new_flags

        if lang == "en":
            parts = [
                f"🔍 **Full Scan Complete** — Risk Score: **{risk['total_score']}/100** ({risk['level']})",
                f"- Total issues found: **{total_issues}**",
                f"- New flags logged: **{new_flags}**",
                f"- Already reported (skipped): **{skipped}**",
                "",
                "**Breakdown:**",
                f"- 🚨 Unknown merchants: {len(anomalies.get('unknown_merchants', []))}",
                f"- 🔁 Duplicates: {len(anomalies.get('duplicate_charges', []))}",
                f"- 💰 Price hikes: {len(anomalies.get('price_hikes', []))}",
                f"- 🔍 3-source discrepancies: {recon.get('total_discrepancies', 0)}",
                f"- 📧 Suspicious emails: {sum(1 for m in email_matches if m.get('match_status') == 'suspicious_email')}",
            ]
        else:
            parts = [
                f"🔍 **Rà soát toàn bộ hoàn tất** — Risk Score: **{risk['total_score']}/100** ({risk['level_vi']})",
                f"- Tổng vấn đề phát hiện: **{total_issues}**",
                f"- Cảnh báo mới ghi nhận: **{new_flags}**",
                f"- Đã báo trước (bỏ qua): **{skipped}**",
                "",
                "**Chi tiết:**",
                f"- 🚨 Khoản lạ: {len(anomalies.get('unknown_merchants', []))}",
                f"- 🔁 Khoản trùng: {len(anomalies.get('duplicate_charges', []))}",
                f"- 💰 Gói tăng giá: {len(anomalies.get('price_hikes', []))}",
                f"- 🔍 Lệch 3 nguồn: {recon.get('total_discrepancies', 0)}",
                f"- 📧 Email nghi giả: {sum(1 for m in email_matches if m.get('match_status') == 'suspicious_email')}",
            ]

        return {"response": NL.join(parts), "type": "scheduled_check", "data": {"risk": risk, "new_flags": new_flags}}

    def _handle_audit_log(self, message: str, lang: str) -> dict[str, Any]:
        flags = audit_log.get_all_flags()
        summary = audit_log.get_summary()

        if lang == "en":
            parts = [f"📝 **Audit Log** — {summary['total_flags']} flags"]
        else:
            parts = [f"📝 **Nhật ký cảnh báo** — {summary['total_flags']} mục"]

        if not flags:
            parts.append("Chưa có cảnh báo nào." if lang == "vi" else "No flags yet.")
        else:
            by_label = summary.get("by_label", {})
            for label, count in by_label.items():
                parts.append(f"- {_label_text(label, lang)}: **{count}**")

            parts.append("")
            recent_label = "**Gần đây nhất:**" if lang == "vi" else "**Recent:**"
            parts.append(recent_label)

            for f in flags[-10:]:
                parts.append(f"- `{f['transaction_ref']}` — {f['reason']} — *{_label_text(f['label'], lang)}* ({f['timestamp'][:16]})")

        return {"response": NL.join(parts), "type": "audit_log", "data": flags}

    def _handle_general(self, message: str, lang: str) -> dict[str, Any]:
        greeting_reply = _greeting_reply(message, lang)
        if greeting_reply:
            return {"response": greeting_reply, "type": "greeting"}

        # Try LLM for anything else. Previously gated on len(message) > 20,
        # which meant short-but-real questions ("bạn tên gì", "how much
        # fee?") always got the generic capability-list dump below instead
        # of an actual answer — length alone doesn't mean "not a question".
        if BYTEPLUS_API_KEY:
            try:
                from llm_client import call_llm
                # Build context from data. analysis["summary"] is
                # {currency: {label: value}} — statement mixes VND/USD/EUR
                # with no conversion, so each currency is listed separately.
                analysis = self._get_statement_analysis(lang)
                anomalies = self._get_anomalies(lang)
                summary_text = " | ".join(
                    f"[{currency}] " + ", ".join(f"{k}: {v}" for k, v in group.items())
                    for currency, group in analysis.get("summary", {}).items()
                )

                system = (
                    "You are Wealify — a financial review assistant for cross-border sellers. "
                    "You are READ-ONLY: never offer to cancel services, transfer money, or send emails to third parties. "
                    "Always use one of these 3 labels: 'Định kỳ đã xác định' / 'Cần bạn tự xác nhận' / 'Chưa đủ dữ liệu'. "
                    "TUYỆT ĐỐI KHÔNG BAO GIỜ nói rằng 'tài khoản của bạn an toàn' hoặc 'không có gì bất thường'. "
                    "Nếu không tìm thấy vấn đề, chỉ được nói 'Hiện tại tôi không tìm thấy khoản nào khớp với dữ liệu sẵn có', cấm dùng từ 'an toàn'. "
                    "Never determine or guarantee the security status of the account. "
                    f"Respond in {'Vietnamese' if lang == 'vi' else 'English'}. Be concise."
                )
                prompt = (
                    f"User question: {message}\n\n"
                    f"Financial data summary: {summary_text}\n"
                    f"Anomalies: {anomalies.get('total_anomalies', 0)} issues found\n"
                    f"Subscriptions: {len(anomalies.get('subscriptions', []))} active\n"
                    f"Price hikes: {len(anomalies.get('price_hikes', []))} detected"
                )
                # DeepSeek V4 Flash is a reasoning model — its "thinking" tokens
                # count against this budget before the final answer, so keep
                # plenty of headroom or replies get cut off mid-thought.
                llm_response = call_llm(prompt, system=system, max_tokens=1500)
                return {"response": llm_response, "type": "llm_response"}
            except Exception as e:
                print(f"[Chat] LLM fallback failed: {e}")

        if lang == "en":
            resp = NL.join([
                "👋 I'm your **Wealify financial review assistant**. I can help you with:",
                "- 📊 **Overview** — \"How much did I spend this month/quarter/year?\"",
                "- 📧 **Email matching** — \"Does this $9.99 charge have a receipt?\"",
                "- 🔍 **3-source check** — \"Any money that left but didn't reach the card?\"",
                "- 📋 **Subscriptions** — \"What subscriptions do I have? Any price increases?\"",
                "- 🔁 **Duplicates** — \"Any double charges or duplicate fees?\"",
                "- 📧 **Send report** — \"Send the report to my email\"",
                "- ⏰ **Dispute deadlines** — \"Any items approaching 60-day deadline?\"",
                "- 🔍 **Full scan** — \"Run a complete check\"",
                "- ❓ **Transaction lookup** — \"What is this $54.99 charge?\"",
                "- 📝 **Audit log** — \"Show flag history\"",
                "",
                "What would you like to check?",
            ])
        else:
            resp = NL.join([
                "👋 Mình là **trợ lý rà soát tài chính Wealify**. Mình có thể giúp bạn:",
                "- 📊 **Tổng quan** — \"Tháng/quý/năm này tôi chi bao nhiêu?\"",
                "- 📧 **Đối soát email** — \"Khoản $9.99 này có email biên lai không?\"",
                "- 🔍 **Đối chiếu 3 nguồn** — \"Có tiền rời tài khoản mà chưa lên thẻ không?\"",
                "- 📋 **Gói đăng ký** — \"Mình có những gói gì? Gói nào tăng giá?\"",
                "- 🔁 **Khoản trùng** — \"Có khoản nào bị tính hai lần không?\"",
                "- 📧 **Gửi báo cáo** — \"Gửi báo cáo vào email của tôi\"",
                "- ⏰ **Nhắc hạn** — \"Khoản nào sắp hết hạn khiếu nại 60 ngày?\"",
                "- 🔍 **Rà soát toàn bộ** — \"Chạy kiểm tra toàn bộ\"",
                "- ❓ **Tra cứu** — \"Khoản $54.99 này là gì?\"",
                "- 📝 **Nhật ký** — \"Xem lịch sử cảnh báo\"",
                "",
                "Bạn muốn kiểm tra gì?",
            ])

        return {"response": resp, "type": "general"}


def _is_confirmation(message: str) -> bool:
    """Check if message is a confirmation."""
    confirmations = [
        "yes", "ok", "confirm", "send", "gửi", "có", "xác nhận",
        "đồng ý", "gửi đi", "chấp nhận", "proceed",
    ]
    return message.strip().lower() in confirmations
