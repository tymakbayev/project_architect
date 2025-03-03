from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
import tempfile
import logging
from typing import Dict, Any, Optional
import asyncio
from pydantic import BaseModel

from src.project_generator import ProjectGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Project Generator API",
    description="API for generating project structures and code based on descriptions",
    version="1.0.0"
)

# Initialize project generator
project_generator = ProjectGenerator()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define request and response models
class ProjectRequest(BaseModel):
    description: str
    output_format: Optional[str] = "zip"  # 'zip' or 'files'

class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str

class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    project_type: Optional[str] = None
    files: Optional[list] = None
    error: Optional[str] = None

@app.post("/projects", response_model=ProjectResponse)
async def generate_project(request: ProjectRequest):
    """
    Start generating a project based on the provided description.
    
    Returns a project ID that can be used to check status and download the result.
    """
    try:
        project_id = await project_generator.generate_project_async(request.description)
        return {
            "project_id": project_id,
            "status": "in_progress",
            "message": "Project generation started"
        }
    except Exception as e:
        logger.error(f"Error starting project generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}", response_model=ProjectStatusResponse)
async def get_project_status(project_id: str):
    """
    Get the status of a project generation task.
    """
    try:
        project = project_generator.get_project(project_id)
        response = {
            "project_id": project_id,
            "status": project["status"]
        }
        
        if project["status"] == "completed":
            response["project_type"] = project.get("project_type")
            response["files"] = project.get("files")
        elif project["status"] == "failed":
            response["error"] = project.get("error")
            
        return response
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    except Exception as e:
        logger.error(f"Error getting project status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/download")
async def download_project(project_id: str):
    """
    Download the generated project as a zip archive.
    """
    try:
        project = project_generator.get_project(project_id)
        
        if project["status"] != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Project is not ready for download. Current status: {project['status']}"
            )
        
        # Create a temporary directory for the project files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Get project files
            files = project_generator.get_project_files(project_id)
            
            # Save files to the temporary directory
            project_generator.output_manager.save_project_files(files, temp_dir)
            
            # Create a zip archive
            zip_path = project_generator.output_manager.create_project_archive(
                temp_dir, 
                os.path.join(tempfile.gettempdir(), f"project_{project_id}.zip")
            )
            
            # Return the zip file
            return FileResponse(
                path=zip_path,
                filename=f"project_{project_id}.zip",
                media_type="application/zip"
            )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    except Exception as e:
        logger.error(f"Error downloading project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/sync", response_model=ProjectStatusResponse)
def generate_project_sync(request: ProjectRequest, background_tasks: BackgroundTasks):
    """
    Generate a project synchronously (blocking operation).
    
    This endpoint will block until the project is generated.
    For large projects, use the asynchronous endpoint instead.
    """
    try:
        # Generate project
        temp_dir = tempfile.mkdtemp()
        result = project_generator.generate_project(request.description, temp_dir)
        
        # Schedule cleanup of temporary files
        background_tasks.add_task(
            project_generator.output_manager.cleanup_temp_files, temp_dir
        )
        
        return {
            "project_id": result["project_id"],
            "status": "completed",
            "project_type": result["project_type"],
            "files": result["files"]
        }
    except Exception as e:
        logger.error(f"Error in synchronous project generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the API with: uvicorn src.interfaces.api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
