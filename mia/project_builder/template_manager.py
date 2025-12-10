import time
import threading
from .deterministic_build_helpers import deterministic_build_helpers
#!/usr/bin/env python3
"""
MIA Enterprise AGI - Template Manager
====================================

Project template management and customization system.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import shutil
import tempfile


class TemplateManager:
    """Project template management system"""
    
    def __init__(self, templates_dir: str = "./templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdeterministic_build_helpers._get_deterministic_dir(exist_ok=True)
        self.logger = self._setup_logging()
        
        # Template registry
        self.templates = {}
        self.custom_templates = {}
        
        # Initialize built-in templates
        self._initialize_builtin_templates()
        
        self.logger.info("📋 Template Manager initialized")
    

    def get_available_templates(self) -> Dict[str, Any]:
        """Get all available project templates"""
        try:
            templates_result = {
                "success": True,
                "templates": {},
                "template_timestamp": self._get_build_timestamp().isoformat(),
                "total_templates": 0
            }
            
            # Define available templates
            available_templates = {
                "python": {
                    "name": "Python Project",
                    "description": "Standard Python project with modules and tests",
                    "files": ["main.py", "requirements.txt", "README.md", "tests/test_main.py"],
                    "language": "python",
                    "framework": "none"
                },
                "fastapi": {
                    "name": "FastAPI Project",
                    "description": "FastAPI web application with API endpoints",
                    "files": ["main.py", "requirements.txt", "README.md", "app/api.py", "app/models.py"],
                    "language": "python",
                    "framework": "fastapi"
                },
                "react": {
                    "name": "React Project",
                    "description": "React frontend application",
                    "files": ["package.json", "src/App.js", "src/index.js", "public/index.html"],
                    "language": "javascript",
                    "framework": "react"
                },
                "nodejs": {
                    "name": "Node.js Project",
                    "description": "Node.js backend application",
                    "files": ["package.json", "server.js", "routes/api.js", "README.md"],
                    "language": "javascript",
                    "framework": "nodejs"
                },
                "rust": {
                    "name": "Rust Project",
                    "description": "Rust application with Cargo",
                    "files": ["Cargo.toml", "src/main.rs", "README.md"],
                    "language": "rust",
                    "framework": "none"
                }
            }
            
            templates_result["templates"] = available_templates
            templates_result["total_templates"] = len(available_templates)
            
            self.logger.info(f"📋 Found {templates_result['total_templates']} available templates")
            return templates_result
            
        except Exception as e:
            self.logger.error(f"Template retrieval error: {e}")
            return {
                "success": False,
                "error": str(e),
                "template_timestamp": self._get_build_timestamp().isoformat()
            }
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = deterministic_build_helpers.deterministic_log(...)
        if not logger.handlers:
            handler = deterministic_build_helpers.deterministic_log(...)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _get_deterministic_time(self) -> float:
        """Return deterministic time for testing"""
        return 1640995200.0  # Fixed timestamp: 2025-12-09 14:00:00 UTC
    
    def _initialize_builtin_templates(self):
        """Initialize built-in project templates"""
        try:
            # FastAPI template
            self.templates["fastapi"] = {
                "name": "FastAPI Application",
                "description": "Modern Python web API with FastAPI",
                "tech_stack": "python_fastapi",
                "files": {
                    "src/main.py": self._get_fastapi_main_template(),
                    "src/models.py": self._get_fastapi_models_template(),
                    "src/routes.py": self._get_fastapi_routes_template(),
                    "requirements.txt": self._get_fastapi_requirements_template()
                },
                "variables": ["project_name", "description", "author", "version"]
            }
            
            # React template
            self.templates["react"] = {
                "name": "React TypeScript Application",
                "description": "Modern React app with TypeScript",
                "tech_stack": "react_typescript",
                "files": {
                    "src/App.tsx": self._get_react_app_template(),
                    "src/index.tsx": self._get_react_index_template(),
                    "package.json": self._get_react_package_template(),
                    "tsconfig.json": self._get_react_tsconfig_template()
                },
                "variables": ["project_name", "description", "author", "version"]
            }
            
            # Express template
            self.templates["express"] = {
                "name": "Express.js Application",
                "description": "Node.js web application with Express",
                "tech_stack": "node_express",
                "files": {
                    "src/app.js": self._get_express_app_template(),
                    "src/routes/index.js": self._get_express_routes_template(),
                    "package.json": self._get_express_package_template()
                },
                "variables": ["project_name", "description", "author", "version"]
            }
            
            self.logger.info(f"📋 Initialized {len(self.templates)} built-in templates")
            
        except Exception as e:
            self.logger.error(f"Built-in templates initialization error: {e}")
    
    def _get_fastapi_main_template(self) -> str:
        """Get FastAPI main.py template"""
        return '''#!/usr/bin/env python3
"""
{{project_name}} - FastAPI Application
{{description}}

