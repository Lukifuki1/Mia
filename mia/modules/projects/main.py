#!/usr/bin/env python3
"""
MIA Project Management System
Handles project creation, management, and execution
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ProjectType(Enum):
    """Project types"""
    WEB_APP = "web_app"
    API = "api"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    DATA_SCIENCE = "data_science"
    AI_ML = "ai_ml"
    GAME = "game"
    LIBRARY = "library"
    SCRIPT = "script"
    OTHER = "other"

class ProjectStatus(Enum):
    """Project status"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

@dataclass
class ProjectConfig:
    """Project configuration"""
    name: str
    description: str
    project_type: ProjectType
    technologies: List[str]
    requirements: List[str]
    output_directory: str
    status: ProjectStatus = ProjectStatus.PLANNING
    created_at: datetime = None
    updated_at: datetime = None

class MIAProjectManager:
    """MIA Project Management System"""
    
    def __init__(self):
        self.logger = logging.getLogger("MIA.Projects")
        self.projects_dir = Path("mia/data/projects")
        self.templates_dir = Path("mia/templates/projects")
        self.active_projects: Dict[str, ProjectConfig] = {}
        
        # Create directories
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing projects
        self._load_projects()
        
        # Initialize templates
        self._initialize_templates()
    
    def get_status(self) -> Dict[str, Any]:
        """Get project manager status"""
        return {
            "active_projects": len(self.active_projects),
            "projects_directory": str(self.projects_dir),
            "templates_directory": str(self.templates_dir),
            "supported_types": [pt.value for pt in ProjectType],
            "project_list": list(self.active_projects.keys())
        }
    
    def _load_projects(self):
        """Load existing projects"""
        try:
            projects_file = self.projects_dir / "projects.json"
            if projects_file.exists():
                with open(projects_file, 'r') as f:
                    projects_data = json.load(f)
                
                for project_name, project_data in projects_data.items():
                    config = ProjectConfig(
                        name=project_data["name"],
                        description=project_data["description"],
                        project_type=ProjectType(project_data["project_type"]),
                        technologies=project_data["technologies"],
                        requirements=project_data["requirements"],
                        output_directory=project_data["output_directory"],
                        status=ProjectStatus(project_data["status"]),
                        created_at=datetime.fromisoformat(project_data["created_at"]) if project_data.get("created_at") else datetime.now(),
                        updated_at=datetime.fromisoformat(project_data["updated_at"]) if project_data.get("updated_at") else datetime.now()
                    )
                    self.active_projects[project_name] = config
                    
                self.logger.info(f"Loaded {len(self.active_projects)} existing projects")
        except Exception as e:
            self.logger.error(f"Failed to load projects: {e}")
    
    def _save_projects(self):
        """Save projects to file"""
        try:
            projects_data = {}
            for project_name, config in self.active_projects.items():
                projects_data[project_name] = {
                    "name": config.name,
                    "description": config.description,
                    "project_type": config.project_type.value,
                    "technologies": config.technologies,
                    "requirements": config.requirements,
                    "output_directory": config.output_directory,
                    "status": config.status.value,
                    "created_at": config.created_at.isoformat() if config.created_at else datetime.now().isoformat(),
                    "updated_at": config.updated_at.isoformat() if config.updated_at else datetime.now().isoformat()
                }
            
            projects_file = self.projects_dir / "projects.json"
            with open(projects_file, 'w') as f:
                json.dump(projects_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save projects: {e}")
    
    def _initialize_templates(self):
        """Initialize project templates"""
        templates = {
            "web_app": {
                "structure": [
                    "src/",
                    "src/components/",
                    "src/pages/",
                    "src/styles/",
                    "public/",
                    "tests/",
                    "docs/"
                ],
                "files": {
                    "package.json": '{\n  "name": "{{project_name}}",\n  "version": "1.0.0",\n  "description": "{{description}}",\n  "main": "src/index.js",\n  "scripts": {\n    "start": "react-scripts start",\n    "build": "react-scripts build",\n    "test": "react-scripts test"\n  }\n}',
                    "README.md": "# {{project_name}}\n\n{{description}}\n\n## Installation\n\n```bash\nnpm install\nnpm start\n```",
                    "src/index.js": 'import React from "react";\nimport ReactDOM from "react-dom";\nimport App from "./App";\n\nReactDOM.render(<App />, document.getElementById("root"));'
                }
            },
            "api": {
                "structure": [
                    "src/",
                    "src/routes/",
                    "src/models/",
                    "src/middleware/",
                    "tests/",
                    "docs/"
                ],
                "files": {
                    "requirements.txt": "fastapi\nuvicorn\npydantic\nsqlalchemy\nalembic",
                    "main.py": 'from fastapi import FastAPI\n\napp = FastAPI(title="{{project_name}}", description="{{description}}")\n\n@app.get("/")\ndef read_root():\n    return {"message": "Hello from {{project_name}}"}',
                    "README.md": "# {{project_name}} API\n\n{{description}}\n\n## Installation\n\n```bash\npip install -r requirements.txt\nuvicorn main:app --reload\n```"
                }
            },
            "script": {
                "structure": [
                    "src/",
                    "tests/",
                    "docs/"
                ],
                "files": {
                    "main.py": '#!/usr/bin/env python3\n"""\n{{project_name}}\n{{description}}\n"""\n\ndef main():\n    print("Hello from {{project_name}}")\n\nif __name__ == "__main__":\n    main()',
                    "requirements.txt": "# Add your dependencies here",
                    "README.md": "# {{project_name}}\n\n{{description}}\n\n## Usage\n\n```bash\npython main.py\n```"
                }
            }
        }
        
        for template_name, template_data in templates.items():
            template_dir = self.templates_dir / template_name
            template_dir.mkdir(exist_ok=True)
            
            # Save template configuration
            config_file = template_dir / "template.json"
            with open(config_file, 'w') as f:
                json.dump(template_data, f, indent=2)
    
    async def create_project(self, name: str, description: str, project_type: ProjectType, 
                           technologies: List[str] = None, requirements: List[str] = None,
                           output_directory: str = None) -> bool:
        """Create a new project"""
        try:
            if technologies is None:
                technologies = []
            if requirements is None:
                requirements = []
            if output_directory is None:
                output_directory = f"projects/{name}"
            
            # Create project configuration
            config = ProjectConfig(
                name=name,
                description=description,
                project_type=project_type,
                technologies=technologies,
                requirements=requirements,
                output_directory=output_directory,
                status=ProjectStatus.PLANNING,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Create project directory
            project_path = Path(output_directory)
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Apply template if available
            await self._apply_template(config, project_path)
            
            # Save project
            self.active_projects[name] = config
            self._save_projects()
            
            self.logger.info(f"Created project: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create project {name}: {e}")
            return False
    
    async def _apply_template(self, config: ProjectConfig, project_path: Path):
        """Apply project template"""
        try:
            template_dir = self.templates_dir / config.project_type.value
            template_file = template_dir / "template.json"
            
            if not template_file.exists():
                self.logger.warning(f"No template found for {config.project_type.value}")
                return
            
            with open(template_file, 'r') as f:
                template_data = json.load(f)
            
            # Create directory structure
            for directory in template_data.get("structure", []):
                (project_path / directory).mkdir(parents=True, exist_ok=True)
            
            # Create files from template
            for file_path, content in template_data.get("files", {}).items():
                # Replace template variables
                content = content.replace("{{project_name}}", config.name)
                content = content.replace("{{description}}", config.description)
                
                file_full_path = project_path / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_full_path, 'w') as f:
                    f.write(content)
            
            self.logger.info(f"Applied template for {config.project_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply template: {e}")
    
    async def update_project_status(self, name: str, status: ProjectStatus) -> bool:
        """Update project status"""
        try:
            if name in self.active_projects:
                self.active_projects[name].status = status
                self.active_projects[name].updated_at = datetime.now()
                self._save_projects()
                self.logger.info(f"Updated project {name} status to {status.value}")
                return True
            else:
                self.logger.error(f"Project {name} not found")
                return False
        except Exception as e:
            self.logger.error(f"Failed to update project status: {e}")
            return False
    
    async def execute_project_command(self, name: str, command: str) -> Dict[str, Any]:
        """Execute command in project directory"""
        try:
            if name not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            config = self.active_projects[name]
            project_path = Path(config.output_directory)
            
            if not project_path.exists():
                return {"success": False, "error": "Project directory not found"}
            
            # Execute command
            result = subprocess.run(
                command,
                shell=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_project_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get project information"""
        if name in self.active_projects:
            config = self.active_projects[name]
            return {
                "name": config.name,
                "description": config.description,
                "type": config.project_type.value,
                "technologies": config.technologies,
                "requirements": config.requirements,
                "output_directory": config.output_directory,
                "status": config.status.value,
                "created_at": config.created_at.isoformat() if config.created_at else None,
                "updated_at": config.updated_at.isoformat() if config.updated_at else None
            }
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        projects = []
        for name, config in self.active_projects.items():
            projects.append({
                "name": config.name,
                "description": config.description,
                "type": config.project_type.value,
                "status": config.status.value,
                "created_at": config.created_at.isoformat() if config.created_at else None
            })
        return projects
    
    async def delete_project(self, name: str, delete_files: bool = False) -> bool:
        """Delete project"""
        try:
            if name not in self.active_projects:
                return False
            
            config = self.active_projects[name]
            
            # Optionally delete project files
            if delete_files:
                project_path = Path(config.output_directory)
                if project_path.exists():
                    import shutil
                    shutil.rmtree(project_path)
            
            # Remove from active projects
            del self.active_projects[name]
            self._save_projects()
            
            self.logger.info(f"Deleted project: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete project {name}: {e}")
            return False

# Global project manager instance
project_manager = MIAProjectManager()

async def create_project(name: str, description: str, project_type: str, 
                        technologies: List[str] = None, requirements: List[str] = None) -> bool:
    """Global function to create project"""
    try:
        pt = ProjectType(project_type)
        return await project_manager.create_project(name, description, pt, technologies, requirements)
    except ValueError:
        return False

def get_project_manager_status() -> Dict[str, Any]:
    """Get project manager status"""
    return project_manager.get_status()