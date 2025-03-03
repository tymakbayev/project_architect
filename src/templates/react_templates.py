#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
React Templates Module.

This module provides templates for generating React project structures, files, and code.
It includes templates for different React project types (standard React apps, Next.js,
React Native, etc.) and common patterns used in React development.

The templates are designed to be flexible and customizable, allowing for generation of
idiomatic React code that follows best practices and conventions.
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


class ReactTemplates:
    """
    Provides templates for React projects.
    
    This class contains static methods that generate code and configuration files
    for React projects, following best practices and conventions.
    """

    @staticmethod
    def package_json(context: Dict[str, Any]) -> str:
        """
        Generate a package.json file for a React project.
        
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
        
        Returns:
            String containing the package.json content
        """
        project_name = context.get('project_name', 'react-app')
        description = context.get('description', 'A React project')
        author = context.get('author', 'Author')
        author_email = context.get('author_email', 'author@example.com')
        version = context.get('version', '0.1.0')
        license_type = context.get('license', 'MIT')
        
        # Default dependencies for a React project
        default_dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.8.0"
        }
        
        # Default dev dependencies for a React project
        default_dev_dependencies = {
            "@testing-library/jest-dom": "^5.16.5",
            "@testing-library/react": "^13.4.0",
            "@testing-library/user-event": "^14.4.3",
            "@types/react": "^18.0.27",
            "@types/react-dom": "^18.0.10",
            "typescript": "^4.9.5",
            "vite": "^4.1.0",
            "@vitejs/plugin-react": "^3.1.0",
            "eslint": "^8.33.0",
            "eslint-plugin-react": "^7.32.2",
            "eslint-plugin-react-hooks": "^4.6.0"
        }
        
        # Default scripts for a React project
        default_scripts = {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview",
            "test": "vitest run",
            "test:watch": "vitest",
            "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
            "format": "prettier --write \"src/**/*.{js,jsx,ts,tsx,css,scss}\""
        }
        
        # Merge provided dependencies with defaults
        dependencies = {**default_dependencies, **(context.get('dependencies', {}))}
        dev_dependencies = {**default_dev_dependencies, **(context.get('dev_dependencies', {}))}
        scripts = {**default_scripts, **(context.get('scripts', {}))}
        
        # Create package.json content
        package_json = {
            "name": project_name,
            "version": version,
            "description": description,
            "author": f"{author} <{author_email}>",
            "license": license_type,
            "type": "module",
            "scripts": scripts,
            "dependencies": dependencies,
            "devDependencies": dev_dependencies,
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
        
        return json.dumps(package_json, indent=2)

    @staticmethod
    def tsconfig_json(context: Dict[str, Any]) -> str:
        """
        Generate a tsconfig.json file for a React TypeScript project.
        
        Args:
            context: Dictionary containing project information:
                - strict: Whether to enable strict type checking
                - jsx: JSX factory to use (default: 'react-jsx')
                - target: ECMAScript target version
                - module: Module system to use
                - additional_options: Additional TypeScript compiler options
        
        Returns:
            String containing the tsconfig.json content
        """
        strict = context.get('strict', True)
        jsx = context.get('jsx', 'react-jsx')
        target = context.get('target', 'ESNext')
        module_system = context.get('module', 'ESNext')
        additional_options = context.get('additional_options', {})
        
        tsconfig = {
            "compilerOptions": {
                "target": target,
                "useDefineForClassFields": True,
                "lib": ["DOM", "DOM.Iterable", "ESNext"],
                "allowJs": False,
                "skipLibCheck": True,
                "esModuleInterop": False,
                "allowSyntheticDefaultImports": True,
                "strict": strict,
                "forceConsistentCasingInFileNames": True,
                "module": module_system,
                "moduleResolution": "Node",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": jsx,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["src/*"]
                }
            },
            "include": ["src"],
            "references": [{ "path": "./tsconfig.node.json" }]
        }
        
        # Merge additional options
        if additional_options:
            tsconfig["compilerOptions"].update(additional_options)
        
        return json.dumps(tsconfig, indent=2)

    @staticmethod
    def vite_config(context: Dict[str, Any]) -> str:
        """
        Generate a vite.config.ts file for a React project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - plugins: Additional Vite plugins to include
                - server_options: Options for the development server
                - build_options: Options for the build process
        
        Returns:
            String containing the vite.config.ts content
        """
        plugins = context.get('plugins', [])
        server_options = context.get('server_options', {})
        build_options = context.get('build_options', {})
        
        # Default server options
        default_server = {
            "port": 3000,
            "open": True
        }
        
        # Default build options
        default_build = {
            "outDir": "dist",
            "sourcemap": True
        }
        
        # Merge with provided options
        server = {**default_server, **server_options}
        build = {**default_build, **build_options}
        
        # Format server options
        server_str = "{\n"
        for key, value in server.items():
            if isinstance(value, bool):
                server_str += f"    {key}: {str(value).lower()},\n"
            elif isinstance(value, (int, float)):
                server_str += f"    {key}: {value},\n"
            else:
                server_str += f"    {key}: '{value}',\n"
        server_str += "  }"
        
        # Format build options
        build_str = "{\n"
        for key, value in build.items():
            if isinstance(value, bool):
                build_str += f"    {key}: {str(value).lower()},\n"
            elif isinstance(value, (int, float)):
                build_str += f"    {key}: {value},\n"
            else:
                build_str += f"    {key}: '{value}',\n"
        build_str += "  }"
        
        # Format plugins
        plugins_str = "react()"
        for plugin in plugins:
            plugins_str += f",\n    {plugin}"
        
        return f"""import {{ defineConfig }} from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({{
  plugins: [
    {plugins_str}
  ],
  resolve: {{
    alias: {{
      '@': path.resolve(__dirname, './src')
    }}
  }},
  server: {server_str},
  build: {build_str}
}})
"""

    @staticmethod
    def eslintrc(context: Dict[str, Any]) -> str:
        """
        Generate an .eslintrc.js file for a React project.
        
        Args:
            context: Dictionary containing project information:
                - typescript: Whether the project uses TypeScript
                - additional_plugins: Additional ESLint plugins to include
                - additional_rules: Additional ESLint rules to include
        
        Returns:
            String containing the .eslintrc.js content
        """
        typescript = context.get('typescript', True)
        additional_plugins = context.get('additional_plugins', [])
        additional_rules = context.get('additional_rules', {})
        
        # Base configuration
        extends_list = [
            "'eslint:recommended'",
            "'plugin:react/recommended'",
            "'plugin:react-hooks/recommended'",
            "'plugin:import/recommended'"
        ]
        
        plugins = ["'react'", "'react-hooks'"]
        
        # Add TypeScript configuration if needed
        if typescript:
            extends_list.extend([
                "'plugin:@typescript-eslint/recommended'",
                "'plugin:import/typescript'"
            ])
            plugins.append("'@typescript-eslint'")
        
        # Add additional plugins
        for plugin in additional_plugins:
            plugins.append(f"'{plugin}'")
        
        # Format extends list
        extends_str = ",\n    ".join(extends_list)
        
        # Format plugins list
        plugins_str = ",\n    ".join(plugins)
        
        # Base rules
        rules = {
            "react/react-in-jsx-scope": "off",
            "react/prop-types": "off",
            "no-unused-vars": typescript and "off" or "warn",
            "react-hooks/rules-of-hooks": "error",
            "react-hooks/exhaustive-deps": "warn"
        }
        
        # Add TypeScript specific rules
        if typescript:
            rules["@typescript-eslint/no-unused-vars"] = "warn"
            rules["@typescript-eslint/explicit-module-boundary-types"] = "off"
            rules["@typescript-eslint/no-explicit-any"] = "warn"
        
        # Add additional rules
        rules.update(additional_rules)
        
        # Format rules
        rules_str = "{\n"
        for key, value in rules.items():
            if isinstance(value, bool):
                rules_str += f"    '{key}': {str(value).lower()},\n"
            elif isinstance(value, (int, float)):
                rules_str += f"    '{key}': {value},\n"
            else:
                rules_str += f"    '{key}': '{value}',\n"
        rules_str += "  }"
        
        return f"""module.exports = {{
  env: {{
    browser: true,
    es2021: true,
    node: true,
    jest: true
  }},
  extends: [
    {extends_str}
  ],
  parser: {typescript and "'@typescript-eslint/parser'" or "'@babel/eslint-parser'"},
  parserOptions: {{
    ecmaFeatures: {{
      jsx: true
    }},
    ecmaVersion: 'latest',
    sourceType: 'module'
  }},
  plugins: [
    {plugins_str}
  ],
  settings: {{
    react: {{
      version: 'detect'
    }},
    'import/resolver': {{
      node: {{
        extensions: ['.js', '.jsx'{typescript and ", '.ts', '.tsx'" or ""}]
      }}
    }}
  }},
  rules: {rules_str}
}}
"""

    @staticmethod
    def prettierrc(context: Dict[str, Any]) -> str:
        """
        Generate a .prettierrc file for a React project.
        
        Args:
            context: Dictionary containing project information:
                - tab_width: Number of spaces per indentation level
                - use_tabs: Whether to use tabs instead of spaces
                - semi: Whether to add semicolons
                - single_quote: Whether to use single quotes
                - additional_options: Additional Prettier options
        
        Returns:
            String containing the .prettierrc content
        """
        tab_width = context.get('tab_width', 2)
        use_tabs = context.get('use_tabs', False)
        semi = context.get('semi', True)
        single_quote = context.get('single_quote', True)
        additional_options = context.get('additional_options', {})
        
        # Base configuration
        config = {
            "printWidth": 100,
            "tabWidth": tab_width,
            "useTabs": use_tabs,
            "semi": semi,
            "singleQuote": single_quote,
            "trailingComma": "es5",
            "bracketSpacing": True,
            "jsxBracketSameLine": False,
            "arrowParens": "avoid",
            "endOfLine": "lf"
        }
        
        # Add additional options
        config.update(additional_options)
        
        return json.dumps(config, indent=2)

    @staticmethod
    def app_component(context: Dict[str, Any]) -> str:
        """
        Generate an App component for a React project.
        
        Args:
            context: Dictionary containing project information:
                - typescript: Whether the project uses TypeScript
                - use_router: Whether to include React Router
                - project_name: Name of the project
        
        Returns:
            String containing the App component content
        """
        typescript = context.get('typescript', True)
        use_router = context.get('use_router', True)
        project_name = context.get('project_name', 'React App')
        
        file_ext = typescript and "tsx" or "jsx"
        
        if use_router:
            return f"""import {{ useState }} from 'react'
import {{ BrowserRouter as Router, Routes, Route, Link }} from 'react-router-dom'
import './App.css'

// Import pages
import Home from './pages/Home'
import About from './pages/About'
import NotFound from './pages/NotFound'

function App{typescript and ": React.FC" or ""} {{
  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <h1>{project_name}</h1>
          <nav>
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/about">About</Link></li>
            </ul>
          </nav>
        </header>
        
        <main>
          <Routes>
            <Route path="/" element={{<Home />}} />
            <Route path="/about" element={{<About />}} />
            <Route path="*" element={{<NotFound />}} />
          </Routes>
        </main>
        
        <footer>
          <p>&copy; {datetime.now().year} {project_name}. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  )
}}

export default App
"""
        else:
            return f"""import {{ useState }} from 'react'
import './App.css'

function App{typescript and ": React.FC" or ""} {{
  const [count, setCount] = useState(0)

  return (
    <div className="app">
      <header className="app-header">
        <h1>{project_name}</h1>
      </header>
      
      <main>
        <div className="card">
          <button onClick={() => setCount(count => count + 1)}>
            count is {{count}}
          </button>
          <p>
            Edit <code>src/App.{file_ext}</code> and save to test HMR
          </p>
        </div>
      </main>
      
      <footer>
        <p>&copy; {datetime.now().year} {project_name}. All rights reserved.</p>
      </footer>
    </div>
  )
}}

export default App
"""

    @staticmethod
    def index_html(context: Dict[str, Any]) -> str:
        """
        Generate an index.html file for a React project.
        
        Args:
            context: Dictionary containing project information:
                - project_name: Name of the project
                - description: Short description of the project
                - favicon: Path to the favicon
                - additional_meta: Additional meta tags to include
                - additional_scripts: Additional scripts to include
        
        Returns:
            String containing the index.html content
        """
        project_name = context.get('project_name', 'React App')
        description = context.get('description', 'A React application')
        favicon = context.get('favicon', '/favicon.ico')
        additional_meta = context.get('additional_meta', [])
        additional_scripts = context.get('additional_scripts', [])
        
        # Format additional meta tags
        meta_tags = ""
        for meta in additional_meta:
            meta_tags += f'    <meta {" ".join([f"{k}=\"{v}\"" for k, v in meta.items()])}>\n'
        
        # Format additional scripts
        scripts = ""
        for script in additional_scripts:
            if isinstance(script, str):
                scripts += f'    <script src="{script}"></script>\n'
            else:
                attrs = " ".join([f"{k}=\"{v}\"" for k, v in script.items() if k != "content"])
                if "content" in script:
                    scripts += f'    <script {attrs}>{script["content"]}</script>\n'
                else:
                    scripts += f'    <script {attrs}></script>\n'
        
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/x-icon" href="{favicon}" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{description}" />
    <meta name="theme-color" content="#000000" />
{meta_tags}
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
{scripts}
  </body>
</html>
"""

    @staticmethod
    def main_entry(context: Dict[str, Any]) -> str:
        """
        Generate a main entry file (main.tsx/jsx) for a React project.
        
        Args:
            context: Dictionary containing project information:
                - typescript: Whether the project uses TypeScript
                - strict_mode: Whether to use React's StrictMode
                - additional_imports: Additional imports to include
                - additional_providers: Additional providers to wrap the App with
        
        Returns:
            String containing the main entry file content
        """
        typescript = context.get('typescript', True)
        strict_mode = context.get('strict_mode', True)
        additional_imports = context.get('additional_imports', [])
        additional_providers = context.get('additional_providers', [])
        
        file_ext = typescript and "tsx" or "jsx"
        
        # Format additional imports
        imports_str = ""
        for imp in additional_imports:
            imports_str += f"import {imp}\n"
        
        # Format providers (components that wrap the App)
        providers_start = ""
        providers_end = ""
        for provider in additional_providers:
            providers_start = f"<{provider}>\n  {providers_start}"
            providers_end = f"{providers_end}\n  </{provider}>"
        
        strict_mode_start = strict_mode and "<React.StrictMode>" or ""
        strict_mode_end = strict_mode and "</React.StrictMode>" or ""
        
        return f"""import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
{imports_str}

ReactDOM.createRoot(document.getElementById('root'){ typescript and " as HTMLElement" or ""}).render(
  {strict_mode_start}
  {providers_start}<App />{providers_end}
  {strict_mode_end}
)
"""

    @staticmethod
    def component_template(context: Dict[str, Any]) -> str:
        """
        Generate a React component template.
        
        Args:
            context: Dictionary containing component information:
                - name: Name of the component
                - typescript: Whether the project uses TypeScript
                - props: Component props definition
                - styles: Whether to include a separate CSS import
                - functional: Whether to use a functional component (vs class)
                - hooks: List of hooks to include
        
        Returns:
            String containing the component template
        """
        name = context.get('name', 'Component')
        typescript = context.get('typescript', True)
        props = context.get('props', {})
        include_styles = context.get('styles', True)
        functional = context.get('functional', True)
        hooks = context.get('hooks', [])
        
        file_ext = typescript and "tsx" or "jsx"
        
        # Generate props interface for TypeScript
        props_interface = ""
        if typescript and props:
            props_interface = f"interface {name}Props {{\n"
            for prop_name, prop_type in props.items():
                required = not prop_type.endswith('?')
                clean_type = prop_type.rstrip('?')
                props_interface += f"  {prop_name}{'' if required else '?'}: {clean_type};\n"
            props_interface += "}\n\n"
        
        # Generate imports for hooks
        hooks_imports = ""
        hooks_declarations = ""
        
        for hook in hooks:
            if hook == 'useState':
                hooks_imports += "import { useState } from 'react';\n"
                hooks_declarations += "  const [state, setState] = useState(initialState);\n"
            elif hook == 'useEffect':
                hooks_imports += "import { useEffect } from 'react';\n"
                hooks_declarations += "  useEffect(() => {\n    // Effect logic\n    return () => {\n      // Cleanup logic\n    };\n  }, []);\n"
            elif hook == 'useContext':
                hooks_imports += "import { useContext } from 'react';\n"
                hooks_declarations += "  const contextValue = useContext(MyContext);\n"
            elif hook == 'useReducer':
                hooks_imports += "import { useReducer } from 'react';\n"
                hooks_declarations += "  const [state, dispatch] = useReducer(reducer, initialState);\n"
            elif hook == 'useCallback':
                hooks_imports += "import { useCallback } from 'react';\n"
                hooks_declarations += "  const memoizedCallback = useCallback(() => {\n    // Function logic\n  }, []);\n"
            elif hook == 'useMemo':
                hooks_imports += "import { useMemo } from 'react';\n"
                hooks_declarations += "  const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);\n"
            elif hook == 'useRef':
                hooks_imports += "import { useRef } from 'react';\n"
                hooks_declarations += "  const refContainer = useRef(null);\n"
        
        # Import React if needed
        react_import = "import React from 'react';\n" if not functional or not hooks_imports else ""
        
        # CSS import
        css_import = f"import './{name}.css';\n" if include_styles else ""
        
        if functional:
            props_param = typescript and f"(props: {name}Props)" or "(props)"
            
            return f"""{react_import}{hooks_imports}{css_import}
{props_interface}const {name} = {props_param} => {{
{hooks_declarations}
  return (
    <div className="{name.lower()}">
      <h2>{name}</h2>
      {/* Component content */}
    </div>
  );
}};

