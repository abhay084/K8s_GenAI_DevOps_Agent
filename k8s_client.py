"""
Kubernetes client wrapper for GenAI Agent - Low-level Kubernetes API operations.
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, List, Optional, Any
import datetime
import base64


class K8sClient:
    """Low-level Kubernetes API wrapper."""
    
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize Kubernetes client.
        
        Args:
            kubeconfig_path: Path to kubeconfig file (optional)
        """
        try:
            if kubeconfig_path:
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                # Try in-cluster config first, then fallback to kubeconfig
                try:
                    config.load_incluster_config()
                except config.ConfigException:
                    config.load_kube_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.version_api = client.VersionApi()
        except Exception as e:
            raise Exception(f"Failed to load Kubernetes config: {e}")
    
    def get_pods(self, namespace: str = "default", label_selector: Optional[str] = None) -> List[Dict]:
        """Get pods from a namespace with optional label selector."""
        try:
            pods = self.v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            
            result = []
            for pod in pods.items:
                # Calculate ready status
                ready = True
                restarts = 0
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        if not container.ready:
                            ready = False
                        restarts += container.restart_count
                
                # Calculate age
                age = self._calculate_age(pod.metadata.creation_timestamp)
                
                result.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "phase": pod.status.phase,
                    "ready": ready,
                    "restarts": restarts,
                    "age": age,
                    "node": pod.spec.node_name,
                    "ip": pod.status.pod_ip
                })
            
            return result
        except ApiException as e:
            raise Exception(f"Error getting pods: {e}")
    
    def get_deployments(self, namespace: str = "default") -> List[Dict]:
        """Get deployments from a namespace."""
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)
            
            result = []
            for deploy in deployments.items:
                age = self._calculate_age(deploy.metadata.creation_timestamp)
                
                result.append({
                    "name": deploy.metadata.name,
                    "namespace": deploy.metadata.namespace,
                    "replicas": deploy.spec.replicas or 0,
                    "ready_replicas": deploy.status.ready_replicas or 0,
                    "available_replicas": deploy.status.available_replicas or 0,
                    "updated_replicas": deploy.status.updated_replicas or 0,
                    "age": age
                })
            
            return result
        except ApiException as e:
            raise Exception(f"Error getting deployments: {e}")
    
    def get_services(self, namespace: str = "default") -> List[Dict]:
        """Get services from a namespace."""
        try:
            services = self.v1.list_namespaced_service(namespace=namespace)
            
            result = []
            for svc in services.items:
                age = self._calculate_age(svc.metadata.creation_timestamp)
                
                # Get external IPs
                external_ips = []
                if svc.status.load_balancer and svc.status.load_balancer.ingress:
                    for ingress in svc.status.load_balancer.ingress:
                        if ingress.ip:
                            external_ips.append(ingress.ip)
                        elif ingress.hostname:
                            external_ips.append(ingress.hostname)
                
                result.append({
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "type": svc.spec.type,
                    "cluster_ip": svc.spec.cluster_ip,
                    "external_ips": external_ips,
                    "ports": [{"port": p.port, "target_port": p.target_port, "protocol": p.protocol} for p in svc.spec.ports or []],
                    "age": age
                })
            
            return result
        except ApiException as e:
            raise Exception(f"Error getting services: {e}")
    
    def get_namespaces(self) -> List[Dict]:
        """Get all namespaces."""
        try:
            namespaces = self.v1.list_namespace()
            
            result = []
            for ns in namespaces.items:
                age = self._calculate_age(ns.metadata.creation_timestamp)
                
                result.append({
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "age": age,
                    "labels": ns.metadata.labels or {}
                })
            
            return result
        except ApiException as e:
            raise Exception(f"Error getting namespaces: {e}")
    
    def scale_deployment(self, name: str, replicas: int, namespace: str = "default") -> Dict:
        """Scale a deployment to specified replicas."""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            # Update replica count
            deployment.spec.replicas = replicas
            
            # Patch the deployment
            self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=deployment
            )
            
            return {
                "name": name,
                "namespace": namespace,
                "replicas": replicas,
                "message": f"Deployment {name} scaled to {replicas} replicas"
            }
        except ApiException as e:
            raise Exception(f"Error scaling deployment: {e}")
    
    def delete_pod(self, name: str, namespace: str = "default") -> Dict:
        """Delete a pod."""
        try:
            self.v1.delete_namespaced_pod(name=name, namespace=namespace)
            
            return {
                "name": name,
                "namespace": namespace,
                "message": f"Pod {name} deleted successfully"
            }
        except ApiException as e:
            raise Exception(f"Error deleting pod: {e}")
    
    def get_pod_logs(self, name: str, namespace: str = "default", tail_lines: int = 100) -> str:
        """Get logs from a pod."""
        try:
            logs = self.v1.read_namespaced_pod_log(
                name=name,
                namespace=namespace,
                tail_lines=tail_lines
            )
            return logs
        except ApiException as e:
            raise Exception(f"Error getting pod logs: {e}")
    
    def create_namespace(self, name: str, labels: Optional[Dict] = None) -> Dict:
        """Create a new namespace."""
        try:
            namespace_body = client.V1Namespace(
                metadata=client.V1ObjectMeta(
                    name=name,
                    labels=labels or {}
                )
            )
            
            self.v1.create_namespace(body=namespace_body)
            
            return {
                "name": name,
                "labels": labels or {},
                "message": f"Namespace {name} created successfully"
            }
        except ApiException as e:
            raise Exception(f"Error creating namespace: {e}")
    
    def delete_namespace(self, name: str) -> Dict:
        """Delete a namespace."""
        try:
            self.v1.delete_namespace(name=name)
            
            return {
                "name": name,
                "message": f"Namespace {name} deleted successfully"
            }
        except ApiException as e:
            raise Exception(f"Error deleting namespace: {e}")
    
    def get_cluster_info(self) -> Dict:
        """Get cluster information."""
        try:
            # Get version info
            version_info = self.version_api.get_code()
            
            # Get node count
            nodes = self.v1.list_node()
            node_count = len(nodes.items)
            
            # Get namespace count
            namespaces = self.v1.list_namespace()
            namespace_count = len(namespaces.items)
            
            return {
                "version": {
                    "git_version": version_info.git_version,
                    "major": version_info.major,
                    "minor": version_info.minor,
                    "platform": version_info.platform
                },
                "node_count": node_count,
                "namespace_count": namespace_count,
                "nodes": [{"name": node.metadata.name, "status": self._get_node_status(node)} for node in nodes.items]
            }
        except ApiException as e:
            raise Exception(f"Error getting cluster info: {e}")
    
    def _calculate_age(self, creation_timestamp) -> str:
        """Calculate age from creation timestamp."""
        if not creation_timestamp:
            return "Unknown"
        
        now = datetime.datetime.now(datetime.timezone.utc)
        age = now - creation_timestamp
        
        if age.days > 0:
            return f"{age.days}d"
        elif age.seconds > 3600:
            return f"{age.seconds // 3600}h"
        elif age.seconds > 60:
            return f"{age.seconds // 60}m"
        else:
            return f"{age.seconds}s"
    
    def _get_node_status(self, node) -> str:
        """Get node status from conditions."""
        if not node.status.conditions:
            return "Unknown"
        
        for condition in node.status.conditions:
            if condition.type == "Ready":
                return "Ready" if condition.status == "True" else "NotReady"
        
        return "Unknown"
    
    # ====== CREATE OPERATIONS ======
    
    def create_pod(self, name: str, image: str, namespace: str = "default", 
                   port: Optional[int] = None, env_vars: Optional[Dict] = None,
                   labels: Optional[Dict] = None) -> Dict:
        """Create a pod."""
        try:
            container = client.V1Container(
                name=name,
                image=image,
                ports=[client.V1ContainerPort(container_port=port)] if port else None,
                env=[client.V1EnvVar(name=k, value=v) for k, v in (env_vars or {}).items()]
            )
            
            pod_spec = client.V1PodSpec(containers=[container])
            
            pod = client.V1Pod(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels or {}
                ),
                spec=pod_spec
            )
            
            self.v1.create_namespaced_pod(namespace=namespace, body=pod)
            
            return {
                "name": name,
                "namespace": namespace,
                "image": image,
                "message": f"Pod {name} created successfully"
            }
        except ApiException as e:
            raise Exception(f"Error creating pod: {e}")
    
    def create_deployment(self, name: str, image: str, replicas: int = 1, 
                         namespace: str = "default", port: Optional[int] = None,
                         env_vars: Optional[Dict] = None, labels: Optional[Dict] = None) -> Dict:
        """Create a deployment."""
        try:
            labels = labels or {"app": name}
            
            container = client.V1Container(
                name=name,
                image=image,
                ports=[client.V1ContainerPort(container_port=port)] if port else None,
                env=[client.V1EnvVar(name=k, value=v) for k, v in (env_vars or {}).items()]
            )
            
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels),
                spec=client.V1PodSpec(containers=[container])
            )
            
            spec = client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels=labels),
                template=template
            )
            
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                spec=spec
            )
            
            self.apps_v1.create_namespaced_deployment(namespace=namespace, body=deployment)
            
            return {
                "name": name,
                "namespace": namespace,
                "replicas": replicas,
                "image": image,
                "message": f"Deployment {name} created successfully"
            }
        except ApiException as e:
            raise Exception(f"Error creating deployment: {e}")
    
    def create_service(self, name: str, port: int, target_port: int, 
                      namespace: str = "default", service_type: str = "ClusterIP",
                      selector: Optional[Dict] = None) -> Dict:
        """Create a service."""
        try:
            selector = selector or {"app": name}
            
            service = client.V1Service(
                metadata=client.V1ObjectMeta(name=name, namespace=namespace),
                spec=client.V1ServiceSpec(
                    selector=selector,
                    ports=[client.V1ServicePort(
                        port=port,
                        target_port=target_port,
                        protocol="TCP"
                    )],
                    type=service_type
                )
            )
            
            self.v1.create_namespaced_service(namespace=namespace, body=service)
            
            return {
                "name": name,
                "namespace": namespace,
                "port": port,
                "type": service_type,
                "message": f"Service {name} created successfully"
            }
        except ApiException as e:
            raise Exception(f"Error creating service: {e}")
    
    def create_configmap(self, name: str, data: Dict[str, str], 
                        namespace: str = "default", labels: Optional[Dict] = None) -> Dict:
        """Create a configmap."""
        try:
            configmap = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels or {}
                ),
                data=data
            )
            
            self.v1.create_namespaced_config_map(namespace=namespace, body=configmap)
            
            return {
                "name": name,
                "namespace": namespace,
                "data_keys": list(data.keys()),
                "message": f"ConfigMap {name} created successfully"
            }
        except ApiException as e:
            raise Exception(f"Error creating configmap: {e}")
    
    def create_secret(self, name: str, data: Dict[str, str], 
                     namespace: str = "default", secret_type: str = "Opaque",
                     labels: Optional[Dict] = None) -> Dict:
        """Create a secret."""
        try:
            import base64
            
            # Encode data in base64
            encoded_data = {k: base64.b64encode(v.encode()).decode() for k, v in data.items()}
            
            secret = client.V1Secret(
                metadata=client.V1ObjectMeta(
                    name=name,
                    namespace=namespace,
                    labels=labels or {}
                ),
                type=secret_type,
                data=encoded_data
            )
            
            self.v1.create_namespaced_secret(namespace=namespace, body=secret)
            
            return {
                "name": name,
                "namespace": namespace,
                "type": secret_type,
                "data_keys": list(data.keys()),
                "message": f"Secret {name} created successfully"
            }
        except ApiException as e:
            raise Exception(f"Error creating secret: {e}")
    
    # ====== READ OPERATIONS (Additional) ======
    
    def get_configmaps(self, namespace: str = "default") -> List[Dict]:
        """Get configmaps from a namespace."""
        try:
            configmaps = self.v1.list_namespaced_config_map(namespace=namespace)
            
            result = []
            for cm in configmaps.items:
                age = self._calculate_age(cm.metadata.creation_timestamp)
                
                result.append({
                    "name": cm.metadata.name,
                    "namespace": cm.metadata.namespace,
                    "data_count": len(cm.data or {}),
                    "data_keys": list((cm.data or {}).keys()),
                    "age": age
                })
            
            return result
        except ApiException as e:
            raise Exception(f"Error getting configmaps: {e}")
    
    def get_secrets(self, namespace: str = "default") -> List[Dict]:
        """Get secrets from a namespace."""
        try:
            secrets = self.v1.list_namespaced_secret(namespace=namespace)
            
            result = []
            for secret in secrets.items:
                age = self._calculate_age(secret.metadata.creation_timestamp)
                
                result.append({
                    "name": secret.metadata.name,
                    "namespace": secret.metadata.namespace,
                    "type": secret.type,
                    "data_count": len(secret.data or {}),
                    "data_keys": list((secret.data or {}).keys()),
                    "age": age
                })
            
            return result
        except ApiException as e:
            raise Exception(f"Error getting secrets: {e}")
    
    # ====== UPDATE OPERATIONS ======
    
    def update_pod_image(self, name: str, container_name: str, new_image: str, 
                        namespace: str = "default") -> Dict:
        """Update pod container image."""
        try:
            pod = self.v1.read_namespaced_pod(name=name, namespace=namespace)
            
            for container in pod.spec.containers:
                if container.name == container_name:
                    container.image = new_image
                    break
            else:
                raise Exception(f"Container {container_name} not found in pod {name}")
            
            self.v1.patch_namespaced_pod(name=name, namespace=namespace, body=pod)
            
            return {
                "name": name,
                "namespace": namespace,
                "container": container_name,
                "new_image": new_image,
                "message": f"Pod {name} container {container_name} updated to {new_image}"
            }
        except ApiException as e:
            raise Exception(f"Error updating pod: {e}")
    
    def update_deployment_image(self, name: str, container_name: str, new_image: str,
                               namespace: str = "default") -> Dict:
        """Update deployment container image."""
        try:
            deployment = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            
            for container in deployment.spec.template.spec.containers:
                if container.name == container_name:
                    container.image = new_image
                    break
            else:
                raise Exception(f"Container {container_name} not found in deployment {name}")
            
            self.apps_v1.patch_namespaced_deployment(name=name, namespace=namespace, body=deployment)
            
            return {
                "name": name,
                "namespace": namespace, 
                "container": container_name,
                "new_image": new_image,
                "message": f"Deployment {name} container {container_name} updated to {new_image}"
            }
        except ApiException as e:
            raise Exception(f"Error updating deployment: {e}")
    
    def update_configmap(self, name: str, data: Dict[str, str], 
                        namespace: str = "default") -> Dict:
        """Update configmap data."""
        try:
            configmap = self.v1.read_namespaced_config_map(name=name, namespace=namespace)
            configmap.data = data
            
            self.v1.patch_namespaced_config_map(name=name, namespace=namespace, body=configmap)
            
            return {
                "name": name,
                "namespace": namespace,
                "data_keys": list(data.keys()),
                "message": f"ConfigMap {name} updated successfully"
            }
        except ApiException as e:
            raise Exception(f"Error updating configmap: {e}")
    
    # ====== DELETE OPERATIONS (Additional) ======
    
    def delete_deployment(self, name: str, namespace: str = "default") -> Dict:
        """Delete a deployment."""
        try:
            self.apps_v1.delete_namespaced_deployment(name=name, namespace=namespace)
            
            return {
                "name": name,
                "namespace": namespace,
                "message": f"Deployment {name} deleted successfully"
            }
        except ApiException as e:
            raise Exception(f"Error deleting deployment: {e}")
    
    def delete_service(self, name: str, namespace: str = "default") -> Dict:
        """Delete a service."""
        try:
            self.v1.delete_namespaced_service(name=name, namespace=namespace)
            
            return {
                "name": name,
                "namespace": namespace,
                "message": f"Service {name} deleted successfully"
            }
        except ApiException as e:
            raise Exception(f"Error deleting service: {e}")
    
    def delete_configmap(self, name: str, namespace: str = "default") -> Dict:
        """Delete a configmap."""
        try:
            self.v1.delete_namespaced_config_map(name=name, namespace=namespace)
            
            return {
                "name": name,
                "namespace": namespace,
                "message": f"ConfigMap {name} deleted successfully"
            }
        except ApiException as e:
            raise Exception(f"Error deleting configmap: {e}")
    
    def delete_secret(self, name: str, namespace: str = "default") -> Dict:
        """Delete a secret."""
        try:
            self.v1.delete_namespaced_secret(name=name, namespace=namespace)
            
            return {
                "name": name,
                "namespace": namespace,
                "message": f"Secret {name} deleted successfully"
            }
        except ApiException as e:
            raise Exception(f"Error deleting secret: {e}")
