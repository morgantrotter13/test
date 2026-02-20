"""
Stripe payment routes for subscriptions.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.auth import require_auth
from app.config import settings
from datetime import datetime
import stripe

router = APIRouter()

# Stripe configuration (read from settings/.env)
stripe.api_key = settings.STRIPE_SECRET_KEY or ""
STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET or ""

# Your Stripe Price IDs (create these in Stripe Dashboard)
PRICE_IDS = {
    "growth": settings.STRIPE_PRICE_MONTHLY or "",   # $99/month (Growth)
    "monthly": settings.STRIPE_PRICE_MONTHLY or "",  # alias for growth
}


class CheckoutRequest(BaseModel):
    price_id: str  # "growth" or "monthly"
    success_url: str
    cancel_url: str


class PortalRequest(BaseModel):
    return_url: str


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a Stripe Checkout session for subscription."""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    price_id = PRICE_IDS.get(request.price_id)
    if not price_id:
        raise HTTPException(status_code=400, detail="Invalid price option")
    
    try:
        # Check if user already has a Stripe customer ID
        if not user.stripe_customer_id:
            # Create a new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={"user_id": str(user.id)}
            )
            user.stripe_customer_id = customer.id
            db.commit()
        
        # All paid plans are "growth"
        plan_type = "growth"
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            mode="subscription",
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={"user_id": str(user.id), "plan_type": plan_type}
        )
        
        return {"checkout_url": session.url, "session_id": session.id}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-portal-session")
async def create_portal_session(
    request: PortalRequest,
    user: User = Depends(require_auth)
):
    """Create a Stripe Customer Portal session for managing subscription."""
    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=request.return_url
        )
        return {"portal_url": session.url}
    
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription-status")
async def get_subscription_status(
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current subscription status."""
    return {
        "is_subscribed": user.is_subscribed,
        "subscription_status": user.subscription_status,
        "subscription_end": user.subscription_end.isoformat() if user.subscription_end else None,
        "plan": user.subscription_plan
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks for subscription events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle subscription events
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        plan_type = session.metadata.get("plan_type", "growth")  # Default to growth
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.is_subscribed = True
                user.subscription_status = "active"
                user.subscription_plan = plan_type  # Save which plan they bought
                db.commit()
    
    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        customer_id = subscription.customer
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_status = subscription.status
            user.is_subscribed = subscription.status == "active"
            if subscription.current_period_end:
                user.subscription_end = datetime.fromtimestamp(subscription.current_period_end)
            db.commit()
    
    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        customer_id = subscription.customer
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.is_subscribed = False
            user.subscription_status = "cancelled"
            db.commit()
    
    return {"status": "success"}
