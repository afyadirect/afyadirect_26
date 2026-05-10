# app/routers/payments.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from ..services.payment_service import PaymentService
from ..services.firebase_service import FirebaseService
from ..schemas.payment import PaymentCreate, PaymentResponse, MpesaCallbackData
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/initiate")
async def initiate_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Initiate a payment"""
    try:
        if payment_data.payment_method == "mpesa":
            result = await PaymentService.process_mpesa_payment(
                phone_number=payment_data.phone_number,
                amount=payment_data.amount,
                appointment_id=payment_data.appointment_id,
                patient_id=current_user['user_id']
            )
        elif payment_data.payment_method == "tigo":
            result = await PaymentService.process_tigo_payment(
                phone_number=payment_data.phone_number,
                amount=payment_data.amount,
                appointment_id=payment_data.appointment_id
            )
        elif payment_data.payment_method == "airtel":
            result = await PaymentService.process_airtel_payment(
                phone_number=payment_data.phone_number,
                amount=payment_data.amount,
                appointment_id=payment_data.appointment_id
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid payment method")
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('message'))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mpesa-callback")
async def mpesa_callback(
    callback_data: MpesaCallbackData,
    background_tasks: BackgroundTasks
):
    """Handle M-Pesa STK Push callback"""
    try:
        background_tasks.add_task(
            PaymentService.handle_mpesa_callback,
            callback_data.dict()
        )
        return {"ResultCode": 0, "ResultDesc": "Success"}
    except Exception as e:
        return {"ResultCode": 1, "ResultDesc": str(e)}

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_status(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get payment status"""
    try:
        payment = await FirebaseService.get_payment(payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payment['userId'] != current_user['user_id'] and current_user['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Not authorized")
        
        return PaymentResponse(
            id=payment['id'],
            appointment_id=payment['appointmentId'],
            amount=payment['amount'],
            payment_method=payment['paymentMethod'],
            status=payment['status'],
            transaction_id=payment.get('transactionId'),
            created_at=payment['createdAt'],
            paid_at=payment.get('paidAt')
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/transactions")
async def get_user_transactions(
    current_user: dict = Depends(get_current_user),
    limit: int = 50
):
    """Get user's payment transactions"""
    try:
        transactions = await FirebaseService.get_user_payments(
            current_user['user_id'],
            limit
        )
        return {"transactions": transactions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))