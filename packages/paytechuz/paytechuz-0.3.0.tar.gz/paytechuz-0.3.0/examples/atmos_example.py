#!/usr/bin/env python3
"""
Atmos Payment Gateway Example

Bu misol Atmos to'lov tizimi bilan qanday ishlashni ko'rsatadi.
"""

import time
from paytechuz.gateways.atmos import AtmosGateway
from paytechuz.gateways.atmos.webhook import AtmosWebhookHandler
from paytechuz.core.exceptions import PaymentException


def main():
    """Atmos integration misoli"""
    
    # 1. Atmos Gateway yaratish
    print("🚀 Atmos Gateway yaratilmoqda...")
    
    atmos = AtmosGateway(
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        store_id="test_store_id",
        terminal_id="test_terminal_id",  # Ixtiyoriy
        is_test_mode=True  # Test muhiti
    )
    
    print("✅ Atmos Gateway muvaffaqiyatli yaratildi!")
    
    # 2. To'lov yaratish
    print("\n💳 To'lov yaratilmoqda...")
    
    try:
        payment = atmos.create_payment(
            account_id="order_12345",
            amount=50000  # 500.00 UZS (tiyin hisobida)
        )
        
        print("✅ To'lov muvaffaqiyatli yaratildi!")
        print(f"   Transaction ID: {payment['transaction_id']}")
        print(f"   Payment URL: {payment['payment_url']}")
        print(f"   Amount: {payment['amount']} UZS")
        print(f"   Status: {payment['status']}")
        
        transaction_id = payment['transaction_id']
        
    except PaymentException as e:
        print(f"❌ To'lov yaratishda xatolik: {e.message}")
        return
    
    # 3. To'lov holatini tekshirish
    print("\n🔍 To'lov holati tekshirilmoqda...")
    
    try:
        status = atmos.check_payment(transaction_id)
        
        print("✅ To'lov holati muvaffaqiyatli tekshirildi!")
        print(f"   Transaction ID: {status['transaction_id']}")
        print(f"   Status: {status['status']}")
        print(f"   Details: {status['details']}")
        
    except PaymentException as e:
        print(f"❌ To'lov holatini tekshirishda xatolik: {e.message}")
    
    # 4. To'lov holatini kuzatish (demo)
    print("\n⏰ To'lov holatini kuzatish (5 soniya)...")
    
    for i in range(5):
        try:
            status = atmos.check_payment(transaction_id)
            current_status = status['status']
            
            print(f"   Urinish {i + 1}: Status = {current_status}")
            
            if current_status == 'success':
                print("   🎉 To'lov muvaffaqiyatli!")
                break
            elif current_status in ['failed', 'cancelled']:
                print("   💔 To'lov muvaffaqiyatsiz!")
                break
                
            time.sleep(1)
            
        except PaymentException as e:
            print(f"   ❌ Xatolik: {e.message}")
            break
    
    # 5. To'lovni bekor qilish (agar pending bo'lsa)
    print("\n🚫 To'lovni bekor qilish...")
    
    try:
        cancel_result = atmos.cancel_payment(
            transaction_id=transaction_id,
            reason="Test uchun bekor qilish"
        )
        
        print("✅ To'lov muvaffaqiyatli bekor qilindi!")
        print(f"   Transaction ID: {cancel_result['transaction_id']}")
        print(f"   Status: {cancel_result['status']}")
        
    except PaymentException as e:
        print(f"❌ To'lovni bekor qilishda xatolik: {e.message}")
    
    # 6. Webhook misoli
    print("\n🔗 Webhook misoli...")
    
    webhook_handler = AtmosWebhookHandler(api_key="test_api_key")
    
    # Webhook ma'lumotlari misoli
    webhook_data = {
        'store_id': 'test_store_id',
        'transaction_id': transaction_id,
        'invoice': 'order_12345',
        'amount': '50000',
        'transaction_time': '2024-01-01 12:00:00',
        'sign': 'test_signature'  # Bu real loyihada to'g'ri imzo bo'lishi kerak
    }
    
    try:
        # Webhook imzosini tekshirish
        is_valid = webhook_handler.verify_signature(
            webhook_data, 
            webhook_data['sign']
        )
        
        if is_valid:
            print("✅ Webhook imzosi to'g'ri!")
        else:
            print("❌ Webhook imzosi noto'g'ri!")
        
        # Webhook qayta ishlash
        response = webhook_handler.handle_webhook(webhook_data)
        
        print(f"📨 Webhook javobi: {response}")
        
    except Exception as e:
        print(f"❌ Webhook qayta ishlashda xatolik: {e}")
    
    print("\n🎯 Atmos integration misoli tugadi!")


