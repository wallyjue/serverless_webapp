"""
ユーザー管理関連のLambda関数

管理者がユーザーを管理するための機能を提供します。
"""
import json
import os
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from utils import (
    create_response,
    create_error_response,
    require_auth,
    require_admin,
    get_cognito_client,
    get_dynamodb_resource,
    get_path_parameter,
    validate_email,
    validate_required_fields
)
from models import User, UserRole, generate_id


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """ユーザー管理のメインハンドラー"""
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if path == '/users' and http_method == 'GET':
            return get_users(event, context)
        elif path == '/users' and http_method == 'POST':
            return create_user(event, context)
        elif path.startswith('/users/') and http_method == 'PUT':
            return update_user(event, context)
        elif path.startswith('/users/') and http_method == 'DELETE':
            return delete_user(event, context)
        else:
            return create_error_response(404, 'Endpoint not found')
    
    except Exception as e:
        print(f"Error in user management handler: {str(e)}")
        return create_error_response(500, 'Internal server error')


@require_auth
@require_admin
def get_users(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """すべてのユーザーを取得（管理者のみ）"""
    try:
        dynamodb = get_dynamodb_resource()
        users_table = dynamodb.Table(os.environ['USERS_TABLE'])
        
        response = users_table.scan()
        users = []
        
        for item in response['Items']:
            user = User.from_dict(item)
            users.append({
                'user_id': user.user_id,
                'email': user.email,
                'role': user.role.value,
                'permissions': user.permissions,
                'created_at': user.created_at,
                'updated_at': user.updated_at
            })
        
        return create_response(200, {'users': users})
        
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return create_error_response(500, 'Failed to retrieve users')


@require_auth
@require_admin
def create_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """新しいユーザーを作成（管理者のみ）"""
    try:
        body = json.loads(event['body'])
        
        # 必須フィールドの検証
        is_valid, error_msg = validate_required_fields(body, ['email', 'password', 'role'])
        if not is_valid:
            return create_error_response(400, error_msg)
        
        email = body['email']
        password = body['password']
        role = body['role']
        permissions = body.get('permissions', [])
        
        # メールアドレスの形式検証
        if not validate_email(email):
            return create_error_response(400, 'Invalid email format')
        
        # 役割の検証
        try:
            user_role = UserRole(role)
        except ValueError:
            return create_error_response(400, 'Invalid role')
        
        # Cognitoでユーザーを作成
        cognito_client = get_cognito_client()
        user_pool_id = os.environ['COGNITO_USER_POOL_ID']
        
        try:
            response = cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'custom:role', 'Value': role}
                ],
                TemporaryPassword=password,
                MessageAction='SUPPRESS'
            )
            
            # 一時パスワードを恒久パスワードに設定
            cognito_client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=email,
                Password=password,
                Permanent=True
            )
            
            # DynamoDBにユーザー情報を保存
            dynamodb = get_dynamodb_resource()
            users_table = dynamodb.Table(os.environ['USERS_TABLE'])
            
            user = User(
                user_id=response['User']['Username'],
                email=email,
                role=user_role,
                permissions=permissions
            )
            
            users_table.put_item(Item=user.to_dict())
            
            return create_response(201, {
                'message': 'User created successfully',
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'role': user.role.value,
                    'permissions': user.permissions,
                    'created_at': user.created_at
                }
            })
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                return create_error_response(409, 'User already exists')
            else:
                return create_error_response(500, 'User creation failed')
                
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')


@require_auth
@require_admin
def update_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """ユーザー情報を更新（管理者のみ）"""
    try:
        user_id = get_path_parameter(event, 'user_id')
        if not user_id:
            return create_error_response(400, 'User ID is required')
        
        body = json.loads(event['body'])
        
        # 更新可能なフィールド
        allowed_fields = ['role', 'permissions']
        update_data = {k: v for k, v in body.items() if k in allowed_fields}
        
        if not update_data:
            return create_error_response(400, 'No valid fields to update')
        
        # DynamoDBからユーザーを取得
        dynamodb = get_dynamodb_resource()
        users_table = dynamodb.Table(os.environ['USERS_TABLE'])
        
        try:
            response = users_table.get_item(Key={'user_id': user_id})
            if 'Item' not in response:
                return create_error_response(404, 'User not found')
            
            user = User.from_dict(response['Item'])
            
            # 役割の更新
            if 'role' in update_data:
                try:
                    new_role = UserRole(update_data['role'])
                    user.role = new_role
                    
                    # Cognitoの属性も更新
                    cognito_client = get_cognito_client()
                    user_pool_id = os.environ['COGNITO_USER_POOL_ID']
                    
                    cognito_client.admin_update_user_attributes(
                        UserPoolId=user_pool_id,
                        Username=user.email,
                        UserAttributes=[
                            {'Name': 'custom:role', 'Value': update_data['role']}
                        ]
                    )
                    
                except ValueError:
                    return create_error_response(400, 'Invalid role')
            
            # 権限の更新
            if 'permissions' in update_data:
                user.permissions = update_data['permissions']
            
            # 更新日時を設定
            from datetime import datetime
            user.updated_at = datetime.utcnow().isoformat()
            
            # DynamoDBを更新
            users_table.put_item(Item=user.to_dict())
            
            return create_response(200, {
                'message': 'User updated successfully',
                'user': {
                    'user_id': user.user_id,
                    'email': user.email,
                    'role': user.role.value,
                    'permissions': user.permissions,
                    'updated_at': user.updated_at
                }
            })
            
        except ClientError as e:
            print(f"Error updating user: {str(e)}")
            return create_error_response(500, 'Failed to update user')
            
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')


@require_auth
@require_admin
def delete_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """ユーザーを削除（管理者のみ）"""
    try:
        user_id = get_path_parameter(event, 'user_id')
        if not user_id:
            return create_error_response(400, 'User ID is required')
        
        # DynamoDBからユーザーを取得
        dynamodb = get_dynamodb_resource()
        users_table = dynamodb.Table(os.environ['USERS_TABLE'])
        
        response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' not in response:
            return create_error_response(404, 'User not found')
        
        user = User.from_dict(response['Item'])
        
        # 自分自身は削除できない
        current_user = event.get('user', {})
        if current_user.get('sub') == user_id:
            return create_error_response(400, 'Cannot delete your own account')
        
        # Cognitoからユーザーを削除
        cognito_client = get_cognito_client()
        user_pool_id = os.environ['COGNITO_USER_POOL_ID']
        
        try:
            cognito_client.admin_delete_user(
                UserPoolId=user_pool_id,
                Username=user.email
            )
            
            # DynamoDBからユーザーを削除
            users_table.delete_item(Key={'user_id': user_id})
            
            return create_response(200, {'message': 'User deleted successfully'})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UserNotFoundException':
                # Cognitoにユーザーが存在しない場合でもDynamoDBからは削除
                users_table.delete_item(Key={'user_id': user_id})
                return create_response(200, {'message': 'User deleted successfully'})
            else:
                return create_error_response(500, 'Failed to delete user')
                
    except ClientError as e:
        print(f"Error deleting user: {str(e)}")
        return create_error_response(500, 'Failed to delete user')