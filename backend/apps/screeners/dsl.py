from typing import Any

ALLOWED_FIELDS = {
    "close",
    "sma_20",
    "sma_50",
    "sma_100",
    "sma_200",
    "ema_12",
    "ema_26",
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_histogram",
    "atr_pct",
    "relative_volume",
    "return_1d",
    "return_5d",
    "return_20d",
    "return_50d",
    "return_252d",
    "distance_high_20",
    "distance_high_252",
    "market_cap",
    "shares_outstanding",
    "pe",
    "pb",
    "ps",
    "ev_ebitda",
    "eps",
    "eps_growth",
    "revenue",
    "revenue_growth",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "roe",
    "roa",
    "debt_equity",
    "current_ratio",
    "quick_ratio",
    "free_cash_flow",
    "strong_buy",
    "buy",
    "hold",
    "sell",
    "strong_sell",
    "analyst_buy_ratio",
    "latest_insider_mspr",
    "insider_net_change",
    "insider_buy_count",
    "insider_sell_count",
    "days_to_earnings",
    "latest_eps_surprise",
    "latest_eps_surprise_pct",
    "sector",
    "industry",
    "exchange",
}
ALLOWED_OPERATORS = {
    ">",
    "<",
    ">=",
    "<=",
    "=",
    "between",
    "not_between",
    "crosses_above",
    "crosses_below",
}


class RuleValidationError(ValueError):
    pass


def validate_rules(group: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(group, dict) or group.get("logic") not in {"AND", "OR"}:
        raise RuleValidationError("Each rule group requires logic AND or OR")
    conditions = group.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        raise RuleValidationError("Each rule group requires non-empty conditions")
    for condition in conditions:
        if "logic" in condition:
            validate_rules(condition)
            continue
        left = condition.get("left")
        operator = condition.get("operator")
        if left not in ALLOWED_FIELDS:
            raise RuleValidationError(f"Field '{left}' is not allowed")
        if operator not in ALLOWED_OPERATORS:
            raise RuleValidationError(f"Operator '{operator}' is not allowed")
        right_field = condition.get("right_field")
        if right_field is not None and right_field not in ALLOWED_FIELDS:
            raise RuleValidationError(f"Field '{right_field}' is not allowed")
        if right_field is None and "value" not in condition:
            raise RuleValidationError("A condition requires value or right_field")
        if operator in {"between", "not_between"}:
            value = condition.get("value")
            if not isinstance(value, list) or len(value) != 2:
                raise RuleValidationError(f"Operator '{operator}' requires two values")
    return group


def _resolve(row: Any, field: str | None, value: Any) -> Any:
    return getattr(row, field, None) if field else value


def _condition_matches(condition: dict[str, Any], current: Any, previous: Any) -> bool:
    left = getattr(current, condition["left"], None)
    right = _resolve(current, condition.get("right_field"), condition.get("value"))
    if left is None or right is None:
        return False
    operator = condition["operator"]
    if operator == ">":
        return left > right
    if operator == "<":
        return left < right
    if operator == ">=":
        return left >= right
    if operator == "<=":
        return left <= right
    if operator == "=":
        return left == right
    if operator == "between":
        return condition["value"][0] <= left <= condition["value"][1]
    if operator == "not_between":
        return not condition["value"][0] <= left <= condition["value"][1]
    if previous is None:
        return False
    previous_left = getattr(previous, condition["left"], None)
    previous_right = _resolve(previous, condition.get("right_field"), condition.get("value"))
    if previous_left is None or previous_right is None:
        return False
    if operator == "crosses_above":
        return previous_left <= previous_right and left > right
    if operator == "crosses_below":
        return previous_left >= previous_right and left < right
    return False


def matches_rules(group: dict[str, Any], current: Any, previous: Any = None) -> bool:
    validate_rules(group)
    results = [
        matches_rules(item, current, previous)
        if "logic" in item
        else _condition_matches(item, current, previous)
        for item in group["conditions"]
    ]
    return all(results) if group["logic"] == "AND" else any(results)
