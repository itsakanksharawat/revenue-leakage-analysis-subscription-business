import pandas as pd
import numpy as np

df = pd.read_csv("Telco_Customer_Churn.csv")
print(df.shape)
print(df.columns)




df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna()


users = df[[
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents"
]].drop_duplicates()

users = users.rename(columns={"customerID": "user_id"})

users.to_csv("users.csv", index=False)

subscriptions = df[[
    "customerID",
    "Contract",
    "tenure",
    "InternetService",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]]

subscriptions = subscriptions.rename(columns={"customerID": "user_id"})

subscriptions.to_csv("subscriptions.csv", index=False)


payments = []

np.random.seed(42)

for _, row in subscriptions.iterrows():
    user_id = row["user_id"]
    tenure = int(row["tenure"])
    monthly_charge = row["MonthlyCharges"]
    churned = row["Churn"] == "Yes"

    for month in range(1, tenure + 1):
        payment_status = "failed" if np.random.rand() < 0.08 else "success"

        payments.append({
            "payment_id": f"{user_id}_{month}",
            "user_id": user_id,
            "payment_month": month,
            "amount": round(monthly_charge, 2),
            "payment_status": payment_status
        })

payments_df = pd.DataFrame(payments)
payments_df.to_csv("payments.csv", index=False)


usage = []

for _, row in subscriptions.iterrows():
    user_id = row["user_id"]
    tenure = int(row["tenure"])
    monthly_charge = row["MonthlyCharges"]
    churned = row["Churn"] == "Yes"

    base_sessions = int(monthly_charge // 10)

    for month in range(1, tenure + 1):
        # Usage decay before churn
        decay = 0.5 if churned and month > tenure - 2 else 1.0

        sessions = max(0, int(np.random.normal(base_sessions * decay, 2)))
        minutes = sessions * np.random.randint(5, 15)

        usage.append({
            "user_id": user_id,
            "month": month,
            "sessions": sessions,
            "minutes_used": minutes
        })

usage_df = pd.DataFrame(usage)
usage_df.to_csv("usage.csv", index=False)

discounts = []

for _, row in subscriptions.iterrows():
    discount = 0

    if row["tenure"] > 24:
        discount = 0.15
    elif row["Churn"] == "Yes":
        discount = 0.20

    discounts.append({
        "user_id": row["user_id"],
        "discount_pct": discount,
        "discount_reason": (
            "loyalty" if row["tenure"] > 24 else
            "retention" if row["Churn"] == "Yes" else
            "none"
        )
    })

discounts_df = pd.DataFrame(discounts)
discounts_df.to_csv("discounts.csv", index=False)
