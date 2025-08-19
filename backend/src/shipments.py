"""
出荷管理関連のLambda関数

出荷のCRUD操作を提供します。
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
from models import Shipment, ShipmentStatus, UserRole, generate_id


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """出荷管理のメインハンドラー"""
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if path == '/shipments' and http_method == 'GET':
            return get_shipments(event, context)
        elif path == '/shipments' and http_method == 'POST':
            return create_shipment(event, context)
        elif path.startswith('/shipments/') and http_method == 'GET':
            return get_shipment(event, context)
        elif path.startswith('/shipments/') and http_method == 'PUT':
            return update_shipment(event, context)
        elif path.startswith('/shipments/') and http_method == 'DELETE':
            return delete_shipment(event, context)
        else:
            return create_error_response(404, 'Endpoint not found')
    
    except Exception as e:
        print(f"Error in shipments handler: {str(e)}")
        return create_error_response(500, 'Internal server error')


@require_auth
def get_shipments(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """出荷の一覧を取得"""
    try:
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        dynamodb = get_dynamodb_resource()
        shipments_table = dynamodb.Table(os.environ['SHIPMENTS_TABLE'])
        
        # クエリパラメータで購買発注書IDによるフィルタリングをサポート
        po_id = get_query_parameter(event, 'po_id')
        
        if po_id:
            # 特定の購買発注書に関連する出荷を取得
            response = shipments_table.query(
                IndexName='po-id-index',
                KeyConditionExpression='po_id = :po_id',
                ExpressionAttributeValues={':po_id': po_id}
            )
        else:
            # 管理者はすべての出荷を閲覧可能、一般ユーザーは自分が作成したもののみ
            if user_role == UserRole.ADMIN.value:
                response = shipments_table.scan()
            else:
                # 一般ユーザーの場合、created_byでフィルタリング
                response = shipments_table.scan(
                    FilterExpression='created_by = :user_id',
                    ExpressionAttributeValues={':user_id': user_id}
                )
        
        shipments = []
        for item in response['Items']:
            shipment = Shipment.from_dict(item)
            shipments.append({
                'shipment_id': shipment.shipment_id,
                'po_id': shipment.po_id,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'status': shipment.status.value,
                'created_by': shipment.created_by,
                'estimated_delivery': shipment.estimated_delivery,
                'actual_delivery': shipment.actual_delivery,
                'created_at': shipment.created_at,
                'updated_at': shipment.updated_at,
                'notes': shipment.notes
            })
        
        # 作成日時で降順ソート
        shipments.sort(key=lambda x: x['created_at'], reverse=True)
        
        return create_response(200, {'shipments': shipments})
        
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def create_shipment(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """新しい出荷を作成"""
    try:
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        # 権限チェック：管理者または shipment_create 権限を持つユーザー
        if user_role != UserRole.ADMIN.value:
            # 一般ユーザーの権限を確認
            if not _check_user_permission(user_id, 'shipment_create'):
                return create_error_response(403, 'Permission denied: shipment_create required')
        
        body = json.loads(event['body'])
        
        # 必須フィールドの検証
        is_valid, error_msg = validate_required_fields(body, ['po_id', 'tracking_number', 'carrier'])
        if not is_valid:
            return create_error_response(400, error_msg)
        
        po_id = body['po_id']
        tracking_number = body['tracking_number']
        carrier = body['carrier']
        estimated_delivery = body.get('estimated_delivery')
        notes = body.get('notes')
        
        # 購買発注書の存在確認
        if not _verify_purchase_order_exists(po_id):
            return create_error_response(400, 'Purchase order not found')
        
        # 出荷を作成
        shipment_id = generate_id()
        shipment = Shipment(
            shipment_id=shipment_id,
            po_id=po_id,
            tracking_number=tracking_number,
            carrier=carrier,
            status=ShipmentStatus.PENDING,
            created_by=user_id,
            estimated_delivery=estimated_delivery,
            notes=notes
        )
        
        # DynamoDBに保存
        dynamodb = get_dynamodb_resource()
        shipments_table = dynamodb.Table(os.environ['SHIPMENTS_TABLE'])
        
        shipments_table.put_item(Item=shipment.to_dict())
        
        return create_response(201, {
            'message': 'Shipment created successfully',
            'shipment': {
                'shipment_id': shipment.shipment_id,
                'po_id': shipment.po_id,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'status': shipment.status.value,
                'created_by': shipment.created_by,
                'estimated_delivery': shipment.estimated_delivery,
                'created_at': shipment.created_at,
                'notes': shipment.notes
            }
        })
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def get_shipment(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """特定の出荷を取得"""
    try:
        shipment_id = get_path_parameter(event, 'shipment_id')
        if not shipment_id:
            return create_error_response(400, 'Shipment ID is required')
        
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        dynamodb = get_dynamodb_resource()
        shipments_table = dynamodb.Table(os.environ['SHIPMENTS_TABLE'])
        
        response = shipments_table.get_item(Key={'shipment_id': shipment_id})
        if 'Item' not in response:
            return create_error_response(404, 'Shipment not found')
        
        shipment = Shipment.from_dict(response['Item'])
        
        # 権限チェック：管理者または作成者のみアクセス可能
        if user_role != UserRole.ADMIN.value and shipment.created_by != user_id:
            return create_error_response(403, 'Access denied')
        
        return create_response(200, {
            'shipment': {
                'shipment_id': shipment.shipment_id,
                'po_id': shipment.po_id,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'status': shipment.status.value,
                'created_by': shipment.created_by,
                'estimated_delivery': shipment.estimated_delivery,
                'actual_delivery': shipment.actual_delivery,
                'created_at': shipment.created_at,
                'updated_at': shipment.updated_at,
                'notes': shipment.notes
            }
        })
        
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def update_shipment(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """出荷を更新"""
    try:
        shipment_id = get_path_parameter(event, 'shipment_id')
        if not shipment_id:
            return create_error_response(400, 'Shipment ID is required')
        
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        body = json.loads(event['body'])
        
        dynamodb = get_dynamodb_resource()
        shipments_table = dynamodb.Table(os.environ['SHIPMENTS_TABLE'])
        
        # 既存の出荷を取得
        response = shipments_table.get_item(Key={'shipment_id': shipment_id})
        if 'Item' not in response:
            return create_error_response(404, 'Shipment not found')
        
        shipment = Shipment.from_dict(response['Item'])
        
        # 権限チェック：管理者または作成者のみ更新可能
        if user_role != UserRole.ADMIN.value and shipment.created_by != user_id:
            return create_error_response(403, 'Access denied')
        
        # 更新可能なフィールド
        allowed_fields = ['tracking_number', 'carrier', 'status', 'estimated_delivery', 'actual_delivery', 'notes']
        update_data = {k: v for k, v in body.items() if k in allowed_fields}
        
        if not update_data:
            return create_error_response(400, 'No valid fields to update')
        
        # フィールドの更新
        if 'tracking_number' in update_data:
            shipment.tracking_number = update_data['tracking_number']
        
        if 'carrier' in update_data:
            shipment.carrier = update_data['carrier']
        
        if 'status' in update_data:
            try:
                new_status = ShipmentStatus(update_data['status'])
                shipment.status = new_status
                
                # ステータスが配送完了になった場合は実際の配送日を設定
                if new_status == ShipmentStatus.DELIVERED and not shipment.actual_delivery:
                    shipment.actual_delivery = datetime.utcnow().isoformat()
                    
            except ValueError:
                return create_error_response(400, 'Invalid status')
        
        if 'estimated_delivery' in update_data:
            shipment.estimated_delivery = update_data['estimated_delivery']
        
        if 'actual_delivery' in update_data:
            shipment.actual_delivery = update_data['actual_delivery']
        
        if 'notes' in update_data:
            shipment.notes = update_data['notes']
        
        # 更新日時を設定
        shipment.updated_at = datetime.utcnow().isoformat()
        
        # DynamoDBを更新
        shipments_table.put_item(Item=shipment.to_dict())
        
        return create_response(200, {
            'message': 'Shipment updated successfully',
            'shipment': {
                'shipment_id': shipment.shipment_id,
                'po_id': shipment.po_id,
                'tracking_number': shipment.tracking_number,
                'carrier': shipment.carrier,
                'status': shipment.status.value,
                'created_by': shipment.created_by,
                'estimated_delivery': shipment.estimated_delivery,
                'actual_delivery': shipment.actual_delivery,
                'updated_at': shipment.updated_at,
                'notes': shipment.notes
            }
        })
        
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')
    except ClientError as e:
        return handle_dynamodb_error(e)


@require_auth
def delete_shipment(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """出荷を削除"""
    try:
        shipment_id = get_path_parameter(event, 'shipment_id')
        if not shipment_id:
            return create_error_response(400, 'Shipment ID is required')
        
        user = event.get('user', {})
        user_role = user.get('custom:role', 'user')
        user_id = user.get('sub')
        
        dynamodb = get_dynamodb_resource()
        shipments_table = dynamodb.Table(os.environ['SHIPMENTS_TABLE'])
        
        # 既存の出荷を取得
        response = shipments_table.get_item(Key={'shipment_id': shipment_id})
        if 'Item' not in response:
            return create_error_response(404, 'Shipment not found')
        
        shipment = Shipment.from_dict(response['Item'])
        
        # 権限チェック：管理者または作成者のみ削除可能
        if user_role != UserRole.ADMIN.value and shipment.created_by != user_id:
            return create_error_response(403, 'Access denied')
        
        # 出荷を削除
        shipments_table.delete_item(Key={'shipment_id': shipment_id})
        
        return create_response(200, {'message': 'Shipment deleted successfully'})
        
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


def _verify_purchase_order_exists(po_id: str) -> bool:
    """購買発注書が存在するかチェック"""
    try:
        dynamodb = get_dynamodb_resource()
        po_table = dynamodb.Table(os.environ['PURCHASE_ORDERS_TABLE'])
        
        response = po_table.get_item(Key={'po_id': po_id})
        return 'Item' in response
        
    except ClientError:
        return False