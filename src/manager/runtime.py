from bedrock_agentcore.runtime import BedrockAgentCoreApp

from manager.worker import create_worker

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    task = payload.get("task", "")
    if not task:
        return {"error": "No task provided"}

    agent = create_worker()
    result = agent(task)

    return {"result": str(result)}


if __name__ == "__main__":
    app.run()
