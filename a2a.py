class NetworkAgent:

    def handle_task(self, task: dict) -> dict:
        return {
            "task_id": task["task_id"],
            "agent": "network_agent",
            "status": "completed",
            "result":{
                "category":"network",
                "action":"case_assigned",
                "assigned_team":"network_team"
            }
        }


class BillingAgent:

    def handle_task(self, task: dict) -> dict:
        return {
            "task_id": task["task_id"],
            "agent": "billing_agent",
            "status": "completed",
            "result":{
                "category":"billing",
                "action":"case_assigned",
                "assigned_team":"billing_team"

            }
        }


class TechnicalAgent:

    def handle_task(self, task: dict) -> dict:
        return {
            "task_id": task["task_id"],
            "agent": "technical_agent",
            "status": "completed",
            "result":{
                "category":"technical",
                "action":"case_assigned",
                "assigned_team":"technnical_team"
            }
        }


class A2ARouter:

    def __init__(self):
        self.agents = {
            "network": NetworkAgent(),
            "billing": BillingAgent(),
            "technical": TechnicalAgent(),
        }

    def send_task(self, task: dict) -> dict:
        category = task["category"]

        agent = self.agents.get(category)

        if agent is None:
            return {
                "task_id": task["task_id"],
                "agent":None,
                "status": "failed",
                "error":{
                    "code":"AGENT_NOT_FOUND",
                    "message":f"No agent available for category: {category}",
                }
            }
        try:
            return agent.handle_task(task)
        except Exception as e:
            return {
                    "task_id": task["task_id"],
                    "agent":category,
                    "status": "failed",
                    "error":{
                        "code":"AGENT_EXECUTION_FAILED",
                        "message":str(e),
                        }
                    }
            