
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Billing Server")

# Mock database (in-memory)
users = {
    "U1001": {
        "plan": "Premium",
        "monthly_bill": 999,
        "status": "active",
    },
    "U1002": {
        "plan": "Basic",
        "monthly_bill": 499,
        "status": "active",
    },
}

# Allowed subscription plans and their prices
PLANS = {
    "Basic": 499,
    "Premium": 999,
    "Family": 1499,
}


@mcp.tool()
def get_user_billing(user_id: str) -> dict:
    """Get billing information for a user using their user ID."""

    user_id = user_id.strip()

    if not user_id:
        return {"error": "User ID cannot be empty"}

    if user_id not in users:
        return {"error": f"User '{user_id}' not found"}

    return {
        "user_id": user_id,
        **users[user_id],
    }


@mcp.tool()
def update_subscription(user_id: str, plan: str) -> dict:
    """Update a user's subscription after approval by the client."""

    user_id = user_id.strip()
    plan = plan.strip().title()

    if not user_id:
        return {"error": "User ID cannot be empty"}

    if user_id not in users:
        return {"error": f"User '{user_id}' not found"}

    if plan not in PLANS:
        return {
            "error": "Invalid subscription plan",
            "allowed_plans": list(PLANS.keys()),
        }

    # Update the in-memory user record
    users[user_id]["plan"] = plan
    users[user_id]["monthly_bill"] = PLANS[plan]

    return {
        "user_id": user_id,
        "new_plan": plan,
        "monthly_bill": PLANS[plan],
        "status": "updated",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")