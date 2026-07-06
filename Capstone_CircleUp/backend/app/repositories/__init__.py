"""
Repositories package — data access layer for CircleUp.

All direct SQLAlchemy queries live here.
Services import from this package instead of writing raw DB queries.
"""

from app.repositories.user_repo import (  # noqa: F401
    get_by_id as get_user_by_id,
    get_by_email as get_user_by_email,
    create as create_user,
    update as update_user,
)

from app.repositories.activity_repo import (  # noqa: F401
    get_by_id as get_activity_by_id,
    create as create_activity,
    update as update_activity,
    get_all as get_all_activities,
    get_by_creator as get_activities_by_creator,
    count_approved_participants,
)

from app.repositories.participation_repo import (  # noqa: F401
    get_by_id as get_request_by_id,
    get_by_activity_and_user,
    get_by_activity as get_requests_by_activity,
    get_by_user as get_requests_by_user,
    get_approved_by_activity,
    create as create_request,
    update as update_request,
)