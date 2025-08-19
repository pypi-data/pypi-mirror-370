from datetime import datetime, timedelta, UTC
from typing import Dict, Type, Callable,Any

import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from abs_exception_core.exceptions import UnauthorizedError,ValidationError


# === JWT Setup ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

# === Password Hashing ===

class JWTFunctions:
    def __init__(self,secret_key: str,algorithm: str,expire_minutes: int=None):
        """
        Args:
            secret_key (str): The secret key for the JWT token.
            algorithm (str): The algorithm for the JWT token.
            expire_minutes (int): The expiration time for the JWT token in minutes.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def verify_password(self,plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password using the password hashing context.

        Args:
            plain_password (str): The plain password to verify.
            hashed_password (str): The hashed password to verify against.
        
        Returns:
            bool: True if the password is verified, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self,password: str) -> str:
        """
        Generate a hashed password using the password hashing context.

        Args:
            password (str): The plain password to hash.
        
        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)


    # === Token Dependencies ===

    async def get_token(self,token=Depends(bearer_scheme)) -> str:
        """
        Get the token from the bearer scheme.

        Args:
            token (str): The token to get.
        
        Returns:
            str: The token without the bearer prefix.
        """
        return str(token.credentials)

    # === JWT Token Creation & Decoding ===

    def create_jwt_token(self,data: dict, expires_delta: timedelta=None) -> str:
        """
        Create a JWT token.

        Args:
            data (dict): The data to encode in the token.
            expires_delta (timedelta): The expiration time for the token.
        
        Returns:
            str: The JWT token.
        """
        payload = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=self.expire_minutes
            )
        payload.update({"exp": expire})
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_jwt(self,token: str) -> dict:
        """
        Decode a JWT token.

        Args:
            token (str): The token to decode.
        
        Returns:
            dict: The decoded token.
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError(detail="Token has expired")
        except jwt.InvalidTokenError:
            raise  ValidationError(detail="Invalid token")

    def get_data(self,token: str = Depends(get_token)) -> Dict:
        """
        Get the data from the JWT token.

        Args:
            token (str): The token to get the data from.
        
        Returns:
            Dict: The decoded token.
        """
        return self.decode_jwt(token)
    
    # === Token Generators ===

    def create_access_token(self,data: Dict, expires_delta: timedelta=None) -> str:
        """
        Create an access token.

        Args:
            data (Dict): The data to encode in the token.
            expires_delta (timedelta): The expiration time for the token.
        
        Returns:
            str: The access token.
        """
        return self.create_jwt_token(data=data, expires_delta=expires_delta)