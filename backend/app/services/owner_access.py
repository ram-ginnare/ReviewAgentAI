from fastapi import HTTPException, status
from backend.app.models.user import User

def require_owner_business(user: User, business_id: int):
    if user.role != 'ADMIN' and (user.role != 'BUSINESS_OWNER' or user.business_id != business_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='BUSINESS_ACCESS_FORBIDDEN', headers={'X-Error-Code':'BUSINESS_ACCESS_FORBIDDEN'})
