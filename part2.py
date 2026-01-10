import pandas as pd
import numpy as np

users = pd.read_csv("users.csv")
subs = pd.read_csv("subscriptions.csv")
payments = pd.read_csv("payments.csv")
usage = pd.read_csv("usage.csv")
discounts = pd.read_csv("discounts.csv")


monthly_leakage = (
    payments
    .assign(
        failed_amount=lambda x: x["amount"].where(
            x["payment_status"] == "failed", 0
        )
    )
    .groupby("payment_month", as_index=False)
    .agg(
        total_revenue=("amount", "sum"),
        failed_revenue=("failed_amount", "sum")
    )
)

monthly_leakage["failure_rate"] = (
    monthly_leakage["failed_revenue"] / monthly_leakage["total_revenue"]
)

monthly_leakage.head()


discount_impact = subs.merge(discounts, on="user_id")

discount_impact["undiscounted_revenue"] = (
    discount_impact["MonthlyCharges"] * discount_impact["tenure"]
)

discount_impact["discounted_revenue"] = (
    discount_impact["MonthlyCharges"] *
    (1 - discount_impact["discount_pct"]) *
    discount_impact["tenure"]
)

discount_impact["discount_loss"] = (
    discount_impact["undiscounted_revenue"] -
    discount_impact["discounted_revenue"]
)

discount_loss_summary = (
    discount_impact
    .groupby("discount_reason", as_index=False)
    .agg(total_discount_loss=("discount_loss", "sum"))
)

discount_loss_summary


usage_summary = (
    usage
    .groupby("user_id", as_index=False)
    .agg(
        avg_sessions=("sessions", "mean"),
        avg_minutes=("minutes_used", "mean")
    )
)

dormant_users = usage_summary[
    (usage_summary["avg_sessions"] < 2) &
    (usage_summary["avg_minutes"] < 10)
]

dormant_users = dormant_users.merge(
    subs[["user_id", "MonthlyCharges"]],
    on="user_id",
    how="left"
)

dormant_revenue_at_risk = dormant_users["MonthlyCharges"].sum()

dormant_revenue_at_risk


priority = pd.DataFrame({
    "Leakage_Type": [
        "Payment Failures",
        "Discount Abuse",
        "Dormant Paid Users"
    ],
    "Estimated_Monthly_Loss": [
        monthly_leakage["failed_revenue"].mean(),
        discount_loss_summary["total_discount_loss"].sum() / subs["tenure"].mean(),
        dormant_revenue_at_risk
    ]
})

priority = priority.sort_values(
    "Estimated_Monthly_Loss", ascending=False
)

priority

print("=== Monthly Leakage ===")
print(monthly_leakage.head())

print("\n=== Discount Loss Summary ===")
print(discount_loss_summary)

print("\n=== Dormant Revenue At Risk ===")
print(dormant_revenue_at_risk)

print("\n=== Priority Table ===")
print(priority)

print(f"Average monthly failed revenue: {monthly_leakage['failed_revenue'].mean():.2f}")


monthly_leakage.to_csv("output_monthly_leakage.csv", index=False)
discount_loss_summary.to_csv("output_discount_loss.csv", index=False)
priority.to_csv("output_priority.csv", index=False)
