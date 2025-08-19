"""
認証関連のLambda関数

ユーザーのログイン、ログアウト、登録機能を提供します。
"""
import json
import os
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError
from utils import (
    create_response, 
    create_error_response, 
    get_cognito_client, 
    get_dynamodb_resource,
    validate_email,
    validate_required_fields
)
from models import User, UserRole, generate_id


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """認証関連のメインハンドラー"""
    http_method = event['httpMethod']
    path = event['path']
    
    try:
        if path == '/auth/login' and http_method == 'POST':
            return login(event)
        elif path == '/auth/logout' and http_method == 'POST':
            return logout(event)
        elif path == '/auth/register' and http_method == 'POST':
            return register(event)
        else:
            return create_error_response(404, 'Endpoint not found')
    
    except Exception as e:
        print(f"Error in auth handler: {str(e)}")
        return create_error_response(500, 'Internal server error')


def login(event: Dict[str, Any]) -> Dict[str, Any]:
    """ユーザーログイン処理"""
    try:
        body = json.loads(event['body'])
        
        # 必須フィールドの検証
        is_valid, error_msg = validate_required_fields(body, ['email', 'password'])
        if not is_valid:
            return create_error_response(400, error_msg)
        
        email = body['email']
        password = body['password']
        
        # メールアドレスの形式検証
        if not validate_email(email):
            return create_error_response(400, 'Invalid email format')
        
        # Cognito認証
        cognito_client = get_cognito_client()
        user_pool_id = os.environ['COGNITO_USER_POOL_ID']
        client_id = os.environ['COGNITO_USER_POOL_CLIENT_ID']
        
        try:
            response = cognito_client.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            
            # 認証成功
            auth_result = response['AuthenticationResult']
            access_token = auth_result['AccessToken']
            id_token = auth_result['IdToken']
            refresh_token = auth_result['RefreshToken']
            
            # ユーザー情報を取得
            user_info = cognito_client.get_user(AccessToken=access_token)
            user_attributes = {attr['Name']: attr['Value'] for attr in user_info['UserAttributes']}
            
            return create_response(200, {
                'message': 'Login successful',
                'tokens': {
                    'access_token': access_token,
                    'id_token': id_token,
                    'refresh_token': refresh_token
                },
                'user': {
                    'email': user_attributes.get('email'),
                    'role': user_attributes.get('custom:role', 'user'),
                    'user_id': user_attributes.get('sub')
                }
            })
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                return create_error_response(401, 'Invalid email or password')
            elif error_code == 'UserNotConfirmedException':
                return create_error_response(401, 'User not confirmed')
            else:
                return create_error_response(500, 'Authentication failed')
                
    except json.JSONDecodeError:
        return create_error_response(400, 'Invalid JSON in request body')


def logout(event: Dict[str, Any]) -> Dict[str, Any]:
    """ユーザーログアウト処理"""
    try:
        # Authorizationヘッダーから認証情報を取得
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return create_error_response(401, 'Authorization header missing')
        
        access_token = auth_header.replace('Bearer ', '')
        
        # Cognitoからログアウト
        cognito_client = get_cognito_client()
        
        try:
            cognito_client.global_sign_out(AccessToken=access_token)
            return create_response(200, {'message': 'Logout successful'})
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                return create_error_response(401, 'Invalid token')
            else:
                return create_error_response(500, 'Logout failed')
                
    except Exception:
        return create_error_response(500, 'Logout failed')


def register(event: Dict[str, Any]) -> Dict[str, Any]:
    """新規ユーザー登録処理（管理者のみ実行可能）"""
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
            user_id = generate_id()
            
            response = cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=email,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    {'Name': 'email_verified', 'Value': 'true'},
                    {'Name': 'custom:role', 'Value': role}
                ],
                TemporaryPassword=password,
                MessageAction='SUPPRESS'  # メール送信を抑制
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
                    'permissions': user.permissions
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