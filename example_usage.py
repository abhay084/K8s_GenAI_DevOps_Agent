"""
Example usage of the Kubernetes GenAI Agent.
"""

import os
from k8s_agent import K8sAgent, K8sTools
from k8s_client import K8sClient


def basic_agent_example():
    """Example of using the K8s Agent with OpenAI."""
    # Initialize agent (requires OPENAI_API_KEY environment variable)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    agent = K8sAgent(api_key)
    
    # Example conversations
    print("=== K8s GenAI Agent Example ===\n")
    
    # List pods
    response = agent.chat("Show me all pods in the default namespace")
    print(f"🤖 Agent: {response}\n")
    
    # Get cluster info
    response = agent.chat("What's the cluster information?")
    print(f"🤖 Agent: {response}\n")
    
    # Scale deployment example
    response = agent.chat("Scale the nginx deployment to 3 replicas")
    print(f"🤖 Agent: {response}\n")


def direct_tools_example():
    """Example of using K8s tools directly without the agent."""
    print("=== Direct K8s Tools Example ===\n")
    
    try:
        # Initialize tools
        k8s_tools = K8sTools()
        
        # List pods
        result = k8s_tools.execute_tool("list_pods", {"namespace": "default"})
        if result["success"]:
            print("📋 Pods in default namespace:")
            for pod in result["data"]:
                print(f"  - {pod['name']} ({pod['phase']}) - Ready: {pod['ready']}")
        else:
            print(f"❌ Error: {result['error']}")
        
        print()
        
        # List deployments
        result = k8s_tools.execute_tool("list_deployments", {"namespace": "default"})
        if result["success"]:
            print("🚀 Deployments in default namespace:")
            for deploy in result["data"]:
                print(f"  - {deploy['name']} - {deploy['ready_replicas']}/{deploy['replicas']} replicas")
        else:
            print(f"❌ Error: {result['error']}")
        
        print()
        
        # Get cluster info
        result = k8s_tools.execute_tool("get_cluster_info", {})
        if result["success"]:
            print("🏭 Cluster Information:")
            info = result["data"]
            print(f"  - Version: {info['version']['git_version']}")
            print(f"  - Nodes: {info['node_count']}")
            print(f"  - Namespaces: {info['namespace_count']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    except Exception as e:
        print(f"❌ Failed to connect to cluster: {e}")


def client_example():
    """Example of using the K8s client directly."""
    print("=== Direct K8s Client Example ===\n")
    
    try:
        # Initialize client
        client = K8sClient()
        
        # Get namespaces
        namespaces = client.get_namespaces()
        print("📁 Namespaces:")
        for ns in namespaces:
            print(f"  - {ns['name']} ({ns['status']})")
        
        print()
        
        # Get pods with labels
        pods = client.get_pods("default", "app=nginx")
        print("📦 Nginx pods:")
        if pods:
            for pod in pods:
                print(f"  - {pod['name']} on {pod['node']} - {pod['phase']}")
        else:
            print("  No nginx pods found")
    
    except Exception as e:
        print(f"❌ Failed to connect to cluster: {e}")


def interactive_example():
    """Run interactive examples."""
    print("Choose an example to run:")
    print("1. Basic Agent Example (requires OpenAI API key)")
    print("2. Direct Tools Example")
    print("3. Direct Client Example")
    print("4. All examples")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        basic_agent_example()
    elif choice == "2":
        direct_tools_example()
    elif choice == "3":
        client_example()
    elif choice == "4":
        basic_agent_example()
        print("\n" + "="*50 + "\n")
        direct_tools_example()
        print("\n" + "="*50 + "\n")
        client_example()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    interactive_example()
