#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Node.js Templates Module.

This module provides templates for generating Node.js project structures, files, and code.
It includes templates for different Node.js project types (Express applications, Next.js,
standard Node.js packages, etc.) and common patterns used in Node.js development.

The templates are designed to be flexible and customizable, allowing for generation of
idiomatic JavaScript/TypeScript code that follows best practices and conventions.
"""

import os
import re
import textwrap
from typing import Dict, Any, List, Optional, Union, Callable, Set
import logging
from pathlib import Path
from datetime import datetime
import json

from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)
setup_logger()


class NodeTemplates:
    """
    Provides templates for Node.js projects.
    
    This class contains static methods that generate code and configuration files
    for Node.js projects, following best practices and conventions.
    """

    @staticmethod
    def package_json(context: Dict[str, Any]) -> str:
        """
        Generate a package.json file for a Node.js project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - description: Short description of the project
                - author: Author's name
                - author_email: Author's email
                - version: Project version
                - dependencies: Dict of dependencies and versions
                - dev_dependencies: Dict of dev dependencies and versions
                - scripts: Dict of npm scripts
                - license: License type
                - keywords: List of keywords
                - repository: Repository URL
                - main: Main entry file
                - type: Module type (commonjs or module)
        
        Returns:
            String containing the package.json content
        """
        project_name = context.get('project_name', 'node-project')
        description = context.get('description', 'A Node.js project')
        author_name = context.get('author', 'Author')
        author_email = context.get('author_email', 'author@example.com')
        version = context.get('version', '0.1.0')
        dependencies = context.get('dependencies', {})
        dev_dependencies = context.get('dev_dependencies', {})
        scripts = context.get('scripts', {
            "start": "node index.js",
            "dev": "nodemon index.js",
            "test": "jest",
            "lint": "eslint ."
        })
        license_type = context.get('license', 'MIT')
        keywords = context.get('keywords', [])
        repository = context.get('repository', '')
        main = context.get('main', 'index.js')
        module_type = context.get('type', 'commonjs')
        
        # Default dependencies if none provided
        if not dependencies:
            dependencies = {
                "express": "^4.18.2",
                "dotenv": "^16.0.3",
                "cors": "^2.8.5",
                "helmet": "^6.0.1"
            }
        
        # Default dev dependencies if none provided
        if not dev_dependencies:
            dev_dependencies = {
                "nodemon": "^2.0.22",
                "jest": "^29.5.0",
                "eslint": "^8.38.0"
            }
        
        # Format author field
        author = f"{author_name} <{author_email}>"
        
        # Create the package.json object
        package_json = {
            "name": project_name,
            "version": version,
            "description": description,
            "main": main,
            "type": module_type,
            "scripts": scripts,
            "keywords": keywords,
            "author": author,
            "license": license_type,
            "dependencies": dependencies,
            "devDependencies": dev_dependencies
        }
        
        # Add repository if provided
        if repository:
            package_json["repository"] = {
                "type": "git",
                "url": repository
            }
        
        # Convert to formatted JSON string
        return json.dumps(package_json, indent=2)

    @staticmethod
    def gitignore() -> str:
        """
        Generate a .gitignore file for a Node.js project.
        
        Returns:
            String containing the .gitignore content
        """
        return """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Diagnostic reports (https://nodejs.org/api/report.html)
report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional stylelint cache
.stylelintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variable files
.env
.env.development.local
.env.test.local
.env.production.local
.env.local

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next
out

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
# Comment in the public line in if your project uses Gatsby and not Next.js
# https://nextjs.org/blog/next-9-1#public-directory-support
# public

# vuepress build output
.vuepress/dist

# vuepress v2.x temp and cache directory
.temp
.cache

# Docusaurus cache and generated files
.docusaurus

# Serverless directories
.serverless/

# FuseBox cache
.fusebox/

# DynamoDB Local files
.dynamodb/

# TernJS port file
.tern-port

# Stores VSCode versions used for testing VSCode extensions
.vscode-test

# yarn v2
.yarn/cache
.yarn/unplugged
.yarn/build-state.yml
.yarn/install-state.gz
.pnp.*

# IDE files
.idea/
.vscode/
*.swp
*.swo
"""

    @staticmethod
    def eslintrc(context: Dict[str, Any]) -> str:
        """
        Generate an .eslintrc.js file for a Node.js project.
        
        Args:
            context: Dictionary containing project information:
                - use_typescript: Boolean indicating if TypeScript is used
                - ecma_version: ECMAScript version to target
                - env: Dictionary of environments to enable
        
        Returns:
            String containing the .eslintrc.js content
        """
        use_typescript = context.get('use_typescript', False)
        ecma_version = context.get('ecma_version', 2022)
        env = context.get('env', {
            'node': True,
            'jest': True,
            'es2022': True
        })
        
        # Format environments
        env_str = ',\n    '.join([f"'{k}': {str(v).lower()}" for k, v in env.items()])
        
        typescript_config = """
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint'],
    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
    ],"""
        
        standard_config = """
    extends: [
        'eslint:recommended',
    ],"""
        
        config = typescript_config if use_typescript else standard_config
        
        return f"""module.exports = {{
    env: {{
        {env_str}
    }},{config}
    parserOptions: {{
        ecmaVersion: {ecma_version},
        sourceType: 'module',
    }},
    rules: {{
        'indent': ['error', 2],
        'linebreak-style': ['error', 'unix'],
        'quotes': ['error', 'single'],
        'semi': ['error', 'always'],
        'no-unused-vars': ['warn'],
        'no-console': ['warn', {{ allow: ['warn', 'error'] }}],
    }}
}};
"""

    @staticmethod
    def jest_config(context: Dict[str, Any]) -> str:
        """
        Generate a jest.config.js file for a Node.js project.
        
        Args:
            context: Dictionary containing project information:
                - use_typescript: Boolean indicating if TypeScript is used
                - test_environment: Test environment to use
                - coverage_threshold: Coverage thresholds
        
        Returns:
            String containing the jest.config.js content
        """
        use_typescript = context.get('use_typescript', False)
        test_environment = context.get('test_environment', 'node')
        coverage_threshold = context.get('coverage_threshold', {
            'branches': 80,
            'functions': 80,
            'lines': 80,
            'statements': 80
        })
        
        # Format coverage thresholds
        coverage_str = ',\n      '.join([f"'{k}': {v}" for k, v in coverage_threshold.items()])
        
        typescript_config = """
  preset: 'ts-jest',
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },"""
        
        config = typescript_config if use_typescript else ""
        
        return f"""module.exports = {{
  testEnvironment: '{test_environment}',{config}
  collectCoverage: true,
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!**/node_modules/**',
    '!**/vendor/**',
    '!**/dist/**',
  ],
  coverageThreshold: {{
      global: {{
        {coverage_str}
      }}
  }},
  testMatch: [
    '**/__tests__/**/*.{js,jsx,ts,tsx}',
    '**/?(*.)+(spec|test).{js,jsx,ts,tsx}'
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/'
  ],
  verbose: true
}};
"""

    @staticmethod
    def tsconfig(context: Dict[str, Any]) -> str:
        """
        Generate a tsconfig.json file for a TypeScript Node.js project.
        
        Args:
            context: Dictionary containing project information:
                - target: TypeScript target (e.g., 'es2022')
                - module: Module system (e.g., 'commonjs')
                - strict: Whether to enable strict type checking
                - outdir: Output directory
        
        Returns:
            String containing the tsconfig.json content
        """
        target = context.get('target', 'es2022')
        module_system = context.get('module', 'commonjs')
        strict = context.get('strict', True)
        outdir = context.get('outdir', 'dist')
        
        return f"""{{
  "compilerOptions": {{
    "target": "{target}",
    "module": "{module_system}",
    "lib": ["es2022"],
    "allowJs": true,
    "outDir": "{outdir}",
    "rootDir": "src",
    "strict": {str(strict).lower()},
    "noImplicitAny": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "moduleResolution": "node",
    "sourceMap": true,
    "declaration": true,
    "declarationMap": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }},
  "include": ["src/**/*"],
  "exclude": ["node_modules", "**/*.test.ts", "dist"]
}}
"""

    @staticmethod
    def readme(context: Dict[str, Any]) -> str:
        """
        Generate a README.md file for a Node.js project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - description: Short description of the project
                - installation: Installation instructions
                - usage: Usage examples
                - features: List of features
                - license: License type
        
        Returns:
            String containing the README.md content
        """
        project_name = context.get('project_name', 'Node.js Project')
        description = context.get('description', 'A Node.js project')
        installation = context.get('installation', 'npm install')
        usage = context.get('usage', 'npm start')
        features = context.get('features', [])
        license_type = context.get('license', 'MIT')
        
        # Format features as a list
        features_md = ""
        if features:
            features_md = "## Features\n\n"
            for feature in features:
                features_md += f"- {feature}\n"
            features_md += "\n"
        
        return f"""# {project_name}

