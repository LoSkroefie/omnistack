from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml
import json
from pathlib import Path

@dataclass
class ResourceRequirement:
    cpu: str
    memory: str
    storage: str
    gpu: Optional[str] = None

@dataclass
class DeploymentConfig:
    service_name: str
    replicas: int
    resources: ResourceRequirement
    environment: Dict[str, str]
    dependencies: List[str]

class DeploymentOptimizer:
    def __init__(self):
        self.supported_platforms = ['kubernetes', 'docker-compose', 'serverless']
        self.resource_profiles = self._load_resource_profiles()

    def optimize_deployment(
        self,
        project_path: str,
        platform: str,
        requirements: Dict
    ) -> Dict:
        """
        Optimize deployment configuration for the given platform.
        
        Args:
            project_path: Path to the project
            platform: Target deployment platform
            requirements: Deployment requirements
            
        Returns:
            Optimized deployment configuration
        """
        if platform not in self.supported_platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Analyze project requirements
        project_analysis = self._analyze_project(project_path)
        
        # Generate optimized configuration
        if platform == 'kubernetes':
            return self._generate_kubernetes_config(
                project_analysis,
                requirements
            )
        elif platform == 'docker-compose':
            return self._generate_docker_compose(
                project_analysis,
                requirements
            )
        else:  # serverless
            return self._generate_serverless_config(
                project_analysis,
                requirements
            )

    def _analyze_project(self, project_path: str) -> Dict:
        """Analyze project structure and requirements."""
        analysis = {
            'services': [],
            'dependencies': [],
            'resource_requirements': {}
        }
        
        project_dir = Path(project_path)
        
        # Detect services
        for dockerfile in project_dir.glob('**/Dockerfile'):
            service_name = dockerfile.parent.name
            analysis['services'].append({
                'name': service_name,
                'dockerfile_path': str(dockerfile),
                'context_path': str(dockerfile.parent)
            })
        
        # Analyze dependencies
        requirements_files = list(project_dir.glob('**/requirements.txt'))
        package_files = list(project_dir.glob('**/package.json'))
        
        for req_file in requirements_files:
            with open(req_file, 'r') as f:
                analysis['dependencies'].extend(f.read().splitlines())
        
        for pkg_file in package_files:
            with open(pkg_file, 'r') as f:
                pkg_data = json.load(f)
                analysis['dependencies'].extend(
                    list(pkg_data.get('dependencies', {}).keys())
                )
        
        return analysis

    def _generate_kubernetes_config(
        self,
        project_analysis: Dict,
        requirements: Dict
    ) -> Dict:
        """Generate optimized Kubernetes configuration."""
        k8s_config = {
            'apiVersion': 'v1',
            'kind': 'List',
            'items': []
        }
        
        for service in project_analysis['services']:
            # Generate deployment
            deployment = {
                'apiVersion': 'apps/v1',
                'kind': 'Deployment',
                'metadata': {
                    'name': service['name']
                },
                'spec': {
                    'replicas': self._calculate_optimal_replicas(
                        service,
                        requirements
                    ),
                    'selector': {
                        'matchLabels': {
                            'app': service['name']
                        }
                    },
                    'template': {
                        'metadata': {
                            'labels': {
                                'app': service['name']
                            }
                        },
                        'spec': {
                            'containers': [{
                                'name': service['name'],
                                'image': f"{service['name']}:latest",
                                'resources': self._calculate_resources(
                                    service,
                                    requirements
                                )
                            }]
                        }
                    }
                }
            }
            
            # Generate service
            service_config = {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {
                    'name': service['name']
                },
                'spec': {
                    'selector': {
                        'app': service['name']
                    },
                    'ports': [{
                        'port': 80,
                        'targetPort': 8000
                    }]
                }
            }
            
            k8s_config['items'].extend([deployment, service_config])
        
        return k8s_config

    def _generate_docker_compose(
        self,
        project_analysis: Dict,
        requirements: Dict
    ) -> Dict:
        """Generate optimized Docker Compose configuration."""
        compose_config = {
            'version': '3.8',
            'services': {}
        }
        
        for service in project_analysis['services']:
            compose_config['services'][service['name']] = {
                'build': {
                    'context': service['context_path'],
                    'dockerfile': service['dockerfile_path']
                },
                'environment': self._generate_environment_vars(service),
                'deploy': {
                    'resources': self._calculate_resources(
                        service,
                        requirements
                    )
                }
            }
        
        return compose_config

    def _generate_serverless_config(
        self,
        project_analysis: Dict,
        requirements: Dict
    ) -> Dict:
        """Generate optimized serverless configuration."""
        serverless_config = {
            'service': project_analysis['services'][0]['name'],
            'provider': {
                'name': 'aws',
                'runtime': 'python3.9',
                'memorySize': self._calculate_lambda_memory(requirements),
                'timeout': 30
            },
            'functions': {}
        }
        
        for service in project_analysis['services']:
            serverless_config['functions'][service['name']] = {
                'handler': f"handler.{service['name']}",
                'events': [{
                    'http': {
                        'path': f"/{service['name']}",
                        'method': 'any'
                    }
                }]
            }
        
        return serverless_config

    def _calculate_optimal_replicas(
        self,
        service: Dict,
        requirements: Dict
    ) -> int:
        """Calculate optimal number of replicas based on requirements."""
        base_replicas = requirements.get('replicas', 1)
        load_factor = requirements.get('load_factor', 1.0)
        return max(1, int(base_replicas * load_factor))

    def _calculate_resources(
        self,
        service: Dict,
        requirements: Dict
    ) -> Dict:
        """Calculate optimal resource allocation."""
        profile = self.resource_profiles.get(
            requirements.get('profile', 'standard'),
            self.resource_profiles['standard']
        )
        
        return {
            'limits': {
                'cpu': profile['cpu'],
                'memory': profile['memory']
            },
            'reservations': {
                'cpu': profile['cpu_min'],
                'memory': profile['memory_min']
            }
        }

    def _calculate_lambda_memory(self, requirements: Dict) -> int:
        """Calculate optimal Lambda memory allocation."""
        base_memory = requirements.get('memory', 128)
        return min(3008, max(128, base_memory))

    def _generate_environment_vars(self, service: Dict) -> Dict:
        """Generate environment variables for service."""
        return {
            'SERVICE_NAME': service['name'],
            'LOG_LEVEL': 'info'
        }

    def _load_resource_profiles(self) -> Dict:
        """Load predefined resource profiles."""
        return {
            'standard': {
                'cpu': '1',
                'cpu_min': '0.5',
                'memory': '1Gi',
                'memory_min': '512Mi'
            },
            'high-performance': {
                'cpu': '2',
                'cpu_min': '1',
                'memory': '2Gi',
                'memory_min': '1Gi'
            },
            'minimal': {
                'cpu': '0.5',
                'cpu_min': '0.25',
                'memory': '512Mi',
                'memory_min': '256Mi'
            }
        }
