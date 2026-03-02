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
import logging

logger = logging.getLogger(__name__)

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
        
        # Append session ID to success URL for verification fallback
        success_url = request.success_url
        separator = "&" if "?" in success_url else "?"
        success_url_with_session = f"{success_url}{separator}session_id={{CHECKOUT_SESSION_ID}}"
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            mode="subscription",
            success_url=success_url_with_session,
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


@router.post("/verify-session")
async def verify_checkout_session(
    request: Request,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Verify a completed Stripe checkout session and activate the subscription.
    This is a fallback in case the webhook doesn't fire or is delayed.
    """
    body = await request.json()
    session_id = body.get("session_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id required")
    
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    try:
        # Retrieve the checkout session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        logger.info(f"Verifying session {session_id} for user {user.id}: status={session.payment_status}, customer={session.customer}")
        
        # Verify this session belongs to this user
        if session.customer != user.stripe_customer_id:
            logger.warning(f"Session customer mismatch: session={session.customer}, user={user.stripe_customer_id}")
            raise HTTPException(status_code=403, detail="Session does not belong to this user")
        
        # Check if payment was successful
        if session.payment_status == "paid":
            if not user.is_subscribed:
                user.is_subscribed = True
                user.subscription_status = "active"
                user.subscription_plan = session.metadata.get("plan_type", "growth")
                db.commit()
                logger.info(f"User {user.id} subscription activated via session verification")
            
            return {
                "verified": True,
                "is_subscribed": True,
                "plan": user.subscription_plan
            }
        else:
            return {
                "verified": False,
                "is_subscribed": user.is_subscribed,
                "plan": user.subscription_plan,
                "payment_status": session.payment_status
            }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error verifying session: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/activate-user")
async def activate_user_subscription(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Manual endpoint to activate a user's subscription by email.
    Use this to fix users who paid but weren't activated.
    """
    body = await request.json()
    email = body.get("email")
    admin_key = body.get("admin_key")
    
    # Simple admin protection — use your JWT_SECRET as the admin key
    if admin_key != settings.JWT_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if not email:
        raise HTTPException(status_code=400, detail="email required")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_subscribed = True
    user.subscription_status = "active"
    user.subscription_plan = "growth"
    db.commit()
    
    logger.info(f"Manually activated subscription for user {user.id} ({user.email})")
    
    return {
        "success": True,
        "user_id": user.id,
        "email": user.email,
        "plan": "growth"
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks for subscription events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    logger.info(f"Webhook received. Signature present: {bool(sig_header)}")
    
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("Webhook secret not configured!")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Webhook: Invalid payload")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Webhook: Invalid signature — check STRIPE_WEBHOOK_SECRET matches Stripe Dashboard")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    logger.info(f"Webhook event: {event.type}")
    
    # Handle subscription events
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")
        plan_type = session.metadata.get("plan_type", "growth")  # Default to growth
        logger.info(f"Checkout completed: user_id={user_id}, plan={plan_type}")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                user.is_subscribed = True
                user.subscription_status = "active"
                user.subscription_plan = plan_type  # Save which plan they bought
                db.commit()
                logger.info(f"User {user_id} activated via webhook")
            else:
                logger.error(f"Webhook: User {user_id} not found in database")
        else:
            logger.error("Webhook: No user_id in session metadata")
    
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
