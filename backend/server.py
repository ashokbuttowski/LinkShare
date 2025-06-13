from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
import requests
import re
from bs4 import BeautifulSoup
import asyncio
import aiohttp

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Create the main app without a prefix
app = FastAPI(title="LinkShare API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LinkCreate(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Link(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LinkMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = await db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return User(**user)

# Metadata extraction functions
async def extract_metadata_from_url(url: str) -> LinkMetadata:
    """Extract metadata from a URL using server-side scraping"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return LinkMetadata()
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = None
                og_title = soup.find('meta', property='og:title')
                if og_title and og_title.get('content'):
                    title = og_title['content']
                elif soup.title:
                    title = soup.title.string
                
                # Extract description
                description = None
                og_desc = soup.find('meta', property='og:description')
                if og_desc and og_desc.get('content'):
                    description = og_desc['content']
                else:
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        description = meta_desc['content']
                
                # Extract image
                image_url = None
                og_image = soup.find('meta', property='og:image')
                if og_image and og_image.get('content'):
                    image_url = og_image['content']
                else:
                    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                    if twitter_image and twitter_image.get('content'):
                        image_url = twitter_image['content']
                
                # Make sure image URL is absolute
                if image_url and not image_url.startswith('http'):
                    from urllib.parse import urljoin
                    image_url = urljoin(url, image_url)
                
                return LinkMetadata(
                    title=title[:200] if title else None,  # Limit title length
                    description=description[:500] if description else None,  # Limit description length
                    image_url=image_url
                )
    
    except Exception as e:
        logger.warning(f"Failed to extract metadata from {url}: {str(e)}")
        return LinkMetadata()

# Authentication Routes
@api_router.post("/auth/register", response_model=Token)
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(email=user_data.email)
    hashed_password = hash_password(user_data.password)
    
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    # Create JWT token
    token = create_jwt_token(user.id, user.email)
    return Token(access_token=token)

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create JWT token
    token = create_jwt_token(user["id"], user["email"])
    return Token(access_token=token)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Link Routes
@api_router.post("/links/extract-metadata", response_model=LinkMetadata)
async def extract_link_metadata(url_data: dict, current_user: User = Depends(get_current_user)):
    """Extract metadata from a URL"""
    url = url_data.get('url')
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    metadata = await extract_metadata_from_url(url)
    return metadata

@api_router.post("/links", response_model=Link)
async def create_link(link_data: LinkCreate, current_user: User = Depends(get_current_user)):
    # If metadata is not provided, try to extract it
    if not link_data.title and not link_data.description and not link_data.image_url:
        try:
            metadata = await extract_metadata_from_url(link_data.url)
            link_data.title = metadata.title
            link_data.description = metadata.description
            link_data.image_url = metadata.image_url
        except Exception as e:
            logger.warning(f"Failed to extract metadata during link creation: {str(e)}")
    
    link = Link(
        user_id=current_user.id,
        url=link_data.url,
        title=link_data.title,
        description=link_data.description,
        image_url=link_data.image_url
    )
    
    await db.links.insert_one(link.dict())
    return link

@api_router.get("/links", response_model=List[Link])
async def get_user_links(current_user: User = Depends(get_current_user)):
    links = await db.links.find({"user_id": current_user.id}).sort("created_at", -1).to_list(1000)
    return [Link(**link) for link in links]

@api_router.delete("/links/{link_id}")
async def delete_link(link_id: str, current_user: User = Depends(get_current_user)):
    result = await db.links.delete_one({"id": link_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    return {"message": "Link deleted successfully"}

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

# CORS middleware MUST be added AFTER including routers
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:10001", "http://localhost:3000", "*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()