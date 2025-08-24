# Advanced Documentation

This document contains detailed usage, configuration, and extension notes for the Kubernetes GenAI Agent.

## Optional Usage

### Programmatic Usage
```python
from k8s_agent import K8sAgent
import os

# Initialize agent
api_key = os.getenv("GROQ_API_KEY")
agent = K8sAgent(api_key)  # default model: "openai/gpt-oss-120b"

# Chat with the agent
response = agent.chat("List all deployments in production namespace")
print(response)
```

### Direct Tool Usage
```python
from k8s_tools import K8sTools

# Initialize tools
tools = K8sTools()

# Execute specific operations
result = tools.execute_tool("list_pods", {"namespace": "default"})
if result["success"]:
    print("Pods:", result["data"])
```

## Available Commands/Operations

The agent can handle these types of requests:

### Resource Listing
- "Show me all pods in the default namespace"
- "List deployments in production"
- "What services are running?"
- "Show all namespaces"

### Create Operations
- "Create a pod named web using image nginx:alpine in default"
- "Create a deployment httpd with 2 replicas"
- "Create a ClusterIP service web-svc on port 80 targeting 8080"
- "Create a configmap app-config with keys db=postgres, mode=prod"
- "Create a secret api-keys with key TOKEN=..."

### Scaling Operations
- "Scale nginx deployment to 3 replicas"
- "Scale down the api-server to 1 replica"

### Update Operations
- "Update deployment api container api to image ghcr.io/org/api:1.2.3"
- "Update pod temp-job container job to image busybox:1.36"
- "Update configmap app-config with new values"

### Troubleshooting
- "Get logs from pod xyz-123"
- "Show me the last 50 lines of logs from failing-pod"
- "What's the cluster information?"

### Management Operations
- "Delete pod problematic-pod-123"
- "Create a namespace called testing"
- "Delete the old-project namespace"

### Delete Operations
- "Delete deployment httpd in default"
- "Delete service web-svc in default"
- "Delete configmap app-config in dev"
- "Delete secret api-keys in default"

### Analysis Requests
- "Which pods are not ready?"
- "Show me pods that have restarted"
- "What's the status of my cluster?"

## Configuration

### Custom Kubeconfig
```python
agent = K8sAgent(api_key, kubeconfig_path="/path/to/custom/kubeconfig")
```

### Model selection
```python
# Default already set to a Groq model via OpenAI-compatible SDK
agent = K8sAgent(api_key, model="openai/gpt-oss-120b")
```

### Custom System Prompt
The system prompt is resolved in this order: `SYSTEM_PROMPT` env var > `prompt/system_promtp.toml` > built-in default.
```python
agent.set_system_prompt("You are a senior DevOps engineer specializing in Kubernetes...")
```

## Security Considerations

- API Key Protection: Never commit your Groq API key to version control
- Cluster Access: The agent has the same permissions as your kubectl configuration
- Destructive Operations: The agent will ask for confirmation before deleting resources
- Network Access: Ensure secure network access to your K8s cluster

## Troubleshooting

### Common Issues

"Failed to load Kubernetes config"
- Ensure kubectl is properly configured
- Check KUBECONFIG environment variable
- Verify cluster connectivity

"Groq API Error"
- Verify GROQ_API_KEY is set correctly
- Check API key permissions and quota
- Ensure internet connectivity

"Permission Denied"
- Check your kubectl permissions
- Verify RBAC settings for required operations
- Test with: `kubectl auth can-i get pods`

## Advanced Usage

### Custom Tools
Extend the agent with custom tools:
```python
# Add custom tool definition
custom_tool = {
    "name": "restart_deployment",
    "description": "Restart a deployment by updating its annotations",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Deployment name"},
            "namespace": {"type": "string", "default": "default"}
        },
        "required": ["name"]
    }
}

# Implement tool logic in K8sTools.execute_tool()
```

### Integration with Other Systems
The agent can be integrated with:
- Slack bots for ChatOps
- Web dashboards
- CI/CD pipelines
- Monitoring systems

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License
This project is open source. See LICENSE file for details.
