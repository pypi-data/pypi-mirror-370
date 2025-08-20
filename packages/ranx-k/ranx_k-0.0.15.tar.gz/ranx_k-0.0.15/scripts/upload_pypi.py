#!/usr/bin/env python3
"""
PyPI 업로드 스크립트
.env 파일에서 토큰을 로드하여 안전하게 업로드합니다.
"""

import os
import sys
import subprocess
from pathlib import Path

# uv를 사용하여 의존성 확인 및 설치
def ensure_dependencies():
    """uv를 사용하여 필요한 의존성을 확인하고 설치합니다."""
    try:
        # uv로 dotenv 설치 확인
        result = subprocess.run(['uv', 'run', 'python', '-c', 'import dotenv'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("📦 python-dotenv 설치 중...")
            subprocess.run(['uv', 'add', 'python-dotenv'], check=True)
        
        # twine 설치 확인
        result = subprocess.run(['uv', 'run', 'python', '-c', 'import twine'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("📦 twine 설치 중...")
            subprocess.run(['uv', 'add', 'twine'], check=True)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ uv 의존성 설치 실패: {e}")
        sys.exit(1)

# 의존성 확인
ensure_dependencies()

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv 로드 실패")
    sys.exit(1)

def main():
    # .env 파일 로드
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("❌ .env 파일이 없습니다!")
        print("📝 .env.example을 참고하여 .env 파일을 생성하세요:")
        print(f"   cp {env_path.parent}/.env.example {env_path}")
        print("   # 그리고 실제 토큰으로 수정하세요")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    # 환경 변수 확인
    username = os.getenv('TWINE_USERNAME')
    password = os.getenv('TWINE_PASSWORD')
    
    if not username or not password:
        print("❌ .env 파일에 TWINE_USERNAME과 TWINE_PASSWORD가 설정되지 않았습니다!")
        sys.exit(1)
    
    if password == 'pypi-your_actual_token_here':
        print("❌ .env 파일의 토큰을 실제 PyPI 토큰으로 변경하세요!")
        sys.exit(1)
    
    print("🚀 PyPI 업로드 시작...")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * 20}...")
    
    # dist 폴더 확인
    dist_path = Path(__file__).parent.parent / 'dist'
    if not dist_path.exists() or not list(dist_path.glob('*.whl')):
        print("❌ dist/ 폴더에 빌드된 패키지가 없습니다!")
        print("   먼저 빌드를 실행하세요: python -m build")
        sys.exit(1)
    
    # uv를 사용한 twine 업로드 실행
    try:
        result = subprocess.run([
            'uv', 'run', 'twine', 'upload', 'dist/*'
        ], check=True, capture_output=True, text=True)
        
        print("✅ PyPI 업로드 성공!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ PyPI 업로드 실패!")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def upload_test():
    """TestPyPI에 업로드"""
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    
    # TestPyPI 환경 변수
    os.environ['TWINE_USERNAME'] = os.getenv('TWINE_TEST_USERNAME', '__token__')
    os.environ['TWINE_PASSWORD'] = os.getenv('TWINE_TEST_PASSWORD', '')
    
    print("🧪 TestPyPI 업로드 시작...")
    
    try:
        result = subprocess.run([
            'uv', 'run', 'twine', 'upload', '--repository', 'testpypi', 'dist/*'
        ], check=True, capture_output=True, text=True)
        
        print("✅ TestPyPI 업로드 성공!")
        print("📦 테스트 설치: pip install -i https://test.pypi.org/simple/ ranx-k")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("❌ TestPyPI 업로드 실패!")
        print(f"Error: {e.stderr}")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        upload_test()
    else:
        main()