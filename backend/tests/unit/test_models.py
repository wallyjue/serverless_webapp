"""
モデルクラスのテスト
"""
import unittest
from datetime import datetime
from src.models import User, UserRole, PurchaseOrder, PurchaseOrderStatus, Shipment, ShipmentStatus


class TestModels(unittest.TestCase):
    """モデルクラスのテスト"""
    
    def test_user_model(self):
        """ユーザーモデルのテスト"""
        user = User(
            user_id="test-user-id",
            email="test@example.com",
            role=UserRole.USER,
            permissions=["purchase_order_create"]
        )
        
        # to_dict メソッドのテスト
        user_dict = user.to_dict()
        self.assertEqual(user_dict['user_id'], "test-user-id")
        self.assertEqual(user_dict['email'], "test@example.com")
        self.assertEqual(user_dict['role'], "user")
        self.assertEqual(user_dict['permissions'], ["purchase_order_create"])
        
        # from_dict メソッドのテスト
        user_from_dict = User.from_dict(user_dict)
        self.assertEqual(user_from_dict.user_id, user.user_id)
        self.assertEqual(user_from_dict.email, user.email)
        self.assertEqual(user_from_dict.role, user.role)
        self.assertEqual(user_from_dict.permissions, user.permissions)
    
    def test_purchase_order_model(self):
        """購買発注書モデルのテスト"""
        items = [
            {"name": "商品A", "quantity": 2, "unit_price": 100.0},
            {"name": "商品B", "quantity": 1, "unit_price": 200.0}
        ]
        
        po = PurchaseOrder(
            po_id="test-po-id",
            supplier="テスト供給者",
            items=items,
            total_amount=400.0,
            status=PurchaseOrderStatus.DRAFT,
            created_by="test-user-id",
            notes="テスト注文"
        )
        
        # to_dict メソッドのテスト
        po_dict = po.to_dict()
        self.assertEqual(po_dict['po_id'], "test-po-id")
        self.assertEqual(po_dict['supplier'], "テスト供給者")
        self.assertEqual(po_dict['items'], items)
        self.assertEqual(po_dict['total_amount'], 400.0)
        self.assertEqual(po_dict['status'], "draft")
        self.assertEqual(po_dict['created_by'], "test-user-id")
        self.assertEqual(po_dict['notes'], "テスト注文")
        
        # from_dict メソッドのテスト
        po_from_dict = PurchaseOrder.from_dict(po_dict)
        self.assertEqual(po_from_dict.po_id, po.po_id)
        self.assertEqual(po_from_dict.supplier, po.supplier)
        self.assertEqual(po_from_dict.items, po.items)
        self.assertEqual(po_from_dict.total_amount, po.total_amount)
        self.assertEqual(po_from_dict.status, po.status)
        self.assertEqual(po_from_dict.created_by, po.created_by)
        self.assertEqual(po_from_dict.notes, po.notes)
    
    def test_shipment_model(self):
        """出荷モデルのテスト"""
        shipment = Shipment(
            shipment_id="test-shipment-id",
            po_id="test-po-id",
            tracking_number="TRK123456",
            carrier="テスト運送会社",
            status=ShipmentStatus.PENDING,
            created_by="test-user-id",
            estimated_delivery="2024-01-15",
            notes="テスト出荷"
        )
        
        # to_dict メソッドのテスト
        shipment_dict = shipment.to_dict()
        self.assertEqual(shipment_dict['shipment_id'], "test-shipment-id")
        self.assertEqual(shipment_dict['po_id'], "test-po-id")
        self.assertEqual(shipment_dict['tracking_number'], "TRK123456")
        self.assertEqual(shipment_dict['carrier'], "テスト運送会社")
        self.assertEqual(shipment_dict['status'], "pending")
        self.assertEqual(shipment_dict['created_by'], "test-user-id")
        self.assertEqual(shipment_dict['estimated_delivery'], "2024-01-15")
        self.assertEqual(shipment_dict['notes'], "テスト出荷")
        
        # from_dict メソッドのテスト
        shipment_from_dict = Shipment.from_dict(shipment_dict)
        self.assertEqual(shipment_from_dict.shipment_id, shipment.shipment_id)
        self.assertEqual(shipment_from_dict.po_id, shipment.po_id)
        self.assertEqual(shipment_from_dict.tracking_number, shipment.tracking_number)
        self.assertEqual(shipment_from_dict.carrier, shipment.carrier)
        self.assertEqual(shipment_from_dict.status, shipment.status)
        self.assertEqual(shipment_from_dict.created_by, shipment.created_by)
        self.assertEqual(shipment_from_dict.estimated_delivery, shipment.estimated_delivery)
        self.assertEqual(shipment_from_dict.notes, shipment.notes)


if __name__ == '__main__':
    unittest.main()