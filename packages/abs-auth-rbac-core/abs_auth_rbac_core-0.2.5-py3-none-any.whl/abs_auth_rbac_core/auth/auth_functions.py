from typing import Callable, Any
from ..models import Users

from abs_exception_core.exceptions import NotFoundError, ValidationError


def get_user_by_attribute(db_session: Callable[...,Any],attribute: str, value: str):
    """
    Get a user by an attribute.

    Args:
        attribute (str): The attribute to get the user by.
        value (str): The value of the attribute.
    
    Returns:
        User: The user object if found, otherwise None.
    """
    with db_session() as session:
        try:
            if not hasattr(Users, attribute):
                raise ValidationError(detail=f"Attribute {attribute} does not exist on the User model")
            
            user = session.query(Users).filter(getattr(Users, attribute) == value).first()

            if not user:
                raise NotFoundError(detail="User not found")
            
            return user
        
        except Exception as e:
            raise e
