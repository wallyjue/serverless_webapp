"""
データモデル定義

DynamoDB用のデータ構造を定義します。
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class UserRole(Enum):
    """ユーザー権限の列挙型"""
    ADMIN = "admin"
    USER = "user"


class PurchaseOrderStatus(Enum):
    """購買発注書のステータス"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"


class ShipmentStatus(Enum):
    """出荷のステータス"""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class User:
    """ユーザーモデル"""
    
    def __init__(
        self,
        user_id: str,
        email: str,
        role: UserRole,
        permissions: Optional[List[str]] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.user_id = user_id
        self.email = email
        self.role = role
        self.permissions = permissions or []
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role': self.role.value,
            'permissions': self.permissions,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """辞書からインスタンスを作成"""
        return cls(
            user_id=data['user_id'],
            email=data['email'],
            role=UserRole(data['role']),
            permissions=data.get('permissions', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class PurchaseOrder:
    """購買発注書モデル"""
    
    def __init__(
        self,
        po_id: str,
        supplier: str,
        items: List[Dict[str, Any]],
        total_amount: float,
        status: PurchaseOrderStatus,
        created_by: str,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.po_id = po_id
        self.supplier = supplier
        self.items = items
        self.total_amount = total_amount
        self.status = status
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'po_id': self.po_id,
            'supplier': self.supplier,
            'items': self.items,
            'total_amount': self.total_amount,
            'status': self.status.value,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurchaseOrder':
        """辞書からインスタンスを作成"""
        return cls(
            po_id=data['po_id'],
            supplier=data['supplier'],
            items=data['items'],
            total_amount=data['total_amount'],
            status=PurchaseOrderStatus(data['status']),
            created_by=data['created_by'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            notes=data.get('notes')
        )


class Shipment:
    """出荷モデル"""
    
    def __init__(
        self,
        shipment_id: str,
        po_id: str,
        tracking_number: str,
        carrier: str,
        status: ShipmentStatus,
        created_by: str,
        estimated_delivery: Optional[str] = None,
        actual_delivery: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        notes: Optional[str] = None
    ):
        self.shipment_id = shipment_id
        self.po_id = po_id
        self.tracking_number = tracking_number
        self.carrier = carrier
        self.status = status
        self.created_by = created_by
        self.estimated_delivery = estimated_delivery
        self.actual_delivery = actual_delivery
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.notes = notes
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'shipment_id': self.shipment_id,
            'po_id': self.po_id,
            'tracking_number': self.tracking_number,
            'carrier': self.carrier,
            'status': self.status.value,
            'created_by': self.created_by,
            'estimated_delivery': self.estimated_delivery,
            'actual_delivery': self.actual_delivery,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Shipment':
        """辞書からインスタンスを作成"""
        return cls(
            shipment_id=data['shipment_id'],
            po_id=data['po_id'],
            tracking_number=data['tracking_number'],
            carrier=data['carrier'],
            status=ShipmentStatus(data['status']),
            created_by=data['created_by'],
            estimated_delivery=data.get('estimated_delivery'),
            actual_delivery=data.get('actual_delivery'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            notes=data.get('notes')
        )


def generate_id() -> str:
    """ユニークIDを生成"""
    return str(uuid.uuid4())