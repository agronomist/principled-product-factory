"""Metering and unit economics module enforcing Contribution Margin and Cohort P&L gates."""

from platform.metering.margin_guard import (
    CohortPnLInput,
    CohortPnLResult,
    CohortPnLValidator,
    ContributionMarginGate,
    MarginDecision,
    MarginEvaluationResult,
    MarginViolationError,
    SixMonthPricingRetroAudit,
    SixMonthRetroAuditInput,
    SixMonthRetroAuditResult,
    UnitEconomicsInput,
)

__all__ = [
    "CohortPnLInput",
    "CohortPnLResult",
    "CohortPnLValidator",
    "ContributionMarginGate",
    "MarginDecision",
    "MarginEvaluationResult",
    "MarginViolationError",
    "SixMonthPricingRetroAudit",
    "SixMonthRetroAuditInput",
    "SixMonthRetroAuditResult",
    "UnitEconomicsInput",
]
