"""
SODA 프로젝트 - 발표 자료 데이터 수집
Dataset 1: 선크림 그룹 월별 시계열
"""

import sys
from pathlib import Path
import pandas as pd

# ============================================
# 경로 설정
# ============================================
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
src_dir = current_file.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from naver_api import NaverDataLab

PROJECT_ROOT = project_root


def collect_dataset_1():
    """
    Dataset 1: 선크림 그룹 월별 검색 트렌드
    
    기간: 2020-02-01 ~ 2025-02-28 (5년)
    키워드: 선크림, 썬크림, 자외선차단제
    결과: CSV 파일 (date, 선크림, 썬크림, 자외선차단제, year, month, season)
    """
    
    print("="*60)
    print("📊 Dataset 1: 선크림 그룹 월별 시계열 수집")
    print("="*60)
    
    # 데이터랩 API 초기화
    datalab = NaverDataLab()
    
    # 저장 경로
    data_dir = PROJECT_ROOT / 'data' / 'presentation'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 수집 설정
    keywords = ["선크림", "썬크림", "자외선차단제"]
    start_date = "2020-02-01"
    end_date = "2025-02-28"
    
    print(f"\n📅 기간: {start_date} ~ {end_date}")
    print(f"🔍 키워드: {', '.join(keywords)}")
    print(f"\n수집 중...", end=" ")
    
    # API 호출
    result = datalab.get_search_trend(
        keywords=keywords,
        start_date=start_date,
        end_date=end_date,
        time_unit="month"
    )
    
    # DataFrame 변환
    df = datalab.to_dataframe(result)
    
    # 추가 컬럼 생성
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['season'] = df['month'].apply(
        lambda x: '겨울' if x in [12,1,2] else ('여름' if x in [6,7,8] else '기타')
    )
    
    print(f"✅ 완료!")
    
    # 데이터 요약
    print(f"\n📊 수집 결과:")
    print(f"   총 개월 수: {len(df)}개월")
    print(f"   기간: {df['date'].min().strftime('%Y-%m')} ~ {df['date'].max().strftime('%Y-%m')}")
    print(f"   컬럼: {', '.join(df.columns.tolist())}")
    
    # 계절별 평균 출력
    print(f"\n📈 계절별 평균 (선크림 기준):")
    seasonal_avg = df.groupby('season')['선크림'].mean()
    for season, value in seasonal_avg.items():
        print(f"   {season}: {value:.1f}")
    
    # 저장
    filepath = data_dir / "01_선크림_월별_트렌드.csv"
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 저장 완료: {filepath}")
    print(f"\n✅ Dataset 1 수집 완료!")
    
    return df


if __name__ == "__main__":
    try:
        df = collect_dataset_1()
        
        print("\n" + "="*60)
        print("📋 데이터 미리보기 (처음 5행)")
        print("="*60)
        print(df.head().to_string())
        
        print("\n" + "="*60)
        print("📋 데이터 미리보기 (마지막 5행)")
        print("="*60)
        print(df.tail().to_string())
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
