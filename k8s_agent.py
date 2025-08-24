"""
Kubernetes GenAI Agent - Main agent class for Kubernetes operations.
"""

import json
import openai
import os
import re
from typing import Dict, List, Optional, Any, Callable
from k8s_tools import K8sTools


DEFAULT_SYSTEM_PROMPT = """You are a helpful Kubernetes operations assistant. You can help users manage their Kubernetes cluster by:

1. Listing and inspecting resources (pods, deployments, services, namespaces)
2. Scaling deployments up or down
3. Getting pod logs for troubleshooting
4. Creating and deleting namespaces
5. Deleting problematic pods
6. Getting cluster information

Always provide clear, concise responses using plain text formatting. Avoid special characters or complex markdown.
When showing resource information, use simple tables with basic ASCII characters only.
If an operation could be destructive (like deleting resources), ask for confirmation first.
Be proactive in suggesting related operations that might be helpful."""


def load_system_prompt(toml_path: str = "prompt/system_promtp.toml") -> str:
    """Load system prompt from env or TOML file.

    Precedence: os.environ['SYSTEM_PROMPT'] > TOML 'system_prompt' > DEFAULT_SYSTEM_PROMPT.
    """
    # 1) Environment variable takes precedence
    env_prompt = os.getenv("SYSTEM_PROMPT")
    if env_prompt:
        return env_prompt

    # 2) Try to load from TOML file if present
    try:
        if os.path.exists(toml_path):
            with open(toml_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Very simple TOML triple-quote parser for system_prompt
            m = re.search(r"system_prompt\s*=\s*\"\"\"(.*?)\"\"\"", content, re.DOTALL)
            if m:
                return m.group(1).strip()
    except Exception:
        pass

    # 3) Fallback
    return DEFAULT_SYSTEM_PROMPT


class K8sAgent:
    """GenAI Agent for Kubernetes operations using OpenAI's function calling."""
    
    def __init__(self, api_key: str, kubeconfig_path: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the K8s GenAI Agent.
        
        Args:
            api_key: Groq API key
            kubeconfig_path: Path to kubeconfig file
            model: Groq model to use (defaults from env or "openai/gpt-oss-120b")
            base_url: OpenAI-compatible base URL (defaults from env or Groq URL)
        """
        resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
        resolved_model = model or os.getenv("MODEL", "openai/gpt-oss-120b")

        self.client = openai.OpenAI(api_key=api_key, base_url=resolved_base_url)
        self.model = resolved_model
        self.k8s_tools = K8sTools(kubeconfig_path)
        self.conversation_history = []
        
        # System prompt for K8s operations (env > TOML > default)
        self.system_prompt = load_system_prompt()

    def chat(self, user_message: str) -> str:
        """
        Process user message and return response.
        
        Args:
            user_message: User's message/query
            
        Returns:
            Agent's response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Prepare messages for OpenAI
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
        
        try:
            # Get tool definitions
            tools = [
                {
                    "type": "function",
                    "function": tool_def
                }
                for tool_def in self.k8s_tools.get_tool_definitions()
            ]
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Handle function calls
            if response_message.tool_calls:
                # Add assistant's response with function calls to history
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": response_message.content,
                    "tool_calls": response_message.tool_calls
                })
                
                # Execute function calls
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Execute the tool
                    function_result = self.k8s_tools.execute_tool(function_name, function_args)
                    
                    # Add function result to conversation
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(function_result)
                    })
                
                # Get final response from assistant
                messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                final_message = final_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_message})
                
                return final_message
            
            else:
                # No function calls, just return the response
                assistant_message = response_message.content
                self.conversation_history.append({"role": "assistant", "content": assistant_message})
                return assistant_message
                
        except Exception as e:
            error_message = f"Error processing request: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_message})
            return error_message

    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> List[Dict]:
        """Get the current conversation history."""
        return self.conversation_history.copy()

    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        self.system_prompt = prompt


class K8sAgentCLI:
    """Command-line interface for the K8s Agent."""
    
    def __init__(self, api_key: str, kubeconfig_path: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """Initialize CLI with agent."""
        self.agent = K8sAgent(api_key, kubeconfig_path, model=model, base_url=base_url)
        
    def run(self):
        """Run the interactive CLI."""
        print("🤖 Kubernetes GenAI Agent")
        print("=" * 50)
        print("I can help you manage your Kubernetes cluster!")
        print("Type 'quit' or 'exit' to stop, 'reset' to clear conversation history.\n")
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                elif user_input.lower() == 'reset':
                    self.agent.reset_conversation()
                    print("\n🔄 Conversation history cleared!")
                    continue
                elif not user_input:
                    continue
                
                print("\n🤖 Agent: ", end="")
                response = self.agent.chat(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


# Utility functions for direct tool usage
def format_pods_table(pods: List[Dict]) -> str:
    """Format pods list as a simple table."""
    if not pods:
        return "No pods found."
    
    # Header
    output = f"{'NAME':<30} {'READY':<8} {'STATUS':<12} {'RESTARTS':<10} {'AGE':<10} {'NODE':<20}\n"
    output += "-" * 90 + "\n"
    
    # Rows
    for pod in pods:
        name = pod['name'][:29] if len(pod['name']) > 29 else pod['name']
        ready = "Yes" if pod['ready'] else "No"
        status = pod['phase']
        restarts = str(pod['restarts'])
        age = pod['age']
        node = pod['node'][:19] if pod['node'] and len(pod['node']) > 19 else (pod['node'] or 'N/A')
        
        output += f"{name:<30} {ready:<8} {status:<12} {restarts:<10} {age:<10} {node:<20}\n"
    
    return output


def format_deployments_table(deployments: List[Dict]) -> str:
    """Format deployments list as a simple table."""
    if not deployments:
        return "No deployments found."
    
    # Header
    output = f"{'NAME':<30} {'READY':<10} {'UP-TO-DATE':<12} {'AVAILABLE':<12} {'AGE':<10}\n"
    output += "-" * 74 + "\n"
    
    # Rows
    for deploy in deployments:
        name = deploy['name'][:29] if len(deploy['name']) > 29 else deploy['name']
        ready = f"{deploy['ready_replicas']}/{deploy['replicas']}"
        up_to_date = str(deploy['replicas'])
        available = str(deploy['available_replicas'])
        age = deploy['age']
        
        output += f"{name:<30} {ready:<10} {up_to_date:<12} {available:<12} {age:<10}\n"
    
    return output


def load_env(env_path: str = ".env") -> None:
    """Load environment variables from a .env file if present.

    Only sets keys that are not already present in os.environ.
    Lines starting with '#' and blank lines are ignored.
    """
    try:
        if not os.path.exists(env_path):
            return
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Fail quietly; runtime env vars can still be provided externally
        pass


if __name__ == "__main__":
    # Load from .env if available (without overriding existing env)
    load_env()

    # Get API key and configuration from environment
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Please set GROQ_API_KEY environment variable or provide it in .env")
        exit(1)

    kubeconfig_path = os.getenv("KUBECONFIG")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    model = os.getenv("MODEL", "openai/gpt-oss-120b")

    # Run CLI
    cli = K8sAgentCLI(api_key, kubeconfig_path, base_url=base_url, model=model)
    cli.run()
