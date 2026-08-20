"""
Finding Schema — Chuẩn theo WLF_cam_nang_trien_khai.pdf Mục 5.

Mỗi finding là đơn vị đầu ra duy nhất. Mọi cảnh báo, mọi dòng trong
bảng đối soát đều là một Finding.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional


# ─── Finding type codes (Phụ lục B) ──────────────────────
FINDING_TYPES = {
    "RECURRING_SUBSCRIPTION",
    "SILENT_PRICE_INCREASE",
    "UNUSED_SUBSCRIPTION_SUSPECT",
    "DUPLICATE_CHARGE",
    "DUPLICATE_PAYIN",
    "DOUBLE_FEE",
    "IN_TRANSIT_NOT_ON_CARD",
    "WALLET_BALANCE_MISMATCH",
    "NO_MATCHING_EMAIL",
    "SUSPICIOUS_EMAIL",
    "UNKNOWN_MERCHANT",
    "UNRECOGNIZED_CHARGE",
}

# ─── Label codes (Phụ lục C) ────────────────────────────
LABEL_CODES = {
    "DINH_KY_DA_XAC_DINH": {
        "vi": "Định kỳ đã xác định",
        "en": "Confirmed recurring",
    },
    "CAN_BAN_TU_XAC_NHAN": {
        "vi": "Cần bạn tự xác nhận",
        "en": "Needs your confirmation",
    },
    "CHUA_DU_DU_LIEU": {
        "vi": "Chưa đủ dữ liệu",
        "en": "Insufficient data",
    },
}

# ─── Threshold config (Phụ lục A) ────────────────────────
THRESHOLDS = {
    "recurring_min_occurrences": 3,
    "recurring_amount_tolerance": 0.05,   # 5%
    "cadence_windows": {
        "weekly":    (6, 8),
        "monthly":   (27, 33),
        "quarterly": (88, 95),
        "yearly":    (360, 370),
    },
    "price_increase_min_delta": 0.50,     # USD
    "duplicate_time_window_hours": 72,
    "in_transit_window_days": 7,
    "in_transit_amount_tolerance": 0.05,  # 5%
    "email_date_window_days": 3,
    "email_match_threshold": 0.80,
    "email_notfound_threshold": 0.50,
    "merchant_fuzzy_threshold": 0.90,
    "lookalike_domain_distance": 2,
    "dispute_window_days": 60,
    "deadline_warning_days": 14,
}


# ─── Rule table R-01→R-15 (Mục 6) ───────────────────────

RULE_TABLE = {
    "R-01": {
        "type": "RECURRING_SUBSCRIPTION",
        "label": "DINH_KY_DA_XAC_DINH",
        "desc": "≥3 lần, chu kỳ đều, biên độ tiền ≤5%",
    },
    "R-02": {
        "type": "RECURRING_SUBSCRIPTION",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "Chỉ 2 lần, hoặc khoảng cách lệch chu kỳ >3 ngày, hoặc biên độ 5-15%",
    },
    "R-03": {
        "type": "SILENT_PRICE_INCREASE",
        "label": "DINH_KY_DA_XAC_DINH",
        "desc": "Chuỗi R-01 + amount[n] > amount[n-1] + chênh > $0.50",
    },
    "R-04": {
        "type": "SILENT_PRICE_INCREASE",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "Chuỗi R-02 mà đã đổi giá",
    },
    "R-05": {
        "type": "UNUSED_SUBSCRIPTION_SUSPECT",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "Chuỗi R-01, còn trừ tiền, không có email ≥2 kỳ",
    },
    "R-06": {
        "type": "DUPLICATE_CHARGE",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "Cùng merchant + cùng amount + Δt ≤ 72h + khác ref + ≤1 email",
    },
    "R-07": {
        "type": "DUPLICATE_CHARGE",
        "label": "CHUA_DU_DU_LIEU",
        "desc": "Như R-06 nhưng merchant_key = null",
    },
    "R-08": {
        "type": "DOUBLE_FEE",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "≥2 khoản cùng loại phí, cùng amount, cùng ngày, quy về cùng giao dịch gốc",
    },
    "R-09": {
        "type": "DUPLICATE_PAYIN",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "≥2 khoản payin cùng amount, cùng ngày, khác ref, cùng nguồn gửi",
    },
    "R-10": {
        "type": "IN_TRANSIT_NOT_ON_CARD",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "transfer_to_card ở sao kê TK, không có ghi có tương ứng (±5%, 7 ngày) ở thẻ",
    },
    "R-11": {
        "type": "WALLET_BALANCE_MISMATCH",
        "label": "CHUA_DU_DU_LIEU",
        "desc": "|(đầu + Σvào − Σra) − cuối| ≥ 1 cent",
    },
    "R-12": {
        "type": "NO_MATCHING_EMAIL",
        "label": "CHUA_DU_DU_LIEU",
        "desc": "Giao dịch chi, điểm khớp email cao nhất < 0.50",
    },
    "R-13": {
        "type": "SUSPICIOUS_EMAIL",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "Domain ∉ allowlist, lookalike, reply-to khác, số tiền ≠",
    },
    "R-14": {
        "type": "UNKNOWN_MERCHANT",
        "label": "CHUA_DU_DU_LIEU",
        "desc": "merchant_key = null sau tra từ điển + fuzzy",
    },
    "R-15": {
        "type": "UNRECOGNIZED_CHARGE",
        "label": "CAN_BAN_TU_XAC_NHAN",
        "desc": "Không thuộc chuỗi định kỳ, không có email, merchant_key = null",
    },
    "R-99": {
        "type": "",
        "label": "CHUA_DU_DU_LIEU",
        "desc": "Không rule nào khớp nhưng vẫn nghi vấn",
    },
}


def get_label_text(label_code: str, lang: str = "vi") -> str:
    """Get display text for a label code."""
    return LABEL_CODES.get(label_code, LABEL_CODES["CHUA_DU_DU_LIEU"])[lang]


def compute_confidence(
    occurrences: int = 0,
    amount_match_exact: bool = False,
    amount_match_pct: float = 0.0,
    has_email: Optional[bool] = None,
    email_suspicious: bool = False,
    merchant_known: bool = False,
) -> float:
    """
    Compute confidence score per PDF formula (Mục 6).
    
    confidence = 0.40 * (số lần lặp chuẩn hoá)
               + 0.30 * (mức khớp số tiền)
               + 0.20 * (có email xác nhận)
               + 0.10 * (merchant tra được từ điển)
    """
    # Occurrence normalization: 2=0.3, 3=0.7, ≥4=1.0
    if occurrences >= 4:
        occ_score = 1.0
    elif occurrences == 3:
        occ_score = 0.7
    elif occurrences == 2:
        occ_score = 0.3
    else:
        occ_score = 0.0

    # Amount match: exact=1.0, ≤5%=0.6
    if amount_match_exact:
        amt_score = 1.0
    elif amount_match_pct <= 0.05:
        amt_score = 0.6
    else:
        amt_score = 0.0

    # Email: has=1.0, suspicious=0.3, none=0.0
    if has_email is True and not email_suspicious:
        email_score = 1.0
    elif email_suspicious:
        email_score = 0.3
    else:
        email_score = 0.0

    # Merchant: known=1.0, unknown=0.0
    merchant_score = 1.0 if merchant_known else 0.0

    confidence = (
        0.40 * occ_score
        + 0.30 * amt_score
        + 0.20 * email_score
        + 0.10 * merchant_score
    )
    return round(confidence, 2)


def compute_fingerprint(
    finding_type: str,
    evidence_refs: list[str],
    amount_cents: int,
    occurred_at: str,
) -> str:
    """
    Compute stable SHA256 fingerprint for a finding.
    Same data → same fingerprint across runs.
    """
    data = json.dumps({
        "type": finding_type,
        "evidence_refs": sorted(evidence_refs),
        "amount_cents": amount_cents,
        "occurred_at": occurred_at,
    }, sort_keys=True)
    return "sha256:" + hashlib.sha256(data.encode()).hexdigest()[:16]


def calc_dispute_deadline(statement_date: str) -> str:
    """
    Calculate dispute deadline = statement_date + 60 days.
    statement_date = ngày NGÂN HÀNG GỬI SAO KÊ (thường cuối tháng).
    """
    try:
        dt = datetime.strptime(statement_date, "%Y-%m-%d")
        deadline = dt + timedelta(days=THRESHOLDS["dispute_window_days"])
        return deadline.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "Unknown"


def calc_statement_date(txn_date: str) -> str:
    """
    Approximate statement_date from transaction date.
    Statement is typically issued at end of month containing the transaction.
    """
    try:
        dt = datetime.strptime(txn_date, "%Y-%m-%d")
        # End of month = 28th of next month (conservative)
        if dt.month == 12:
            stmt = datetime(dt.year + 1, 1, 28)
        else:
            stmt = datetime(dt.year, dt.month + 1, 28)
        return stmt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return txn_date


def calc_days_left(dispute_deadline: str) -> Optional[int]:
    """Calculate days left until deadline (computed at render time, not stored)."""
    try:
        deadline = datetime.strptime(dispute_deadline, "%Y-%m-%d")
        return (deadline - datetime.utcnow()).days
    except (ValueError, TypeError):
        return None


_finding_counter = 0


def make_finding(
    finding_type: str,
    label_rule_id: str,
    title_vi: str,
    title_en: str,
    explanation_vi: str,
    explanation_en: str,
    amount_cents: int,
    currency: str = "USD",
    occurred_at: str = "",
    evidence_refs: list[str] | None = None,
    evidence_sources: list[dict] | None = None,
    statement_date: str = "",
    merchant_key: Optional[str] = None,
    merchant_display_vi: str = "",
    recommended_action_vi: str = "",
    draft_available: bool = False,
    confidence: float = 0.0,
    severity_rank: int = 2,
) -> dict[str, Any]:
    """
    Create a Finding object conforming to PDF schema (Mục 5.1).
    """
    global _finding_counter
    _finding_counter += 1

    if evidence_refs is None:
        evidence_refs = []

    # Get label from rule table
    rule = RULE_TABLE.get(label_rule_id, RULE_TABLE.get("R-99", {}))
    label_code = rule.get("label", "CHUA_DU_DU_LIEU")

    # Compute statement_date if not provided
    if not statement_date and occurred_at:
        statement_date = calc_statement_date(occurred_at)

    # Compute dispute_deadline
    dispute_deadline = calc_dispute_deadline(statement_date)

    # Compute fingerprint
    fingerprint = compute_fingerprint(
        finding_type, evidence_refs, amount_cents, occurred_at
    )

    return {
        "finding_id": f"F-2026-{_finding_counter:06d}",
        "type": finding_type,
        "severity_rank": severity_rank,
        "label": label_code,
        "label_vi": get_label_text(label_code, "vi"),
        "label_en": get_label_text(label_code, "en"),
        "label_rule_id": label_rule_id,
        "confidence": confidence,
        "title_vi": title_vi,
        "title_en": title_en,
        "explanation_vi": explanation_vi,
        "explanation_en": explanation_en,
        "amount_cents": amount_cents,
        "currency": currency,
        "occurred_at": occurred_at,
        "evidence_refs": evidence_refs,
        "evidence_sources": evidence_sources or [],
        "statement_date": statement_date,
        "dispute_deadline": dispute_deadline,
        "days_left": calc_days_left(dispute_deadline),
        "merchant_key": merchant_key,
        "merchant_display_vi": merchant_display_vi,
        "recommended_action_vi": recommended_action_vi,
        "draft_available": draft_available,
        "fingerprint": fingerprint,
        "status": "new",
        "first_seen_at": datetime.utcnow().isoformat() + "Z",
        "last_seen_at": datetime.utcnow().isoformat() + "Z",
    }