export default {name};
"""
        else:
            props_type = typescript and f": {name}Props" or ""
            
            return f"""{react_import}{css_import}
{props_interface}class {name} extends React.Component{typescript and f"<{name}Props>" or ""} {{
  constructor(props{props_type}) {{
    super(props);
    this.state = {{
      // Initial state
    }};
  }}

  componentDidMount() {{
    // Mount logic
  }}

  componentWillUnmount() {{
    // Unmount logic
  }}

  render() {{
    return (
      <div className="{name.lower()}">
        <h2>{name}</h2>
        {/* Component content */}
      </div>
    );
  }}
}}

export default {name};
"""

    @staticmethod
    def redux_store(context: Dict[str, Any]) -> str:
        """
        Generate Redux store configuration for a React project.
        
        Args:
            context: Dictionary containing store information:
                - typescript: Whether the project uses TypeScript
                - slices: List of Redux slices to include
                - middleware: List of additional middleware to include
                - use_rtk: Whether to use Redux Toolkit (vs plain Redux)
        
        Returns:
            String containing the Redux store configuration
        """
        typescript = context.get('typescript', True)
        slices = context.get('slices', ['counter'])
        middleware = context.get('middleware', [])
        use_rtk = context.get('use_rtk', True)
        
        if use_rtk:
            # Generate imports for slices
            slice_imports = ""
            reducer_config = ""
            
            for slice in slices:
                pascal_case = ''.join(word.capitalize() for word in slice.split('_'))
                slice_imports += f"import {slice}Reducer from './features/{slice}/{slice}Slice';\n"
                reducer_config += f"    {slice}: {slice}Reducer,\n"
            
            # Generate middleware configuration
            middleware_imports = ""
            middleware_config = ""
            
            for mw in middleware:
                middleware_imports += f"import {mw} from './{mw}';\n"
                middleware_config += f"      {mw},\n"
            
            if middleware:
                middleware_setup = f"""    middleware: (getDefaultMiddleware) => 
      getDefaultMiddleware().concat([
{middleware_config}      ]),"""
            else:
                middleware_setup = ""
            
            return f"""import {{ configureStore{typescript and ", Action, ThunkAction" or ""} }} from '@reduxjs/toolkit';
{slice_imports}{middleware_imports}

