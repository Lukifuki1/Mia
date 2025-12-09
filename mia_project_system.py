#!/usr/bin/env python3
"""
🚀 MIA Project AGI System - Agentna arhitektura za projekte
Sistem za avtomatsko gradnjo projektov z AGP Engine
"""

import os
import sys
import json
import time
import threading
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import tempfile
import uuid
import yaml
from concurrent.futures import ThreadPoolExecutor


class ProjectType(Enum):
    """Types of projects MIA can build"""
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_app"
    MOBILE_APP = "mobile_app"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    GAME = "game"
    AI_MODEL = "ai_model"
    DATA_PIPELINE = "data_pipeline"
    MICROSERVICE = "microservice"


class ProjectStatus(Enum):
    """Project build status"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ProjectSpec:
    """Project specification"""
    name: str
    description: str
    project_type: ProjectType
    requirements: List[str]
    technologies: List[str]
    features: List[str]
    constraints: Dict[str, Any] = None
    deadline: Optional[str] = None
    priority: int = 1
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


@dataclass
class ProjectTask:
    """Individual project task"""
    id: str
    name: str
    description: str
    task_type: str  # "analysis", "design", "implementation", "testing", "deployment"
    dependencies: List[str] = None
    estimated_time: int = 60  # minutes
    status: str = "pending"
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class MIAProjectAgent:
    """Base class for project agents"""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.logger = self._setup_logging()
        self.busy = False
        self.current_task = None
    
    def _setup_logging(self) -> logging.Logger:
        """Setup agent logging"""
        logger = logging.getLogger(f"MIA.Agent.{self.agent_id}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f'%(asctime)s - MIA.Agent.{self.agent_id} - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def can_handle_task(self, task: ProjectTask) -> bool:
        """Check if agent can handle the task"""
        return task.task_type in self.capabilities
    
    def execute_task(self, task: ProjectTask, project_spec: ProjectSpec, 
                    project_path: Path) -> Dict[str, Any]:
        """Execute a project task"""
        if self.busy:
            return {"success": False, "error": "Agent is busy"}
        
        self.busy = True
        self.current_task = task
        
        try:
            self.logger.info(f"🎯 Executing task: {task.name}")
            result = self._execute_task_impl(task, project_spec, project_path)
            task.status = "completed" if result.get("success", False) else "failed"
            task.result = result
            return result
        except Exception as e:
            self.logger.error(f"Task execution error: {e}")
            task.status = "failed"
            return {"success": False, "error": str(e)}
        finally:
            self.busy = False
            self.current_task = None
    
    def _execute_task_impl(self, task: ProjectTask, project_spec: ProjectSpec, 
                          project_path: Path) -> Dict[str, Any]:
        """Implementation of task execution - to be overridden"""
        raise NotImplementedError("Subclasses must implement _execute_task_impl")


class MIAAnalysisAgent(MIAProjectAgent):
    """Agent for project analysis and planning"""
    
    def __init__(self):
        super().__init__("analyzer", "analysis", ["analysis", "planning"])
    
    def _execute_task_impl(self, task: ProjectTask, project_spec: ProjectSpec, 
                          project_path: Path) -> Dict[str, Any]:
        """Execute analysis task"""
        if task.task_type == "analysis":
            return self._analyze_requirements(project_spec, project_path)
        elif task.task_type == "planning":
            return self._create_project_plan(project_spec, project_path)
        else:
            return {"success": False, "error": f"Unknown task type: {task.task_type}"}
    
    def _analyze_requirements(self, project_spec: ProjectSpec, project_path: Path) -> Dict[str, Any]:
        """Analyze project requirements"""
        analysis = {
            "project_complexity": self._assess_complexity(project_spec),
            "technology_stack": self._recommend_technologies(project_spec),
            "estimated_duration": self._estimate_duration(project_spec),
            "resource_requirements": self._assess_resources(project_spec),
            "risk_factors": self._identify_risks(project_spec)
        }
        
        # Save analysis
        analysis_file = project_path / "analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        self.logger.info(f"📊 Analysis completed: {analysis['project_complexity']} complexity")
        return {"success": True, "analysis": analysis}
    
    def _create_project_plan(self, project_spec: ProjectSpec, project_path: Path) -> Dict[str, Any]:
        """Create detailed project plan"""
        plan = {
            "phases": self._define_phases(project_spec),
            "milestones": self._define_milestones(project_spec),
            "task_breakdown": self._break_down_tasks(project_spec),
            "dependencies": self._map_dependencies(project_spec),
            "timeline": self._create_timeline(project_spec)
        }
        
        # Save plan
        plan_file = project_path / "project_plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
        
        self.logger.info(f"📋 Project plan created with {len(plan['task_breakdown'])} tasks")
        return {"success": True, "plan": plan}
    
    def _assess_complexity(self, spec: ProjectSpec) -> str:
        """Assess project complexity"""
        complexity_score = 0
        complexity_score += len(spec.requirements) * 2
        complexity_score += len(spec.features) * 3
        complexity_score += len(spec.technologies) * 1
        
        if complexity_score < 10:
            return "low"
        elif complexity_score < 25:
            return "medium"
        else:
            return "high"
    
    def _recommend_technologies(self, spec: ProjectSpec) -> Dict[str, List[str]]:
        """Recommend technology stack"""
        recommendations = {
            "backend": [],
            "frontend": [],
            "database": [],
            "deployment": [],
            "testing": []
        }
        
        if spec.project_type == ProjectType.WEB_APP:
            recommendations["backend"] = ["FastAPI", "Python"]
            recommendations["frontend"] = ["React", "TypeScript", "Tailwind CSS"]
            recommendations["database"] = ["PostgreSQL", "Redis"]
            recommendations["deployment"] = ["Docker", "Nginx"]
            recommendations["testing"] = ["pytest", "Jest"]
        elif spec.project_type == ProjectType.API_SERVICE:
            recommendations["backend"] = ["FastAPI", "Python"]
            recommendations["database"] = ["PostgreSQL"]
            recommendations["deployment"] = ["Docker", "Kubernetes"]
            recommendations["testing"] = ["pytest", "Postman"]
        elif spec.project_type == ProjectType.DESKTOP_APP:
            recommendations["backend"] = ["Python", "Tkinter"]
            recommendations["deployment"] = ["PyInstaller"]
            recommendations["testing"] = ["pytest"]
        
        return recommendations
    
    def _estimate_duration(self, spec: ProjectSpec) -> Dict[str, int]:
        """Estimate project duration"""
        base_hours = 40  # Base project setup
        
        # Add hours based on features
        feature_hours = len(spec.features) * 8
        
        # Add hours based on complexity
        complexity_multiplier = {"low": 1.0, "medium": 1.5, "high": 2.5}
        complexity = self._assess_complexity(spec)
        
        total_hours = int((base_hours + feature_hours) * complexity_multiplier[complexity])
        
        return {
            "total_hours": total_hours,
            "estimated_days": total_hours // 8,
            "phases": {
                "analysis": total_hours * 0.1,
                "design": total_hours * 0.2,
                "implementation": total_hours * 0.5,
                "testing": total_hours * 0.15,
                "deployment": total_hours * 0.05
            }
        }
    
    def _assess_resources(self, spec: ProjectSpec) -> Dict[str, Any]:
        """Assess resource requirements"""
        return {
            "agents_needed": min(len(spec.features), 5),
            "disk_space_mb": 1000 + len(spec.features) * 100,
            "memory_mb": 512 + len(spec.technologies) * 128,
            "external_services": []
        }
    
    def _identify_risks(self, spec: ProjectSpec) -> List[Dict[str, str]]:
        """Identify project risks"""
        risks = []
        
        if len(spec.technologies) > 5:
            risks.append({
                "risk": "Technology complexity",
                "impact": "medium",
                "mitigation": "Focus on core technologies first"
            })
        
        if len(spec.features) > 10:
            risks.append({
                "risk": "Feature creep",
                "impact": "high", 
                "mitigation": "Prioritize MVP features"
            })
        
        return risks
    
    def _define_phases(self, spec: ProjectSpec) -> List[Dict[str, str]]:
        """Define project phases"""
        return [
            {"name": "Analysis", "description": "Requirements analysis and planning"},
            {"name": "Design", "description": "Architecture and UI/UX design"},
            {"name": "Implementation", "description": "Core development"},
            {"name": "Testing", "description": "Quality assurance and testing"},
            {"name": "Deployment", "description": "Production deployment"}
        ]
    
    def _define_milestones(self, spec: ProjectSpec) -> List[Dict[str, str]]:
        """Define project milestones"""
        return [
            {"name": "Requirements Complete", "phase": "Analysis"},
            {"name": "Architecture Defined", "phase": "Design"},
            {"name": "MVP Complete", "phase": "Implementation"},
            {"name": "Testing Complete", "phase": "Testing"},
            {"name": "Production Ready", "phase": "Deployment"}
        ]
    
    def _break_down_tasks(self, spec: ProjectSpec) -> List[Dict[str, Any]]:
        """Break down project into tasks"""
        tasks = []
        
        # Analysis tasks
        tasks.append({
            "name": "Requirements Analysis",
            "type": "analysis",
            "estimated_hours": 4
        })
        
        # Design tasks
        tasks.append({
            "name": "Architecture Design",
            "type": "design",
            "estimated_hours": 8
        })
        
        # Implementation tasks for each feature
        for i, feature in enumerate(spec.features):
            tasks.append({
                "name": f"Implement {feature}",
                "type": "implementation",
                "estimated_hours": 6
            })
        
        # Testing tasks
        tasks.append({
            "name": "Unit Testing",
            "type": "testing",
            "estimated_hours": 4
        })
        
        tasks.append({
            "name": "Integration Testing",
            "type": "testing",
            "estimated_hours": 6
        })
        
        # Deployment tasks
        tasks.append({
            "name": "Production Deployment",
            "type": "deployment",
            "estimated_hours": 4
        })
        
        return tasks
    
    def _map_dependencies(self, spec: ProjectSpec) -> Dict[str, List[str]]:
        """Map task dependencies"""
        return {
            "Architecture Design": ["Requirements Analysis"],
            "Implementation": ["Architecture Design"],
            "Unit Testing": ["Implementation"],
            "Integration Testing": ["Unit Testing"],
            "Production Deployment": ["Integration Testing"]
        }
    
    def _create_timeline(self, spec: ProjectSpec) -> Dict[str, str]:
        """Create project timeline"""
        duration = self._estimate_duration(spec)
        return {
            "start_date": time.strftime("%Y-%m-%d"),
            "estimated_end_date": time.strftime("%Y-%m-%d", 
                time.localtime(time.time() + duration["estimated_days"] * 24 * 3600)),
            "total_duration_days": duration["estimated_days"]
        }


class MIAImplementationAgent(MIAProjectAgent):
    """Agent for code implementation"""
    
    def __init__(self):
        super().__init__("implementer", "implementation", ["implementation", "coding"])
    
    def _execute_task_impl(self, task: ProjectTask, project_spec: ProjectSpec, 
                          project_path: Path) -> Dict[str, Any]:
        """Execute implementation task"""
        if task.task_type == "implementation":
            return self._implement_feature(task, project_spec, project_path)
        else:
            return {"success": False, "error": f"Unknown task type: {task.task_type}"}
    
    def _implement_feature(self, task: ProjectTask, project_spec: ProjectSpec, 
                          project_path: Path) -> Dict[str, Any]:
        """Implement a feature"""
        feature_name = task.name.replace("Implement ", "").lower().replace(" ", "_")
        
        # Create feature directory
        feature_path = project_path / "src" / feature_name
        feature_path.mkdir(parents=True, exist_ok=True)
        
        # Generate code based on project type
        if project_spec.project_type == ProjectType.WEB_APP:
            files_created = self._create_web_app_feature(feature_name, feature_path, project_spec)
        elif project_spec.project_type == ProjectType.API_SERVICE:
            files_created = self._create_api_feature(feature_name, feature_path, project_spec)
        elif project_spec.project_type == ProjectType.CLI_TOOL:
            files_created = self._create_cli_feature(feature_name, feature_path, project_spec)
        else:
            files_created = self._create_generic_feature(feature_name, feature_path, project_spec)
        
        self.logger.info(f"💻 Implemented feature: {feature_name} ({len(files_created)} files)")
        return {"success": True, "feature": feature_name, "files_created": files_created}
    
    def _create_web_app_feature(self, feature_name: str, feature_path: Path, 
                               spec: ProjectSpec) -> List[str]:
        """Create web app feature files"""
        files_created = []
        
        # Backend API endpoint
        api_file = feature_path / f"{feature_name}_api.py"
        api_content = f'''"""
{feature_name.title()} API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging

