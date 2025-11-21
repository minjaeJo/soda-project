"""
SODA 프로젝트 - 발표 자료 데이터 수집
Dataset 3 (최종 v2): 기상청 UV-B 지수 + 네이버 자외선 검색량
- 개선: 매월 전체 일자 정오(12:00) 데이터 평균
"""

import sys
from pathlib import Path
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import calendar

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


def parse_kma_uv_response(text):
    """
    기상청 UV API 텍스트 응답 파싱
    
    Returns:
        dict: {'uvb_avg': 평균, 'uvb_max': 최대, 'uvb_min': 최소, 'count': 지점수}
    """
    lines = text.strip().split('\n')
    uvb_values = []
    
    for line in lines:
        line = line.strip()
        # 주석이나 구분선 건너뛰기
        if not line or line.startswith('#') or line.startswith('|') or line.startswith('-'):
            continue
        
        # 데이터 라인 파싱
        parts = line.split()
        if len(parts) >= 7:
            try:
                # 포맷: YYMMDDHHMI STN UVB UVA EUV UV-B UV-A TEMP1 TEMP2
                uvb_index = float(parts[5])  # UV-B 지수 ⭐
                
                # 유효한 값만 수집 (-999는 제외)
                if uvb_index >= 0:
                    uvb_values.append(uvb_index)
            except (ValueError, IndexError):
                continue
    
    if len(uvb_values) > 0:
        return {
            'uvb_avg': sum(uvb_values) / len(uvb_values),
            'uvb_max': max(uvb_values),
            'uvb_min': min(uvb_values),
            'count': len(uvb_values)
        }
    else:
        return None


def get_kma_uv_daily(date, auth_key, hour=12, minute=0):
    """
    특정 일자의 UV 데이터 조회
    
    Args:
        date: datetime 객체
        auth_key: API 인증키
        hour: 시 (기본 12시 = 정오)
        minute: 분 (기본 0분)
    
    Returns:
        dict or None
    """
    date_str = date.strftime(f'%Y%m%d{hour:02d}{minute:02d}')
    
    url = 'https://apihub.kma.go.kr/api/typ01/url/kma_sfctm_uv.php'
    params = {
        'tm': date_str,
        'stn': 0,  # 전체 지점
        'help': 1,
        'authKey': auth_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        result = parse_kma_uv_response(response.text)
        return result
        
    except requests.exceptions.RequestException as e:
        # API 오류는 조용히 처리 (일부 날짜 실패 허용)
        return None
    except Exception as e:
        return None


def get_kma_uv_monthly(year, month, auth_key):
    """
    특정 월의 UV 데이터 수집 (매일 정오 기준)
    
    Args:
        year: 연도
        month: 월
        auth_key: API 인증키
    
    Returns:
        dict: {'avg': 월평균, 'max': 월최대, 'min': 월최소, 'days': 수집일수}
    """
    # 해당 월의 일수
    _, last_day = calendar.monthrange(year, month)
    
    daily_values = []
    
    for day in range(1, last_day + 1):
        date = datetime(year, month, day)
        
        # 매일 정오(12:00) 데이터 수집
        data = get_kma_uv_daily(date, auth_key, hour=12, minute=0)
        
        if data:
            daily_values.append(data['uvb_avg'])
        
        # API 제한 고려 (0.3초 대기)
        time.sleep(0.3)
    
    if len(daily_values) > 0:
        return {
            'avg': sum(daily_values) / len(daily_values),
            'max': max(daily_values),
            'min': min(daily_values),
            'days': len(daily_values),
            'total_days': last_day
        }
    else:
        return None


def collect_kma_uv_monthly_avg(start_year=2020, start_month=2, end_year=2025, end_month=2):
    """
    월별 UV-B 지수 평균 수집
    """
    
    print("="*60)
    print("🌞 [Phase 1] 기상청 UV-B 지수 월별 평균 수집")
    print("="*60)
    
    AUTH_KEY = "sZWy8JkwTmGVsvCZMP5hRw"
    
    print(f"\n📅 수집 기간: {start_year}-{start_month:02d} ~ {end_year}-{end_month:02d}")
    print(f"📍 측정 지점: 전국 평균")
    print(f"🕐 측정 시각: 매일 정오(12:00)")
    print(f"📊 방법: 각 월의 전체 일자 평균")
    
    # 월 범위 생성
    months = []
    current_year = start_year
    current_month = start_month
    
    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        months.append((current_year, current_month))
        
        # 다음 달로
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1
    
    print(f"\n📊 총 {len(months)}개월 데이터 수집 예정")
    print(f"⏱️ 예상 소요 시간: 약 {len(months) * 0.3 * 30 / 60:.0f}분 (각 월 평균 30일)")
    
    # 데이터 수집
    results = []
    success_count = 0
    
    for i, (year, month) in enumerate(months, 1):
        print(f"\n[{i}/{len(months)}] {year}-{month:02d} 수집 중... ", end="")
        
        data = get_kma_uv_monthly(year, month, AUTH_KEY)
        
        result = {
            'date': f'{year}-{month:02d}-01',
            'year': year,
            'month': month
        }
        
        if data:
            coverage = (data['days'] / data['total_days']) * 100
            print(f"✅ 완료 (평균 UV-B: {data['avg']:.2f}, {data['days']}/{data['total_days']}일, {coverage:.0f}%)")
            
            result['UVB평균'] = round(data['avg'], 2)
            result['UVB최대'] = round(data['max'], 2)
            result['UVB최소'] = round(data['min'], 2)
            result['수집일수'] = data['days']
            result['전체일수'] = data['total_days']
            result['커버리지'] = round(coverage, 1)
            result['api_success'] = True
            
            success_count += 1
            
            # 첫 번째 결과 상세 출력
            if i == 1:
                print(f"\n   💡 UV-B 지수 설명:")
                print(f"      0-2:  낮음")
                print(f"      3-5:  보통")
                print(f"      6-7:  높음")
                print(f"      8-10: 매우 높음")
                print(f"      11+:  위험")
        else:
            print(f"⚠️ 데이터 수집 실패")
            result['UVB평균'] = None
            result['UVB최대'] = None
            result['UVB최소'] = None
            result['수집일수'] = 0
            result['전체일수'] = calendar.monthrange(year, month)[1]
            result['커버리지'] = 0
            result['api_success'] = False
    
        results.append(result)
    
    df = pd.DataFrame(results)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"\n✅ 기상청 데이터 수집 완료: {success_count}/{len(months)}개월")
    
    # 평균 커버리지 계산
    if success_count > 0:
        avg_coverage = df[df['api_success'] == True]['커버리지'].mean()
        print(f"   평균 데이터 커버리지: {avg_coverage:.1f}%")
    
    return df


