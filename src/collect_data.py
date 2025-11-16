# src/collect_data.py
import pandas as pd
from pathlib import Path
import time
import sys

# ============================================
# 임포트 처리 (직접 실행 vs 패키지 임포트)
# ============================================
try:
    # 패키지로 임포트될 때
    from . import PROJECT_ROOT, get_data_dir
    from .naver_api import NaverDataLab, NaverShopping, NaverBlog
except ImportError:
    # 직접 실행될 때
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # config 임포트
    import config
    PROJECT_ROOT = project_root
    
    # data 디렉토리 함수
    def get_data_dir():
        data_dir = PROJECT_ROOT / 'data'
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    # naver_api 임포트
    from naver_api import NaverDataLab, NaverShopping, NaverBlog

def collect_all_data():
    """모든 데이터 수집"""
    
    print("🚀 데이터 수집 시작...\n")
    
    # data 폴더 경로 (자동으로 생성됨)
    data_dir = get_data_dir()
    
    # ============================================
    # 1. 검색 트렌드 (메인 키워드)
    # ============================================
    print("📊 1/5: 검색 트렌드 수집 중...")
    
    datalab = NaverDataLab()
    
    # 주요 키워드 검색량 (월별, 3년치)
    keywords_main = ["선크림", "자외선차단제", "스키장", "보드"]
    
    result = datalab.get_search_trend(
        keywords=keywords_main,
        start_date="2022-01-01",
        end_date="2025-11-15",
        time_unit="month"
    )
    
    df_trend = datalab.to_dataframe(result)
    df_trend.to_csv(data_dir / "01_search_trend_monthly.csv", 
                    index=False, encoding='utf-8-sig')
    print(f"  ✅ 저장: 01_search_trend_monthly.csv ({len(df_trend)}행)\n")
    
    time.sleep(1)  # API 호출 간격
    
    # ============================================
    # 2. 주별 검색량 (타이밍 분석용)
    # ============================================
    print("📊 2/5: 주별 검색량 수집 중...")
    
    result_weekly = datalab.get_search_trend(
        keywords=["선크림"],
        start_date="2024-09-01",
        end_date="2025-11-15",
        time_unit="week"
    )
    
    df_weekly = datalab.to_dataframe(result_weekly)
    df_weekly.to_csv(data_dir / "02_search_trend_weekly.csv", 
                     index=False, encoding='utf-8-sig')
    print(f"  ✅ 저장: 02_search_trend_weekly.csv ({len(df_weekly)}행)\n")
    
    time.sleep(1)
    
    # ============================================
    # 3. 세그먼트별 검색 (6개)
    # ============================================
    print("📊 3/5: 세그먼트별 데이터 수집 중...")
    
    segments = [
        ("20대 여성", "f", ["3", "4"]),
        ("30대 여성", "f", ["5", "6"]),
        ("40대 여성", "f", ["7", "8"]),
        ("20대 남성", "m", ["3", "4"]),
        ("30대 남성", "m", ["5", "6"]),
        ("40대 남성", "m", ["7", "8"]),
    ]
    
    for name, gender, ages in segments:
        result_seg = datalab.get_search_trend(
            keywords=["선크림"],
            start_date="2023-01-01",
            end_date="2025-11-15",
            time_unit="month",
            gender=gender,
            ages=ages
        )
        
        df_seg = datalab.to_dataframe(result_seg)
        filename = f"03_segment_{name.replace(' ', '_')}.csv"
        df_seg.to_csv(data_dir / filename, index=False, encoding='utf-8-sig')
        print(f"  ✅ {name}: {len(df_seg)}행")
        
        time.sleep(1)
    
    print()
    
    # ============================================
    # 4. 경쟁 브랜드 검색량
    # ============================================
    print("📊 4/5: 경쟁사 검색량 수집 중...")
    
    brands = ["라운드랩 선크림", "토리든 선크림", "닥터지 선크림"]
    
    result_brands = datalab.get_search_trend(
        keywords=brands,
        start_date="2022-01-01",
        end_date="2025-11-15",
        time_unit="month"
    )
    
    df_brands = datalab.to_dataframe(result_brands)
    df_brands.to_csv(data_dir / "04_competitor_brands.csv", 
                     index=False, encoding='utf-8-sig')
    print(f"  ✅ 저장: 04_competitor_brands.csv ({len(df_brands)}행)\n")
    
    time.sleep(1)
    
    # ============================================
    # 5. 쇼핑 제품 데이터
    # ============================================
    print("📊 5/5: 쇼핑 제품 수집 중...")
    
    shopping = NaverShopping()
    
    # 선크림 제품 500개
    items = shopping.get_all_products("선크림", max_results=500)
    df_products = shopping.to_dataframe(items)
    df_products.to_csv(data_dir / "05_shopping_products.csv", 
                       index=False, encoding='utf-8-sig')
    print(f"  ✅ 저장: 05_shopping_products.csv ({len(df_products)}행)\n")
    
    # ============================================
    # 완료
    # ============================================
    print("=" * 60)
    print("✅ 모든 데이터 수집 완료!")
    print("=" * 60)
    print(f"\n📁 저장 위치: {data_dir}")
    print("\n수집된 파일:")
    print("  1. 01_search_trend_monthly.csv")
    print("  2. 02_search_trend_weekly.csv")
    print("  3. 03_segment_*.csv (6개)")
    print("  4. 04_competitor_brands.csv")
    print("  5. 05_shopping_products.csv")
    
    return data_dir

if __name__ == "__main__":
    # 직접 실행할 때
    collect_all_data()
