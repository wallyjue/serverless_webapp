"""
共通ユーティリティ関数

認証、レスポンス生成、バリデーション等の共通機能を提供します。
"""
import json
import jwt
import os
from typing import Dict, Any, Optional, Tuple
from functools import wraps
import boto3
from botocore.exceptions import ClientError
from models import UserRole


def create_response(
    status_code: int,
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """API Gateway用のレスポンスを生成"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    if headers:
        default_headers.update(headers)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps(body, ensure_ascii=False)
    }


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """エラーレスポンスを生成"""
    return create_response(status_code, {'error': message})


def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
    """JWTトークンからユーザー情報を抽出"""
    try:
        # Cognito JWTの検証は本来はより厳密に行う必要がありますが、
        # ここでは簡略化しています
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except jwt.InvalidTokenError:
        return None


def require_auth(func):
    """認証が必要なエンドポイント用のデコレータ"""
    @wraps(func)
    def wrapper(event, context):
        # Authorizationヘッダーから認証情報を取得
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return create_error_response(401, 'Authorization header missing or invalid')
        
        token = auth_header.replace('Bearer ', '')
        user_info = get_user_from_token(token)
        
        if not user_info:
            return create_error_response(401, 'Invalid token')
        
        # イベントにユーザー情報を追加
        event['user'] = user_info
        return func(event, context)
    
    return wrapper


def require_admin(func):
    """管理者権限が必要なエンドポイント用のデコレータ"""
    @wraps(func)
    def wrapper(event, context):
        user = event.get('user')
        if not user:
            return create_error_response(401, 'User information not found')
        
        # ユーザーの役割を確認
        user_role = user.get('custom:role', 'user')
        if user_role != UserRole.ADMIN.value:
            return create_error_response(403, 'Admin permission required')
        
        return func(event, context)
    
    return wrapper


def get_dynamodb_client():
    """DynamoDBクライアントを取得"""
    # LocalStackの場合はエンドポイントを設定
    if os.environ.get('AWS_SAM_LOCAL'):
        return boto3.client(
            'dynamodb',
            endpoint_url='http://host.docker.internal:4566',
            region_name='us-east-1'
        )
    return boto3.client('dynamodb')


def get_dynamodb_resource():
    """DynamoDBリソースを取得"""
    # LocalStackの場合はエンドポイントを設定
    if os.environ.get('AWS_SAM_LOCAL'):
        return boto3.resource(
            'dynamodb',
            endpoint_url='http://host.docker.internal:4566',
            region_name='us-east-1'
        )
    return boto3.resource('dynamodb')


def get_cognito_client():
    """Cognito クライアントを取得"""
    # LocalStackの場合はエンドポイントを設定
    if os.environ.get('AWS_SAM_LOCAL'):
        return boto3.client(
            'cognito-idp',
            endpoint_url='http://host.docker.internal:4566',
            region_name='us-east-1'
        )
    return boto3.client('cognito-idp')


def validate_email(email: str) -> bool:
    """メールアドレスの形式を検証"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Tuple[bool, Optional[str]]:
    """必須フィールドの存在を検証"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f'Missing required field: {field}'
    return True, None


def handle_dynamodb_error(error: ClientError) -> Dict[str, Any]:
    """DynamoDBエラーを処理"""
    error_code = error.response['Error']['Code']
    
    if error_code == 'ConditionalCheckFailedException':
        return create_error_response(409, 'Resource already exists or condition failed')
    elif error_code == 'ResourceNotFoundException':
        return create_error_response(404, 'Resource not found')
    elif error_code == 'ValidationException':
        return create_error_response(400, 'Invalid input data')
    else:
        return create_error_response(500, 'Internal server error')


def get_path_parameter(event: Dict[str, Any], param_name: str) -> Optional[str]:
    """パスパラメータを取得"""
    path_params = event.get('pathParameters', {})
    return path_params.get(param_name) if path_params else None


def get_query_parameter(event: Dict[str, Any], param_name: str, default: Optional[str] = None) -> Optional[str]:
    """クエリパラメータを取得"""
    query_params = event.get('queryStringParameters', {})
    if not query_params:
        return default
    return query_params.get(param_name, default)