def collect_naver_uv_search():
    """
    네이버 DataLab 자외선 검색량 수집
    """
    
    print("\n" + "="*60)
    print("🔍 [Phase 2] 네이버 자외선 검색량 수집")
    print("="*60)
    
    datalab = NaverDataLab()
    
    start_date = "2020-02-01"
    end_date = "2025-02-28"
    
    print(f"\n📅 기간: {start_date} ~ {end_date}")
    
    # 자외선 관련 키워드
    keywords = [
        "자외선",
        "자외선 차단",
        "UV 차단"
    ]
    
    print(f"\n🔍 검색 키워드:")
    for i, kw in enumerate(keywords, 1):
        print(f"   {i}. {kw}")
    
    # 데이터 수집
    all_data = {}
    
    for keyword in keywords:
        print(f"\n🔍 [{keyword}] 수집 중...", end=" ")
        
        try:
            result = datalab.get_search_trend(
                keywords=[keyword],
                start_date=start_date,
                end_date=end_date,
                time_unit="month"
            )
            
            df_temp = datalab.to_dataframe(result)
            
            if keyword in df_temp.columns and len(df_temp) > 0:
                all_data[keyword] = df_temp[[keyword, 'date']].copy()
                print(f"✅ 완료 ({len(df_temp)}개월)")
            else:
                print(f"⚠️ 데이터 없음")
                all_data[keyword] = None
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"❌ 오류: {e}")
            all_data[keyword] = None
    
    # 데이터 병합
    print(f"\n📊 데이터 병합 중...", end=" ")
    
    base_df = None
    max_length = 0
    
    for keyword, data in all_data.items():
        if data is not None and len(data) > max_length:
            base_df = pd.DataFrame({'date': data['date'].values})
            max_length = len(data)
    
    if base_df is None:
        raise Exception("네이버 데이터 수집 실패")
    
    # 각 키워드 데이터 추가
    for keyword, data in all_data.items():
        clean_name = keyword.replace(' ', '')
        
        if data is not None and len(data) > 0:
            temp_df = pd.DataFrame({
                'date': data['date'].values,
                clean_name: data[keyword].values
            })
            base_df = base_df.merge(temp_df, on='date', how='left')
            base_df[clean_name] = base_df[clean_name].fillna(0)
        else:
            base_df[clean_name] = 0
    
    # 통합 검색 지수 (평균)
    search_columns = [kw.replace(' ', '') for kw in keywords 
                      if kw.replace(' ', '') in base_df.columns]
    
    if len(search_columns) > 0:
        base_df['자외선검색지수'] = base_df[search_columns].mean(axis=1)
    
    print(f"✅ 완료!")
    
    print(f"\n✅ 네이버 데이터 수집 완료: {len(base_df)}개월")
    
    return base_df


