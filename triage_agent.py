class TriageAgent:

    def classify(self, description: str) -> dict:
        text = description.lower()

        if any(word in text for word in [
            "bill", "invoice", "payment", "charge"
        ]):
            category = "billing"

        elif any(word in text for word in [
            "internet", "network", "connection",
            "wifi", "connectivity"
        ]):
            category = "network"

        else:
            category = "technical"

        return {
            "category": category,
            "description": description
        }


if __name__ == "__main__":
    agent = TriageAgent()

    result = agent.classify(
        "My internet keeps disconnecting"
    )

    print(result)