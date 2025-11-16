# naver_api.py
import requests
import json
import pandas as pd
from datetime import datetime
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

class NaverDataLab:
    """네이버 데이터랩 API"""
    
    def __init__(self):
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET
        self.url = "https://openapi.naver.com/v1/datalab/search"
    
    def get_search_trend(self, keywords, start_date, end_date, 
                         time_unit='month', device='', gender='', ages=[]):
        """
        검색 트렌드 조회
        
        Parameters:
        - keywords: list of str (최대 5개)
        - start_date: "YYYY-MM-DD"
        - end_date: "YYYY-MM-DD"
        - time_unit: 'date'(불가!), 'week', 'month'
        - device: '', 'pc', 'mo'
        - gender: '', 'm', 'f'
        - ages: [] or ['1','2'] ~ ['11']
        """
        
        # 키워드 그룹 생성
        keyword_groups = []
        for keyword in keywords:
            keyword_groups.append({
                "groupName": keyword,
                "keywords": [keyword]
            })
        
        # 요청 바디
        body = {
            "startDate": start_date.replace("-", ""),
            "endDate": end_date.replace("-", ""),
            "timeUnit": time_unit,
            "keywordGroups": keyword_groups
        }
        
        # 선택 파라미터
        if device:
            body["device"] = device
        if gender:
            body["gender"] = gender
        if ages:
            body["ages"] = ages
        
        # API 요청
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.url, headers=headers, 
                                data=json.dumps(body))
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 오류 {response.status_code}: {response.text}")
    
    def to_dataframe(self, api_response):
        """API 응답을 DataFrame으로 변환"""
        results = api_response['results']
        
        # 날짜 추출
        dates = [item['period'] for item in results[0]['data']]
        
        # DataFrame 생성
        df = pd.DataFrame({'date': dates})
        
        # 각 키워드 추가
        for result in results:
            keyword = result['title']
            ratios = [item['ratio'] for item in result['data']]
            df[keyword] = ratios
        
        # 날짜 변환
        df['date'] = pd.to_datetime(df['date'])
        
        return df


class NaverShopping:
    """네이버 쇼핑 검색 API"""
    
    def __init__(self):
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET
        self.url = "https://openapi.naver.com/v1/search/shop.json"
    
    def search_products(self, query, display=100, start=1, sort='sim'):
        """
        쇼핑 검색
        
        Parameters:
        - query: 검색어
        - display: 결과 수 (최대 100)
        - start: 시작 위치 (1~1000)
        - sort: 'sim'(정확도), 'date', 'asc'(가격↑), 'dsc'(가격↓)
        """
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        
        response = requests.get(self.url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 오류 {response.status_code}: {response.text}")
    
    def get_all_products(self, query, max_results=500):
        """여러 페이지 수집"""
        all_items = []
        
        for start in range(1, max_results, 100):
            try:
                result = self.search_products(query, display=100, start=start)
                items = result['items']
                all_items.extend(items)
                
                if len(items) < 100:
                    break
                    
            except Exception as e:
                print(f"Error at start={start}: {e}")
                break
        
        return all_items
    
    def to_dataframe(self, items):
        """제품 리스트를 DataFrame으로"""
        import re
        
        df = pd.DataFrame(items)
        
        # 가격 정수 변환
        df['lprice'] = df['lprice'].astype(int)
        if 'hprice' in df.columns:
            df['hprice'] = df['hprice'].astype(int)
        
        # HTML 태그 제거
        df['title'] = df['title'].apply(lambda x: re.sub('<.*?>', '', x))
        
        return df


class NaverBlog:
    """네이버 블로그 검색 API"""
    
    def __init__(self):
        self.client_id = NAVER_CLIENT_ID
        self.client_secret = NAVER_CLIENT_SECRET
        self.url = "https://openapi.naver.com/v1/search/blog.json"
    
    def search_blogs(self, query, display=100, start=1, sort='sim'):
        """블로그 검색"""
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort  # 'sim' or 'date'
        }
        
        response = requests.get(self.url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API 오류 {response.status_code}")
    
    def get_all_blogs(self, query, max_results=1000):
        """여러 페이지 수집"""
        all_items = []
        
        for start in range(1, max_results, 100):
            try:
                result = self.search_blogs(query, display=100, start=start)
                items = result['items']
                all_items.extend(items)
                
                if len(items) < 100:
                    break
                    
            except Exception as e:
                print(f"Error at start={start}: {e}")
                break
        
        return all_items
    
    def to_dataframe(self, items):
        """블로그 리스트를 DataFrame으로"""
        import re
        
        df = pd.DataFrame(items)
        
        # HTML 태그 제거
        df['title'] = df['title'].apply(lambda x: re.sub('<.*?>', '', x))
        df['description'] = df['description'].apply(lambda x: re.sub('<.*?>', '', x))
        
        # 날짜 변환
        df['postdate'] = pd.to_datetime(df['postdate'], format='%Y%m%d')
        
        return df