def merge_and_analyze(kma_df, naver_df):
    """
    기상청 UV-B + 네이버 검색량 병합 및 분석
    """
    
    print("\n" + "="*60)
    print("🔗 [Phase 3] 데이터 병합 및 분석")
    print("="*60)
    
    # 날짜 기준으로 병합
    kma_cols = ['date', 'UVB평균', 'UVB최대', 'UVB최소', '수집일수', '커버리지', 'api_success']
    kma_merge = kma_df[[col for col in kma_cols if col in kma_df.columns]]
    
    merged_df = pd.merge(
        naver_df,
        kma_merge,
        on='date',
        how='left'
    )
    
    # 추가 컬럼
    merged_df['year'] = merged_df['date'].dt.year
    merged_df['month'] = merged_df['date'].dt.month
    merged_df['season'] = merged_df['month'].apply(
        lambda x: '겨울' if x in [12,1,2] else ('여름' if x in [6,7,8] else '기타')
    )
    
    print(f"\n📊 병합 결과:")
    print(f"   총 개월 수: {len(merged_df)}개월")
    print(f"   기간: {merged_df['date'].min().strftime('%Y-%m')} ~ {merged_df['date'].max().strftime('%Y-%m')}")
    
    # 계절별 통계
    print(f"\n📈 계절별 통계:")
    print(f"\n{'구분':<10} | {'자외선검색지수':>12} | {'UVB평균':>8}")
    print(f"{'-'*10}-+-{'-'*12}-+-{'-'*8}")
    
    for season in ['겨울', '여름', '기타']:
        season_df = merged_df[merged_df['season'] == season]
        if len(season_df) > 0:
            search_avg = season_df['자외선검색지수'].mean() if '자외선검색지수' in season_df.columns else 0
            uv_avg = season_df['UVB평균'].mean() if 'UVB평균' in season_df.columns else 0
            print(f"{season:<10} | {search_avg:12.2f} | {uv_avg:8.2f}")
    
    # Gap 분석
    print(f"\n💡 인식 공백(Perception Gap) 분석:")
    
    winter_df = merged_df[merged_df['season'] == '겨울']
    summer_df = merged_df[merged_df['season'] == '여름']
    
    if len(winter_df) > 0 and len(summer_df) > 0:
        winter_search = winter_df['자외선검색지수'].mean()
        summer_search = summer_df['자외선검색지수'].mean()
        
        winter_uv = winter_df['UVB평균'].mean() if 'UVB평균' in winter_df.columns else 0
        summer_uv = summer_df['UVB평균'].mean() if 'UVB평균' in summer_df.columns else 0
        
        print(f"\n   [검색량 비교]")
        print(f"   - 겨울 검색:     {winter_search:6.2f}")
        print(f"   - 여름 검색:     {summer_search:6.2f}")
        search_ratio = (winter_search / summer_search * 100) if summer_search > 0 else 0
        print(f"   - 겨울/여름:     {search_ratio:6.1f}%")
        
        if winter_uv > 0 and summer_uv > 0:
            print(f"\n   [UV-B 지수 비교]")
            print(f"   - 겨울 UV-B:     {winter_uv:6.2f}")
            print(f"   - 여름 UV-B:     {summer_uv:6.2f}")
            uv_ratio = (winter_uv / summer_uv * 100)
            print(f"   - 겨울/여름:     {uv_ratio:6.1f}%")
            
            gap = uv_ratio - search_ratio
            print(f"\n   [Gap 분석]")
            print(f"   - UV 비율:       {uv_ratio:6.1f}% (겨울/여름)")
            print(f"   - 검색 비율:     {search_ratio:6.1f}% (겨울/여름)")
            print(f"   - Gap:           {gap:+6.1f}%p")
            
            if gap > 10:
                print(f"\n   ✅ 명확한 인식 공백 존재!")
                print(f"      겨울 UV 위험도는 상대적으로 높지만")
                print(f"      사람들의 인식(검색)은 훨씬 낮음")
            elif gap < -10:
                print(f"\n   ℹ️ 검색량이 UV 대비 높음")
                print(f"      겨울 자외선 인식이 실제보다 과도")
            else:
                print(f"\n   ℹ️ UV와 검색량이 적절히 비례")
                
            # 스키장 고도+반사 보정 시나리오
            print(f"\n🎿 스키장 시나리오 (고도 + 반사 보정):")
            print(f"   - 스키장 평균 고도: 1000m+")
            print(f"   - UV-B 고도 보정: +35% (고도 1000m당 10-15% 증가)")
            print(f"   - 눈 반사율: +80% (UV-B의 80%가 반사)")
            print(f"   - 총 보정 계수: 1.35 × 1.8 = 2.43배")
            
            winter_uv_ski = winter_uv * 2.43
            ski_uv_ratio = (winter_uv_ski / summer_uv * 100)
            ski_gap = ski_uv_ratio - search_ratio
            
            print(f"\n   - 평지 겨울 UV-B:     {winter_uv:6.2f}")
            print(f"   - 스키장 실제 UV-B:   {winter_uv_ski:6.2f} (보정 후)")
            print(f"   - 여름 평지 대비:     {ski_uv_ratio:6.1f}%")
            print(f"   - 검색 비율:          {search_ratio:6.1f}%")
            print(f"   - 스키장 Gap:         {ski_gap:+6.1f}%p")
            
            if ski_gap > 30:
                print(f"\n   ✅✅ 스키장은 극심한 인식 공백!")
                print(f"      스키장 실제 위험도는 여름과 비슷하거나 더 높지만")
                print(f"      사람들은 겨울이라 방심")
                print(f"      → 교육형 캠페인의 완벽한 근거!")
        else:
            print(f"\n   ⚠️ UV 데이터 부족으로 Gap 분석 불가")
    
    # 저장
    data_dir = PROJECT_ROOT / 'data' / 'presentation'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = data_dir / "03_UV지수_검색량_비교.csv"
    merged_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 저장 완료: {filepath}")
    
    return merged_df