{description}

## Installation

```bash
{installation}
```

## Usage

```bash
{usage}
```

{features_md}## License

This project is licensed under the {license_type} License - see the LICENSE file for details.
"""

    @staticmethod
    def env_example(context: Dict[str, Any]) -> str:
        """
        Generate a .env.example file for a Node.js project.
        
        Args:
            context: Dictionary containing project information:
                - env_vars: Dictionary of environment variables and descriptions
                - port: Default port for the application
        
        Returns:
            String containing the .env.example content
        """
        env_vars = context.get('env_vars', {})
        port = context.get('port', 3000)
        
        # Add default environment variables if not provided
        if not env_vars:
            env_vars = {
                'NODE_ENV': 'development',
                'PORT': port,
                'LOG_LEVEL': 'info',
                'DATABASE_URL': 'mongodb://localhost:27017/mydatabase',
                'JWT_SECRET': 'your-secret-key',
                'API_KEY': 'your-api-key'
            }
        
        # Format environment variables with comments
        env_content = ""
        for key, value in env_vars.items():
            if isinstance(value, dict) and 'value' in value and 'description' in value:
                env_content += f"# {value['description']}\n{key}={value['value']}\n\n"
            else:
                env_content += f"{key}={value}\n"
        
        return env_content.strip()

    @staticmethod
    def express_app(context: Dict[str, Any]) -> str:
        """
        Generate an Express.js application file.
        
        Args:
            context: Dictionary containing project information:
                - port: Port for the Express server
                - use_typescript: Boolean indicating if TypeScript is used
                - routes: List of route objects
                - middleware: List of middleware to include
        
        Returns:
            String containing the Express app code
        """
        port = context.get('port', 3000)
        use_typescript = context.get('use_typescript', False)
        routes = context.get('routes', [])
        middleware = context.get('middleware', ['cors', 'helmet', 'express.json', 'express.urlencoded'])
        
        # Determine file extension
        ext = 'ts' if use_typescript else 'js'
        
        # Type annotations for TypeScript
        req_type = 'Request' if use_typescript else ''
        res_type = 'Response' if use_typescript else ''
        next_type = 'NextFunction' if use_typescript else ''
        
        # Import statements
        imports = f"import express{' from' if use_typescript else ''} 'express';\n"
        
        if use_typescript:
            imports += "import { Request, Response, NextFunction } from 'express';\n"
        
        for mid in middleware:
            if mid not in ['express.json', 'express.urlencoded']:
                imports += f"import {mid}{' from' if use_typescript else ''} '{mid}';\n"
        
        imports += "import dotenv from 'dotenv';\n\n"
        
        # Middleware setup
        middleware_setup = ""
        for mid in middleware:
            if mid == 'express.json':
                middleware_setup += "app.use(express.json());\n"
            elif mid == 'express.urlencoded':
                middleware_setup += "app.use(express.urlencoded({ extended: true }));\n"
            else:
                middleware_setup += f"app.use({mid}());\n"
        
        # Routes setup
        routes_setup = ""
        if routes:
            routes_setup = "\n// Routes\n"
            for route in routes:
                path = route.get('path', '/')
                method = route.get('method', 'get')
                handler = route.get('handler', 'handleDefault')
                
                routes_setup += f"app.{method}('{path}', {handler});\n"
        else:
            # Default route
            routes_setup = f"""
