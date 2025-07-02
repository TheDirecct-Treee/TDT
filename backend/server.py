from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
import bcrypt
import jwt
from enum import Enum
import re
import paypalrestsdk
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-here')
security = HTTPBearer()

# PayPal Configuration
paypalrestsdk.configure({
    "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

# Mailgun Configuration
MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
MAILGUN_FROM_EMAIL = os.environ.get('MAILGUN_FROM_EMAIL', 'noreply@direct-tree.com')

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Email utility functions
def send_email(to_email: str, subject: str, html_content: str):
    """Send email using Mailgun"""
    try:
        if not MAILGUN_API_KEY or MAILGUN_API_KEY == "PLACEHOLDER_MAILGUN_KEY":
            logger.info(f"Email would be sent to {to_email}: {subject}")
            return True
            
        # Mailgun API endpoint
        mailgun_url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
        
        # Prepare the email data
        data = {
            "from": f"The Direct Tree <{MAILGUN_FROM_EMAIL}>",
            "to": to_email,
            "subject": subject,
            "html": html_content
        }
        
        # Send email via Mailgun API
        response = requests.post(
            mailgun_url,
            auth=("api", MAILGUN_API_KEY),
            data=data
        )
        
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Email send error: {str(e)}")
        return False