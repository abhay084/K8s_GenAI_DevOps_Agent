# Kubernetes GenAI Agent

A powerful GenAI agent for Kubernetes cluster operations using OpenAI's function calling capabilities. This agent can help you manage your K8s cluster through natural language conversations.

## Features

🤖 **Natural Language Interface**: Chat with your K8s cluster using plain English  
📋 **Resource Management**: List and inspect pods, deployments, services, namespaces  
⚡ **Scaling Operations**: Scale deployments up or down  
🔍 **Troubleshooting**: Get pod logs and cluster information  
🏗️ **Namespace Management**: Create and delete namespaces  
🗑️ **Pod Cleanup**: Delete problematic pods  
📊 **Cluster Insights**: Get comprehensive cluster information  

## Architecture

- **`k8s_client.py`**: Low-level Kubernetes API wrapper
- **`k8s_tools.py`**: Tool definitions for the GenAI agent
- **`k8s_agent.py`**: Main agent with OpenAI integration and CLI
- **`example_usage.py`**: Usage examples and demonstrations

## Prerequisites

1. **Kubernetes Cluster**: Access to a K8s cluster with properly configured `kubectl`
2. **OpenAI API Key**: For the GenAI agent functionality
3. **Python 3.8+**: Required for the application

## Installation

1. **Clone or download the project**:
   ```bash
   cd /path/to/K8s-DevOps-GenAI-Agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   export KUBECONFIG="/path/to/your/kubeconfig"  # Optional, uses default if not set
   ```

## Quick Start

### 1. Interactive CLI Agent

Run the interactive agent:

```bash
python k8s_agent.py
```

Example conversation:
```
💬 You: Show me all pods in the kube-system namespace
🤖 Agent: Here are the pods in the kube-system namespace:
- coredns-558bd4d5db-xyz123 (Running) - Ready: ✓
- etcd-minikube (Running) - Ready: ✓  
- kube-apiserver-minikube (Running) - Ready: ✓
...

💬 You: Scale my nginx deployment to 5 replicas
🤖 Agent: I've successfully scaled the nginx deployment to 5 replicas.

💬 You: What's wrong with my failing pods?
🤖 Agent: Let me check for pods that aren't running... [provides analysis]
```

### 2. Programmatic Usage

```python
from k8s_agent import K8sAgent
import os

# Initialize agent
api_key = os.getenv("OPENAI_API_KEY")
agent = K8sAgent(api_key)

# Chat with the agent
response = agent.chat("List all deployments in production namespace")
print(response)
```

### 3. Direct Tool Usage

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

### Scaling Operations
- "Scale nginx deployment to 3 replicas"
- "Scale down the api-server to 1 replica"

### Troubleshooting
- "Get logs from pod xyz-123"
- "Show me the last 50 lines of logs from failing-pod"
- "What's the cluster information?"

### Management Operations
- "Delete pod problematic-pod-123"
- "Create a namespace called testing"
- "Delete the old-project namespace"

### Analysis Requests
- "Which pods are not ready?"
- "Show me pods that have restarted"
- "What's the status of my cluster?"

## Configuration

### Custom Kubeconfig
```python
agent = K8sAgent(api_key, kubeconfig_path="/path/to/custom/kubeconfig")
```

### Different OpenAI Model
```python
agent = K8sAgent(api_key, model="gpt-3.5-turbo")
```

### Custom System Prompt
```python
agent.set_system_prompt("You are a senior DevOps engineer specializing in Kubernetes...")
```

## Security Considerations

⚠️ **Important Security Notes**:

1. **API Key Protection**: Never commit your OpenAI API key to version control
2. **Cluster Access**: The agent has the same permissions as your kubectl configuration
3. **Destructive Operations**: The agent will ask for confirmation before deleting resources
4. **Network Access**: Ensure secure network access to your K8s cluster

## Troubleshooting

### Common Issues

**"Failed to load Kubernetes config"**
- Ensure kubectl is properly configured
- Check KUBECONFIG environment variable
- Verify cluster connectivity

**"OpenAI API Error"**
- Verify OPENAI_API_KEY is set correctly
- Check API key permissions and quota
- Ensure internet connectivity

**"Permission Denied"**
- Check your kubectl permissions
- Verify RBAC settings for required operations
- Test with: `kubectl auth can-i get pods`

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Examples

Run the examples:
```bash
python example_usage.py
```

This will show you different ways to use the agent and tools.

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

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples
3. Open an issue on GitHub

---

**Happy Kubernetes management! 🚀**