// Default route
app.get('/', ({req_type} req, {res_type} res) => {{
  res.json({{ message: 'Welcome to the API' }});
}});

// Health check route
app.get('/health', ({req_type} req, {res_type} res) => {{
  res.status(200).json({{ status: 'UP' }});
}});
"""
        
        # Error handling middleware
        error_handler = f"""
// Error handling middleware
app.use(({req_type} req, {res_type} res, {next_type} next) => {{
  res.status(404).json({{ message: 'Not Found' }});
}});

app.use((err, {req_type} req, {res_type} res, {next_type} next) => {{
  console.error(err.stack);
  res.status(500).json({{ message: 'Internal Server Error' }});
}});
"""
        
        return f"""{imports}// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
const PORT = process.env.PORT || {port};

// Middleware
{middleware_setup}{routes_setup}{error_handler}
// Start server
app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});

export default app;
"""

    @staticmethod
    def express_route(context: Dict[str, Any]) -> str:
        """
        Generate an Express.js route file.
        
        Args:
            context: Dictionary containing project information:
                - route_name: Name of the route (e.g., 'users')
                - use_typescript: Boolean indicating if TypeScript is used
                - endpoints: List of endpoint objects
                - use_controller: Boolean indicating if controllers should be used
        
        Returns:
            String containing the Express route code
        """
        route_name = context.get('route_name', 'users')
        use_typescript = context.get('use_typescript', False)
        endpoints = context.get('endpoints', [])
        use_controller = context.get('use_controller', True)
        
        # Determine file extension
        ext = 'ts' if use_typescript else 'js'
        
        # Type annotations for TypeScript
        req_type = 'Request' if use_typescript else ''
        res_type = 'Response' if use_typescript else ''
        next_type = 'NextFunction' if use_typescript else ''
        
        # Import statements
        imports = f"import express{' from' if use_typescript else ''} 'express';\n"
        
        if use_typescript:
            imports += "import { Request, Response, NextFunction } from 'express';\n"
        
        if use_controller:
            imports += f"import {{ {route_name.capitalize()}Controller }} from '../controllers/{route_name}.controller{('.' + ext) if use_typescript else ''}';\n"
        
        imports += "\nconst router = express.Router();\n"
        
        if use_controller:
            imports += f"const controller = new {route_name.capitalize()}Controller();\n"
        
        # Endpoints setup
        endpoints_setup = "\n// Route endpoints\n"
        
        if not endpoints:
            # Default endpoints
            endpoints = [
                {'method': 'get', 'path': '/', 'description': f'Get all {route_name}'},
                {'method': 'get', 'path': '/:id', 'description': f'Get {route_name} by ID'},
                {'method': 'post', 'path': '/', 'description': f'Create a new {route_name}'},
                {'method': 'put', 'path': '/:id', 'description': f'Update {route_name} by ID'},
                {'method': 'delete', 'path': '/:id', 'description': f'Delete {route_name} by ID'}
            ]
        
        for endpoint in endpoints:
            path = endpoint.get('path', '/')
            method = endpoint.get('method', 'get')
            description = endpoint.get('description', f'Handle {method.upper()} request')
            
            if use_controller:
                handler = f"controller.{method}{path.replace('/', '').replace(':', '').capitalize() or 'All'}"
                endpoints_setup += f"// {description}\nrouter.{method}('{path}', {handler});\n\n"
            else:
                endpoints_setup += f"""// {description}
