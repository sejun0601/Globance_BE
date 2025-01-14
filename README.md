# Globance Backend

## DB diagram
![Frame 1](https://github.com/user-attachments/assets/ea797810-15e8-4cc5-bc6b-177bd592bed8)

- `Django`를 이용해서 DB 구축
- NewsAPI 에서 6시간마다 `Crontab`을 사용해서 뉴스 데이터를 받아온다.
```
0 */6 * * * /root/venv/bin/python /root/Globance_BE/manage.py fetch_top_headlines  >> /root/Globance_BE/logs/file.log 2>&1
```

- `Geoparser` 를 이용해서 뉴스의 제목, 설명, 본문에서 위치 데이터를 뽑아낸다.
- `Facebook BART-Large-CNN` 을 이용해서 뉴스 텍스트를 전부 요약하고 핵심단어를 추출해 핵심단어의 개수로 중요도 점수를 매긴다.
- `Django` 를 이용해서 해당 데이터를 모두 `DB`에 저장한다.
- 요청이 들어왔을때 데이터를 `GeoJson` 형태로 변환하여 반환한다.

## Endpoint

### Base Url (GET)
```
GET http://{server ip address}/api/news/
```

### - NEWs Geojson Data 
    news_geojson/

### parameters

limit = 정수


category = 
- 'business'
- 'entertainment'
- 'general'
- 'health'
- 'science'
- 'sports'
- 'technology'

(여러 카테고리 가능 : 카테고리가 여러개일때는 각 카테고리가 limit의 수 만큼 반환됨)

### - Weekly News Summary
    weekly_news/

### parameters
limit = 정수


## GeoJson Response

예시) GET http://{server ip address}/api/news/news_geojson/?limit=1&category=general

```
{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -118.24368,
                    34.05223
                ]
            },
            "properties": {
                "title": "L.A. fires live updates: Winds to strengthen as blaze heads toward major highway; at least 16 dead - The Washington Post",
                "description": "Follow the latest news, updates and containment efforts for the wildfires burning in Los Angeles, including the Palisades and Eaton fires.",
                "url": "https://www.washingtonpost.com/weather/2025/01/12/los-angeles-fires-california-updates-palisades-eaton/",
                "published_at": "2025-01-12T08:18:53+00:00",
                "summary": "Weather officials are predicting that Santa Ana winds, which can fan flames and carry dangerous embers, will continue through Wednesday. Follow the latest news, updates and containment efforts for the wildfires burning in Los Angeles, including the Palisades and Eaton fires.",
                "importance": 41,
                "category": "general",
                "preview_title": "",
                "preview_description": "",
                "preview_image": ""
            }
        }
    ]
}

```

## Weekly News Summary Response

```
{
    "combined_summaries": "Alcohol effects may increase with age as brain changes. Alcohol tolerance may not decrease with age, but older adults may experience increased alcohol effects because of changes in brain function and physiology. Some people in their 60s and 70s may notice that their usual glass of red wine with dinner seems to hit them a bit harder than it did in their young…\n\nScientists Reveal New Weight Loss Hack: Drink This Berry Juice Every Day To Burn More Fat - SciTechDaily Elderberry juice may improve metabolism and gut health, as a recent study found it lowers blood sugar and boosts fat burning due to its high anthocyanin content. A recent study led by Washington State University suggests that elderberry Juice may support",
    "limit": 2
}
```