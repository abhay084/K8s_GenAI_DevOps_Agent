"""
Kubernetes tools for GenAI Agent - Tool definitions for Kubernetes operations.
"""

import json
from typing import Dict, List, Optional, Any
from k8s_client import K8sClient


class K8sTools:
    """Collection of Kubernetes tools for GenAI agent."""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """Initialize with K8s client."""
        self.k8s_client = K8sClient(kubeconfig_path)
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get all tool definitions for the agent."""
        return [
            {
                "name": "list_pods",
                "description": "List pods in a namespace with optional label selector",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace to list pods from",
                            "default": "default"
                        },
                        "label_selector": {
                            "type": "string",
                            "description": "Label selector to filter pods (e.g., 'app=nginx')"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_deployments",
                "description": "List deployments in a namespace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace to list deployments from",
                            "default": "default"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_services",
                "description": "List services in a namespace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace to list services from",
                            "default": "default"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_namespaces",
                "description": "List all namespaces in the cluster",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "scale_deployment",
                "description": "Scale a deployment to specified number of replicas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the deployment to scale"
                        },
                        "replicas": {
                            "type": "integer",
                            "description": "Number of replicas to scale to"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the deployment",
                            "default": "default"
                        }
                    },
                    "required": ["name", "replicas"]
                }
            },
            {
                "name": "delete_pod",
                "description": "Delete a specific pod",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the pod to delete"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the pod",
                            "default": "default"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_pod_logs",
                "description": "Get logs from a pod",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the pod to get logs from"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the pod",
                            "default": "default"
                        },
                        "tail_lines": {
                            "type": "integer",
                            "description": "Number of log lines to retrieve from the end",
                            "default": 100
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "create_namespace",
                "description": "Create a new namespace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the namespace to create"
                        },
                        "labels": {
                            "type": "object",
                            "description": "Labels to add to the namespace"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "delete_namespace",
                "description": "Delete a namespace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the namespace to delete"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "get_cluster_info",
                "description": "Get cluster information including version and node count",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            # CREATE OPERATIONS
            {
                "name": "create_pod",
                "description": "Create a pod with specified image and configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the pod to create"
                        },
                        "image": {
                            "type": "string",
                            "description": "Container image to use (e.g., 'nginx:alpine', 'httpd:latest')"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace for the pod",
                            "default": "default"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Container port to expose (optional)"
                        },
                        "env_vars": {
                            "type": "object",
                            "description": "Environment variables as key-value pairs (optional)"
                        },
                        "labels": {
                            "type": "object",
                            "description": "Labels to apply to the pod (optional)"
                        }
                    },
                    "required": ["name", "image"]
                }
            },
            {
                "name": "create_deployment",
                "description": "Create a deployment with specified image and replica count",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the deployment to create"
                        },
                        "image": {
                            "type": "string",
                            "description": "Container image to use"
                        },
                        "replicas": {
                            "type": "integer",
                            "description": "Number of replicas",
                            "default": 1
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace for the deployment",
                            "default": "default"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Container port to expose (optional)"
                        },
                        "env_vars": {
                            "type": "object",
                            "description": "Environment variables as key-value pairs (optional)"
                        },
                        "labels": {
                            "type": "object",
                            "description": "Labels to apply to the deployment (optional)"
                        }
                    },
                    "required": ["name", "image"]
                }
            },
            {
                "name": "create_service",
                "description": "Create a service to expose pods or deployments",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the service to create"
                        },
                        "port": {
                            "type": "integer",
                            "description": "Service port"
                        },
                        "target_port": {
                            "type": "integer",
                            "description": "Target port on the pods"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace for the service",
                            "default": "default"
                        },
                        "service_type": {
                            "type": "string",
                            "description": "Service type (ClusterIP, NodePort, LoadBalancer)",
                            "default": "ClusterIP"
                        },
                        "selector": {
                            "type": "object",
                            "description": "Label selector to match pods (optional)"
                        }
                    },
                    "required": ["name", "port", "target_port"]
                }
            },
            {
                "name": "create_configmap",
                "description": "Create a configmap with key-value data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the configmap to create"
                        },
                        "data": {
                            "type": "object",
                            "description": "Configuration data as key-value pairs"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace for the configmap",
                            "default": "default"
                        },
                        "labels": {
                            "type": "object",
                            "description": "Labels to apply to the configmap (optional)"
                        }
                    },
                    "required": ["name", "data"]
                }
            },
            {
                "name": "create_secret",
                "description": "Create a secret with sensitive data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the secret to create"
                        },
                        "data": {
                            "type": "object",
                            "description": "Secret data as key-value pairs"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace for the secret",
                            "default": "default"
                        },
                        "secret_type": {
                            "type": "string",
                            "description": "Secret type",
                            "default": "Opaque"
                        },
                        "labels": {
                            "type": "object",
                            "description": "Labels to apply to the secret (optional)"
                        }
                    },
                    "required": ["name", "data"]
                }
            },
            # READ OPERATIONS (Additional)
            {
                "name": "list_configmaps",
                "description": "List configmaps in a namespace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace to list configmaps from",
                            "default": "default"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_secrets",
                "description": "List secrets in a namespace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace to list secrets from",
                            "default": "default"
                        }
                    },
                    "required": []
                }
            },
            # UPDATE OPERATIONS
            {
                "name": "update_pod_image",
                "description": "Update container image in a pod",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the pod to update"
                        },
                        "container_name": {
                            "type": "string",
                            "description": "Name of the container to update"
                        },
                        "new_image": {
                            "type": "string",
                            "description": "New container image"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the pod",
                            "default": "default"
                        }
                    },
                    "required": ["name", "container_name", "new_image"]
                }
            },
            {
                "name": "update_deployment_image",
                "description": "Update container image in a deployment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the deployment to update"
                        },
                        "container_name": {
                            "type": "string",
                            "description": "Name of the container to update"
                        },
                        "new_image": {
                            "type": "string",
                            "description": "New container image"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the deployment",
                            "default": "default"
                        }
                    },
                    "required": ["name", "container_name", "new_image"]
                }
            },
            {
                "name": "update_configmap",
                "description": "Update configmap data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the configmap to update"
                        },
                        "data": {
                            "type": "object",
                            "description": "New configuration data as key-value pairs"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the configmap",
                            "default": "default"
                        }
                    },
                    "required": ["name", "data"]
                }
            },
            # DELETE OPERATIONS (Additional)
            {
                "name": "delete_deployment",
                "description": "Delete a deployment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the deployment to delete"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the deployment",
                            "default": "default"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "delete_service",
                "description": "Delete a service",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the service to delete"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the service",
                            "default": "default"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "delete_configmap",
                "description": "Delete a configmap",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the configmap to delete"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the configmap",
                            "default": "default"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "delete_secret",
                "description": "Delete a secret",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the secret to delete"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "Kubernetes namespace of the secret",
                            "default": "default"
                        }
                    },
                    "required": ["name"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters."""
        try:
            if tool_name == "list_pods":
                namespace = parameters.get("namespace", "default")
                label_selector = parameters.get("label_selector")
                result = self.k8s_client.get_pods(namespace, label_selector)
                return {"success": True, "data": result}
            
            elif tool_name == "list_deployments":
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.get_deployments(namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "list_services":
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.get_services(namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "list_namespaces":
                result = self.k8s_client.get_namespaces()
                return {"success": True, "data": result}
            
            elif tool_name == "scale_deployment":
                name = parameters["name"]
                replicas = parameters["replicas"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.scale_deployment(name, replicas, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "delete_pod":
                name = parameters["name"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.delete_pod(name, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "get_pod_logs":
                name = parameters["name"]
                namespace = parameters.get("namespace", "default")
                tail_lines = parameters.get("tail_lines", 100)
                result = self.k8s_client.get_pod_logs(name, namespace, tail_lines)
                return {"success": True, "data": {"logs": result}}
            
            elif tool_name == "create_namespace":
                name = parameters["name"]
                labels = parameters.get("labels")
                result = self.k8s_client.create_namespace(name, labels)
                return {"success": True, "data": result}
            
            elif tool_name == "delete_namespace":
                name = parameters["name"]
                result = self.k8s_client.delete_namespace(name)
                return {"success": True, "data": result}
            
            elif tool_name == "get_cluster_info":
                result = self.k8s_client.get_cluster_info()
                return {"success": True, "data": result}
            
            # CREATE OPERATIONS
            elif tool_name == "create_pod":
                name = parameters["name"]
                image = parameters["image"]
                namespace = parameters.get("namespace", "default")
                port = parameters.get("port")
                env_vars = parameters.get("env_vars")
                labels = parameters.get("labels")
                result = self.k8s_client.create_pod(name, image, namespace, port, env_vars, labels)
                return {"success": True, "data": result}
            
            elif tool_name == "create_deployment":
                name = parameters["name"]
                image = parameters["image"]
                replicas = parameters.get("replicas", 1)
                namespace = parameters.get("namespace", "default")
                port = parameters.get("port")
                env_vars = parameters.get("env_vars")
                labels = parameters.get("labels")
                result = self.k8s_client.create_deployment(name, image, replicas, namespace, port, env_vars, labels)
                return {"success": True, "data": result}
            
            elif tool_name == "create_service":
                name = parameters["name"]
                port = parameters["port"]
                target_port = parameters["target_port"]
                namespace = parameters.get("namespace", "default")
                service_type = parameters.get("service_type", "ClusterIP")
                selector = parameters.get("selector")
                result = self.k8s_client.create_service(name, port, target_port, namespace, service_type, selector)
                return {"success": True, "data": result}
            
            elif tool_name == "create_configmap":
                name = parameters["name"]
                data = parameters["data"]
                namespace = parameters.get("namespace", "default")
                labels = parameters.get("labels")
                result = self.k8s_client.create_configmap(name, data, namespace, labels)
                return {"success": True, "data": result}
            
            elif tool_name == "create_secret":
                name = parameters["name"]
                data = parameters["data"]
                namespace = parameters.get("namespace", "default")
                secret_type = parameters.get("secret_type", "Opaque")
                labels = parameters.get("labels")
                result = self.k8s_client.create_secret(name, data, namespace, secret_type, labels)
                return {"success": True, "data": result}
            
            # READ OPERATIONS (Additional)
            elif tool_name == "list_configmaps":
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.get_configmaps(namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "list_secrets":
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.get_secrets(namespace)
                return {"success": True, "data": result}
            
            # UPDATE OPERATIONS
            elif tool_name == "update_pod_image":
                name = parameters["name"]
                container_name = parameters["container_name"]
                new_image = parameters["new_image"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.update_pod_image(name, container_name, new_image, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "update_deployment_image":
                name = parameters["name"]
                container_name = parameters["container_name"]
                new_image = parameters["new_image"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.update_deployment_image(name, container_name, new_image, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "update_configmap":
                name = parameters["name"]
                data = parameters["data"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.update_configmap(name, data, namespace)
                return {"success": True, "data": result}
            
            # DELETE OPERATIONS (Additional)
            elif tool_name == "delete_deployment":
                name = parameters["name"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.delete_deployment(name, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "delete_service":
                name = parameters["name"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.delete_service(name, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "delete_configmap":
                name = parameters["name"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.delete_configmap(name, namespace)
                return {"success": True, "data": result}
            
            elif tool_name == "delete_secret":
                name = parameters["name"]
                namespace = parameters.get("namespace", "default")
                result = self.k8s_client.delete_secret(name, namespace)
                return {"success": True, "data": result}
            
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
