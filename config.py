"""
환경 변수를 불러와서 설정 관리
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 네이버 API 인증 정보
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# API 키 확인
if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
    raise ValueError(
        "⚠️ API 키가 설정되지 않았습니다!\n"
        ".env 파일을 생성하고 NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 입력하세요.\n"
        ".env.example 파일을 참고하세요."
    )

# 프로젝트 설정
PROJECT_NAME = os.getenv("PROJECT_NAME", "soda-project")
START_DATE = os.getenv("START_DATE", "2025-11-15")
END_DATE = os.getenv("END_DATE", "2025-11-22")

# 분석 대상 키워드
KEYWORDS_MAIN = ["선크림", "자외선차단제", "스키장", "보드"]
KEYWORDS_BRANDS = ["라운드랩 선크림", "토리든 선크림", "닥터지 선크림"]

# 타겟 세그먼트
SEGMENTS = [
    ("20대 여성", "f", ["3", "4"]),
    ("30대 여성", "f", ["5", "6"]),
    ("40대 여성", "f", ["7", "8"]),
    ("20대 남성", "m", ["3", "4"]),
    ("30대 남성", "m", ["5", "6"]),
    ("40대 남성", "m", ["7", "8"]),
]

print(f"✅ Config 로드 완료: {PROJECT_NAME}")