def main():
    """
    Dataset 3 최종 수집 메인 함수
    """
    
    print("="*60)
    print("📊 Dataset 3: UV-B 지수 vs 자외선 검색량 비교")
    print("="*60)
    
    print(f"\n🎯 목적:")
    print(f"   과학적 위험(UV-B 지수) vs 주관적 인식(검색량) Gap 증명")
    print(f"   → 겨울/스키장의 인식 공백을 객관적 데이터로 증명")
    
    print(f"\n📊 개선 사항:")
    print(f"   ✅ 매월 전체 일자의 정오(12:00) 데이터 평균")
    print(f"   ✅ UV-B 지수 사용 (피부 화상 원인)")
    print(f"   ✅ 스키장 고도+반사 보정 포함")
    
    try:
        # Phase 1: 기상청 UV 데이터
        print(f"\n⏳ Phase 1 시작...")
        kma_df = collect_kma_uv_monthly_avg(
            start_year=2020,
            start_month=2,
            end_year=2025,
            end_month=2
        )
        
        # Phase 2: 네이버 검색량
        print(f"\n⏳ Phase 2 시작...")
        naver_df = collect_naver_uv_search()
        
        # Phase 3: 병합 및 분석
        print(f"\n⏳ Phase 3 시작...")
        final_df = merge_and_analyze(kma_df, naver_df)
        
        # 결과 출력
        print("\n" + "="*60)
        print("📋 최종 데이터 미리보기 (처음 10행)")
        print("="*60)
        
        display_cols = ['date', 'year', 'month', 'season', 
                       '자외선검색지수', 'UVB평균', '커버리지']
        available_cols = [col for col in display_cols if col in final_df.columns]
        print(final_df[available_cols].head(10).to_string())
        
        print("\n" + "="*60)
        print("📋 겨울 데이터 샘플")
        print("="*60)
        winter_sample = final_df[final_df['season'] == '겨울'][available_cols].head(5)
        print(winter_sample.to_string())
        
        print("\n" + "="*60)
        print("✅ Dataset 3 수집 완료!")
        print("="*60)
        
        print(f"\n📊 발표 자료 활용:")
        print(f"   1. UV-B 지수 vs 검색량 시계열 그래프")
        print(f"   2. 겨울/여름 비교 막대 차트")
        print(f"   3. Gap 분석 → 인식 공백 증명")
        print(f"   4. 스키장 시나리오 → 교육 캠페인 근거")
        
        return final_df
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    df = main()