export const store = configureStore({{
  reducer: {{
{reducer_config}  }},
{middleware_setup}
}});

{typescript and f"""
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
""" or ""}
"""
        else:
            # Plain Redux setup
            # Generate imports for reducers
            reducer_imports = ""
            reducer_config = ""
            
            for slice in slices:
                pascal_case = ''.join(word.capitalize() for word in slice.split('_'))
                reducer_imports += f"import {slice}Reducer from './reducers/{slice}Reducer';\n"
                reducer_config += f"    {slice}: {slice}Reducer,\n"
            
            # Generate middleware configuration
            middleware_imports = "import { applyMiddleware } from 'redux';\n"
            middleware_config = ""
            
            if 'thunk' in middleware:
                middleware_imports += "import thunk from 'redux-thunk';\n"
                middleware_config += "thunk, "
                middleware.remove('thunk')
            
            for mw in middleware:
                middleware_imports += f"import {mw} from './{mw}';\n"
                middleware_config += f"{mw}, "
            
            middleware_setup = f"const middlewareEnhancer = applyMiddleware({middleware_config.rstrip(', ')});\n" if middleware_config else ""
            
            return f"""import {{ createStore, combineReducers{typescript and ", Store" or ""} }} from 'redux';
{middleware_imports}{reducer_imports}

