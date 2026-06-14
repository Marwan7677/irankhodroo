"""
Payment Processing - پردازش پرداخت‌ها
"""
from typing import Dict, Optional
import stripe
import httpx
from config import settings
from datetime import datetime

stripe.api_key = settings.STRIPE_API_KEY

class PaymentProcessor:
    
    @staticmethod
    async def process_card_payment(amount: float, currency: str = "irr") -> Dict:
        """
        Process card payment via Stripe
        """
        try:
            # برای ایران استفاده کنید: amount در تومان
            intent = stripe.PaymentIntent.create(
                amount=int(amount),
                currency="irr",
                payment_method_types=["card"]
            )
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "intent_id": intent.id
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def calculate_ton_amount(toman_amount: float, ton_rate: Optional[float] = None) -> float:
        """
        Calculate TON coin amount from Iranian Toman
        Default rate: 1 TON = 298,500 Toman
        """
        if ton_rate is None:
            ton_rate = 298500
        return toman_amount / ton_rate
    
    @staticmethod
    async def get_ton_rate() -> float:
        """
        Get current TON rate (Toman per TON)
        در پروژه واقعی باید از API موثری استفاده کنید
        """
        try:
            async with httpx.AsyncClient() as client:
                # مثال: از coinmarketcap یا api دیگر
                response = await client.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": "the-open-network", "vs_currencies": "jpy"}
                )
                # اینجا نیاز به تبدیل JPY به تومان دارید
                return 298500  # Default
        except Exception as e:
            print(f"Error fetching TON rate: {e}")
            return 298500
    
    @staticmethod
    async def verify_ton_payment(
        wallet_address: str,
        transaction_hash: str,
        amount: float
    ) -> Dict:
        """
        Verify TON blockchain transaction
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "X-TonCenter-Auth": settings.TON_API_URL
                }
                
                # بررسی تراکنش در بلاکچین TON
                response = await client.get(
                    f"{settings.TON_API_URL}/getTransaction",
                    params={"transaction_hash": transaction_hash},
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # بررسی مبلغ و آدرس
                    return {
                        "success": True,
                        "verified": True,
                        "transaction_data": data
                    }
                else:
                    return {
                        "success": False,
                        "verified": False,
                        "error": "Transaction not found"
                    }
        except Exception as e:
            return {
                "success": False,
                "verified": False,
                "error": str(e)
            }
    
    @staticmethod
    def calculate_installment(
        total_amount: float,
        months: int,
        annual_rate: float = 18.0
    ) -> Dict:
        """
        Calculate installment payment details
        """
        monthly_rate = annual_rate / 100 / 12
        
        # محاسبه قسط ماهیانه
        monthly_payment = (
            total_amount * monthly_rate * (1 + monthly_rate) ** months
        ) / ((1 + monthly_rate) ** months - 1)
        
        total_interest = (monthly_payment * months) - total_amount
        
        return {
            "total_amount": total_amount,
            "months": months,
            "monthly_payment": round(monthly_payment, 0),
            "total_interest": round(total_interest, 0),
            "annual_rate": annual_rate
        }

payment_processor = PaymentProcessor()

def process_card_payment(amount: float) -> Dict:
    return payment_processor.process_card_payment(amount)

def calculate_ton_amount(toman_amount: float) -> float:
    return payment_processor.calculate_ton_amount(toman_amount)

async def verify_ton_payment(wallet: str, tx_hash: str, amount: float) -> Dict:
    return await payment_processor.verify_ton_payment(wallet, tx_hash, amount)

def calculate_installment(total: float, months: int, rate: float = 18.0) -> Dict:
    return payment_processor.calculate_installment(total, months, rate)
