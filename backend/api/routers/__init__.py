from .about.endpoints import router as about_router
from .healthcheck.endpoints import router as healthcheck_router
from .project.endpoints import router as project_router
from .projects.endpoints import router as projects_router

__all__ = [about_router, healthcheck_router, project_router, projects_router]
