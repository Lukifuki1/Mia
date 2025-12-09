#!/usr/bin/env python3
"""
MIA Enterprise Project Builder
==============================

Modularized project builder using dedicated project builder modules.
"""

import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modularized project builder components
from mia.project_builder import (
    ProjectGenerator,
    TemplateManager,
    BuildSystem,
    DeploymentManager
)
from mia.project_builder.project_generator import ProjectConfig, ProjectType, TechStack


class EnterpriseProjectBuilder:
    """Modularized enterprise project builder system"""
    
    def __init__(self, workspace_dir: str = "./generated_projects"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logging()
        
        # Initialize modular project builder components
        self.project_generator = ProjectGenerator(workspace_dir)
        self.template_manager = TemplateManager()
        self.build_system = BuildSystem()
        self.deployment_manager = DeploymentManager()
        
        # Project management
        self.projects = {}
        
        self.logger.info("🏗️ Modularized Enterprise Project Builder initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger("MIA.ProjectBuilder.EnterpriseProjectBuilder")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_deterministic_time(self) -> float:
        """Return deterministic time for testing"""
        return 1640995200.0  # Fixed timestamp: 2022-01-01 00:00:00 UTC
    
    def create_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete project using modular components"""
        try:
            self.logger.info(f"🏗️ Creating project: {project_config.get('name', 'Unknown')}")
            
            # Convert config to ProjectConfig
            config = ProjectConfig(
                name=project_config.get("name", "new-project"),
                description=project_config.get("description", "Generated project"),
                project_type=ProjectType(project_config.get("project_type", "web_app")),
                tech_stack=TechStack(project_config.get("tech_stack", "python_fastapi")),
                author=project_config.get("author", "MIA Enterprise"),
                version=project_config.get("version", "0.1.0"),
                license=project_config.get("license", "MIT"),
                include_tests=project_config.get("include_tests", True),
                include_docs=project_config.get("include_docs", True),
                include_ci_cd=project_config.get("include_ci_cd", True),
                include_docker=project_config.get("include_docker", True),
                database=project_config.get("database"),
                features=project_config.get("features", [])
            )
            
            # Generate project using ProjectGenerator
            generation_result = self.project_generator.generate_project(config)
            
            if not generation_result.get("success", False):
                return generation_result
            
            # Store project info
            project_id = f"{config.name}_{int(self._get_deterministic_time())}"
            self.projects[project_id] = {
                "config": project_config,
                "generation_result": generation_result,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "project_id": project_id,
                "success": True,
                "project_path": generation_result["project_path"],
                "generation_result": generation_result
            }
            
        except Exception as e:
            self.logger.error(f"Project creation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def build_project(self, project_id: str, build_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build a project using BuildSystem"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project not found: {project_id}")
            
            project_info = self.projects[project_id]
            project_path = project_info["generation_result"]["project_path"]
            
            # Build project using BuildSystem
            build_result = self.build_system.build_project(project_path, build_config)
            
            # Update project info
            project_info["build_result"] = build_result
            project_info["last_build"] = datetime.now().isoformat()
            
            return build_result
            
        except Exception as e:
            self.logger.error(f"Project build error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def deploy_project(self, project_id: str, deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a project using DeploymentManager"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project not found: {project_id}")
            
            project_info = self.projects[project_id]
            project_path = project_info["generation_result"]["project_path"]
            
            # Deploy project using DeploymentManager
            deployment_result = self.deployment_manager.deploy_project(project_path, deployment_config)
            
            # Update project info
            project_info["deployment_result"] = deployment_result
            project_info["last_deployment"] = datetime.now().isoformat()
            
            return deployment_result
            
        except Exception as e:
            self.logger.error(f"Project deployment error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_templates(self) -> Dict[str, List[str]]:
        """Get available project templates"""
        return self.template_manager.list_templates()
    
    def create_custom_template(self, template_name: str, template_data: Dict[str, Any]) -> bool:
        """Create a custom project template"""
        return self.template_manager.create_custom_template(template_name, template_data)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all created projects"""
        return [
            {
                "project_id": project_id,
                "name": info["config"]["name"],
                "created_at": info["created_at"],
                "status": "deployed" if "deployment_result" in info else "built" if "build_result" in info else "created"
            }
            for project_id, info in self.projects.items()
        ]
    
    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed project information"""
        return self.projects.get(project_id)
    
    def generate_project_report(self, project_id: str) -> Dict[str, Any]:
        """Generate comprehensive project report"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"Project not found: {project_id}")
            
            project_info = self.projects[project_id]
            
            report = {
                "project_id": project_id,
                "report_timestamp": datetime.now().isoformat(),
                "project_config": project_info["config"],
                "generation_summary": {
                    "success": project_info["generation_result"].get("success", False),
                    "files_generated": len(project_info["generation_result"].get("generated_files", [])),
                    "project_path": project_info["generation_result"].get("project_path")
                },
                "build_summary": {},
                "deployment_summary": {},
                "recommendations": []
            }
            
            # Add build summary if available
            if "build_result" in project_info:
                build_result = project_info["build_result"]
                report["build_summary"] = {
                    "success": build_result.get("success", False),
                    "build_steps": len(build_result.get("build_steps", [])),
                    "artifacts": build_result.get("artifacts", [])
                }
            
            # Add deployment summary if available
            if "deployment_result" in project_info:
                deployment_result = project_info["deployment_result"]
                report["deployment_summary"] = {
                    "success": deployment_result.get("success", False),
                    "deployment_url": deployment_result.get("deployment_url"),
                    "deployment_id": deployment_result.get("deployment_id")
                }
            
            # Generate recommendations
            report["recommendations"] = self._generate_project_recommendations(project_info)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Project report generation error: {e}")
            return {
                "project_id": project_id,
                "error": str(e),
                "report_timestamp": datetime.now().isoformat()
            }
    
    def _generate_project_recommendations(self, project_info: Dict[str, Any]) -> List[str]:
        """Generate project recommendations"""
        recommendations = []
        
        config = project_info["config"]
        
        # Check for missing features
        if not config.get("include_tests", True):
            recommendations.append("Add comprehensive test suite")
        
        if not config.get("include_docs", True):
            recommendations.append("Add project documentation")
        
        if not config.get("include_ci_cd", True):
            recommendations.append("Set up CI/CD pipeline")
        
        if not config.get("include_docker", True):
            recommendations.append("Add Docker containerization")
        
        # Check build status
        if "build_result" in project_info:
            build_result = project_info["build_result"]
            if not build_result.get("success", False):
                recommendations.append("Fix build issues")
        else:
            recommendations.append("Build the project")
        
        # Check deployment status
        if "deployment_result" not in project_info:
            recommendations.append("Deploy the project")
        
        # General recommendations
        recommendations.extend([
            "Implement security best practices",
            "Add monitoring and logging",
            "Set up automated backups",
            "Consider performance optimization"
        ])
        
        return recommendations


def main():
    """Main execution function"""
    print("🏗️ MIA Enterprise Project Builder")
    print("=" * 50)
    
    builder = EnterpriseProjectBuilder()
    
    # Example project creation
    project_config = {
        "name": "sample-api",
        "description": "Sample FastAPI application",
        "project_type": "api_service",
        "tech_stack": "python_fastapi",
        "author": "MIA Enterprise",
        "include_tests": True,
        "include_docs": True,
        "include_ci_cd": True,
        "include_docker": True
    }
    
    # Create project
    result = builder.create_project(project_config)
    
    if result.get("success", False):
        project_id = result["project_id"]
        print(f"\n✅ Project created successfully!")
        print(f"Project ID: {project_id}")
        print(f"Project Path: {result['project_path']}")
        
        # List available templates
        templates = builder.get_project_templates()
        print(f"\n📋 Available Templates:")
        print(f"Built-in: {', '.join(templates['builtin'])}")
        print(f"Custom: {', '.join(templates['custom'])}")
        
        # Generate report
        report = builder.generate_project_report(project_id)
        print(f"\n📊 PROJECT REPORT:")
        print(f"Files Generated: {report['generation_summary']['files_generated']}")
        
        recommendations = report.get("recommendations", [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"  {i}. {rec}")
    else:
        print(f"❌ Project creation failed: {result.get('error', 'Unknown error')}")
    
    return result


if __name__ == "__main__":
    main()
