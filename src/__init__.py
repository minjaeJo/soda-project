# src/__init__.py
"""
프로젝트 전역 설정 및 초기화
"""

import sys
import os
from pathlib import Path

# ============================================
# 프로젝트 루트 경로 자동 탐지
# ============================================
def get_project_root():
    """
    config.py가 있는 프로젝트 루트 디렉토리를 찾습니다.
    """
    current = Path(__file__).resolve().parent  # src/ 폴더
    project_root = current.parent  # 프로젝트 루트
    
    # config.py가 있는지 확인
    if (project_root / 'config.py').exists():
        return project_root
    
    # 없으면 상위로 계속 탐색
    for parent in current.parents:
        if (parent / 'config.py').exists():
            return parent
    
    raise FileNotFoundError("config.py를 찾을 수 없습니다. 프로젝트 루트에 config.py가 있는지 확인하세요.")

# 프로젝트 루트를 sys.path에 추가 ✅
PROJECT_ROOT = get_project_root()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))  # ✅ 'src' 제거!

# ============================================
# config 임포트 및 전역 변수 설정
# ============================================
try:
    import config
    
    NAVER_CLIENT_ID = config.NAVER_CLIENT_ID
    NAVER_CLIENT_SECRET = config.NAVER_CLIENT_SECRET
    
except ImportError as e:
    raise ImportError(
        f"config.py를 불러올 수 없습니다: {e}\n"
        f"프로젝트 루트: {PROJECT_ROOT}\n"
        f"sys.path: {sys.path[:3]}\n"  # 디버깅용
        f"config.py 경로를 확인하세요."
    )

except AttributeError as e:
    raise AttributeError(
        f"config.py에 필수 설정이 없습니다: {e}\n"
        ".env 파일을 생성하고 다음 항목을 추가하세요:\n"
        "  NAVER_CLIENT_ID=your_client_id\n"
        "  NAVER_CLIENT_SECRET=your_client_secret"
    )

# ============================================
# 편의 함수
# ============================================
def get_data_dir():
    """data/ 디렉토리 경로 반환"""
    return PROJECT_ROOT / 'data'

def get_output_dir():
    """outputs/ 디렉토리 경로 반환"""
    return PROJECT_ROOT / 'outputs'

# 필요한 디렉토리 자동 생성
for dir_path in [get_data_dir(), get_output_dir()]:
    dir_path.mkdir(exist_ok=True)

# ============================================
# 버전 정보
# ============================================
__version__ = '1.0.0'
__all__ = [
    'NAVER_CLIENT_ID',
    'NAVER_CLIENT_SECRET',
    'PROJECT_ROOT',
    'get_data_dir',
    'get_output_dir',
]