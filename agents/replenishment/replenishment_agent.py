from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timedelta
import uuid
import math


# ----------------------------
# ✅ Utilities
# ----------------------------

def safe_eval(expr: str, variables: dict):
    """
    Evaluate simple math expression safely.
    Supports +, -, *, /, (), variables.
    """
    allowed_names = {k: v for k, v in variables.items() if isinstance(v, (int, float))}
    try:
        return eval(expr, {"__builtins__": None, "math": math}, allowed_names)
    except Exception as e:
        print(f"❌ Eval error: {e} in expression: {expr}")
        return None


def merge_policy_with_blueprint(method_name: str, blueprint: dict, user_policy: dict) -> dict:
    """
    Merge standard blueprint method with user customizations
    """
    method = next((m for m in blueprint["methods"] if m["method_name"] == method_name), None)
    if not method:
        raise ValueError(f"Method {method_name} not found in blueprint")

    merged = {
        **method,
        "trigger_condition": user_policy.get("custom_trigger", method["trigger_condition"]),
        "action_logic": user_policy.get("custom_action", method["action_logic"]),
        "parameters": {**method["parameters"], **user_policy}
    }
    return merged


# ----------------------------
# ✅ Replenishment Agent
# ----------------------------

class ReplenishmentAgent:
    def __init__(self, company_id: UUID, db: AsyncSession, blueprint: dict):
        self.company_id = company_id
        self.db = db
        self.blueprint = blueprint

    async def run(self):
        products = await self.fetch_product_data()
        planned_orders = []

        for product in products:
            policy = await self.get_segment_policy(product["segment"])
            if not policy:
                continue

            merged_policy = merge_policy_with_blueprint(
                method_name=policy["replenishment_policy"],
                blueprint=self.blueprint,
                user_policy=policy["policy_parameters"]
            )

            variables = self.extract_variables(product, merged_policy["parameters"])

            # Check trigger
            if not safe_eval(merged_policy["trigger_condition"], variables):
                continue

            # Evaluate action logic (supports "order_quantity = ..." too)
            expression = merged_policy["action_logic"]
            if "=" in expression:
                _, rhs = expression.split("=", 1)
                expression = rhs.strip()

            qty = safe_eval(expression, variables)
            if qty and qty > 0:
                await self.create_planned_order(
                    product["product_id"],
                    product.get("location_id"),
                    qty,
                    policy["replenishment_policy"],
                    policy["policy_parameters"]
                )
                planned_orders.append({
                    "product_id": str(product["product_id"]),
                    "order_quantity": qty,
                    "reason": merged_policy["trigger_condition"]
                })

                print(f"✅ Created planned order for {product['product_id']} — Qty: {qty}")

        await self.db.commit()
        return planned_orders

    async def fetch_product_data(self):
        query = text("""
            SELECT 
                p.product_id AS product_id,
                p.segment,
                p.location_id,
                COALESCE(oh.quantity, 0) AS inventory,
                COALESCE((
                    SELECT SUM(s.quantity)
                    FROM sales_orders s
                    WHERE s.product_id = p.product_id AND s.order_date > CURRENT_DATE
                ), 0) AS forecast_quantity
            FROM products p
            LEFT JOIN on_hand_inventory oh ON oh.product_id = p.product_id
            WHERE p.company_id = :company_id
        """)
        result = await self.db.execute(query, {"company_id": str(self.company_id)})
        return result.mappings().all()

    async def get_segment_policy(self, segment_name: str):
        result = await self.db.execute(text("""
            SELECT replenishment_policy, policy_parameters
            FROM segment_policies
            WHERE segment_name = :segment_name AND company_id = :company_id
        """), {"segment_name": segment_name, "company_id": str(self.company_id)})
        row = result.mappings().first()
        return row if row else None

    def extract_variables(self, product_row, parameters_config):
        values = {}

        for key, param in parameters_config.items():
            if key in ["custom_trigger", "custom_action"]:
                continue

            if isinstance(param, dict):
                source = param.get("source", "")
                default = param.get("default", 0)
            else:
                source = ""
                default = param

            if source == "inventory":
                values[key] = float(product_row.get("inventory", default))
            elif source == "forecast":
                values[key] = float(product_row.get("forecast_quantity", default))
            else:
                try:
                    values[key] = float(default)
                except Exception as e:
                    print(f"⚠️ Skipped key `{key}` — cannot convert `{default}` to float")
                    continue

        return values

    async def create_planned_order(self, product_id, location_id, quantity, method, policy_params):
        today = datetime.utcnow().date()
        offset_days = int(policy_params.get("lead_time_offset_days", 0))
        lead_time = int(policy_params.get("lead_time", 7))

        order_date = today + timedelta(days=offset_days)
        delivery_date = order_date + timedelta(days=lead_time)

        await self.db.execute(text("""
            INSERT INTO purchase_orders (
                po_id, company_id, product_id, location_id, order_type, 
                quantity, status, created_at, order_date, expected_delivery
            ) VALUES (
                :id, :company_id, :product_id, :location_id, :order_type, 
                :order_quantity, :order_status, :created_at, :order_date, :delivery_date
            )
        """), {
            "id": str(uuid.uuid4()),
            "company_id": str(self.company_id),
            "product_id": str(product_id),
            "location_id": str(location_id) if location_id else None,
            "order_type": 3,
            "order_quantity": quantity,
            "order_status": "planned",
            "created_at": datetime.utcnow(),
            "order_date": order_date,
            "delivery_date": delivery_date
        })
