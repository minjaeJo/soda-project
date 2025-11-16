# tests/test_api.py
"""
네이버 API 연결 테스트 스크립트
"""

import sys
import os

# ============================================
# 🔧 경로 설정 (가장 중요!)
# ============================================
# 현재 파일의 절대 경로
current_file = os.path.abspath(__file__)
print(f"📍 현재 파일: {current_file}")

# tests 폴더 경로
tests_dir = os.path.dirname(current_file)
print(f"📁 tests 폴더: {tests_dir}")

# 프로젝트 루트 경로 (tests의 상위)
project_root = os.path.dirname(tests_dir)
print(f"📁 프로젝트 루트: {project_root}")

# Python 경로에 루트 추가
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"✅ sys.path에 추가됨: {project_root}")

print(f"\n현재 sys.path:")
for p in sys.path[:3]:
    print(f"  - {p}")
print()

# ============================================
# config import
# ============================================
try:
    import config
    NAVER_CLIENT_ID = config.NAVER_CLIENT_ID
    NAVER_CLIENT_SECRET = config.NAVER_CLIENT_SECRET
    print(f"✅ config.py 로드 성공")
    
except ImportError as e:
    print(f"❌ config.py를 불러올 수 없습니다: {e}")
    print(f"\n🔍 디버깅 정보:")
    print(f"  현재 작업 디렉토리: {os.getcwd()}")
    print(f"  프로젝트 루트: {project_root}")
    print(f"  config.py 존재 여부: {os.path.exists(os.path.join(project_root, 'config.py'))}")
    sys.exit(1)
    
except AttributeError as e:
    print(f"❌ config.py에 API 키가 없습니다: {e}")
    print(f"  .env 파일을 생성하고 API 키를 입력하세요")
    sys.exit(1)

import requests
import json
from datetime import datetime

# ============================================
# 색상 출력
# ============================================
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"   {text}")

# ============================================
# 테스트 함수들
# ============================================
def test_config():
    """API 키 확인"""
    print_header("1. API 키 설정 확인")
    
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print_error("API 키가 설정되지 않았습니다")
        print_info("해결 방법:")
        print_info("1. .env.example을 복사하여 .env 파일 생성")
        print_info("2. 네이버 개발자 센터에서 API 키 발급")
        print_info("   https://developers.naver.com/apps/#/register")
        print_info("3. .env 파일에 API 키 입력")
        return False
    
    # API 키 마스킹
    masked_id = NAVER_CLIENT_ID[:4] + "*" * (len(NAVER_CLIENT_ID) - 8) + NAVER_CLIENT_ID[-4:]
    masked_secret = NAVER_CLIENT_SECRET[:4] + "*" * (len(NAVER_CLIENT_SECRET) - 8) + NAVER_CLIENT_SECRET[-4:]
    
    print_success("API 키 로드 성공")
    print_info(f"Client ID: {masked_id}")
    print_info(f"Client Secret: {masked_secret}")
    
    return True

def test_datalab_api():
    """데이터랩 API 테스트"""
    print_header("2. 데이터랩 API 테스트")
    
    try:
        url = "https://openapi.naver.com/v1/datalab/search"
        
        body = {
            "startDate": "2025-01-01",
            "endDate": "2025-01-31",
            "timeUnit": "month",
            "keywordGroups": [
                {
                    "groupName": "테스트",
                    "keywords": ["테스트"]
                }
            ]
        }
        
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
            "Content-Type": "application/json"
        }
        
        print_info("API 요청 중...")
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        if response.status_code == 200:
            data = response.json()
            print_success("데이터랩 API 연결 성공!")
            
            if 'results' in data and len(data['results']) > 0:
                print_success(f"검색 트렌드 데이터 수신 ({len(data['results'][0]['data'])}개)")
            
            return True
            
        elif response.status_code == 401:
            print_error("인증 실패 (401)")
            print_info("API 키가 올바른지 확인하세요")
            return False
            
        elif response.status_code == 403:
            print_error("접근 거부 (403)")
            print_info("데이터랩 API를 애플리케이션에 추가하세요")
            return False
            
        else:
            print_error(f"API 오류 (HTTP {response.status_code})")
            print_info(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"테스트 실패: {e}")
        return False

def test_shopping_api():
    """쇼핑 검색 API 테스트"""
    print_header("3. 쇼핑 검색 API 테스트")
    
    try:
        url = "https://openapi.naver.com/v1/search/shop.json"
        
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        params = {"query": "테스트", "display": 5}
        
        print_info("API 요청 중...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print_success("쇼핑 검색 API 연결 성공!")
            
            if 'items' in data and len(data['items']) > 0:
                print_success(f"검색 결과: {data['total']}건")
            
            return True
        else:
            print_error(f"API 오류 (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print_error(f"테스트 실패: {e}")
        return False

def test_blog_api():
    """블로그 검색 API 테스트"""
    print_header("4. 블로그 검색 API 테스트")
    
    try:
        url = "https://openapi.naver.com/v1/search/blog.json"
        
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        params = {"query": "테스트", "display": 5}
        
        print_info("API 요청 중...")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print_success("블로그 검색 API 연결 성공!")
            
            if 'items' in data and len(data['items']) > 0:
                print_success(f"검색 결과: {data['total']}건")
            
            return True
        else:
            print_error(f"API 오류 (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print_error(f"테스트 실패: {e}")
        return False

# ============================================
# 메인
# ============================================
def main():
    """전체 테스트 실행"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}🧪 네이버 API 연결 테스트{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"테스트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {}
    
    # API 키 확인
    results['config'] = test_config()
    
    if not results['config']:
        print_warning("\nAPI 키 설정이 완료되지 않아 테스트를 중단합니다")
        return
    
    # API 테스트
    results['datalab'] = test_datalab_api()
    results['shopping'] = test_shopping_api()
    results['blog'] = test_blog_api()
    
    # 결과 요약
    print_header("테스트 결과 요약")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n총 {total}개 테스트 중 {passed}개 성공\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print()
    
    if passed == total:
        print_success("🎉 모든 테스트 통과!")
        print_info("\n다음 단계:")
        print_info("python scripts/01_collect_data.py")
    else:
        print_warning("일부 테스트가 실패했습니다")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}테스트 중단{Colors.END}")
