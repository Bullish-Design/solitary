from llm_sandbox import SandboxSession
import docker


client = docker.from_env()  # picks up /var/run/docker.sock

print(f"\nDocker containers currently running:\n")
for c in client.containers.list():
    print(f"    {c.name}: {c.id}")

with SandboxSession(
    # backend="docker",
    # client=client,  # Use custom client instead of docker.from_env()
    # dockerfile="./config/Dockerfile",
    lang="python",
    # runtime_config=runtime_config,
) as session:
    result = session.run("""
print("Hello from LLM Sandbox!")
print("I'm running in a secure container.")
    """)

    print(result.stdout)