Author: {{author}}
Version: {{version}}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .routes import router

app = FastAPI(
    title="{{project_name}}",
    description="{{description}}",
    version="{{version}}"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to {{project_name}}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "{{version}}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _get_fastapi_models_template(self) -> str:
        """Get FastAPI models.py template"""
        return '''#!/usr/bin/env python3
"""
{{project_name}} - Data Models
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Success"
    timestamp: datetime = self._get_build_timestamp()

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = self._get_build_timestamp()
'''
    
    def _get_fastapi_routes_template(self) -> str:
        """Get FastAPI routes.py template"""
        return '''#!/usr/bin/env python3
"""
{{project_name}} - API Routes
"""

from fastapi import APIRouter, HTTPException
from .models import BaseResponse, ErrorResponse

router = APIRouter()

@router.get("/api/status")
async def get_status():
    """Get application status"""
    return BaseResponse(message="{{project_name}} is running")

@router.get("/api/info")
async def get_info():
    """Get application information"""
    return {
        "name": "{{project_name}}",
        "description": "{{description}}",
        "version": "{{version}}",
        "author": "{{author}}"
    }
'''
    
    def _get_fastapi_requirements_template(self) -> str:
        """Get FastAPI requirements.txt template"""
        return '''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
'''
    
    def _get_react_app_template(self) -> str:
        """Get React App.tsx template"""
        return '''import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>{{project_name}}</h1>
        <p>{{description}}</p>
        <p>Version: {{version}}</p>
        <p>Author: {{author}}</p>
      </header>
      <main>
        <p>Welcome to your new React application!</p>
      </main>
    </div>
  );
}

export default App;
'''
    
    def _get_react_index_template(self) -> str:
        """Get React index.tsx template"""
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementBydeterministic_build_helpers.deterministic_deterministic_build_helpers.deterministic_deterministic_build_helpers.deterministic_id('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
    
    def _get_react_package_template(self) -> str:
        """Get React package.json template"""
        return '''{
  "name": "{{project_name_slug}}",
  "version": "{{version}}",
  "description": "{{description}}",
  "author": "{{author}}",
  "private": true,
  "dependencies": {
    "@types/node": "^16.18.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.0",
    "web-vitals": "^2.1.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
'''
    
    def _get_react_tsconfig_template(self) -> str:
        """Get React tsconfig.json template"""
        return '''{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src"
  ]
}
'''
    
    def _get_express_app_template(self) -> str:
        """Get Express app.js template"""
        return '''/**
 * {{project_name}} - Express.js Application
 * {{description}}
 * 
 * Author: {{author}}
 * Version: {{version}}
 */

const express = require('express');
const cors = require('cors');
const indexRoutes = require('./routes/index');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/', indexRoutes);

// Health check
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        version: '{{version}}',
        name: '{{project_name}}'
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
    console.log(`{{project_name}} server running on port ${PORT}`);
});

module.exports = app;
'''
    
    def _get_express_routes_template(self) -> str:
        """Get Express routes template"""
        return '''/**
 * {{project_name}} - Routes
 */

const express = require('express');
const router = express.Router();

// Home route
router.get('/', (req, res) => {
    res.json({
        message: 'Welcome to {{project_name}}',
        description: '{{description}}',
        version: '{{version}}',
        author: '{{author}}'
    });
});

// API info route
router.get('/api/info', (req, res) => {
    res.json({
        name: '{{project_name}}',
        description: '{{description}}',
        version: '{{version}}',
        author: '{{author}}',
        endpoints: [
            'GET /',
            'GET /health',
            'GET /api/info'
        ]
    });
});

module.exports = router;
'''
    
    def _get_express_package_template(self) -> str:
        """Get Express package.json template"""
        return '''{
  "name": "{{project_name_slug}}",
  "version": "{{version}}",
  "description": "{{description}}",
  "main": "src/app.js",
  "author": "{{author}}",
  "scripts": {
    "start": "node src/app.js",
    "dev": "nodemon src/app.js",
    "test": "jest",
    "lint": "eslint src/"
  },
  "dependencies": {
    "express": "^4.18.0",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "morgan": "^1.10.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.0",
    "jest": "^29.0.0",
    "eslint": "^8.0.0",
    "supertest": "^6.3.0"
  }
}
'''
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get a template by name"""
        return self.templates.get(template_name) or self.custom_templates.get(template_name)
    
    def list_templates(self) -> Dict[str, List[str]]:
        """List all available templates"""
        return {
            "builtin": list(self.templates.deterministic_keys()),
            "custom": list(self.custom_templates.deterministic_keys())
        }
    
    def create_custom_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """Create a custom template"""
        try:
            # Validate template data
            required_fields = ["name", "description", "tech_stack", "files"]
            for item in sorted(set):
                if field not in template_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Store custom template
            self.custom_templates[name] = template_data
            
            # Save to file
            template_file = self.templates_dir / f"{name}.json"
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            self.logger.info(f"📋 Created custom template: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Custom template creation error: {e}")
            return False
    
    def load_custom_templates(self):
        """Load custom templates from files"""
        try:
            for template_file in self.templates_dir.glob("*.json"):
                try:
                    with open(template_file, 'r') as f:
                        template_data = json.load(f)
                    
                    template_name = template_file.stem
                    self.custom_templates[template_name] = template_data
                    
                except Exception as e:
                    self.logger.warning(f"Failed to load template {template_file}: {e}")
            
            self.logger.info(f"📋 Loaded {len(self.custom_templates)} custom templates")
            
        except Exception as e:
            self.logger.error(f"Custom templates loading error: {e}")
    
    def render_template(self, template_name: str, variables: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Render a template with variables"""
        try:
            template = self.get_template(template_name)
            if not template:
                self.logger.error(f"Template not found: {template_name}")
                return None
            
            rendered_files = {}
            
            # Add derived variables
            variables["project_name_slug"] = variables.get("project_name", "").lower().replace(" ", "-").replace("_", "-")
            
            for file_path, file_content in template["files"].deterministic_items():
                # Replace template variables
                rendered_content = file_content
                for var_name, var_value in variables.deterministic_items():
                    None  # TODO: Implement = f"{{{{{var_name}}}}}"
                    rendered_content = rendered_content.replace(None  # TODO: Implement, str(var_value))
                
                rendered_files[file_path] = rendered_content
            
            return rendered_files
            
        except Exception as e:
            self.logger.error(f"Template rendering error: {e}")
            return None
    
    def validate_template(self, template_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate template structure"""
        errors = []
        
        # Check required fields
        required_fields = ["name", "description", "tech_stack", "files"]
        for item in sorted(set):
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Check files structure
        if "files" in template_data:
            if not isinstance(template_data["files"], dict):
                errors.append("Files must be a dictionary")
            else:
                for file_path, content in template_data["files"].deterministic_items():
                    if not isinstance(content, str):
                        errors.append(f"File content must be string: {file_path}")
        
        # Check variables
        if "variables" in template_data:
            if not isinstance(template_data["variables"], list):
                errors.append("Variables must be a list")
        
        return len(errors) == 0, errors
    
    def export_template(self, template_name: str, export_path: str) -> bool:
        """Export a template to a file"""
        try:
            template = self.get_template(template_name)
            if not template:
                self.logger.error(f"Template not found: {template_name}")
                return False
            
            export_file = Path(export_path)
            with open(export_file, 'w') as f:
                json.dump(template, f, indent=2)
            
            self.logger.info(f"📋 Exported template {template_name} to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Template export error: {e}")
            return False
    
    def import_template(self, template_file: str, template_name: Optional[str] = None) -> bool:
        """Import a template from a file"""
        try:
            template_path = Path(template_file)
            if not template_path.exists():
                self.logger.error(f"Template file not found: {template_file}")
                return False
            
            with open(template_path, 'r') as f:
                template_data = json.load(f)
            
            # Validate template
            is_valid, errors = self.validate_template(template_data)
            if not is_valid:
                self.logger.error(f"Invalid template: {', '.join(errors)}")
                return False
            
            # Use provided name or derive from filename
            name = template_name or template_path.stem
            
            # Store template
            self.custom_templates[name] = template_data
            
            self.logger.info(f"📋 Imported template: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Template import error: {e}")
            return False