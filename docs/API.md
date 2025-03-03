# Project Architect API Documentation

## Overview

Project Architect provides a RESTful API for programmatically analyzing project descriptions and generating complete project architectures, structures, and code files for various technology stacks. This document describes the available endpoints, request/response formats, authentication methods, and usage examples.

## Base URL

```
https://api.project-architect.example.com/v1
```

For local development:

```
http://localhost:8000/v1
```

## Authentication

The API uses API key authentication. You must include your API key in the request headers:

```
Authorization: Bearer YOUR_API_KEY
```

To obtain an API key, please contact the Project Architect team or register through the web interface.

## Rate Limiting

The API is rate-limited to protect our services and ensure fair usage:

- 60 requests per minute per API key
- 1000 requests per day per API key

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1620000000
```

## API Endpoints

### Project Analysis

#### Analyze Project Description

```
POST /analyze
```

Analyzes a project description to determine its type, requirements, and recommended architecture.

**Request Body:**

```json
{
  "project_name": "my_awesome_app",
  "description": "A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality.",
  "additional_context": {
    "target_audience": "individual users",
    "deployment_environment": "cloud",
    "preferred_technologies": ["python", "react"]
  }
}
```

**Response:**

```json
{
  "request_id": "req_123456789",
  "status": "success",
  "data": {
    "project_type": {
      "type": "web_application",
      "subtype": "fullstack",
      "confidence": 0.95
    },
    "requirements": [
      {
        "id": "req_1",
        "description": "User authentication system",
        "category": "security",
        "priority": "high"
      },
      {
        "id": "req_2",
        "description": "Expense tracking functionality",
        "category": "core_feature",
        "priority": "high"
      },
      {
        "id": "req_3",
        "description": "Dashboard visualization",
        "category": "ui",
        "priority": "medium"
      },
      {
        "id": "req_4",
        "description": "CSV export functionality",
        "category": "data_processing",
        "priority": "low"
      }
    ],
    "recommended_technologies": {
      "frontend": ["react", "typescript", "chart.js"],
      "backend": ["python", "fastapi", "sqlalchemy"],
      "database": ["postgresql"],
      "deployment": ["docker", "aws"]
    }
  }
}
```

### Architecture Generation

#### Generate Architecture Plan

```
POST /architecture
```

Generates a detailed architecture plan based on project analysis.

**Request Body:**

```json
{
  "project_name": "my_awesome_app",
  "description": "A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality.",
  "project_type": {
    "type": "web_application",
    "subtype": "fullstack"
  },
  "requirements": [
    {
      "id": "req_1",
      "description": "User authentication system",
      "category": "security",
      "priority": "high"
    },
    {
      "id": "req_2",
      "description": "Expense tracking functionality",
      "category": "core_feature",
      "priority": "high"
    }
  ],
  "preferred_technologies": {
    "frontend": ["react"],
    "backend": ["python", "fastapi"],
    "database": ["postgresql"]
  }
}
```

**Response:**

```json
{
  "request_id": "req_123456790",
  "status": "success",
  "data": {
    "architecture_plan": {
      "components": [
        {
          "id": "comp_1",
          "name": "Frontend Application",
          "type": "frontend",
          "description": "React-based SPA for user interface",
          "technologies": ["react", "typescript", "chart.js"],
          "responsibilities": [
            "User interface rendering",
            "Client-side form validation",
            "Data visualization"
          ]
        },
        {
          "id": "comp_2",
          "name": "Backend API",
          "type": "backend",
          "description": "FastAPI-based REST API",
          "technologies": ["python", "fastapi", "sqlalchemy"],
          "responsibilities": [
            "Authentication and authorization",
            "Business logic processing",
            "Database operations"
          ]
        },
        {
          "id": "comp_3",
          "name": "Database",
          "type": "database",
          "description": "PostgreSQL database for data storage",
          "technologies": ["postgresql"],
          "responsibilities": [
            "Data persistence",
            "Data integrity",
            "Query processing"
          ]
        }
      ],
      "dependencies": [
        {
          "source": "comp_1",
          "target": "comp_2",
          "type": "http",
          "description": "Frontend communicates with backend via REST API"
        },
        {
          "source": "comp_2",
          "target": "comp_3",
          "type": "sql",
          "description": "Backend connects to database for data persistence"
        }
      ],
      "data_flows": [
        {
          "id": "flow_1",
          "source": "comp_1",
          "target": "comp_2",
          "description": "User authentication requests",
          "data_format": "JSON",
          "protocol": "HTTPS"
        },
        {
          "id": "flow_2",
          "source": "comp_2",
          "target": "comp_3",
          "description": "Database queries for user data",
          "data_format": "SQL",
          "protocol": "TCP"
        }
      ],
      "deployment_diagram": {
        "environments": [
          {
            "name": "Production",
            "components": [
              {
                "component_id": "comp_1",
                "hosting": "AWS S3 + CloudFront"
              },
              {
                "component_id": "comp_2",
                "hosting": "AWS ECS"
              },
              {
                "component_id": "comp_3",
                "hosting": "AWS RDS"
              }
            ]
          },
          {
            "name": "Development",
            "components": [
              {
                "component_id": "comp_1",
                "hosting": "Local Node.js server"
              },
              {
                "component_id": "comp_2",
                "hosting": "Local Python environment"
              },
              {
                "component_id": "comp_3",
                "hosting": "Docker container"
              }
            ]
          }
        ]
      }
    }
  }
}
```

### Project Structure Generation

#### Generate Project Structure

```
POST /structure
```

Generates a project structure based on the architecture plan.

**Request Body:**

```json
{
  "project_name": "my_awesome_app",
  "architecture_plan": {
    "components": [
      {
        "id": "comp_1",
        "name": "Frontend Application",
        "type": "frontend",
        "technologies": ["react", "typescript"]
      },
      {
        "id": "comp_2",
        "name": "Backend API",
        "type": "backend",
        "technologies": ["python", "fastapi"]
      }
    ]
  },
  "preferred_structure": "monorepo"
}
```

**Response:**

```json
{
  "request_id": "req_123456791",
  "status": "success",
  "data": {
    "project_structure": {
      "root": {
        "name": "my_awesome_app",
        "type": "directory",
        "children": [
          {
            "name": "frontend",
            "type": "directory",
            "children": [
              {
                "name": "src",
                "type": "directory",
                "children": [
                  {
                    "name": "components",
                    "type": "directory",
                    "children": []
                  },
                  {
                    "name": "pages",
                    "type": "directory",
                    "children": []
                  },
                  {
                    "name": "App.tsx",
                    "type": "file",
                    "description": "Main application component"
                  },
                  {
                    "name": "index.tsx",
                    "type": "file",
                    "description": "Application entry point"
                  }
                ]
              },
              {
                "name": "package.json",
                "type": "file",
                "description": "Frontend dependencies and scripts"
              },
              {
                "name": "tsconfig.json",
                "type": "file",
                "description": "TypeScript configuration"
              }
            ]
          },
          {
            "name": "backend",
            "type": "directory",
            "children": [
              {
                "name": "app",
                "type": "directory",
                "children": [
                  {
                    "name": "api",
                    "type": "directory",
                    "children": []
                  },
                  {
                    "name": "models",
                    "type": "directory",
                    "children": []
                  },
                  {
                    "name": "main.py",
                    "type": "file",
                    "description": "Application entry point"
                  }
                ]
              },
              {
                "name": "requirements.txt",
                "type": "file",
                "description": "Python dependencies"
              }
            ]
          },
          {
            "name": "README.md",
            "type": "file",
            "description": "Project documentation"
          },
          {
            "name": "docker-compose.yml",
            "type": "file",
            "description": "Docker Compose configuration"
          }
        ]
      }
    }
  }
}
```

### Code Generation

#### Generate Code Files

```
POST /code
```

Generates code files based on the project structure and architecture plan.

**Request Body:**

```json
{
  "project_name": "my_awesome_app",
  "architecture_plan": {
    "components": [
      {
        "id": "comp_1",
        "name": "Frontend Application",
        "type": "frontend",
        "technologies": ["react", "typescript"]
      },
      {
        "id": "comp_2",
        "name": "Backend API",
        "type": "backend",
        "technologies": ["python", "fastapi"]
      }
    ]
  },
  "project_structure": {
    "root": {
      "name": "my_awesome_app",
      "type": "directory",
      "children": [
        {
          "name": "backend",
          "type": "directory",
          "children": [
            {
              "name": "app",
              "type": "directory",
              "children": [
                {
                  "name": "main.py",
                  "type": "file",
                  "description": "Application entry point"
                }
              ]
            }
          ]
        }
      ]
    }
  },
  "files_to_generate": [
    "backend/app/main.py"
  ]
}
```

**Response:**

```json
{
  "request_id": "req_123456792",
  "status": "success",
  "data": {
    "generated_files": [
      {
        "path": "backend/app/main.py",
        "content": "from fastapi import FastAPI, Depends, HTTPException\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI(title=\"My Awesome App API\", version=\"0.1.0\")\n\n# Configure CORS\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[\"*\"],\n    allow_credentials=True,\n    allow_methods=[\"*\"],\n    allow_headers=[\"*\"],\n)\n\n@app.get(\"/\")\nasync def root():\n    return {\"message\": \"Welcome to My Awesome App API\"}\n\nif __name__ == \"__main__\":\n    import uvicorn\n    uvicorn.run(app, host=\"0.0.0.0\", port=8000)\n"
      }
    ]
  }
}
```

### Dependency Management

#### Generate Dependency Specifications

```
POST /dependencies
```

Generates dependency specifications for the project.

**Request Body:**

```json
{
  "project_name": "my_awesome_app",
  "architecture_plan": {
    "components": [
      {
        "id": "comp_1",
        "name": "Frontend Application",
        "type": "frontend",
        "technologies": ["react", "typescript"]
      },
      {
        "id": "comp_2",
        "name": "Backend API",
        "type": "backend",
        "technologies": ["python", "fastapi"]
      }
    ]
  }
}
```

**Response:**

```json
{
  "request_id": "req_123456793",
  "status": "success",
  "data": {
    "dependencies": [
      {
        "component_id": "comp_1",
        "file_path": "frontend/package.json",
        "content": {
          "name": "my-awesome-app-frontend",
          "version": "0.1.0",
          "private": true,
          "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.4.0",
            "axios": "^1.1.0",
            "chart.js": "^4.0.0",
            "react-chartjs-2": "^5.0.0"
          },
          "devDependencies": {
            "typescript": "^4.8.0",
            "@types/react": "^18.0.0",
            "@types/react-dom": "^18.0.0"
          },
          "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject"
          }
        }
      },
      {
        "component_id": "comp_2",
        "file_path": "backend/requirements.txt",
        "content": "fastapi==0.95.0\nuvicorn==0.21.1\npydantic==1.10.7\nsqlalchemy==2.0.9\npsycopg2-binary==2.9.6\npython-jose==3.3.0\npasslib==1.7.4\npython-multipart==0.0.6\n"
      }
    ]
  }
}
```

### Complete Project Generation

#### Generate Complete Project

```
POST /generate
```

Performs end-to-end project generation, from analysis to code generation.

**Request Body:**

```json
{
  "project_name": "my_awesome_app",
  "description": "A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality.",
  "additional_context": {
    "target_audience": "individual users",
    "deployment_environment": "cloud",
    "preferred_technologies": ["python", "react"]
  }
}
```

**Response:**

```json
{
  "request_id": "req_123456794",
  "status": "success",
  "data": {
    "project_id": "proj_987654321",
    "download_url": "https://api.project-architect.example.com/v1/download/proj_987654321",
    "expires_at": "2023-05-01T12:00:00Z",
    "summary": {
      "project_type": {
        "type": "web_application",
        "subtype": "fullstack"
      },
      "components": [
        "Frontend (React)",
        "Backend API (FastAPI)",
        "Database (PostgreSQL)"
      ],
      "file_count": 42,
      "directory_count": 15
    }
  }
}
```

#### Download Generated Project

```
GET /download/{project_id}
```

Downloads the generated project as a ZIP file.

**Parameters:**

- `project_id`: The ID of the generated project

**Response:**

A ZIP file containing the complete project structure and files.

### Status Endpoints

#### Check Generation Status

```
GET /status/{request_id}
```

Checks the status of an asynchronous generation request.

**Parameters:**

- `request_id`: The ID of the request to check

**Response:**

```json
{
  "request_id": "req_123456794",
  "status": "processing",
  "progress": 65,
  "estimated_completion_time": "2023-04-15T10:30:00Z",
  "message": "Generating code files..."
}
```

#### Health Check

```
GET /health
```

Checks the health status of the API.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "3d 12h 5m",
  "services": {
    "anthropic_api": "operational",
    "github_api": "operational",
    "database": "operational"
  }
}
```

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK`: The request was successful
- `201 Created`: The resource was successfully created
- `400 Bad Request`: The request was invalid or malformed
- `401 Unauthorized`: Authentication failed or was not provided
- `403 Forbidden`: The authenticated user does not have permission to access the resource
- `404 Not Found`: The requested resource was not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: An error occurred on the server

Error responses follow this format:

```json
{
  "status": "error",
  "error": {
    "code": "invalid_request",
    "message": "Invalid project description",
    "details": "Project description must be at least 10 characters long"
  }
}
```

## Webhooks

For long-running operations, you can register a webhook URL to receive notifications when the operation completes:

```
POST /generate
X-Webhook-URL: https://your-server.com/webhook
```

When the operation completes, a POST request will be sent to your webhook URL with the following payload:

```json
{
  "event": "project.generated",
  "request_id": "req_123456794",
  "project_id": "proj_987654321",
  "status": "success",
  "timestamp": "2023-04-15T10:35:00Z",
  "data": {
    "download_url": "https://api.project-architect.example.com/v1/download/proj_987654321",
    "expires_at": "2023-05-01T12:00:00Z"
  }
}
```

## SDK Examples

### Python

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.project-architect.example.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Generate a complete project
response = requests.post(
    f"{BASE_URL}/generate",
    headers=headers,
    json={
        "project_name": "my_awesome_app",
        "description": "A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality.",
        "additional_context": {
            "preferred_technologies": ["python", "react"]
        }
    }
)

if response.status_code == 200:
    data = response.json()
    project_id = data["data"]["project_id"]
    download_url = data["data"]["download_url"]
    print(f"Project generated successfully. Download URL: {download_url}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.project-architect.example.com/v1';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// Generate a complete project
axios.post(`${BASE_URL}/generate`, {
  project_name: 'my_awesome_app',
  description: 'A web application for tracking personal expenses with user authentication, dashboard visualization, and CSV export functionality.',
  additional_context: {
    preferred_technologies: ['python', 'react']
  }
}, { headers })
  .then(response => {
    const { project_id, download_url } = response.data.data;
    console.log(`Project generated successfully. Download URL: ${download_url}`);
  })
  .catch(error => {
    console.error('Error:', error.response ? error.response.status : error.message);
    console.error(error.response ? error.response.data : error);
  });
```

## API Versioning

The API is versioned using URL path versioning. The current version is `v1`. When breaking changes are introduced, a new version will be released, and the old version will be maintained for a deprecation period.

## Support

If you encounter any issues or have questions about the API, please contact our support team at support@project-architect.example.com or open an issue on our GitHub repository.

## Changelog

### v1.0.0 (2023-04-01)

- Initial release of the Project Architect API
- Support for project analysis, architecture generation, structure generation, code generation, and dependency management
- Support for complete end-to-end project generation

### v1.1.0 (2023-05-15)

- Added support for custom templates
- Improved error handling and validation
- Enhanced project type detection
- Added support for more technology stacks

## Future Roadmap

- GraphQL API support
- Real-time collaboration features
- Integration with CI/CD platforms
- Support for more complex project types
- AI-assisted code customization
- Project evolution and maintenance recommendations