def payment_monitoring_example():
    """To'lov holatini kuzatish misoli"""
    
    print("\n📊 To'lov holatini kuzatish misoli...")
    
    atmos = AtmosGateway(
        consumer_key="test_consumer_key",
        consumer_secret="test_consumer_secret",
        store_id="test_store_id",
        is_test_mode=True
    )
    
    def monitor_payment(transaction_id, max_attempts=10):
        """To'lov holatini kuzatish"""
        
        for attempt in range(max_attempts):
            try:
                status = atmos.check_payment(transaction_id)
                current_status = status['status']
                
                print(f"   Urinish {attempt + 1}: Status = {current_status}")
                
                if current_status == 'success':
                    print("   ✅ To'lov muvaffaqiyatli!")
                    return True
                elif current_status in ['failed', 'cancelled']:
                    print("   ❌ To'lov muvaffaqiyatsiz!")
                    return False
                
                # 30 soniya kutish (demo uchun 3 soniya)
                time.sleep(3)
                
            except PaymentException as e:
                print(f"   ❌ Xatolik: {e.message}")
                return False
                
        print("   ⏰ Maksimal urinishlar soni tugadi")
        return False
    
    # Misol uchun to'lov yaratish
    try:
        payment = atmos.create_payment(
            account_id="order_67890",
            amount=25000  # 250.00 UZS
        )
        
        print(f"💳 To'lov yaratildi: {payment['transaction_id']}")
        
        # To'lov holatini kuzatish
        success = monitor_payment(payment['transaction_id'], max_attempts=3)
        
        if success:
            print("🎉 To'lov muvaffaqiyatli yakunlandi!")
        else:
            print("💔 To'lov muvaffaqiyatsiz yakunlandi!")
            
    except PaymentException as e:
        print(f"❌ To'lov yaratishda xatolik: {e.message}")


def webhook_example():
    """Webhook qayta ishlash misoli"""
    
    print("\n🔗 Webhook qayta ishlash misoli...")
    
    webhook_handler = AtmosWebhookHandler(api_key="your_api_key")
    
    def process_webhook(webhook_data):
        """Webhook ma'lumotlarini qayta ishlash"""
        
        try:
            response = webhook_handler.handle_webhook(webhook_data)
            
            if response['status'] == 1:
                # To'lov muvaffaqiyatli
                transaction_id = webhook_data.get('transaction_id')
                amount = webhook_data.get('amount')
                invoice = webhook_data.get('invoice')
                
                print(f"✅ To'lov muvaffaqiyatli!")
                print(f"   Transaction ID: {transaction_id}")
                print(f"   Order ID: {invoice}")
                print(f"   Amount: {amount}")
                
                # Bu yerda buyurtma holatini yangilash kerak
                # update_order_status(invoice, 'paid')
                
            else:
                print(f"❌ Webhook xatosi: {response.get('message', 'Unknown error')}")
                
            return response
            
        except Exception as e:
            print(f"❌ Webhook qayta ishlashda xatolik: {e}")
            return {
                'status': 0,
                'message': f'Error: {str(e)}'
            }
    
    # Webhook ma'lumotlari misoli
    sample_webhook_data = {
        'store_id': '12345',
        'transaction_id': 'txn_123456',
        'invoice': 'order_12345',
        'amount': '50000',
        'transaction_time': '2024-01-01 12:00:00',
        'sign': 'calculated_signature'
    }
    
    print("📨 Webhook ma'lumotlari qayta ishlanmoqda...")
    response = process_webhook(sample_webhook_data)
    print(f"📤 Webhook javobi: {response}")


if __name__ == "__main__":
    print("🎯 Atmos Payment Gateway Misollari")
    print("=" * 50)
    
    # Asosiy misol
    main()
    
    # Qo'shimcha misollar
    payment_monitoring_example()
    webhook_example()
    
    print("\n✨ Barcha misollar tugadi!")
    print("\n📚 Qo'shimcha ma'lumot uchun:")
    print("   - Atmos dokumentatsiyasi: https://atmos.uz/developers")
    print("   - PayTechUZ GitHub: https://github.com/PayTechUz/paytechuz")
