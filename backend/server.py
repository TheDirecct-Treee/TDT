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
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
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

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@direct-tree.com')

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Enums
class UserRole(str, Enum):
    CUSTOMER = "customer"
    BUSINESS_OWNER = "business_owner"
    ADMIN = "admin"

class BusinessStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    TRIAL = "trial"

# Bahamas Islands
BAHAMAS_ISLANDS = [
    "New Providence", "Grand Bahama", "Abaco", "Eleuthera", "Exuma", 
    "Andros", "Cat Island", "Long Island", "San Salvador", "Rum Cay",
    "Crooked Island", "Acklins", "Mayaguana", "Inagua", "Bimini",
    "Berry Islands", "Ragged Island"
]

BUSINESS_CATEGORIES = [
    "Restaurant", "Hotel", "Tour Operator", "Transportation", "Retail",
    "Health & Medical", "Construction", "Education", "Legal Services",
    "Barbers", "Make up Artist", "Mechanics", "Electrician", "Handyman", 
    "Plumbers", "Car Cleaning/Detailing", "Photographers", "Bakers", 
    "Graphic Designers", "Cellphone Repairs", "Aestheticians", 
    "Hair Stylist/Braiders", "A/C Technician", "Carpenters", "Catering",
    "Shipping Companies", "Pet Grooming", "Seamstress", "Car Rentals",
    "Fishing Charters", "Other"
]

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole
    phone: Optional[str] = None
    email_verified: bool = False
    verification_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: UserRole
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class EmailVerification(BaseModel):
    token: str

class BusinessProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_name: str
    description: str
    category: str
    island: str
    address: str
    phone: str
    email: EmailStr
    website: Optional[str] = None
    business_hours: Dict[str, str] = {}
    services: List[str] = []
    photos: List[str] = []
    license_number: str
    license_document: Optional[str] = None
    status: BusinessStatus = BusinessStatus.PENDING
    subscription_status: SubscriptionStatus = SubscriptionStatus.TRIAL
    trial_end_date: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    rating_average: float = 0.0
    rating_count: int = 0
    accepts_appointments: bool = False
    appointment_duration: int = 60  # minutes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BusinessCreate(BaseModel):
    business_name: str
    description: str
    category: str
    island: str
    address: str
    phone: str
    email: EmailStr
    website: Optional[str] = None
    business_hours: Dict[str, str] = {}
    services: List[str] = []
    license_number: str
    accepts_appointments: bool = False
    appointment_duration: int = 60

