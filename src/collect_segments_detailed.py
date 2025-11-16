"""
SODA 프로젝트 - 전체 세그먼트 데이터 수집 (상세 버전)
================================================

수집 대상:
- 선크림 × 6개 세그먼트
- 스키장 × 6개 세그먼트  
- 스키 × 6개 세그먼트
- 스노우보드 × 6개 세그먼트

총 24개 CSV 파일 생성 + 4×6 교차 분석 매트릭스
"""
    
import sys
from pathlib import Path
import time
from datetime import datetime

# ============================================
# 임포트 처리 (직접 실행 vs 패키지 임포트)
# ============================================
try:
    # 패키지로 임포트될 때
    from . import PROJECT_ROOT, get_data_dir
    from .naver_api import NaverDataLab
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
    from naver_api import NaverDataLab

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def collect_all_segments():
    """전체 세그먼트 데이터 수집"""
    
    # 1. 초기화
    print_section("🚀 SODA 프로젝트 - 전체 세그먼트 데이터 수집 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    datalab = NaverDataLab()
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    # 2. 세그먼트 정의
    segments = [
        ("20대 여성", "f", ["3", "4"]),
        ("30대 여성", "f", ["5", "6"]),
        ("40대 여성", "f", ["7", "8"]),
        ("20대 남성", "m", ["3", "4"]),
        ("30대 남성", "m", ["5", "6"]),
        ("40대 남성", "m", ["7", "8"]),
    ]
    
    # 3. 키워드 그룹 정의
    keyword_groups = [
        ("선크림", ["선크림"]),
        ("스키장", ["스키장"]),
        ("스키", ["스키"]),
        ("스노우보드", ["스노우보드"])
    ]
    
    # 4. 수집 기간 설정
    start_date = "2023-01-01"
    end_date = "2025-11-15"
    
    print(f"\n📅 수집 기간: {start_date} ~ {end_date}")
    print(f"📊 키워드 그룹: {len(keyword_groups)}개")
    print(f"👥 세그먼트: {len(segments)}개")
    print(f"📁 생성될 파일: {len(keyword_groups) * len(segments)}개")
    
    # 5. 데이터 수집 및 통계 저장
    print_section("📥 데이터 수집 중...")
    
    all_stats = {}  # {keyword_name: {segment_name: avg_value}}
    total_files = len(keyword_groups) * len(segments)
    current_file = 0
    
    for keyword_name, keywords in keyword_groups:
        print(f"\n🔍 [{keyword_name}] 키워드 수집 시작...")
        all_stats[keyword_name] = {}
        
        for name, gender, ages in segments:
            current_file += 1
            progress = (current_file / total_files) * 100
            
            print(f"  [{current_file}/{total_files}] ({progress:.1f}%) {name} 수집 중...", end=" ")
            
            try:
                # API 호출
                result_seg = datalab.get_search_trend(
                    keywords=keywords,
                    start_date=start_date,
                    end_date=end_date,
                    time_unit="month",
                    gender=gender,
                    ages=ages
                )
                
                # DataFrame 변환
                df_seg = datalab.to_dataframe(result_seg)
                
                # 평균 검색량 계산 (통계용)
                first_keyword = keywords[0]
                avg_value = df_seg[first_keyword].mean()
                all_stats[keyword_name][name] = avg_value
                
                # 파일 저장
                filename = f"03_segment_{keyword_name}_{name.replace(' ', '_')}.csv"
                filepath = data_dir / filename
                df_seg.to_csv(filepath, index=False, encoding='utf-8-sig')
                
                print(f"✅ (평균: {avg_value:.2f})")
                
                # API 제한 고려 (초당 1회 제한 회피)
                time.sleep(0.3)
                
            except Exception as e:
                print(f"❌ 오류: {str(e)}")
                all_stats[keyword_name][name] = 0
    
    print(f"\n✅ 총 {current_file}개 파일 수집 완료!")
    
    # 6. 통계 요약
    print_section("📊 키워드별 평균 검색량 요약")
    
    for keyword_name in keyword_groups:
        kw_name = keyword_name[0]
        print(f"\n[{kw_name}]")
        
        # 세그먼트별 평균을 리스트로 정렬
        stats = all_stats[kw_name]
        sorted_segments = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (seg_name, avg_val) in enumerate(sorted_segments, 1):
            bar_length = int(avg_val / 2)  # 시각화용 막대
            bar = "█" * bar_length
            print(f"  {rank}위. {seg_name:12s}: {avg_val:6.2f} {bar}")
    
    # 7. 4×6 교차 분석 매트릭스
    print_section("🎯 4×6 교차 분석 매트릭스")
    
    # 헤더 출력
    segment_names = [seg[0] for seg in segments]
    header = "키워드      │ " + " │ ".join([f"{name:6s}" for name in segment_names])
    print("\n" + header)
    print("─" * len(header))
    
    # 각 키워드별 데이터 출력
    for keyword_name, _ in keyword_groups:
        stats = all_stats[keyword_name]
        row_data = [stats.get(name, 0) for name in segment_names]
        row = f"{keyword_name:12s}│ " + " │ ".join([f"{val:6.2f}" for val in row_data])
        print(row)
    
    # 8. 키워드별 1위 세그먼트 비교
    print_section("🏆 키워드별 1위 세그먼트")
    
    top_segments = {}
    for keyword_name, _ in keyword_groups:
        stats = all_stats[keyword_name]
        top_segment = max(stats.items(), key=lambda x: x[1])
        top_segments[keyword_name] = top_segment
        print(f"  {keyword_name:12s}: {top_segment[0]} ({top_segment[1]:.2f})")
    
    # 9. 선크림 vs 스포츠 교차 분석 프리뷰
    print_section("🔍 선크림 vs 스포츠 교차 분석 프리뷰")
    
    suncream_stats = all_stats["선크림"]
    suncream_avg = sum(suncream_stats.values()) / len(suncream_stats)
    
    print(f"\n선크림 전체 평균: {suncream_avg:.2f}")
    
    for sport_name in ["스키장", "스키", "스노우보드"]:
        sport_stats = all_stats[sport_name]
        sport_avg = sum(sport_stats.values()) / len(sport_stats)
        print(f"{sport_name} 전체 평균: {sport_avg:.2f}")
    
    print("\n💡 세그먼트별 4사분면 분석:")
    print("─" * 80)
    print(f"{'세그먼트':12s} │ {'선크림':8s} │ {'스키장':8s} │ {'스키':8s} │ {'보드':8s} │ 블루오션 후보")
    print("─" * 80)
    
    for seg_name in segment_names:
        sc_val = suncream_stats[seg_name]
        resort_val = all_stats["스키장"][seg_name]
        ski_val = all_stats["스키"][seg_name]
        board_val = all_stats["스노우보드"][seg_name]
        
        # 블루오션 판단: 선크림 낮음 + 스포츠 높음
        sc_status = "↑" if sc_val > suncream_avg else "↓"
        
        # 각 스포츠별 블루오션 여부
        blueocean_flags = []
        
        if resort_val > all_stats["스키장"][max(all_stats["스키장"], key=all_stats["스키장"].get)] * 0.8:
            if sc_val < suncream_avg:
                blueocean_flags.append("스키장")
        
        if ski_val > all_stats["스키"][max(all_stats["스키"], key=all_stats["스키"].get)] * 0.8:
            if sc_val < suncream_avg:
                blueocean_flags.append("스키")
        
        if board_val > all_stats["스노우보드"][max(all_stats["스노우보드"], key=all_stats["스노우보드"].get)] * 0.8:
            if sc_val < suncream_avg:
                blueocean_flags.append("보드")
        
        blueocean_str = ", ".join(blueocean_flags) if blueocean_flags else "-"
        
        print(f"{seg_name:12s} │ {sc_val:6.2f}{sc_status} │ {resort_val:6.2f} │ {ski_val:6.2f} │ {board_val:6.2f} │ {blueocean_str}")
    
    print("─" * 80)
    
    # 10. 블루오션 세그먼트 요약
    print_section("💎 블루오션 세그먼트 발견")
    
    print("\n각 스포츠별 블루오션 후보:")
    
    for sport_name in ["스키장", "스키", "스노우보드"]:
        sport_stats = all_stats[sport_name]
        sport_max = max(sport_stats.values())
        
        print(f"\n[{sport_name}] 블루오션:")
        
        blueocesan_found = False
        for seg_name in segment_names:
            sc_val = suncream_stats[seg_name]
            sport_val = sport_stats[seg_name]
            
            # 조건: 스포츠 관심 높음(상위 50%) + 선크림 인식 낮음(평균 이하)
            if sport_val > sport_max * 0.5 and sc_val < suncream_avg:
                blueocesan_found = True
                print(f"  ✨ {seg_name}: {sport_name} 관심 {sport_val:.2f} / 선크림 인식 {sc_val:.2f}")
                print(f"     → 전략: '{sport_name} UV 차단 교육' 캠페인 타겟!")
        
        if not blueocesan_found:
            print(f"  ℹ️  명확한 블루오션 없음 (대부분 선크림 인식 높음)")
    
    # 11. 선크림 vs 각 스포츠 블루오션 매트릭스
    print_section("📍 선크림 vs 각 스포츠 블루오션 매트릭스")
    
    print("\n4사분면 분석 (각 스포츠별로 선크림과 비교):")
    print("─" * 70)
    
    for sport_name in ["스키장", "스키", "스노우보드"]:
        sport_stats = all_stats[sport_name]
        sport_avg = sum(sport_stats.values()) / len(sport_stats)
        
        print(f"\n[선크림 vs {sport_name}]")
        print(f"  선크림 평균: {suncream_avg:.2f} / {sport_name} 평균: {sport_avg:.2f}\n")
        
        # 4사분면 분류
        quadrants = {
            "A (둘 다 높음)": [],
            "B (블루오션!)": [],
            "C (선크림만 높음)": [],
            "D (둘 다 낮음)": []
        }
        
        for seg_name in segment_names:
            sc_val = suncream_stats[seg_name]
            sport_val = sport_stats[seg_name]
            
            if sc_val >= suncream_avg and sport_val >= sport_avg:
                quadrants["A (둘 다 높음)"].append(f"{seg_name} (선크림:{sc_val:.1f}, {sport_name}:{sport_val:.1f})")
            elif sc_val < suncream_avg and sport_val >= sport_avg:
                quadrants["B (블루오션!)"].append(f"{seg_name} (선크림:{sc_val:.1f}↓, {sport_name}:{sport_val:.1f}↑)")
            elif sc_val >= suncream_avg and sport_val < sport_avg:
                quadrants["C (선크림만 높음)"].append(f"{seg_name} (선크림:{sc_val:.1f}, {sport_name}:{sport_val:.1f})")
            else:
                quadrants["D (둘 다 낮음)"].append(f"{seg_name} (선크림:{sc_val:.1f}, {sport_name}:{sport_val:.1f})")
        
        # 결과 출력
        for quad_name, segs in quadrants.items():
            if segs:
                symbol = "🎯" if "블루오션" in quad_name else "  "
                print(f"  {symbol} {quad_name}:")
                for seg in segs:
                    print(f"     - {seg}")
            else:
                print(f"     {quad_name}: 없음")
    
    print("\n" + "─" * 70)
    
    # 12. 다음 단계 안내
    print_section("📌 다음 단계")
    
    print("""
    ✅ 수집 완료된 데이터:
    - data/ 폴더에 24개 CSV 파일 생성
    - 선크림, 스키장, 스키, 스노우보드 각 6개 세그먼트
    """)
    
    print_section("✅ 전체 수집 완료!")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        collect_all_segments()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()