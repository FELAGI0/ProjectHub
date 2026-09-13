"""Import all SQLAlchemy models so they are registered in metadata.

This module is imported by Alembic's env.py and by the application
startup to ensure all models are visible to SQLAlchemy and Alembic.
"""

from app.modules.project_members import models as _project_members_models  # noqa: F401
from app.modules.projects import models as _projects_models  # noqa: F401
from app.modules.tasks import models as _tasks_models  # noqa: F401
from app.modules.users import models as _users_models  # noqa: F401