router.{method}('{path}', ({req_type} req, {res_type} res, {next_type} next) => {{
  try {{
    // Implementation for {method.upper()} {path}
    res.json({{ message: '{description}' }});
  }} catch (error) {{
    next(error);
  }}
}});

"""
        
        return f"""{imports}{endpoints_setup}export default router;
"""

    @staticmethod
    def express_controller(context: Dict[str, Any]) -> str:
        """
        Generate an Express.js controller file.
        
        Args:
            context: Dictionary containing project information:
                - controller_name: Name of the controller (e.g., 'users')
                - use_typescript: Boolean indicating if TypeScript is used
                - methods: List of method objects
                - use_service: Boolean indicating if services should be used
        
        Returns:
            String containing the Express controller code
        """
        controller_name = context.get('controller_name', 'users')
        use_typescript = context.get('use_typescript', False)
        methods = context.get('methods', [])
        use_service = context.get('use_service', True)
        
        # Determine file extension
        ext = 'ts' if use_typescript else 'js'
        
        # Type annotations for TypeScript
        req_type = 'Request' if use_typescript else ''
        res_type = 'Response' if use_typescript else ''
        next_type = 'NextFunction' if use_typescript else ''
        
        # Import statements
        imports = ""
        
        if use_typescript:
            imports += "import { Request, Response, NextFunction } from 'express';\n"
        
        if use_service:
            imports += f"import {{ {controller_name.capitalize()}Service }} from '../services/{controller_name}.service{('.' + ext) if use_typescript else ''}';\n\n"
        
        # Class definition
        class_def = f"export class {controller_name.capitalize()}Controller {{\n"
        
        if use_service:
            class_def += f"  private service{': ' + controller_name.capitalize() + 'Service' if use_typescript else ''};\n\n"
            class_def += f"  constructor() {{\n"
            class_def += f"    this.service = new {controller_name.capitalize()}Service();\n"
            class_def += f"  }}\n\n"
        
        # Methods
        if not methods:
            # Default methods
            methods = [
                {'name': 'getAll', 'path': '/', 'method': 'get', 'description': f'Get all {controller_name}'},
                {'name': 'getById', 'path': '/:id', 'method': 'get', 'description': f'Get {controller_name} by ID'},
                {'name': 'create', 'path': '/', 'method': 'post', 'description': f'Create a new {controller_name}'},
                {'name': 'update', 'path': '/:id', 'method': 'put', 'description': f'Update {controller_name} by ID'},
                {'name': 'delete', 'path': '/:id', 'method': 'delete', 'description': f'Delete {controller_name} by ID'}
            ]
        
        methods_code = ""
        for method in methods:
            name = method.get('name', 'handleRequest')
            description = method.get('description', 'Handle request')
            
            methods_code += f"  /**\n   * {description}\n   */\n"
            methods_code += f"  async {name}({req_type} req, {res_type} res, {next_type} next) {{\n"
            methods_code += f"    try {{\n"
            
            if use_service:
                if name == 'getAll':
                    methods_code += f"      const items = await this.service.findAll();\n"
                    methods_code += f"      res.json(items);\n"
                elif name == 'getById':
                    methods_code += f"      const id = req.params.id;\n"
                    methods_code += f"      const item = await this.service.findById(id);\n"
                    methods_code += f"      if (!item) {{\n"
                    methods_code += f"        return res.status(404).json({{ message: 'Not found' }});\n"
                    methods_code += f"      }}\n"
                    methods_code += f"      res.json(item);\n"
                elif name == 'create':
                    methods_code += f"      const data = req.body;\n"
                    methods_code += f"      const newItem = await this.service.create(data);\n"
                    methods_code += f"      res.status(201).json(newItem);\n"
                elif name == 'update':
                    methods_code += f"      const id = req.params.id;\n"
                    methods_code += f"      const data = req.body;\n"
                    methods_code += f"      const updated = await this.service.update(id, data);\n"
                    methods_code += f"      if (!updated) {{\n"
                    methods_code += f"        return res.status(404).json({{ message: 'Not found' }});\n"
                    methods_code += f"      }}\n"
                    methods_code += f"      res.json(updated);\n"
                elif name == 'delete':
                    methods_code += f"      const id = req.params.id;\n"
                    methods_code += f"      const deleted = await this.service.delete(id);\n"
                    methods_code += f"      if (!deleted) {{\n"
                    methods_code += f"        return res.status(404).json({{ message: 'Not found' }});\n"
                    methods_code += f"      }}\n"
                    methods_code += f"      res.status(204).send();\n"
                else:
                    methods_code += f"      // Implementation for {name}\n"
                    methods_code += f"      res.json({{ message: '{description}' }});\n"
            else:
                methods_code += f"      // Implementation for {name}\n"
                methods_code += f"      res.json({{ message: '{description}' }});\n"
            
            methods_code += f"    }} catch (error) {{\n"
            methods_code += f"      next(error);\n"
            methods_code += f"    }}\n"
            methods_code += f"  }}\n\n"
        
        # Remove trailing newline
        methods_code = methods_code.rstrip()
        
        return f"""{imports}{class_def}{methods_code}
}}
"""

    @staticmethod
    def express_service(context: Dict[str, Any]) -> str:
        """
        Generate an Express.js service file.
        
        Args:
            context: Dictionary containing project information:
                - service_name: Name of the service (e.g., 'users')
                - use_typescript: Boolean indicating if TypeScript is used
                - methods: List of method objects
                - use_model: Boolean indicating if models should be used
                - model_name: Name of the model to use
        
        Returns:
            String containing the Express service code
        """
        service_name = context.get('service_name', 'users')
        use_typescript = context.get('use_typescript', False)
        methods = context.get('methods', [])
        use_model = context.get('use_model', True)
        model_name = context.get('model_name', service_name.capitalize())
        
        # Determine file extension
        ext = 'ts' if use_typescript else 'js'
        
        # Import statements
        imports = ""
        
        if use_model:
            imports += f"import {model_name} from '../models/{service_name}.model{('.' + ext) if use_typescript else ''}';\n\n"
        
        # Type definitions for TypeScript
        types = ""
        if use_typescript:
            types = f"""interface {model_name}Data {{
  [key: string]: any;
}}

"""
        
        # Class definition
        class_def = f"export class {service_name.capitalize()}Service {{\n"
        
        # Methods
        if not methods:
            # Default methods
            methods = [
                {'name': 'findAll', 'description': f'Find all {service_name}'},
                {'name': 'findById', 'description': f'Find {service_name} by ID', 'params': [{'name': 'id', 'type': 'string'}]},
                {'name': 'create', 'description': f'Create a new {service_name}', 'params': [{'name': 'data', 'type': f'{model_name}Data'}]},
                {'name': 'update', 'description': f'Update {service_name} by ID', 'params': [{'name': 'id', 'type': 'string'