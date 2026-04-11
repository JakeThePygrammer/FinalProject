import requests

def get_city_display_name(city_query: str) -> str:
    q = (city_query or "").strip() # ова е името на градот којшто го има дадено корисникот
    if not q:
        return ""

    url = "https://nominatim.openstreetmap.org/search" # url-то на АПИто за градови коешто го користиме
    params = {"q": q, "format": "json", "limit": 1} # параметри коишто ги праќаме - име на градот, json формат и лимитираме на 1 резултат
    headers = {"User-Agent": "city-bite-finder-student-app"}

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data:
            return data[0].get("display_name") or q
        return q
    except Exception:
        return q