class Review(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    user_id: Optional[str] = None  # None for anonymous reviews
    customer_name: Optional[str] = None  # For anonymous reviews
    rating: int = Field(..., ge=1, le=5)
    comment: str
    is_anonymous: bool = False
    is_approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewCreate(BaseModel):
    business_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    is_anonymous: bool = False
    customer_name: Optional[str] = None

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    customer_id: str
    appointment_date: datetime
    duration: int = 60  # minutes
    service: str
    status: AppointmentStatus = AppointmentStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AppointmentCreate(BaseModel):
    business_id: str
    appointment_date: datetime
    service: str
    notes: Optional[str] = None

# PayPal Models
class SubscriptionRequest(BaseModel):
    plan_id: str

class SubscriptionResponse(BaseModel):
    subscription_id: str
    approval_url: str
    status: str

class PayPalSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    business_id: str
    paypal_subscription_id: str
    plan_id: str
    status: str
    amount: str = "20.00"
    currency: str = "USD"
    trial_days: int = 7
    trial_end_date: datetime
    next_billing_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Photo Models
class PhotoMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    original_filename: str
    cloudinary_url: str
    cloudinary_public_id: str
    optimized_url: str
    thumbnail_url: str
    file_size: int
    content_type: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

# Email utility functions
def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SendGrid"""
    try:
        if SENDGRID_API_KEY == "PLACEHOLDER_SENDGRID_KEY":
            logger.info(f"Email would be sent to {to_email}: {subject}")
            return True
            
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        logger.error(f"Email send error: {str(e)}")
        return False

def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return str(uuid.uuid4())

def send_verification_email(user_email: str, user_name: str, verification_token: str):
    """Send email verification"""
    verification_url = f"{os.environ.get('FRONTEND_URL')}/verify-email?token={verification_token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0ea5e9, #14b8a6); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Welcome to The Direct Tree! 🌳</h1>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <h2 style="color: #1e293b;">Hi {user_name}!</h2>
                <p style="color: #475569; font-size: 16px;">
                    Thanks for joining The Direct Tree - your trusted Bahamas business directory!
                </p>
                <p style="color: #475569; font-size: 16px;">
                    Please verify your email address to activate your account:
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background: linear-gradient(135deg, #f97316, #ec4899); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold;
                              display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #64748b; font-size: 14px;">
                    If the button doesn't work, copy and paste this link: <br>
                    <a href="{verification_url}">{verification_url}</a>
                </p>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <p style="color: #64748b; font-size: 12px; text-align: center;">
                    © 2025 The Direct Tree. Connecting businesses across the Bahamas.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email(user_email, "Verify Your Email - The Direct Tree", html_content)

def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email after verification"""
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0ea5e9, #14b8a6); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Welcome to The Direct Tree! 🎉</h1>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <h2 style="color: #1e293b;">Welcome aboard, {user_name}!</h2>
                <p style="color: #475569; font-size: 16px;">
                    Your email has been verified and your account is now active!
                </p>
                <p style="color: #475569; font-size: 16px;">
                    You can now:
                </p>
                <ul style="color: #475569; font-size: 16px;">
                    <li>Browse businesses across all Bahamas islands</li>
                    <li>Leave reviews and ratings</li>
                    <li>Book appointments with local businesses</li>
                    <li>Connect with trusted, licensed professionals</li>
                </ul>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.environ.get('FRONTEND_URL')}" 
                       style="background: linear-gradient(135deg, #0ea5e9, #14b8a6); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold;
                              display: inline-block;">
                        Start Exploring
                    </a>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(user_email, "Welcome to The Direct Tree!", html_content)

def send_payment_confirmation_email(user_email: str, user_name: str, amount: str):
    """Send payment confirmation email"""
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #22c55e, #16a34a); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Payment Confirmed! ✅</h1>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <h2 style="color: #1e293b;">Thank you, {user_name}!</h2>
                <p style="color: #475569; font-size: 16px;">
                    Your subscription payment of ${amount}/month has been confirmed.
                </p>
                <p style="color: #475569; font-size: 16px;">
                    Your business profile is now active and visible to customers across the Bahamas!
                </p>
                <div style="background: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #166534; margin: 0 0 10px 0;">What's included:</h3>
                    <ul style="color: #166534; margin: 0;">
                        <li>Business profile listing</li>
                        <li>Customer reviews & ratings</li>
                        <li>Photo gallery uploads</li>
                        <li>Appointment booking system</li>
                        <li>Business analytics</li>
                    </ul>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.environ.get('FRONTEND_URL')}/dashboard" 
                       style="background: linear-gradient(135deg, #f97316, #ec4899); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold;
                              display: inline-block;">
                        Go to Dashboard
                    </a>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(user_email, "Payment Confirmed - The Direct Tree", html_content)

