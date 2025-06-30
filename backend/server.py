from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Depends
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
    "Beauty & Spa", "Health & Medical", "Automotive", "Real Estate",
    "Legal Services", "Financial Services", "Construction", "Entertainment",
    "Education", "Technology", "Other"
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
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(**user_data.dict())
    user.password = hashed_password
    
    await db.users.insert_one(user.dict())
    
    # Create JWT token
    token = create_jwt_token(user.id, user.role.value)
    
    return {
        "message": "User registered successfully",
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
async def execute_subscription(subscription_id: str, payer_id: str):
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