#!/usr/bin/env python
"""
Render 배포 환경에서 관리자 계정을 생성하는 스크립트
로컬에서 Render 데이터베이스에 연결하여 실행

사용법:
python create_admin.py --database-url "postgresql://..." --username admin --email admin@admin.com --password admin123
"""

import os
import sys

# Django 설정 모듈 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
import argparse


def create_admin_user(username, email, password):
    """관리자 계정 생성"""
    from django.contrib.auth import get_user_model
    from django.db import connection
    
    User = get_user_model()
    
    try:
        # 데이터베이스 연결 확인
        connection.ensure_connection()
        print(f"✓ 데이터베이스 연결 성공: {connection.settings_dict['NAME']}")
        
        # 이미 존재하는 사용자 확인
        if User.objects.filter(username=username).exists():
            print(f"⚠️  사용자 '{username}'가 이미 존재합니다.")
            print("기존 사용자를 관리자로 설정하고 비밀번호를 업데이트합니다...")
            
            user = User.objects.get(username=username)
            user.is_superuser = True
            user.is_staff = True
            if email:
                user.email = email
            user.set_password(password)
            user.save()
            print(f"✓ 사용자 '{username}'를 관리자로 설정하고 비밀번호를 업데이트했습니다.")
            return
        
        # 새 관리자 계정 생성
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ 관리자 계정 '{username}' 생성 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Render 배포 환경에서 Django 관리자 계정 생성')
    parser.add_argument('--database-url', required=True, help='Render DATABASE_URL')
    parser.add_argument('--username', default='admin', help='관리자 사용자명 (기본값: admin)')
    parser.add_argument('--email', required=True, help='관리자 이메일')
    parser.add_argument('--password', required=True, help='관리자 비밀번호')
    
    args = parser.parse_args()
    
    # DATABASE_URL 설정 (django.setup() 전에 설정해야 함)
    os.environ['DATABASE_URL'] = args.database_url
    
    # Django 설정 로드 (DATABASE_URL 설정 후)
    django.setup()
    
    print("\n" + "="*50)
    print("Render 관리자 계정 생성")
    print("="*50)
    print(f"사용자명: {args.username}")
    print(f"이메일: {args.email}")
    print("="*50 + "\n")
    
    create_admin_user(args.username, args.email, args.password)


if __name__ == '__main__':
    main()