def send_appointment_notification(business_email: str, customer_email: str, appointment_details: dict):
    """Send appointment notifications to both business and customer"""
    business_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">New Appointment Booking! 📅</h1>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <h2 style="color: #1e293b;">You have a new appointment request</h2>
                <div style="background: #dbeafe; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Service:</strong> {appointment_details.get('service', 'N/A')}</p>
                    <p style="margin: 5px 0;"><strong>Date & Time:</strong> {appointment_details.get('date', 'N/A')}</p>
                    <p style="margin: 5px 0;"><strong>Customer:</strong> {appointment_details.get('customer', 'N/A')}</p>
                    <p style="margin: 5px 0;"><strong>Notes:</strong> {appointment_details.get('notes', 'None')}</p>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.environ.get('FRONTEND_URL')}/dashboard" 
                       style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold;
                              display: inline-block;">
                        Manage Appointments
                    </a>
                </div>
            </div>
        </body>
    </html>
    """
    
    customer_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #10b981, #059669); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Appointment Request Sent! ✅</h1>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <h2 style="color: #1e293b;">Your appointment request has been submitted</h2>
                <p style="color: #475569; font-size: 16px;">
                    We've sent your appointment request to the business. They will contact you to confirm.
                </p>
                <div style="background: #d1fae5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Service:</strong> {appointment_details.get('service', 'N/A')}</p>
                    <p style="margin: 5px 0;"><strong>Requested Date:</strong> {appointment_details.get('date', 'N/A')}</p>
                    <p style="margin: 5px 0;"><strong>Business:</strong> {appointment_details.get('business', 'N/A')}</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Send to both
    send_email(business_email, "New Appointment Request - The Direct Tree", business_html)
    send_email(customer_email, "Appointment Request Sent - The Direct Tree", customer_html)

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    user = await db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

def filter_profanity(text: str) -> str:
    # Simple profanity filter - you can enhance this
    profanity_words = ['damn', 'shit', 'fuck', 'asshole', 'bitch']  # Add more as needed
    for word in profanity_words:
        text = re.sub(r'\b' + word + r'\b', '*' * len(word), text, flags=re.IGNORECASE)
    return text

# File upload utility functions
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_image_file(file: UploadFile):
    """Validate uploaded image file"""
    # Check file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail=f"Invalid file type. Allowed types: {ALLOWED_IMAGE_TYPES}")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size: 10MB")
    
    return file_size

async def upload_to_cloudinary(file: UploadFile, business_id: str) -> PhotoMetadata:
    """Upload image to Cloudinary and return metadata"""
    try:
        if os.environ.get('CLOUDINARY_CLOUD_NAME') == 'PLACEHOLDER_CLOUD_NAME':
            # Mock response for development
            photo_id = str(uuid.uuid4())
            return PhotoMetadata(
                business_id=business_id,
                original_filename=file.filename,
                cloudinary_url=f"https://mock-cloudinary.com/{photo_id}",
                cloudinary_public_id=photo_id,
                optimized_url=f"https://mock-cloudinary.com/{photo_id}/optimized",
                thumbnail_url=f"https://mock-cloudinary.com/{photo_id}/thumb",
                file_size=validate_image_file(file),
                content_type=file.content_type
            )
        
        # Upload with optimization
        result = cloudinary.uploader.upload(
            file.file,
            folder=f"businesses/{business_id}",
            transformation=[
                {'width': 1920, 'crop': 'limit'},
                {'quality': 'auto:best'},
                {'format': 'webp'}
            ]
        )
        
        # Generate optimized and thumbnail URLs
        optimized_url = cloudinary.CloudinaryImage(result['public_id']).build_url(
            width=800, height=600, crop="fill", quality="auto:best", format="webp"
        )
        
        thumbnail_url = cloudinary.CloudinaryImage(result['public_id']).build_url(
            width=300, height=200, crop="fill", quality="auto:best", format="webp"
        )
        
        return PhotoMetadata(
            business_id=business_id,
            original_filename=file.filename,
            cloudinary_url=result['secure_url'],
            cloudinary_public_id=result['public_id'],
            optimized_url=optimized_url,
            thumbnail_url=thumbnail_url,
            file_size=result['bytes'],
            content_type=file.content_type
        )
        
    except Exception as e:
        logger.error(f"Cloudinary upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Routes
@api_router.get("/")
async def root():
    return {"message": "The Direct Tree - Bahamas Business Directory API"}

@api_router.get("/islands")
async def get_islands():
    return {"islands": BAHAMAS_ISLANDS}

@api_router.get("/categories")
async def get_categories():
    return {"categories": BUSINESS_CATEGORIES}

# Authentication Routes
@api_router.post("/register")
async def register(user_data: UserCreate, background_tasks: BackgroundTasks):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Create user (inactive until verified)
    user = User(**user_data.dict())
    user.password = hashed_password
    user.email_verified = False
    user.verification_token = verification_token
    user.is_active = False
    
    await db.users.insert_one(user.dict())
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        user.email,
        f"{user.first_name} {user.last_name}",
        verification_token
    )
    
    return {
        "message": "User registered successfully. Please check your email to verify your account.",
        "email": user.email
    }

@api_router.post("/verify-email")
async def verify_email(verification: EmailVerification, background_tasks: BackgroundTasks):
    # Find user with verification token
    user_data = await db.users.find_one({"verification_token": verification.token})
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    
    user = User(**user_data)
    
    # Update user as verified and active
    await db.users.update_one(
        {"id": user.id},
        {
            "$set": {
                "email_verified": True,
                "is_active": True,
                "verification_token": None
            }
        }
    )
    
    # Send welcome email
    background_tasks.add_task(
        send_welcome_email,
        user.email,
        f"{user.first_name} {user.last_name}"
    )
    
    # Create JWT token
    token = create_jwt_token(user.id, user.role.value)
    
    return {
        "message": "Email verified successfully",
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
    }

@api_router.post("/login")
async def login(login_data: UserLogin):
    # Find user
    user_data = await db.users.find_one({"email": login_data.email})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(**user_data)
    
    # Check if email is verified
    if not user.email_verified:
        raise HTTPException(status_code=401, detail="Please verify your email before logging in")
    
    # Verify password
    if not verify_password(login_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token = create_jwt_token(user.id, user.role.value)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role
        }
    }

@api_router.post("/resend-verification")
async def resend_verification(email: EmailStr, background_tasks: BackgroundTasks):
    # Find user
    user_data = await db.users.find_one({"email": email})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = User(**user_data)
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new verification token
    verification_token = generate_verification_token()
    
    # Update user with new token
    await db.users.update_one(
        {"id": user.id},
        {"$set": {"verification_token": verification_token}}
    )
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        user.email,
        f"{user.first_name} {user.last_name}",
        verification_token
    )
    
    return {"message": "Verification email sent"}

# Business Routes
@api_router.post("/business/create", response_model=BusinessProfile)
async def create_business(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.BUSINESS_OWNER:
        raise HTTPException(status_code=403, detail="Only business owners can create businesses")
    
    # Check if user already has a business
    existing_business = await db.businesses.find_one({"user_id": current_user.id})
    if existing_business:
        raise HTTPException(status_code=400, detail="You already have a business registered")
    
    # Create business with user_id
    business_dict = business_data.dict()
    business_dict["user_id"] = current_user.id
    business = BusinessProfile(**business_dict)
    
    await db.businesses.insert_one(business.dict())
    return business

@api_router.get("/business/{business_id}", response_model=BusinessProfile)
async def get_business(business_id: str):
    business_data = await db.businesses.find_one({"id": business_id})
    if not business_data:
        raise HTTPException(status_code=404, detail="Business not found")
    return BusinessProfile(**business_data)

@api_router.get("/businesses")
async def get_businesses(
    island: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = "approved",
    skip: int = 0,
    limit: int = 50
):
    query = {}
    if island:
        query["island"] = island
    if category:
        query["category"] = category
    if status:
        query["status"] = status
    
    businesses = await db.businesses.find(query).skip(skip).limit(limit).to_list(limit)
    return [BusinessProfile(**business) for business in businesses]

# Photo upload routes
@api_router.post("/business/{business_id}/upload-photos")
async def upload_business_photos(
    business_id: str,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    # Verify business ownership
    business = await db.businesses.find_one({"id": business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    uploaded_photos = []
    
    for file in files:
        try:
            # Upload to Cloudinary
            photo_metadata = await upload_to_cloudinary(file, business_id)
            
            # Save metadata to database
            await db.photos.insert_one(photo_metadata.dict())
            
            # Add photo URL to business photos array
            await db.businesses.update_one(
                {"id": business_id},
                {"$push": {"photos": photo_metadata.optimized_url}}
            )
            
            uploaded_photos.append({
                "id": photo_metadata.id,
                "url": photo_metadata.optimized_url,
                "thumbnail": photo_metadata.thumbnail_url
            })
            
        except Exception as e:
            logger.error(f"Error uploading photo {file.filename}: {str(e)}")
            continue
    
    return {
        "message": f"Successfully uploaded {len(uploaded_photos)} photos",
        "photos": uploaded_photos
    }

@api_router.get("/business/{business_id}/photos")
async def get_business_photos(business_id: str):
    photos = await db.photos.find({"business_id": business_id}).to_list(100)
    return [PhotoMetadata(**photo) for photo in photos]

@api_router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: str, current_user: User = Depends(get_current_user)):
    # Get photo metadata
    photo_data = await db.photos.find_one({"id": photo_id})
    if not photo_data:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    photo = PhotoMetadata(**photo_data)
    
    # Verify business ownership
    business = await db.businesses.find_one({"id": photo.business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Delete from Cloudinary
        if os.environ.get('CLOUDINARY_CLOUD_NAME') != 'PLACEHOLDER_CLOUD_NAME':
            cloudinary.uploader.destroy(photo.cloudinary_public_id)
        
        # Remove from database
        await db.photos.delete_one({"id": photo_id})
        
        # Remove from business photos array
        await db.businesses.update_one(
            {"id": photo.business_id},
            {"$pull": {"photos": photo.optimized_url}}
        )
        
        return {"message": "Photo deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting photo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete photo")

# Review Routes
@api_router.post("/review/create", response_model=Review)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    # Check if business exists
    business = await db.businesses.find_one({"id": review_data.business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Filter profanity
    filtered_comment = filter_profanity(review_data.comment)
    
    review = Review(**review_data.dict())
    review.comment = filtered_comment
    
    if not review.is_anonymous:
        review.user_id = current_user.id
    else:
        review.user_id = None
    
    await db.reviews.insert_one(review.dict())
    
    # Update business rating
    await update_business_rating(review_data.business_id)
    
    return review

@api_router.get("/business/{business_id}/reviews")
async def get_business_reviews(
    business_id: str,
    approved_only: bool = True,
    skip: int = 0,
    limit: int = 20
):
    query = {"business_id": business_id}
    if approved_only:
        query["is_approved"] = True
    
    reviews = await db.reviews.find(query).skip(skip).limit(limit).to_list(limit)
    return [Review(**review) for review in reviews]

# Appointment Routes
@api_router.post("/appointment/create", response_model=Appointment)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = Depends()
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can book appointments")
    
    # Check if business exists and accepts appointments
    business = await db.businesses.find_one({"id": appointment_data.business_id})
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business_obj = BusinessProfile(**business)
    if not business_obj.accepts_appointments:
        raise HTTPException(status_code=400, detail="This business does not accept appointments")
    
    appointment = Appointment(**appointment_data.dict())
    appointment.customer_id = current_user.id
    appointment.duration = business_obj.appointment_duration
    
    await db.appointments.insert_one(appointment.dict())
    
    # Send appointment notifications
    background_tasks.add_task(
        send_appointment_notification,
        business_obj.email,
        current_user.email,
        {
            "service": appointment.service,
            "date": appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p"),
            "customer": f"{current_user.first_name} {current_user.last_name}",
            "business": business_obj.business_name,
            "notes": appointment.notes or "None"
        }
    )
    
    return appointment

@api_router.get("/business/{business_id}/appointments")
async def get_business_appointments(
    business_id: str,
    current_user: User = Depends(get_current_user)
):
    # Check if user owns this business
    business = await db.businesses.find_one({"id": business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    appointments = await db.appointments.find({"business_id": business_id}).to_list(100)
    return [Appointment(**appointment) for appointment in appointments]

# Admin Routes
@api_router.get("/admin/businesses/pending")
async def get_pending_businesses(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    businesses = await db.businesses.find({"status": BusinessStatus.PENDING}).to_list(100)
    return [BusinessProfile(**business) for business in businesses]

@api_router.put("/admin/business/{business_id}/approve")
async def approve_business(
    business_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"status": BusinessStatus.APPROVED, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return {"message": "Business approved successfully"}

@api_router.put("/admin/business/{business_id}/reject")
async def reject_business(
    business_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.businesses.update_one(
        {"id": business_id},
        {"$set": {"status": BusinessStatus.REJECTED, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Business not found")
    
    return {"message": "Business rejected"}

@api_router.get("/admin/reviews/pending")
async def get_pending_reviews(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    reviews = await db.reviews.find({"is_approved": False}).to_list(100)
    return [Review(**review) for review in reviews]

@api_router.put("/admin/review/{review_id}/approve")
async def approve_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.reviews.update_one(
        {"id": review_id},
        {"$set": {"is_approved": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {"message": "Review approved successfully"}

# PayPal Routes
@api_router.post("/paypal/create-plan")
async def create_billing_plan():
    try:
        billing_plan = paypalrestsdk.BillingPlan({
            "name": "The Direct Tree Monthly Subscription",
            "description": "$20/month recurring subscription for business owners",
            "type": "INFINITE",
            "payment_definitions": [{
                "name": "Regular payment definition",
                "type": "REGULAR",
                "frequency": "MONTH",
                "frequency_interval": "1",
                "amount": {
                    "value": "20.00",
                    "currency": "USD"
                },
                "cycles": "0"
            }],
            "merchant_preferences": {
                "setup_fee": {
                    "value": "0.00",
                    "currency": "USD"
                },
                "return_url": f"{os.environ.get('FRONTEND_URL')}/subscription/success",
                "cancel_url": f"{os.environ.get('FRONTEND_URL')}/subscription/cancel",
                "auto_bill_amount": "YES",
                "initial_fail_amount_action": "CONTINUE",
                "max_fail_attempts": "3"
            }
        })

        if billing_plan.create():
            if billing_plan.activate():
                # Store in database
                plan_data = {
                    "id": str(uuid.uuid4()),
                    "paypal_plan_id": billing_plan.id,
                    "name": billing_plan.name,
                    "amount": "20.00",
                    "currency": "USD",
                    "status": "ACTIVE",
                    "created_at": datetime.utcnow()
                }
                await db.billing_plans.insert_one(plan_data)
                return {"plan_id": billing_plan.id, "status": "ACTIVE"}
            else:
                raise HTTPException(status_code=500, detail="Failed to activate billing plan")
        else:
            raise HTTPException(status_code=500, detail="Failed to create billing plan")
    except Exception as e:
        logger.error(f"Error creating billing plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/paypal/create-subscription", response_model=SubscriptionResponse)
async def create_subscription(
    request: SubscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        if current_user.role != UserRole.BUSINESS_OWNER:
            raise HTTPException(status_code=403, detail="Only business owners can create subscriptions")
        
        # Get user's business
        business = await db.businesses.find_one({"user_id": current_user.id})
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
        
        # Check if subscription already exists
        existing_subscription = await db.subscriptions.find_one({"user_id": current_user.id})
        if existing_subscription:
            raise HTTPException(status_code=400, detail="Subscription already exists")
        
        # Calculate trial end date
        trial_end = datetime.utcnow() + timedelta(days=7)
        
        billing_agreement = paypalrestsdk.BillingAgreement({
            "name": "The Direct Tree Monthly Subscription",
            "description": "$20/month subscription with 7-day trial",
            "start_date": trial_end.isoformat() + "Z",
            "plan": {
                "id": request.plan_id
            },
            "payer": {
                "payment_method": "paypal",
                "payer_info": {
                    "email": current_user.email
                }
            }
        })

        if billing_agreement.create():
            # Store subscription in database
            subscription_data = PayPalSubscription(
                user_id=current_user.id,
                business_id=business["id"],
                paypal_subscription_id=billing_agreement.id,
                plan_id=request.plan_id,
                status="PENDING",
                trial_end_date=trial_end
            )
            
            await db.subscriptions.insert_one(subscription_data.dict())
            
            # Get approval URL
            approval_url = None
            for link in billing_agreement.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return SubscriptionResponse(
                subscription_id=billing_agreement.id,
                approval_url=approval_url,
                status="PENDING"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create subscription")
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/paypal/execute-subscription/{subscription_id}")
async def execute_subscription(
    subscription_id: str, 
    payer_id: str,
    background_tasks: BackgroundTasks = Depends()
):
    try:
        billing_agreement = paypalrestsdk.BillingAgreement.find(subscription_id)
        
        if billing_agreement.execute({"payer_id": payer_id}):
            # Update subscription status in database
            await db.subscriptions.update_one(
                {"paypal_subscription_id": subscription_id},
                {
                    "$set": {
                        "status": "ACTIVE",
                        "activated_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update business subscription status
            subscription = await db.subscriptions.find_one({"paypal_subscription_id": subscription_id})
            if subscription:
                await db.businesses.update_one(
                    {"id": subscription["business_id"]},
                    {"$set": {"subscription_status": SubscriptionStatus.ACTIVE}}
                )
                
                # Get user info for email
                user = await db.users.find_one({"id": subscription["user_id"]})
                if user:
                    # Send payment confirmation email
                    background_tasks.add_task(
                        send_payment_confirmation_email,
                        user["email"],
                        f"{user['first_name']} {user['last_name']}",
                        "20.00"
                    )
            
            return {"status": "ACTIVE", "message": "Subscription activated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to execute subscription")
    except Exception as e:
        logger.error(f"Error executing subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/paypal/cancel-subscription/{subscription_id}")
async def cancel_subscription(subscription_id: str, current_user: User = Depends(get_current_user)):
    try:
        # Verify user owns this subscription
        subscription = await db.subscriptions.find_one({
            "paypal_subscription_id": subscription_id,
            "user_id": current_user.id
        })
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        billing_agreement = paypalrestsdk.BillingAgreement.find(subscription_id)
        
        cancel_note = {
            "note": "Subscription cancelled by user request"
        }
        
        if billing_agreement.cancel(cancel_note):
            # Update subscription status in database
            await db.subscriptions.update_one(
                {"paypal_subscription_id": subscription_id},
                {
                    "$set": {
                        "status": "CANCELLED",
                        "cancelled_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update business subscription status
            await db.businesses.update_one(
                {"id": subscription["business_id"]},
                {"$set": {"subscription_status": SubscriptionStatus.CANCELLED}}
            )
            
            return {"status": "CANCELLED", "message": "Subscription cancelled successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/paypal/subscription-status")
async def get_user_subscription_status(current_user: User = Depends(get_current_user)):
    try:
        # Get from database
        subscription = await db.subscriptions.find_one({"user_id": current_user.id})
        
        if not subscription:
            return {"status": "NONE", "message": "No subscription found"}
        
        # Verify with PayPal
        billing_agreement = paypalrestsdk.BillingAgreement.find(subscription["paypal_subscription_id"])
        
        # Update database if status changed
        if billing_agreement.state != subscription["status"]:
            await db.subscriptions.update_one(
                {"paypal_subscription_id": subscription["paypal_subscription_id"]},
                {
                    "$set": {
                        "status": billing_agreement.state,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        return {
            "subscription_id": subscription["paypal_subscription_id"],
            "status": billing_agreement.state,
            "amount": subscription["amount"],
            "currency": subscription["currency"],
            "trial_end_date": subscription.get("trial_end_date"),
            "next_billing_date": getattr(billing_agreement.agreement_details, 'next_billing_date', None) if hasattr(billing_agreement, 'agreement_details') else None
        }
    except Exception as e:
        logger.error(f"Error checking subscription status: {str(e)}")
        return {"status": "ERROR", "message": str(e)}

# Utility function to update business rating
async def update_business_rating(business_id: str):
    reviews = await db.reviews.find({"business_id": business_id, "is_approved": True}).to_list(1000)
    if reviews:
        total_rating = sum(review["rating"] for review in reviews)
        average_rating = total_rating / len(reviews)
        await db.businesses.update_one(
            {"id": business_id},
            {"$set": {"rating_average": round(average_rating, 1), "rating_count": len(reviews)}}
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
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