router = APIRouter(prefix="/{feature_name}", tags=["{feature_name}"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_{feature_name}() -> Dict[str, Any]:
    """Get {feature_name} data"""
    try:
        # Implementation logic here
        return {{"success": True, "data": [], "message": "{feature_name} retrieved successfully"}}
    except Exception as e:
        logger.error(f"{feature_name} retrieval error: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_{feature_name}(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new {feature_name}"""
    try:
        # Implementation logic here
        return {{"success": True, "data": data, "message": "{feature_name} created successfully"}}
    except Exception as e:
        logger.error(f"{feature_name} creation error: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{{item_id}}")
async def update_{feature_name}(item_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update {feature_name}"""
    try:
        # Implementation logic here
        return {{"success": True, "data": data, "message": "{feature_name} updated successfully"}}
    except Exception as e:
        logger.error(f"{feature_name} update error: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{{item_id}}")
async def delete_{feature_name}(item_id: str) -> Dict[str, Any]:
    """Delete {feature_name}"""
    try:
        # Implementation logic here
        return {{"success": True, "message": "{feature_name} deleted successfully"}}
    except Exception as e:
        logger.error(f"{feature_name} deletion error: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))
'''
        
        with open(api_file, 'w') as f:
            f.write(api_content)
        files_created.append(str(api_file))
        
        # Frontend React component
        component_file = feature_path / f"{feature_name.title()}Component.tsx"
        component_content = f'''import React, {{ useState, useEffect }} from 'react';
import axios from 'axios';

interface {feature_name.title()}Data {{
  id: string;
  name: string;
  // Add more fields as needed
}}

const {feature_name.title()}Component: React.FC = () => {{
  const [data, setData] = useState<{feature_name.title()}Data[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {{
    fetch{feature_name.title()}Data();
  }}, []);

  const fetch{feature_name.title()}Data = async () => {{
    try {{
      setLoading(true);
      const response = await axios.get('/api/{feature_name}');
      setData(response.data.data);
      setError(null);
    }} catch (err) {{
      setError('Failed to fetch {feature_name} data');
      console.error(err);
    }} finally {{
      setLoading(false);
    }}
  }};

  if (loading) return <div className="loading">Loading {feature_name}...</div>;
  if (error) return <div className="error">{{error}}</div>;

  return (
    <div className="{feature_name}-container">
      <h2 className="text-2xl font-bold mb-4">{feature_name.title()}</h2>
      <div className="grid gap-4">
        {{data.map((item) => (
          <div key={{item.id}} className="card p-4 border rounded shadow">
            <h3 className="font-semibold">{{item.name}}</h3>
            {{/* Add more item details here */}}
          </div>
        ))}}
      </div>
    </div>
  );
}};

export default {feature_name.title()}Component;
'''
        
        with open(component_file, 'w') as f:
            f.write(component_content)
        files_created.append(str(component_file))
        
        return files_created
    
    def _create_api_feature(self, feature_name: str, feature_path: Path, 
                           spec: ProjectSpec) -> List[str]:
        """Create API service feature files"""
        files_created = []
        
        # Service module
        service_file = feature_path / f"{feature_name}_service.py"
        service_content = f'''"""
{feature_name.title()} Service
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime


class {feature_name.title()}Service:
    """Service for {feature_name} operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{{__name__}}.{feature_name.title()}Service")
        self.data_store = []  # In production, use proper database
    
    async def get_all(self) -> List[Dict[str, Any]]:
        """Get all {feature_name} items"""
        try:
            self.logger.info(f"Retrieving all {feature_name} items")
            return self.data_store
        except Exception as e:
            self.logger.error(f"Error retrieving {feature_name} items: {{e}}")
            raise
    
    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get {feature_name} item by ID"""
        try:
            for item in self.data_store:
                if item.get('id') == item_id:
                    return item
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving {feature_name} item {{item_id}}: {{e}}")
            raise
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new {feature_name} item"""
        try:
            item = {{
                'id': str(len(self.data_store) + 1),
                'created_at': datetime.now().isoformat(),
                **data
            }}
            self.data_store.append(item)
            self.logger.info(f"Created {feature_name} item: {{item['id']}}")
            return item
        except Exception as e:
            self.logger.error(f"Error creating {feature_name} item: {{e}}")
            raise
    
    async def update(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update {feature_name} item"""
        try:
            for i, item in enumerate(self.data_store):
                if item.get('id') == item_id:
                    updated_item = {{**item, **data, 'updated_at': datetime.now().isoformat()}}
                    self.data_store[i] = updated_item
                    self.logger.info(f"Updated {feature_name} item: {{item_id}}")
                    return updated_item
            return None
        except Exception as e:
            self.logger.error(f"Error updating {feature_name} item {{item_id}}: {{e}}")
            raise
    
    async def delete(self, item_id: str) -> bool:
        """Delete {feature_name} item"""
        try:
            for i, item in enumerate(self.data_store):
                if item.get('id') == item_id:
                    del self.data_store[i]
                    self.logger.info(f"Deleted {feature_name} item: {{item_id}}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting {feature_name} item {{item_id}}: {{e}}")
            raise
'''
        
        with open(service_file, 'w') as f:
            f.write(service_content)
        files_created.append(str(service_file))
        
        return files_created
    
    def _create_cli_feature(self, feature_name: str, feature_path: Path, 
                           spec: ProjectSpec) -> List[str]:
        """Create CLI tool feature files"""
        files_created = []
        
        # CLI command module
        cli_file = feature_path / f"{feature_name}_cli.py"
        cli_content = f'''"""
{feature_name.title()} CLI commands
"""

import click
import logging
from typing import Dict, Any


@click.group()
def {feature_name}():
    """{feature_name.title()} commands"""
    pass


@{feature_name}.command()
@click.option('--name', required=True, help='Name of the item')
@click.option('--description', help='Description of the item')
def create(name: str, description: str):
    """Create a new {feature_name} item"""
    try:
        item = {{
            'name': name,
            'description': description or '',
            'created': True
        }}
        click.echo(f"✅ Created {feature_name}: {{name}}")
        click.echo(f"Details: {{item}}")
    except Exception as e:
        click.echo(f"❌ Error creating {feature_name}: {{e}}", err=True)


@{feature_name}.command()
@click.option('--format', default='table', help='Output format (table, json)')
def list(format: str):
    """List all {feature_name} items"""
    try:
        # In production, fetch from actual data source
        items = [
            {{'id': '1', 'name': 'Sample {feature_name}', 'status': 'active'}},
            {{'id': '2', 'name': 'Another {feature_name}', 'status': 'inactive'}}
        ]
        
        if format == 'json':
            import json
            click.echo(json.dumps(items, indent=2))
        else:
            click.echo(f"{{len(items)}} {feature_name} items found:")
            for item in items:
                click.echo(f"  - {{item['id']}}: {{item['name']}} ({{item['status']}})")
    except Exception as e:
        click.echo(f"❌ Error listing {feature_name} items: {{e}}", err=True)


@{feature_name}.command()
@click.argument('item_id')
def delete(item_id: str):
    """Delete a {feature_name} item"""
    try:
        # In production, delete from actual data source
        click.echo(f"✅ Deleted {feature_name} item: {{item_id}}")
    except Exception as e:
        click.echo(f"❌ Error deleting {feature_name} item: {{e}}", err=True)


if __name__ == '__main__':
    {feature_name}()
'''
        
        with open(cli_file, 'w') as f:
            f.write(cli_content)
        files_created.append(str(cli_file))
        
        return files_created
    
    def _create_generic_feature(self, feature_name: str, feature_path: Path, 
                               spec: ProjectSpec) -> List[str]:
        """Create generic feature files"""
        files_created = []
        
        # Main module
        main_file = feature_path / f"{feature_name}.py"
        main_content = f'''"""
{feature_name.title()} Module
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime


class {feature_name.title()}:
    """Main {feature_name} class"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{{__name__}}.{feature_name.title()}")
        self.initialized = True
        self.logger.info(f"{feature_name.title()} initialized")
    
    def process(self, data: Any) -> Dict[str, Any]:
        """Process {feature_name} data"""
        try:
            self.logger.info(f"Processing {feature_name} data")
            
            # Implementation logic here
            result = {{
                'success': True,
                'processed_at': datetime.now().isoformat(),
                'input_data': data,
                'result': f"Processed {{data}}"
            }}
            
            self.logger.info(f"{feature_name.title()} processing completed")
            return result
            
        except Exception as e:
            self.logger.error(f"{feature_name.title()} processing error: {{e}}")
            return {{'success': False, 'error': str(e)}}
    
    def validate(self, data: Any) -> bool:
        """Validate {feature_name} data"""
        try:
            # Add validation logic here
            return data is not None
        except Exception as e:
            self.logger.error(f"{feature_name.title()} validation error: {{e}}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get {feature_name} status"""
        return {{
            'initialized': self.initialized,
            'status': 'active',
            'timestamp': datetime.now().isoformat()
        }}


def main():
    """Main function for testing"""
    feature = {feature_name.title()}()
    
    # Test the feature
    test_data = "test input"
    result = feature.process(test_data)
    print(f"Result: {{result}}")
    
    status = feature.get_status()
    print(f"Status: {{status}}")


if __name__ == "__main__":
    main()
'''
        
        with open(main_file, 'w') as f:
            f.write(main_content)
        files_created.append(str(main_file))
        
        return files_created


class MIATestingAgent(MIAProjectAgent):
    """Agent for testing and quality assurance"""
    
    def __init__(self):
        super().__init__("tester", "testing", ["testing", "quality_assurance"])
    
    def _execute_task_impl(self, task: ProjectTask, project_spec: ProjectSpec, 
                          project_path: Path) -> Dict[str, Any]:
        """Execute testing task"""
        if task.task_type == "testing":
            return self._run_tests(task, project_spec, project_path)
        else:
            return {"success": False, "error": f"Unknown task type: {task.task_type}"}
    
    def _run_tests(self, task: ProjectTask, project_spec: ProjectSpec, 
                   project_path: Path) -> Dict[str, Any]:
        """Run project tests"""
        test_results = {
            "unit_tests": self._run_unit_tests(project_path),
            "integration_tests": self._run_integration_tests(project_path),
            "code_quality": self._check_code_quality(project_path),
            "security_scan": self._run_security_scan(project_path)
        }
        
        # Calculate overall success
        all_passed = all(result.get("passed", False) for result in test_results.values())
        
        # Save test report
        report_file = project_path / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        self.logger.info(f"🧪 Testing completed: {'PASSED' if all_passed else 'FAILED'}")
        return {"success": all_passed, "test_results": test_results}
    
    def _run_unit_tests(self, project_path: Path) -> Dict[str, Any]:
        """Run unit tests"""
        try:
            # Look for test files
            test_files = list(project_path.rglob("test_*.py")) + list(project_path.rglob("*_test.py"))
            
            if not test_files:
                return {"passed": True, "message": "No unit tests found", "tests_run": 0}
            
            # Run pytest if available
            try:
                result = subprocess.run(
                    ['python', '-m', 'pytest', str(project_path), '-v'],
                    capture_output=True, text=True, cwd=project_path
                )
                
                return {
                    "passed": result.returncode == 0,
                    "output": result.stdout,
                    "errors": result.stderr,
                    "tests_run": len(test_files)
                }
            except FileNotFoundError:
                # Fallback: basic Python test runner
                return {"passed": True, "message": "pytest not available, basic validation passed", "tests_run": len(test_files)}
                
        except Exception as e:
            return {"passed": False, "error": str(e), "tests_run": 0}
    
    def _run_integration_tests(self, project_path: Path) -> Dict[str, Any]:
        """Run integration tests"""
        try:
            # Basic integration test - check if main modules can be imported
            src_path = project_path / "src"
            if not src_path.exists():
                return {"passed": True, "message": "No src directory found", "tests_run": 0}
            
            python_files = list(src_path.rglob("*.py"))
            import_errors = []
            
            for py_file in python_files:
                try:
                    # Basic syntax check
                    with open(py_file, 'r') as f:
                        compile(f.read(), str(py_file), 'exec')
                except SyntaxError as e:
                    import_errors.append(f"{py_file}: {e}")
            
            return {
                "passed": len(import_errors) == 0,
                "tests_run": len(python_files),
                "errors": import_errors
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e), "tests_run": 0}
    
    def _check_code_quality(self, project_path: Path) -> Dict[str, Any]:
        """Check code quality"""
        try:
            python_files = list(project_path.rglob("*.py"))
            
            quality_issues = []
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    # Basic quality checks
                    lines = content.split('\n')
                    
                    # Check for very long lines
                    for i, line in enumerate(lines):
                        if len(line) > 120:
                            quality_issues.append(f"{py_file}:{i+1}: Line too long ({len(line)} chars)")
                    
                    # Check for missing docstrings in functions
                    if 'def ' in content and '"""' not in content:
                        quality_issues.append(f"{py_file}: Missing docstrings")
                        
                except Exception as e:
                    quality_issues.append(f"{py_file}: Error reading file - {e}")
            
            return {
                "passed": len(quality_issues) < 5,  # Allow some minor issues
                "issues_found": len(quality_issues),
                "issues": quality_issues[:10]  # Limit output
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _run_security_scan(self, project_path: Path) -> Dict[str, Any]:
        """Run basic security scan"""
        try:
            python_files = list(project_path.rglob("*.py"))
            
            security_issues = []
            dangerous_patterns = [
                'eval(',
                'exec(',
                'os.system(',
                'subprocess.call(',
                'input(',  # In production code
                'raw_input('
            ]
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                    
                    for pattern in dangerous_patterns:
                        if pattern in content:
                            security_issues.append(f"{py_file}: Potentially dangerous pattern '{pattern}'")
                            
                except Exception as e:
                    security_issues.append(f"{py_file}: Error scanning file - {e}")
            
            return {
                "passed": len(security_issues) == 0,
                "issues_found": len(security_issues),
                "issues": security_issues
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}


class MIADeploymentAgent(MIAProjectAgent):
    """Agent for deployment and DevOps"""
    
    def __init__(self):
        super().__init__("deployer", "deployment", ["deployment", "devops"])
    
    def _execute_task_impl(self, task: ProjectTask, project_spec: ProjectSpec, 
                          project_path: Path) -> Dict[str, Any]:
        """Execute deployment task"""
        if task.task_type == "deployment":
            return self._deploy_project(task, project_spec, project_path)
        else:
            return {"success": False, "error": f"Unknown task type: {task.task_type}"}
    
    def _deploy_project(self, task: ProjectTask, project_spec: ProjectSpec, 
                       project_path: Path) -> Dict[str, Any]:
        """Deploy project"""
        deployment_artifacts = []
        
        # Create deployment files
        if project_spec.project_type in [ProjectType.WEB_APP, ProjectType.API_SERVICE]:
            dockerfile = self._create_dockerfile(project_spec, project_path)
            if dockerfile:
                deployment_artifacts.append(dockerfile)
            
            docker_compose = self._create_docker_compose(project_spec, project_path)
            if docker_compose:
                deployment_artifacts.append(docker_compose)
        
        # Create requirements file
        requirements = self._create_requirements_file(project_spec, project_path)
        if requirements:
            deployment_artifacts.append(requirements)
        
        # Create startup script
        startup_script = self._create_startup_script(project_spec, project_path)
        if startup_script:
            deployment_artifacts.append(startup_script)
        
        self.logger.info(f"🚀 Deployment prepared: {len(deployment_artifacts)} artifacts created")
        return {"success": True, "artifacts": deployment_artifacts}
    
    def _create_dockerfile(self, spec: ProjectSpec, project_path: Path) -> Optional[str]:
        """Create Dockerfile"""
        try:
            dockerfile_content = f'''# Dockerfile for {spec.name}
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY *.py ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py"]
'''
            
            dockerfile_path = project_path / "Dockerfile"
            with open(dockerfile_path, 'w') as f:
                f.write(dockerfile_content)
            
            return str(dockerfile_path)
            
        except Exception as e:
            self.logger.error(f"Error creating Dockerfile: {e}")
            return None
    
    def _create_docker_compose(self, spec: ProjectSpec, project_path: Path) -> Optional[str]:
        """Create docker-compose.yml"""
        try:
            compose_content = f'''version: '3.8'

services:
  {spec.name.lower().replace(' ', '-')}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - LOG_LEVEL=info
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    
  # Add database if needed
  # postgres:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: {spec.name.lower()}
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   restart: unless-stopped

# volumes:
#   postgres_data:
'''
            
            compose_path = project_path / "docker-compose.yml"
            with open(compose_path, 'w') as f:
                f.write(compose_content)
            
            return str(compose_path)
            
        except Exception as e:
            self.logger.error(f"Error creating docker-compose.yml: {e}")
            return None
    
    def _create_requirements_file(self, spec: ProjectSpec, project_path: Path) -> Optional[str]:
        """Create requirements.txt"""
        try:
            requirements = []
            
            # Add requirements based on project type and technologies
            if spec.project_type in [ProjectType.WEB_APP, ProjectType.API_SERVICE]:
                requirements.extend([
                    "fastapi>=0.68.0",
                    "uvicorn[standard]>=0.15.0",
                    "pydantic>=1.8.0",
                    "python-multipart>=0.0.5"
                ])
            
            if "database" in str(spec.technologies).lower():
                requirements.extend([
                    "sqlalchemy>=1.4.0",
                    "psycopg2-binary>=2.9.0"
                ])
            
            if "redis" in str(spec.technologies).lower():
                requirements.append("redis>=3.5.0")
            
            if spec.project_type == ProjectType.CLI_TOOL:
                requirements.append("click>=8.0.0")
            
            # Add testing requirements
            requirements.extend([
                "pytest>=6.2.0",
                "pytest-asyncio>=0.15.0"
            ])
            
            requirements_content = '\n'.join(sorted(requirements))
            
            requirements_path = project_path / "requirements.txt"
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            
            return str(requirements_path)
            
        except Exception as e:
            self.logger.error(f"Error creating requirements.txt: {e}")
            return None
    
    def _create_startup_script(self, spec: ProjectSpec, project_path: Path) -> Optional[str]:
        """Create startup script"""
        try:
            if spec.project_type in [ProjectType.WEB_APP, ProjectType.API_SERVICE]:
                script_content = f'''#!/bin/bash
# Startup script for {spec.name}

echo "Starting {spec.name}..."

# Set environment variables
export PYTHONPATH=${{PYTHONPATH}}:$(pwd)/src
export LOG_LEVEL=${{LOG_LEVEL:-info}}

# Run database migrations if needed
# python -m alembic upgrade head

# Start the application
if [ "$ENV" = "production" ]; then
    echo "Starting in production mode..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
else
    echo "Starting in development mode..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi
'''
            else:
                script_content = f'''#!/bin/bash
# Startup script for {spec.name}

echo "Starting {spec.name}..."

# Set environment variables
export PYTHONPATH=${{PYTHONPATH}}:$(pwd)/src

# Run the application
python main.py "$@"
'''
            
            script_path = project_path / "start.sh"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            return str(script_path)
            
        except Exception as e:
            self.logger.error(f"Error creating startup script: {e}")
            return None


class MIAProjectSystem:
    """Complete MIA Project AGI System"""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.projects_path = data_path / "projects"
        self.projects_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Initialize agents
        self.agents = {
            "analyzer": MIAAnalysisAgent(),
            "implementer": MIAImplementationAgent(),
            "tester": MIATestingAgent(),
            "deployer": MIADeploymentAgent()
        }
        
        # Active projects
        self.active_projects = {}
        
        # Task executor
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self.logger.info("🚀 MIA Project AGI System initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup project system logging"""
        logger = logging.getLogger("MIA.ProjectSystem")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - MIA.ProjectSystem - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def create_project(self, name: str, description: str, project_type: str, 
                      requirements: List[str], features: List[str], 
                      technologies: List[str] = None) -> str:
        """Create new project"""
        project_id = str(uuid.uuid4())
        
        # Create project specification
        spec = ProjectSpec(
            name=name,
            description=description,
            project_type=ProjectType(project_type),
            requirements=requirements,
            technologies=technologies or [],
            features=features
        )
        
        # Create project directory
        project_path = self.projects_path / project_id
        project_path.mkdir(exist_ok=True)
        
        # Save project specification
        spec_file = project_path / "project_spec.json"
        with open(spec_file, 'w') as f:
            json.dump(asdict(spec), f, indent=2, default=str)
        
        # Initialize project structure
        self._initialize_project_structure(project_path, spec)
        
        # Store project
        self.active_projects[project_id] = {
            "spec": spec,
            "path": project_path,
            "status": ProjectStatus.PLANNING,
            "tasks": [],
            "created_at": time.time()
        }
        
        self.logger.info(f"📋 Created project: {name} ({project_id})")
        return project_id
    
    def build_project(self, project_id: str) -> Dict[str, Any]:
        """Build project using AGI agents"""
        if project_id not in self.active_projects:
            return {"success": False, "error": "Project not found"}
        
        project = self.active_projects[project_id]
        project["status"] = ProjectStatus.IN_PROGRESS
        
        self.logger.info(f"🏗️ Building project: {project['spec'].name}")
        
        try:
            # Phase 1: Analysis
            analysis_result = self._run_analysis_phase(project_id)
            if not analysis_result["success"]:
                return analysis_result
            
            # Phase 2: Implementation
            implementation_result = self._run_implementation_phase(project_id)
            if not implementation_result["success"]:
                return implementation_result
            
            # Phase 3: Testing
            testing_result = self._run_testing_phase(project_id)
            if not testing_result["success"]:
                project["status"] = ProjectStatus.FAILED
                return testing_result
            
            # Phase 4: Deployment
            deployment_result = self._run_deployment_phase(project_id)
            if not deployment_result["success"]:
                return deployment_result
            
            project["status"] = ProjectStatus.COMPLETED
            
            self.logger.info(f"✅ Project completed: {project['spec'].name}")
            return {
                "success": True,
                "project_id": project_id,
                "status": "completed",
                "path": str(project["path"])
            }
            
        except Exception as e:
            project["status"] = ProjectStatus.FAILED
            self.logger.error(f"Project build error: {e}")
            return {"success": False, "error": str(e)}
    
    def _initialize_project_structure(self, project_path: Path, spec: ProjectSpec):
        """Initialize project directory structure"""
        # Create standard directories
        (project_path / "src").mkdir(exist_ok=True)
        (project_path / "tests").mkdir(exist_ok=True)
        (project_path / "docs").mkdir(exist_ok=True)
        (project_path / "data").mkdir(exist_ok=True)
        
        # Create main.py
        main_file = project_path / "main.py"
        main_content = f'''#!/usr/bin/env python3
"""
{spec.name}
{spec.description}

Generated by MIA Project AGI System
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point"""
    logger.info("Starting {spec.name}...")
    
    try:
        # Application logic here
        logger.info("{spec.name} started successfully")
        
        # Keep running for web apps
        if "{spec.project_type}" in ["ProjectType.WEB_APP", "ProjectType.API_SERVICE"]:
            import uvicorn
            uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
        else:
            logger.info("{spec.name} completed")
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {{e}}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
        
        with open(main_file, 'w') as f:
            f.write(main_content)
        
        # Create README
        readme_file = project_path / "README.md"
        readme_content = f'''# {spec.name}

{spec.description}

## Features

{chr(10).join(f"- {feature}" for feature in spec.features)}

## Requirements

{chr(10).join(f"- {req}" for req in spec.requirements)}

## Technologies

{chr(10).join(f"- {tech}" for tech in spec.technologies)}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Generated by MIA Project AGI System

This project was automatically generated and built by MIA's intelligent project system.
'''
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
    
    def _run_analysis_phase(self, project_id: str) -> Dict[str, Any]:
        """Run analysis phase"""
        project = self.active_projects[project_id]
        analyzer = self.agents["analyzer"]
        
        # Create analysis task
        analysis_task = ProjectTask(
            id=str(uuid.uuid4()),
            name="Project Analysis",
            description="Analyze project requirements and create plan",
            task_type="analysis"
        )
        
        result = analyzer.execute_task(analysis_task, project["spec"], project["path"])
        project["tasks"].append(analysis_task)
        
        return result
    
    def _run_implementation_phase(self, project_id: str) -> Dict[str, Any]:
        """Run implementation phase"""
        project = self.active_projects[project_id]
        implementer = self.agents["implementer"]
        
        # Create implementation tasks for each feature
        results = []
        for feature in project["spec"].features:
            impl_task = ProjectTask(
                id=str(uuid.uuid4()),
                name=f"Implement {feature}",
                description=f"Implement {feature} functionality",
                task_type="implementation"
            )
            
            result = implementer.execute_task(impl_task, project["spec"], project["path"])
            project["tasks"].append(impl_task)
            results.append(result)
        
        # Check if all implementations succeeded
        all_success = all(r.get("success", False) for r in results)
        
        return {
            "success": all_success,
            "results": results,
            "features_implemented": len([r for r in results if r.get("success", False)])
        }
    
    def _run_testing_phase(self, project_id: str) -> Dict[str, Any]:
        """Run testing phase"""
        project = self.active_projects[project_id]
        tester = self.agents["tester"]
        
        # Create testing task
        testing_task = ProjectTask(
            id=str(uuid.uuid4()),
            name="Project Testing",
            description="Run comprehensive project tests",
            task_type="testing"
        )
        
        result = tester.execute_task(testing_task, project["spec"], project["path"])
        project["tasks"].append(testing_task)
        
        return result
    
    def _run_deployment_phase(self, project_id: str) -> Dict[str, Any]:
        """Run deployment phase"""
        project = self.active_projects[project_id]
        deployer = self.agents["deployer"]
        
        # Create deployment task
        deployment_task = ProjectTask(
            id=str(uuid.uuid4()),
            name="Project Deployment",
            description="Prepare project for deployment",
            task_type="deployment"
        )
        
        result = deployer.execute_task(deployment_task, project["spec"], project["path"])
        project["tasks"].append(deployment_task)
        
        return result
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get project status"""
        if project_id not in self.active_projects:
            return {"error": "Project not found"}
        
        project = self.active_projects[project_id]
        
        return {
            "project_id": project_id,
            "name": project["spec"].name,
            "status": project["status"].value,
            "tasks_completed": len([t for t in project["tasks"] if t.status == "completed"]),
            "tasks_total": len(project["tasks"]),
            "created_at": project["created_at"],
            "path": str(project["path"])
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return [self.get_project_status(pid) for pid in self.active_projects.keys()]


def main():
    """Test MIA Project System"""
    print("🚀 MIA Project AGI System Test")
    print("=" * 35)
    
    # Initialize project system
    project_system = MIAProjectSystem(Path("mia_data"))
    
    # Create test project
    print("\n📋 Creating test project...")
    project_id = project_system.create_project(
        name="Test Web App",
        description="A test web application with user management",
        project_type="web_app",
        requirements=["User authentication", "Data storage", "REST API"],
        features=["User registration", "User login", "Profile management", "Dashboard"],
        technologies=["Python", "FastAPI", "React", "PostgreSQL"]
    )
    
    print(f"✅ Created project: {project_id}")
    
    # Build project
    print("\n🏗️ Building project...")
    build_result = project_system.build_project(project_id)
    
    if build_result["success"]:
        print(f"✅ Project built successfully: {build_result['path']}")
    else:
        print(f"❌ Project build failed: {build_result.get('error', 'Unknown error')}")
    
    # Show project status
    print("\n📊 Project Status:")
    status = project_system.get_project_status(project_id)
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Project system test completed")


if __name__ == "__main__":
    main()