const rootReducer = combineReducers({{
{reducer_config}}});

{typescript and "export type RootState = ReturnType<typeof rootReducer>;\n" or ""}
{middleware_setup}
export const store = createStore(rootReducer{middleware_setup and ", middlewareEnhancer" or ""});
"""

    @staticmethod
    def redux_slice(context: Dict[str, Any]) -> str:
        """
        Generate a Redux Toolkit slice for a React project.
        
        Args:
            context: Dictionary containing slice information:
                - name: Name of the slice
                - typescript: Whether the project uses TypeScript
                - initial_state: Initial state of the slice
                - reducers: List of reducers to include
                - extra_reducers: List of extra reducers to include
                - async_thunks: List of async thunks to include
        
        Returns:
            String containing the Redux slice
        """
        name = context.get('name', 'counter')
        typescript = context.get('typescript', True)
        initial_state = context.get('initial_state', {})
        reducers = context.get('reducers', [])
        extra_reducers = context.get('extra_reducers', [])
        async_thunks = context.get('async_thunks', [])
        
        # Default initial state if not provided
        if not initial_state:
            if name == 'counter':
                initial_state = {'value': 0, 'status': 'idle'}
            elif name == 'auth':
                initial_state = {'user': None, 'token': None, 'status': 'idle', 'error': None}
            elif name == 'todos':
                initial_state = {'items': [], 'status': 'idle', 'error': None}
            else:
                initial_state = {'status':