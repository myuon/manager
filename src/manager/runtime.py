import os
import sys

# Ensure src/ is on the path for AgentCore Runtime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bedrock_agentcore.runtime import BedrockAgentCoreApp


def _load_secrets():
    """Load secrets from AWS Secrets Manager if OPENAI_API_KEY is not set."""
    if os.environ.get("OPENAI_API_KEY"):
        return
    try:
        import boto3
        client = boto3.client("secretsmanager", region_name="us-east-1")
        resp = client.get_secret_value(SecretId="manager-worker/openai-api-key")
        os.environ["OPENAI_API_KEY"] = resp["SecretString"]
    except Exception:
        pass


app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    _load_secrets()
    from manager.worker import create_worker

    task = payload.get("task", "")
    if not task:
        return {"error": "No task provided"}

    agent = create_worker()
    result = agent(task)

    return {"result": str(result)}


if __name__ == "__main__":
    app.run()
