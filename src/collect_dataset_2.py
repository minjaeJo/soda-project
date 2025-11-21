"""
SODA 프로젝트 - 발표 자료 데이터 수집
Dataset 2: 겨울 실외활동 월별 시계열
"""

import sys
from pathlib import Path
import pandas as pd
import time

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


def collect_dataset_2():
    """
    Dataset 2: 겨울 실외활동 그룹별 월별 검색 트렌드
    
    기간: 2020-02-01 ~ 2025-02-28 (5년)
    키워드 그룹:
    - 스키 그룹: 스키, 스키장, 스노우보드
    - 등산: 등산, 트레킹
    - 러닝: 러닝, 조깅
    - 골프: 골프
    - 낚시: 낚시, 바다낚시
    
    결과: CSV 파일 (date, 스키그룹, 등산그룹, 러닝그룹, 골프, 낚시그룹)
    """
    
    print("="*60)
    print("📊 Dataset 2: 겨울 실외활동 그룹별 월별 시계열 수집")
    print("="*60)
    
    # 데이터랩 API 초기화
    datalab = NaverDataLab()
    
    # 저장 경로
    data_dir = PROJECT_ROOT / 'data' / 'presentation'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 수집 설정
    start_date = "2020-02-01"
    end_date = "2025-02-28"
    
    print(f"\n📅 기간: {start_date} ~ {end_date}")
    
    # 활동 그룹 정의
    activity_groups = {
        "스키": ["스키", "스키장", "스노우보드"],
        "등산": ["등산", "트레킹"],
        "러닝": ["러닝", "조깅"],
        "골프": ["골프"],
        "낚시": ["낚시", "바다낚시"]
    }
    
    print(f"\n🏃 활동 그룹:")
    for name, keywords in activity_groups.items():
        print(f"   {name}: {', '.join(keywords)}")
    
    # 각 그룹별로 개별 수집 (API는 한 번에 최대 5개까지만 비교 가능)
    all_data = {}
    
    for group_name, keywords in activity_groups.items():
        print(f"\n🔍 [{group_name}] 수집 중...", end=" ")
        
        try:
            result = datalab.get_search_trend(
                keywords=keywords,
                start_date=start_date,
                end_date=end_date,
                time_unit="month"
            )
            
            df_temp = datalab.to_dataframe(result)
            
            # 그룹 평균 계산
            group_avg = df_temp[keywords].mean(axis=1)
            all_data[group_name] = group_avg
            
            print(f"✅ 완료 ({len(df_temp)}개월)")
            
            time.sleep(0.3)  # API 제한 회피
            
        except Exception as e:
            print(f"❌ 오류: {e}")
            all_data[group_name] = None
    
    # 모든 데이터를 하나의 DataFrame으로 합치기
    print(f"\n📊 데이터 병합 중...", end=" ")
    
    # 날짜 기준 DataFrame 생성 (첫 번째 성공한 데이터에서 날짜 추출)
    base_df = None
    for group_name, data in all_data.items():
        if data is not None:
            base_df = pd.DataFrame({'date': df_temp['date']})
            break
    
    if base_df is None:
        raise Exception("모든 그룹 수집 실패")
    
    # 각 그룹 데이터 추가
    for group_name, data in all_data.items():
        if data is not None:
            base_df[f'{group_name}_그룹'] = data.values
        else:
            base_df[f'{group_name}_그룹'] = 0
    
    # 추가 컬럼
    base_df['year'] = base_df['date'].dt.year
    base_df['month'] = base_df['date'].dt.month
    base_df['season'] = base_df['month'].apply(
        lambda x: '겨울' if x in [12,1,2] else ('여름' if x in [6,7,8] else '기타')
    )
    
    print(f"✅ 완료!")
    
    # 데이터 요약
    print(f"\n📊 수집 결과:")
    print(f"   총 개월 수: {len(base_df)}개월")
    print(f"   기간: {base_df['date'].min().strftime('%Y-%m')} ~ {base_df['date'].max().strftime('%Y-%m')}")
    print(f"   컬럼: {', '.join(base_df.columns.tolist())}")
    
    # 겨울 평균 계산 및 순위
    print(f"\n📈 겨울(12,1,2월) 평균 순위:")
    winter_df = base_df[base_df['season'] == '겨울']
    
    winter_avg = {}
    for col in base_df.columns:
        if col.endswith('_그룹'):
            activity_name = col.replace('_그룹', '')
            avg = winter_df[col].mean()
            winter_avg[activity_name] = avg
    
    # 정렬
    sorted_activities = sorted(winter_avg.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (activity, value) in enumerate(sorted_activities, 1):
        bar = "█" * int(value / 5)
        print(f"   {rank}위. {activity:8s}: {value:6.1f} {bar}")
    
    # 저장
    filepath = data_dir / "02_겨울활동_월별_트렌드.csv"
    base_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 저장 완료: {filepath}")
    print(f"\n✅ Dataset 2 수집 완료!")
    
    return base_df


if __name__ == "__main__":
    try:
        df = collect_dataset_2()
        
        print("\n" + "="*60)
        print("📋 데이터 미리보기 (처음 5행)")
        print("="*60)
        print(df.head().to_string())
        
        print("\n" + "="*60)
        print("📋 겨울 데이터만 (처음 5행)")
        print("="*60)
        winter_df = df[df['season'] == '겨울']
        print(winter_df.head().to_string())
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
