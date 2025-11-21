"""
SODA 프로젝트 - Dataset 4: 세그먼트별 통합 데이터 수집
====================================================

목표: 선크림 × 스포츠 관심도를 세그먼트별로 분석
출력: 하나의 통합 DataFrame (long format)

수집 대상:
- 선크림 × 6개 세그먼트
- 스키장 × 6개 세그먼트  
- 스키 × 6개 세그먼트
- 스노우보드 × 6개 세그먼트

총 24개 조합 → 1개 통합 CSV 파일
"""

import sys
from pathlib import Path
import time
from datetime import datetime
import pandas as pd

# ============================================
# 경로 및 임포트 설정
# ============================================
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
src_dir = current_file.parent

# sys.path 설정
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# naver_api 임포트
from naver_api import NaverDataLab

# 전역 변수
PROJECT_ROOT = project_root


def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def main():
    """메인 실행 함수"""
    
    # 1. 초기화
    print_section("🚀 Dataset 4: 세그먼트별 통합 데이터 수집 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    datalab = NaverDataLab()
    data_dir = PROJECT_ROOT / 'data' / 'presentation'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. 세그먼트 정의
    segments = [
        ("20대 여성", "f", ["3", "4"], "20대", "여성"),
        ("30대 여성", "f", ["5", "6"], "30대", "여성"),
        ("40대 여성", "f", ["7", "8"], "40대", "여성"),
        ("20대 남성", "m", ["3", "4"], "20대", "남성"),
        ("30대 남성", "m", ["5", "6"], "30대", "남성"),
        ("40대 남성", "m", ["7", "8"], "40대", "남성"),
    ]
    
    # 3. 키워드 그룹 정의
    keywords = ["선크림", "스키장", "스키", "스노우보드"]
    
    # 4. 수집 기간 설정
    start_date = "2023-01-01"
    end_date = "2025-11-15"
    
    print(f"\n📅 수집 기간: {start_date} ~ {end_date}")
    print(f"📊 키워드: {len(keywords)}개")
    print(f"👥 세그먼트: {len(segments)}개")
    print(f"📁 총 조합: {len(keywords) * len(segments)}개")
    print(f"📦 출력: 1개 통합 CSV 파일 (long format)")
    
    # 5. 데이터 수집
    print_section("📥 데이터 수집 중...")
    
    all_data_list = []
    stats_summary = {}  # {keyword: {segment: avg_value}}
    
    total = len(keywords) * len(segments)
    current = 0
    
    for keyword in keywords:
        print(f"\n🔍 [{keyword}] 키워드 수집 시작...")
        stats_summary[keyword] = {}
        
        for seg_name, gender, ages, age_group, gender_kr in segments:
            current += 1
            progress = (current / total) * 100
            
            print(f"  [{current}/{total}] ({progress:.1f}%) {seg_name} 수집 중...", end=" ")
            
            try:
                # API 호출
                result = datalab.get_search_trend(
                    keywords=[keyword],
                    start_date=start_date,
                    end_date=end_date,
                    time_unit="month",
                    gender=gender,
                    ages=ages
                )
                
                # DataFrame 변환
                df = datalab.to_dataframe(result)
                
                # year, month 컬럼 추가
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                
                # 평균 계산
                avg_value = df[keyword].mean()
                stats_summary[keyword][seg_name] = avg_value
                
                # Long format으로 변환
                for _, row in df.iterrows():
                    all_data_list.append({
                        'date': row['date'],
                        'keyword': keyword,
                        'segment': seg_name,
                        'gender': gender_kr,
                        'age_group': age_group,
                        'search_volume': row[keyword],
                        'year': row['year'],
                        'month': row['month']
                    })
                
                print(f"✅ (평균: {avg_value:.2f})")
                
                # API 제한 대기
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ 오류: {str(e)}")
                stats_summary[keyword][seg_name] = 0
    
    print(f"\n✅ 총 {current}개 조합 수집 완료!")
    
    # 6. 통합 DataFrame 생성
    print_section("📦 통합 DataFrame 생성 중...")
    
    df_unified = pd.DataFrame(all_data_list)
    
    print(f"✅ 통합 DataFrame 생성 완료!")
    print(f"   - 총 행 수: {len(df_unified):,}개")
    print(f"   - 기간: {df_unified['date'].min()} ~ {df_unified['date'].max()}")
    print(f"   - 키워드: {df_unified['keyword'].nunique()}개")
    print(f"   - 세그먼트: {df_unified['segment'].nunique()}개")
    
    # 7. 통합 파일 저장
    output_file = data_dir / "04_세그먼트별_통합_데이터.csv"
    df_unified.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n💾 통합 데이터 저장: {output_file}")
    
    # 8. 피벗 테이블 생성
    print_section("📊 피벗 테이블 생성 (세그먼트 × 키워드 평균)")
    
    pivot_avg = df_unified.groupby(['segment', 'keyword'])['search_volume'].mean().unstack(fill_value=0)
    
    # 세그먼트 순서 정렬
    segment_order = [seg[0] for seg in segments]
    pivot_avg = pivot_avg.reindex(segment_order)
    
    print("\n평균 검색량 매트릭스:")
    print(pivot_avg.round(2))
    
    # 피벗 테이블 저장
    pivot_file = data_dir / "04_세그먼트_키워드_평균_매트릭스.csv"
    pivot_avg.to_csv(pivot_file, encoding='utf-8-sig')
    print(f"\n💾 피벗 테이블 저장: {pivot_file}")
    
    # 9. 통계 요약
    print_section("📊 키워드별 평균 검색량 요약")
    
    for keyword in keywords:
        print(f"\n[{keyword}]")
        stats = stats_summary[keyword]
        sorted_segments = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (seg_name, avg_val) in enumerate(sorted_segments, 1):
            bar_length = int(avg_val / 2) if avg_val > 0 else 0
            bar = "█" * bar_length
            print(f"  {rank}위. {seg_name:12s}: {avg_val:6.2f} {bar}")
    
    # 10. 블루오션 분석
    print_section("💎 블루오션 세그먼트 분석")
    
    # 선크림 평균 기준선
    suncream_stats = stats_summary["선크림"]
    suncream_avg = sum(suncream_stats.values()) / len(suncream_stats)
    
    print(f"\n📌 선크림 전체 평균: {suncream_avg:.2f}")
    print(f"   블루오션 기준: 선크림 < {suncream_avg:.2f} AND 스포츠 관심 높음\n")
    
    # 각 스포츠별 블루오션 찾기
    for sport_name in ["스키장", "스키", "스노우보드"]:
        sport_stats = stats_summary[sport_name]
        sport_avg = sum(sport_stats.values()) / len(sport_stats)
        sport_max = max(sport_stats.values())
        
        print(f"[{sport_name}] (평균: {sport_avg:.2f})")
        
        blueocean_found = False
        for seg_name in segment_order:
            sc_val = suncream_stats[seg_name]
            sport_val = sport_stats[seg_name]
            
            # 블루오션 조건: 스포츠 관심 높음(상위 50%) + 선크림 인식 낮음(평균 이하)
            if sport_val > sport_max * 0.5 and sc_val < suncream_avg:
                blueocean_found = True
                print(f"  💎 {seg_name}: {sport_name} {sport_val:.2f} / 선크림 {sc_val:.2f}")
                print(f"     → 전략: '{sport_name} UV 차단 교육' 캠페인 타겟!")
        
        if not blueocean_found:
            print(f"  ℹ️  명확한 블루오션 없음 (대부분 선크림 인식 높음)")
        print()
    
    # 11. 4사분면 분석
    print_section("📍 4사분면 분석 (선크림 vs 각 스포츠)")
    
    for sport_name in ["스키장", "스키", "스노우보드"]:
        sport_stats = stats_summary[sport_name]
        sport_avg = sum(sport_stats.values()) / len(sport_stats)
        
        print(f"\n[선크림 vs {sport_name}]")
        print(f"  선크림 평균: {suncream_avg:.2f} / {sport_name} 평균: {sport_avg:.2f}")
        
        quadrants = {
            "A (둘 다 높음)": [],
            "B (블루오션!)": [],
            "C (선크림만 높음)": [],
            "D (둘 다 낮음)": []
        }
        
        for seg_name in segment_order:
            sc_val = suncream_stats[seg_name]
            sport_val = sport_stats[seg_name]
            
            if sc_val >= suncream_avg and sport_val >= sport_avg:
                quadrants["A (둘 다 높음)"].append(f"{seg_name} (SC:{sc_val:.1f}, SP:{sport_val:.1f})")
            elif sc_val < suncream_avg and sport_val >= sport_avg:
                quadrants["B (블루오션!)"].append(f"{seg_name} (SC:{sc_val:.1f}↓, SP:{sport_val:.1f}↑)")
            elif sc_val >= suncream_avg and sport_val < sport_avg:
                quadrants["C (선크림만 높음)"].append(f"{seg_name} (SC:{sc_val:.1f}, SP:{sport_val:.1f})")
            else:
                quadrants["D (둘 다 낮음)"].append(f"{seg_name} (SC:{sc_val:.1f}, SP:{sport_val:.1f})")
        
        # 출력
        for quad_name, segs in quadrants.items():
            if segs:
                symbol = "🎯" if "블루오션" in quad_name else "  "
                print(f"  {symbol} {quad_name}:")
                for seg in segs:
                    print(f"     - {seg}")
    
    # 12. 블루오션 세그먼트 종합
    print_section("🏆 최종 블루오션 세그먼트 종합")
    
    blueocean_summary = {}
    for seg_name in segment_order:
        sc_val = suncream_stats[seg_name]
        blueocean_sports = []
        
        for sport_name in ["스키장", "스키", "스노우보드"]:
            sport_val = stats_summary[sport_name][seg_name]
            sport_avg = sum(stats_summary[sport_name].values()) / len(stats_summary[sport_name])
            
            if sc_val < suncream_avg and sport_val >= sport_avg:
                blueocean_sports.append(sport_name)
        
        if blueocean_sports:
            blueocean_summary[seg_name] = blueocean_sports
    
    if blueocean_summary:
        print("\n💎 블루오션 세그먼트 발견:")
        for seg_name, sports in blueocean_summary.items():
            print(f"  🎯 {seg_name}: {', '.join(sports)}")
            print(f"     선크림: {suncream_stats[seg_name]:.2f} (낮음)")
            for sport in sports:
                print(f"     {sport}: {stats_summary[sport][seg_name]:.2f} (높음)")
    else:
        print("\n⚠️  명확한 블루오션 세그먼트 없음")
        print("   → 대부분의 세그먼트가 이미 선크림 인식이 높음")
    
    # 13. 완료 메시지
    print_section("✅ Dataset 4 수집 완료!")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n생성된 파일:")
    print(f"  1. {output_file.name}")
    print(f"  2. {pivot_file.name}")
    
    return df_unified, pivot_avg


# ============================================
# 실행
# ============================================
if __name__ == "__main__":
    try:
        df_unified, pivot_avg = main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()