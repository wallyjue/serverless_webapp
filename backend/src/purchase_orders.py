"""
購買発注書管理関連のLambda関数

購買発注書のCRUD操作を提供します。
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from utils import (
    create_response,
    create_error_response,
    require_auth,
    get_dynamodb_resource,
    get_path_parameter,
    get_query_parameter,
    validate_required_fields,
    handle_dynamodb_error
)
from models import PurchaseOrder, PurchaseOrderStatus, UserRole, generate_id


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """購買発注書管理のメインハンドラー"""
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if path == '/purchase-orders' and http_method == 'GET':
            return get_purchase_orders(event, context)
        elif path == '/purchase-orders' and http_method == 'POST':
            return create_purchase_order(event, context)
        elif path.startswith('/purchase-orders/') and http_method == 'GET':
            return get_purchase_order(event, context)
        elif path.startswith('/purchase-orders/') and http_method == 'PUT':
            return update_purchase_order(event, context)
        elif path.startswith('/purchase-orders/') and http_method == 'DELETE':
            return delete_purchase_order(event, context)
        else:
            return create_error_response(404, 'Endpoint not found')
    
    except Exception as e:
        print(f"Error in purchase orders handler: {str(e)}")
        return create_error_response(500, 'Internal server error')


@require_auth
def get_purchase_orders(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """購買発注書の一覧を取得"""
    try:
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        dynamodb = get_dynamodb_resource()
        po_table = dynamodb.Table(os.environ['PURCHASE_ORDERS_TABLE'])
        
        # 管理者はすべての発注書を閲覧可能、一般ユーザーは自分が作成したもののみ
        if user_role == UserRole.ADMIN.value:
            response = po_table.scan()
        else:
            # 一般ユーザーの場合、created_byでフィルタリング
            response = po_table.scan(
                FilterExpression='created_by = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
        
        purchase_orders = []
        for item in response['Items']:
            po = PurchaseOrder.from_dict(item)
            purchase_orders.append({
                'po_id': po.po_id,
                'supplier': po.supplier,
                'items': po.items,
                'total_amount': po.total_amount,
                'status': po.status.value,
                'created_by': po.created_by,
                'created_at': po.created_at,
                'updated_at': po.updated_at,
                'notes': po.notes
            })
        
        # 作成日時で降順ソート
        purchase_orders.sort(key=lambda x: x['created_at'], reverse=True)
        
        return create_response(200, {'purchase_orders': purchase_orders})
        
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def create_purchase_order(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """新しい購買発注書を作成"""
    try:
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        # 権限チェック：管理者または purchase_order_create 権限を持つユーザー
        if user_role != UserRole.ADMIN.value:
            # 一般ユーザーの権限を確認
            if not _check_user_permission(user_id, 'purchase_order_create'):
                return create_error_response(403, 'Permission denied: purchase_order_create required')
        
        body = json.loads(event['body'])
        
        # 必須フィールドの検証
        is_valid, error_msg = validate_required_fields(body, ['supplier', 'items', 'total_amount'])
        if not is_valid:
            return create_error_response(400, error_msg)
        
        supplier = body['supplier']
        items = body['items']
        total_amount = body['total_amount']
        notes = body.get('notes')
        
        # アイテムの検証
        if not isinstance(items, list) or len(items) == 0:
            return create_error_response(400, 'Items must be a non-empty list')
        
        for item in items:
            if not isinstance(item, dict) or 'name' not in item or 'quantity' not in item or 'unit_price' not in item:
                return create_error_response(400, 'Each item must have name, quantity, and unit_price')
        
        # 金額の検証
        if not isinstance(total_amount, (int, float)) or total_amount <= 0:
            return create_error_response(400, 'Total amount must be a positive number')
        
        # 購買発注書を作成
        po_id = generate_id()
        purchase_order = PurchaseOrder(
            po_id=po_id,
            supplier=supplier,
            items=items,
            total_amount=total_amount,
            status=PurchaseOrderStatus.DRAFT,
            created_by=user_id,
            notes=notes
        )
        
        # DynamoDBに保存
        dynamodb = get_dynamodb_resource()
        po_table = dynamodb.Table(os.environ['PURCHASE_ORDERS_TABLE'])
        
        po_table.put_item(Item=purchase_order.to_dict())
        
        return create_response(201, {
            'message': 'Purchase order created successfully',
            'purchase_order': {
                'po_id': purchase_order.po_id,
                'supplier': purchase_order.supplier,
                'items': purchase_order.items,
                'total_amount': purchase_order.total_amount,
                'status': purchase_order.status.value,
                'created_by': purchase_order.created_by,
                'created_at': purchase_order.created_at,
                'notes': purchase_order.notes
            }
        })
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def get_purchase_order(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """特定の購買発注書を取得"""
    try:
        po_id = get_path_parameter(event, 'po_id')
        if not po_id:
            return create_error_response(400, 'Purchase order ID is required')
        
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        dynamodb = get_dynamodb_resource()
        po_table = dynamodb.Table(os.environ['PURCHASE_ORDERS_TABLE'])
        
        response = po_table.get_item(Key={'po_id': po_id})
        if 'Item' not in response:
            return create_error_response(404, 'Purchase order not found')
        
        purchase_order = PurchaseOrder.from_dict(response['Item'])
        
        # 権限チェック：管理者または作成者のみアクセス可能
        if user_role != UserRole.ADMIN.value and purchase_order.created_by != user_id:
            return create_error_response(403, 'Access denied')
        
        return create_response(200, {
            'purchase_order': {
                'po_id': purchase_order.po_id,
                'supplier': purchase_order.supplier,
                'items': purchase_order.items,
                'total_amount': purchase_order.total_amount,
                'status': purchase_order.status.value,
                'created_by': purchase_order.created_by,
                'created_at': purchase_order.created_at,
                'updated_at': purchase_order.updated_at,
                'notes': purchase_order.notes
            }
        })
        
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def update_purchase_order(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """購買発注書を更新"""
    try:
        po_id = get_path_parameter(event, 'po_id')
        if not po_id:
            return create_error_response(400, 'Purchase order ID is required')
        
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        body = json.loads(event['body'])
        
        dynamodb = get_dynamodb_resource()
        po_table = dynamodb.Table(os.environ['PURCHASE_ORDERS_TABLE'])
        
        # 既存の発注書を取得
        response = po_table.get_item(Key={'po_id': po_id})
        if 'Item' not in response:
            return create_error_response(404, 'Purchase order not found')
        
        purchase_order = PurchaseOrder.from_dict(response['Item'])
        
        # 権限チェック：管理者または作成者のみ更新可能
        if user_role != UserRole.ADMIN.value and purchase_order.created_by != user_id:
            return create_error_response(403, 'Access denied')
        
        # 更新可能なフィールド
        allowed_fields = ['supplier', 'items', 'total_amount', 'status', 'notes']
        update_data = {k: v for k, v in body.items() if k in allowed_fields}
        
        if not update_data:
            return create_error_response(400, 'No valid fields to update')
        
        # フィールドの更新
        if 'supplier' in update_data:
            purchase_order.supplier = update_data['supplier']
        
        if 'items' in update_data:
            items = update_data['items']
            if not isinstance(items, list) or len(items) == 0:
                return create_error_response(400, 'Items must be a non-empty list')
            purchase_order.items = items
        
        if 'total_amount' in update_data:
            total_amount = update_data['total_amount']
            if not isinstance(total_amount, (int, float)) or total_amount <= 0:
                return create_error_response(400, 'Total amount must be a positive number')
            purchase_order.total_amount = total_amount
        
        if 'status' in update_data:
            try:
                purchase_order.status = PurchaseOrderStatus(update_data['status'])
            except ValueError:
                return create_error_response(400, 'Invalid status')
        
        if 'notes' in update_data:
            purchase_order.notes = update_data['notes']
        
        # 更新日時を設定
        purchase_order.updated_at = datetime.utcnow().isoformat()
        
        # DynamoDBを更新
        po_table.put_item(Item=purchase_order.to_dict())
        
        return create_response(200, {
            'message': 'Purchase order updated successfully',
            'purchase_order': {
                'po_id': purchase_order.po_id,
                'supplier': purchase_order.supplier,
                'items': purchase_order.items,
                'total_amount': purchase_order.total_amount,
                'status': purchase_order.status.value,
                'created_by': purchase_order.created_by,
                'updated_at': purchase_order.updated_at,
                'notes': purchase_order.notes
            }
        })
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def delete_purchase_order(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """購買発注書を削除"""
    try:
        po_id = get_path_parameter(event, 'po_id')
        if not po_id:
            return create_error_response(400, 'Purchase order ID is required')
        
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        dynamodb = get_dynamodb_resource()
        po_table = dynamodb.Table(os.environ['PURCHASE_ORDERS_TABLE'])
        
        # 既存の発注書を取得
        response = po_table.get_item(Key={'po_id': po_id})
        if 'Item' not in response:
            return create_error_response(404, 'Purchase order not found')
        
        purchase_order = PurchaseOrder.from_dict(response['Item'])
        
        # 権限チェック：管理者または作成者のみ削除可能
        if user_role != UserRole.ADMIN.value and purchase_order.created_by != user_id:
            return create_error_response(403, 'Access denied')
        
        # 発注書を削除
        po_table.delete_item(Key={'po_id': po_id})
        
        return create_response(200, {'message': 'Purchase order deleted successfully'})
        
    except ClientError as e:
        return handle_dynamodb_error(e)


def _check_user_permission(user_id: str, permission: str) -> bool:
    """ユーザーが特定の権限を持っているかチェック"""
    try:
        dynamodb = get_dynamodb_resource()
        users_table = dynamodb.Table(os.environ['USERS_TABLE'])
        
        response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' not in response:
            return False
        
        user_permissions = response['Item'].get('permissions', [])
        return permission in user_permissions
        
    except ClientError:
        return False