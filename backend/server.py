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
MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN', 'sandboxf8c8a7f3d9d44ea08c7f8b5c2e1a6b0d.mailgun.org')
MAILGUN_FROM_EMAIL = os.environ.get('MAILGUN_FROM_EMAIL', 'noreply@direct-tree.com')

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
    "Fishing Charters", "Gym", "Personal Trainers", "Other"
]

# Event Categories
EVENT_CATEGORIES = [
    "Concert", "Festival", "Market", "Sports", "Food & Drink", "Art & Culture",
    "Workshop", "Conference", "Charity", "Community", "Religious", "Business",
    "Education", "Health & Wellness", "Family", "Nightlife", "Happy Hour", "Other"
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
    profile_photo: Optional[str] = None  # Main business profile photo
    cover_photo: Optional[str] = None   # Cover/banner photo
    logo: Optional[str] = None          # Business logo
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
    profile_photo: Optional[str] = None
    cover_photo: Optional[str] = None
    logo: Optional[str] = None

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

# Business FAQ Models
class BusinessFAQ(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    business_id: str
    question: str
    answer: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FAQCreate(BaseModel):
    question: str
    answer: str

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    is_active: Optional[bool] = None

# Event Models
class Event(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    island: str
    location: str
    event_date: datetime
    start_time: str
    end_time: str
    organizer_name: str
    organizer_email: EmailStr
    organizer_phone: Optional[str] = None
    ticket_price: Optional[str] = None
    ticket_link: Optional[str] = None
    event_image: Optional[str] = None
    is_paid: bool = False
    payment_date: Optional[datetime] = None
    paypal_payment_id: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EventCreate(BaseModel):
    title: str
    description: str
    category: str
    island: str
    location: str
    event_date: datetime
    start_time: str
    end_time: str
    organizer_name: str
    organizer_email: EmailStr
    organizer_phone: Optional[str] = None
    ticket_price: Optional[str] = None
    ticket_link: Optional[str] = None

class EventPayment(BaseModel):
    event_id: str
    paypal_payment_id: str

# Apartment Listing Models
class ApartmentListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    address: str
    island: str
    bedrooms: int
    bathrooms: int
    monthly_rent: float
    currency: str = "USD"
    property_type: str  # "Apartment", "House", "Condo", "Room", "Studio"
    furnishing: str  # "Furnished", "Semi-Furnished", "Unfurnished"
    amenities: List[str] = []  # ["Pool", "Gym", "Parking", "A/C", "Washer/Dryer", etc.]
    utilities_included: List[str] = []  # ["Water", "Electricity", "Internet", "Cable", etc.]
    lease_duration: str  # "Monthly", "6 Months", "1 Year", "Negotiable"
    available_date: datetime
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    photos: List[str] = []  # URLs to photos
    is_paid: bool = False
    payment_date: Optional[datetime] = None
    paypal_payment_id: Optional[str] = None
    is_active: bool = True
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApartmentListingCreate(BaseModel):
    title: str
    description: str
    address: str
    island: str
    bedrooms: int
    bathrooms: int
    monthly_rent: float
    property_type: str
    furnishing: str
    amenities: List[str] = []
    utilities_included: List[str] = []
    lease_duration: str
    available_date: datetime
    contact_name: str
    contact_email: EmailStr
    contact_phone: str

class ApartmentPayment(BaseModel):
    listing_id: str
    paypal_payment_id: str

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
    """Send email using Mailgun"""
    try:
        if not MAILGUN_API_KEY or MAILGUN_API_KEY == "PLACEHOLDER_MAILGUN_KEY":
            logger.info(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            return True
        
        logger.info(f"Attempting to send email to {to_email} via Mailgun")
        
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
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Mailgun API error: {response.status_code} - {response.text}")
            return False
            
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
            <div style="background: linear-gradient(135deg, #16a34a, #ca8a04); padding: 20px; text-align: center;">
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
                       style="background: linear-gradient(135deg, #16a34a, #ca8a04); 
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
            <div style="background: linear-gradient(135deg, #16a34a, #ca8a04); padding: 20px; text-align: center;">
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
                       style="background: linear-gradient(135deg, #16a34a, #ca8a04); 
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
                        <li>FAQ management</li>
                        <li>Business analytics</li>
                    </ul>
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.environ.get('FRONTEND_URL')}/dashboard" 
                       style="background: linear-gradient(135deg, #16a34a, #ca8a04); 
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
            <div style="background: linear-gradient(135deg, #16a34a, #ca8a04); padding: 20px; text-align: center;">
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
                       style="background: linear-gradient(135deg, #16a34a, #ca8a04); 
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

def send_event_payment_confirmation(organizer_email: str, organizer_name: str, event_title: str, event_date: str):
    """Send event payment confirmation email"""
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #f59e0b, #ec4899); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Event Payment Confirmed! 🎉</h1>
            </div>
            <div style="padding: 20px; background: #f8fafc;">
                <h2 style="color: #1e293b;">Hi {organizer_name}!</h2>
                <p style="color: #475569; font-size: 16px;">
                    Your payment of $5.00 has been confirmed and your event is now live on The Direct Tree!
                </p>
                <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #92400e; margin: 0 0 10px 0;">Event Details:</h3>
                    <p style="color: #92400e; margin: 5px 0;"><strong>Title:</strong> {event_title}</p>
                    <p style="color: #92400e; margin: 5px 0;"><strong>Date:</strong> {event_date}</p>
                </div>
                <p style="color: #475569; font-size: 16px;">
                    Your event will be visible to everyone browsing The Direct Tree. You can manage your event anytime from your organizer dashboard.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.environ.get('FRONTEND_URL')}/events" 
                       style="background: linear-gradient(135deg, #f59e0b, #ec4899); 
                              color: white; 
                              padding: 15px 30px; 
                              text-decoration: none; 
                              border-radius: 25px; 
                              font-weight: bold;
                              display: inline-block;">
                        View Your Event
                    </a>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(organizer_email, f"Event Payment Confirmed - {event_title}", html_content)

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

@api_router.get("/event-categories")
async def get_event_categories():
    return {"categories": EVENT_CATEGORIES}

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
@api_router.get("/businesses/search")
async def search_businesses(
    q: str,
    island: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = "approved",
    skip: int = 0,
    limit: int = 50
):
    """Search businesses by name, description, category, or services"""
    query = {"status": status} if status else {}
    
    # Add text search conditions
    search_conditions = []
    if q:
        search_pattern = {"$regex": q, "$options": "i"}  # Case-insensitive
        search_conditions.extend([
            {"business_name": search_pattern},
            {"description": search_pattern},
            {"category": search_pattern},
            {"services": {"$elemMatch": search_pattern}}
        ])
    
    if search_conditions:
        query["$or"] = search_conditions
    
    # Add filters
    if island:
        query["island"] = island
    if category:
        query["category"] = category
    
    businesses = await db.businesses.find(query).skip(skip).limit(limit).to_list(limit)
    return [BusinessProfile(**business) for business in businesses]

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

# Business Profile Photo Routes
@api_router.post("/business/{business_id}/upload-profile-photo")
async def upload_business_profile_photo(
    business_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Verify business ownership
    business = await db.businesses.find_one({"id": business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Upload to Cloudinary
        photo_metadata = await upload_to_cloudinary(file, business_id)
        
        # Update business profile photo
        await db.businesses.update_one(
            {"id": business_id},
            {"$set": {"profile_photo": photo_metadata.optimized_url, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": "Profile photo uploaded successfully",
            "photo_url": photo_metadata.optimized_url
        }
        
    except Exception as e:
        logger.error(f"Error uploading profile photo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload profile photo")

@api_router.post("/business/{business_id}/upload-cover-photo")
async def upload_business_cover_photo(
    business_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Verify business ownership
    business = await db.businesses.find_one({"id": business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Upload to Cloudinary
        photo_metadata = await upload_to_cloudinary(file, business_id)
        
        # Update business cover photo
        await db.businesses.update_one(
            {"id": business_id},
            {"$set": {"cover_photo": photo_metadata.optimized_url, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": "Cover photo uploaded successfully",
            "photo_url": photo_metadata.optimized_url
        }
        
    except Exception as e:
        logger.error(f"Error uploading cover photo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload cover photo")

@api_router.post("/business/{business_id}/upload-logo")
async def upload_business_logo(
    business_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # Verify business ownership
    business = await db.businesses.find_one({"id": business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Upload to Cloudinary
        photo_metadata = await upload_to_cloudinary(file, business_id)
        
        # Update business logo
        await db.businesses.update_one(
            {"id": business_id},
            {"$set": {"logo": photo_metadata.optimized_url, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": "Logo uploaded successfully",
            "photo_url": photo_metadata.optimized_url
        }
        
    except Exception as e:
        logger.error(f"Error uploading logo: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload logo")

# Business FAQ Routes
@api_router.get("/business/{business_id}/faqs")
async def get_business_faqs(business_id: str):
    faqs = await db.business_faqs.find({"business_id": business_id, "is_active": True}).to_list(100)
    return [BusinessFAQ(**faq) for faq in faqs]

@api_router.post("/business/{business_id}/faqs", response_model=BusinessFAQ)
async def create_business_faq(
    business_id: str,
    faq_data: FAQCreate,
    current_user: User = Depends(get_current_user)
):
    # Verify business ownership
    business = await db.businesses.find_one({"id": business_id, "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    faq = BusinessFAQ(**faq_data.dict(), business_id=business_id)
    await db.business_faqs.insert_one(faq.dict())
    return faq

@api_router.put("/business/faqs/{faq_id}", response_model=BusinessFAQ)
async def update_business_faq(
    faq_id: str,
    faq_data: FAQUpdate,
    current_user: User = Depends(get_current_user)
):
    # Get FAQ and verify ownership
    faq_doc = await db.business_faqs.find_one({"id": faq_id})
    if not faq_doc:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    business = await db.businesses.find_one({"id": faq_doc["business_id"], "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = {k: v for k, v in faq_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.business_faqs.update_one({"id": faq_id}, {"$set": update_data})
    
    updated_faq = await db.business_faqs.find_one({"id": faq_id})
    return BusinessFAQ(**updated_faq)

@api_router.delete("/business/faqs/{faq_id}")
async def delete_business_faq(
    faq_id: str,
    current_user: User = Depends(get_current_user)
):
    # Get FAQ and verify ownership
    faq_doc = await db.business_faqs.find_one({"id": faq_id})
    if not faq_doc:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    business = await db.businesses.find_one({"id": faq_doc["business_id"], "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.business_faqs.delete_one({"id": faq_id})
    return {"message": "FAQ deleted successfully"}

# Enhanced Appointment Routes
@api_router.post("/appointment/create", response_model=Appointment)
async def create_appointment(
    appointment_data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
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
    
    appointments = await db.appointments.find({"business_id": business_id}).sort("appointment_date", 1).to_list(100)
    
    # Get customer details for each appointment
    enriched_appointments = []
    for appointment in appointments:
        customer = await db.users.find_one({"id": appointment["customer_id"]})
        appointment_obj = Appointment(**appointment)
        appointment_dict = appointment_obj.dict()
        if customer:
            appointment_dict["customer_name"] = f"{customer['first_name']} {customer['last_name']}"
            appointment_dict["customer_email"] = customer["email"]
            appointment_dict["customer_phone"] = customer.get("phone", "")
        enriched_appointments.append(appointment_dict)
    
    return enriched_appointments

@api_router.put("/appointment/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    status: AppointmentStatus,
    current_user: User = Depends(get_current_user)
):
    # Get appointment
    appointment = await db.appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    # Verify business ownership
    business = await db.businesses.find_one({"id": appointment["business_id"], "user_id": current_user.id})
    if not business:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update status
    await db.appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": f"Appointment {status.value} successfully"}

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

# Event Routes
@api_router.get("/events")
async def get_events(
    island: Optional[str] = None,
    category: Optional[str] = None,
    date: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    query = {"is_active": True, "is_paid": True}
    
    if island:
        query["island"] = island
    if category:
        query["category"] = category
    if date:
        # Parse date and find events for that day
        try:
            event_date = datetime.strptime(date, "%Y-%m-%d")
            next_day = event_date + timedelta(days=1)
            query["event_date"] = {"$gte": event_date, "$lt": next_day}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    events = await db.events.find(query).sort("event_date", 1).skip(skip).limit(limit).to_list(limit)
    return [Event(**event) for event in events]

@api_router.post("/event/create", response_model=Event)
async def create_event(event_data: EventCreate):
    # Create event (unpaid initially)
    event = Event(**event_data.dict())
    event.is_paid = False
    
    await db.events.insert_one(event.dict())
    return event

@api_router.get("/event/{event_id}", response_model=Event)
async def get_event(event_id: str):
    event_data = await db.events.find_one({"id": event_id})
    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(**event_data)

# Event Payment Routes
@api_router.post("/event/{event_id}/create-payment")
async def create_event_payment(event_id: str):
    # Get event
    event_data = await db.events.find_one({"id": event_id})
    if not event_data:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = Event(**event_data)
    
    if event.is_paid:
        raise HTTPException(status_code=400, detail="Event already paid")
    
    try:
        # Create PayPal payment for $5
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{os.environ.get('FRONTEND_URL')}/event/payment-success?event_id={event_id}",
                "cancel_url": f"{os.environ.get('FRONTEND_URL')}/event/payment-cancel?event_id={event_id}"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Event Listing: {event.title}",
                        "sku": f"event-{event_id}",
                        "price": "5.00",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": "5.00",
                    "currency": "USD"
                },
                "description": f"Payment for event listing: {event.title}"
            }]
        })

        if payment.create():
            # Get approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return {
                "payment_id": payment.id,
                "approval_url": approval_url,
                "status": "created"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create payment")
            
    except Exception as e:
        logger.error(f"Error creating event payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/event/{event_id}/execute-payment")
async def execute_event_payment(
    event_id: str,
    payment_id: str,
    payer_id: str,
    background_tasks: BackgroundTasks
):
    try:
        # Execute PayPal payment
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Update event as paid
            await db.events.update_one(
                {"id": event_id},
                {
                    "$set": {
                        "is_paid": True,
                        "payment_date": datetime.utcnow(),
                        "paypal_payment_id": payment_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get event for email notification
            event_data = await db.events.find_one({"id": event_id})
            if event_data:
                event = Event(**event_data)
                # Send confirmation email
                background_tasks.add_task(
                    send_event_payment_confirmation,
                    event.organizer_email,
                    event.organizer_name,
                    event.title,
                    event.event_date.strftime("%B %d, %Y")
                )
            
            return {"status": "success", "message": "Payment confirmed. Your event is now live!"}
        else:
            raise HTTPException(status_code=500, detail="Failed to execute payment")
            
    except Exception as e:
        logger.error(f"Error executing event payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/my-events")
async def get_my_events(organizer_email: str):
    events = await db.events.find({"organizer_email": organizer_email}).sort("event_date", 1).to_list(100)
    return [Event(**event) for event in events]

@api_router.put("/event/{event_id}")
async def update_event(
    event_id: str,
    event_data: EventCreate,
    organizer_email: str
):
    # Verify organizer ownership
    event = await db.events.find_one({"id": event_id, "organizer_email": organizer_email})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or access denied")
    
    update_data = event_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.events.update_one({"id": event_id}, {"$set": update_data})
    
    updated_event = await db.events.find_one({"id": event_id})
    return Event(**updated_event)

@api_router.delete("/event/{event_id}")
async def delete_event(event_id: str, organizer_email: str):
    # Verify organizer ownership
    event = await db.events.find_one({"id": event_id, "organizer_email": organizer_email})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or access denied")
    
    await db.events.update_one(
        {"id": event_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Event deleted successfully"}

# Apartment Listing Routes
@api_router.get("/apartments")
async def get_apartments(
    island: Optional[str] = None,
    property_type: Optional[str] = None,
    min_rent: Optional[float] = None,
    max_rent: Optional[float] = None,
    bedrooms: Optional[int] = None,
    skip: int = 0,
    limit: int = 50
):
    query = {"is_active": True, "is_paid": True, "is_available": True}
    
    if island:
        query["island"] = island
    if property_type:
        query["property_type"] = property_type
    if bedrooms:
        query["bedrooms"] = bedrooms
    if min_rent is not None or max_rent is not None:
        rent_query = {}
        if min_rent is not None:
            rent_query["$gte"] = min_rent
        if max_rent is not None:
            rent_query["$lte"] = max_rent
        query["monthly_rent"] = rent_query
    
    apartments = await db.apartments.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [ApartmentListing(**apartment) for apartment in apartments]

@api_router.post("/apartment/create", response_model=ApartmentListing)
async def create_apartment_listing(apartment_data: ApartmentListingCreate):
    apartment_dict = apartment_data.model_dump()
    apartment_dict["id"] = str(uuid.uuid4())
    apartment_dict["created_at"] = datetime.utcnow()
    apartment_dict["updated_at"] = datetime.utcnow()
    
    await db.apartments.insert_one(apartment_dict)
    
    return ApartmentListing(**apartment_dict)

@api_router.get("/apartment/{listing_id}", response_model=ApartmentListing)
async def get_apartment_listing(listing_id: str):
    apartment = await db.apartments.find_one({"id": listing_id, "is_active": True})
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment listing not found")
    
    return ApartmentListing(**apartment)

@api_router.post("/apartment/{listing_id}/create-payment")
async def create_apartment_payment(listing_id: str):
    # Verify listing exists
    listing = await db.apartments.find_one({"id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Apartment listing not found")
    
    if listing.get("is_paid", False):
        raise HTTPException(status_code=400, detail="Apartment listing is already paid")
    
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/apartment/payment/success",
                "cancel_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/apartment/payment/cancel"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": f"Apartment Listing: {listing['title']}",
                        "sku": "apartment_listing",
                        "price": "10.00",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": "10.00",
                    "currency": "USD"
                },
                "description": f"Payment for apartment listing: {listing['title']}"
            }]
        })
        
        if payment.create():
            # Store payment info
            await db.apartment_payments.insert_one({
                "payment_id": payment.id,
                "listing_id": listing_id,
                "amount": 10.00,
                "currency": "USD",
                "status": "created",
                "created_at": datetime.utcnow()
            })
            
            # Find approval URL
            approval_url = None
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    break
            
            return {
                "payment_id": payment.id,
                "approval_url": approval_url
            }
        else:
            logging.error(f"PayPal payment creation failed: {payment.error}")
            raise HTTPException(status_code=400, detail="Payment creation failed")
    
    except Exception as e:
        logging.error(f"Error creating apartment payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {str(e)}")

@api_router.post("/apartment/{listing_id}/execute-payment")
async def execute_apartment_payment(listing_id: str, payment_data: ApartmentPayment):
    try:
        payment = paypalrestsdk.Payment.find(payment_data.paypal_payment_id)
        
        if payment.execute({"payer_id": payment_data.paypal_payment_id}):
            # Update listing as paid
            await db.apartments.update_one(
                {"id": listing_id},
                {
                    "$set": {
                        "is_paid": True,
                        "payment_date": datetime.utcnow(),
                        "paypal_payment_id": payment_data.paypal_payment_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Update payment record
            await db.apartment_payments.update_one(
                {"payment_id": payment_data.paypal_payment_id},
                {
                    "$set": {
                        "status": "completed",
                        "executed_at": datetime.utcnow()
                    }
                }
            )
            
            return {"message": "Payment successful! Your apartment listing is now live."}
        else:
            logging.error(f"PayPal payment execution failed: {payment.error}")
            raise HTTPException(status_code=400, detail="Payment execution failed")
    
    except Exception as e:
        logging.error(f"Error executing apartment payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment execution failed: {str(e)}")

@api_router.post("/apartment/{listing_id}/upload-photo")
async def upload_apartment_photo(
    listing_id: str,
    file: UploadFile = File(...),
    contact_email: str = Form(...)
):
    # Verify listing ownership
    listing = await db.apartments.find_one({"id": listing_id, "contact_email": contact_email})
    if not listing:
        raise HTTPException(status_code=404, detail="Apartment listing not found or access denied")
    
    # Check photo limit (max 6 photos)
    current_photos = listing.get("photos", [])
    if len(current_photos) >= 6:
        raise HTTPException(status_code=400, detail="Maximum 6 photos allowed per listing")
    
    try:
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"apartment_listings/{listing_id}",
            transformation=[
                {"width": 800, "height": 600, "crop": "fill", "quality": "auto"},
            ]
        )
        
        # Update listing with new photo
        new_photos = current_photos + [upload_result["secure_url"]]
        await db.apartments.update_one(
            {"id": listing_id},
            {
                "$set": {
                    "photos": new_photos,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Photo uploaded successfully",
            "photo_url": upload_result["secure_url"],
            "total_photos": len(new_photos)
        }
    
    except Exception as e:
        logging.error(f"Error uploading apartment photo: {str(e)}")
        raise HTTPException(status_code=500, detail="Photo upload failed")

@api_router.get("/my-apartments")
async def get_my_apartment_listings(contact_email: str):
    listings = await db.apartments.find({"contact_email": contact_email, "is_active": True}).sort("created_at", -1).to_list(100)
    return [ApartmentListing(**listing) for listing in listings]

@api_router.put("/apartment/{listing_id}")
async def update_apartment_listing(
    listing_id: str,
    apartment_data: ApartmentListingCreate,
    contact_email: str
):
    # Verify listing ownership
    existing_listing = await db.apartments.find_one({"id": listing_id, "contact_email": contact_email})
    if not existing_listing:
        raise HTTPException(status_code=404, detail="Apartment listing not found or access denied")
    
    update_data = apartment_data.model_dump()
    update_data["updated_at"] = datetime.utcnow()
    
    await db.apartments.update_one(
        {"id": listing_id},
        {"$set": update_data}
    )
    
    return {"message": "Apartment listing updated successfully"}

@api_router.delete("/apartment/{listing_id}")
async def delete_apartment_listing(listing_id: str, contact_email: str):
    # Verify listing ownership
    listing = await db.apartments.find_one({"id": listing_id, "contact_email": contact_email})
    if not listing:
        raise HTTPException(status_code=404, detail="Apartment listing not found or access denied")
    
    await db.apartments.update_one(
        {"id": listing_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Apartment listing deleted successfully"}

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
    background_tasks: BackgroundTasks
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

# Admin utility endpoint (for initial setup)
@api_router.post("/admin/promote-user")
async def promote_user_to_admin(email: str, current_user: User = Depends(get_current_user)):
    """Promote a user to admin role - use this for initial admin setup"""
    # Only allow if current user is already admin OR no admins exist yet
    admin_count = await db.users.count_documents({"role": "admin"})
    
    if admin_count > 0 and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only existing admins can promote users")
    
    result = await db.users.update_one(
        {"email": email},
        {"$set": {"role": "admin"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {email} promoted to admin successfully"}

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