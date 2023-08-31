import os
from app import app
from flask import jsonify, request, Response
from dotenv import load_dotenv
import requests

load_dotenv()

_MAX_COUNT = 50
_DEFAULT_COUNT = 10

_flask_request = request # alias to not confuse "request" with "requests"
_subscription_key = os.environ["AZURE_KEY"]

@app.route('/')
def index():
    return "PressKit Bing News API.\n Usage: /articles?keywords=[comma or space separated list of keywords]&count=[int where 1 <= n <= 50]"

@app.route('/articles')
def test_route():
    keywords = _flask_request.args.get('keywords')
    count = _flask_request.args.get('count')
    
    if not keywords:
        return Response(response="Missing required query param: 'keywords'.", status=400)
    if not count:
        count = _DEFAULT_COUNT
    if not count.isnumeric():
        return Response(response=f"'count' expected to be an integer value, given {count}")

    count = int(count)
    if count < 1 or count > _MAX_COUNT:
        return Response(response=f"'count' param must be between 1 and {_MAX_COUNT}. Given {count}", status=400)
    
    search_url = "https://api.bing.microsoft.com/v7.0/news/search"
    search_term = keywords.replace(',', ' ')
    headers = {"Ocp-Apim-Subscription-Key": _subscription_key}
    params = {
        "q": search_term,
        "count": count,
        "responseFilter": "News",
        "textDecorations": True,
        "textFormat": "HTML"
        }
    
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    raw_results = response.json()["value"]
    
    search_results = []
    for article in raw_results: # filter article data
        required_keys = [
            "datePublished",
            "name", # headline
            "description", #blurb
            "url",
            "provider" #exception
            ]
        
        key_missing = False
        for k in required_keys:
            if not k in article:
                key_missing = True
        if key_missing:
            continue
        
        # I had to do this weird stuff because the publisher's name is stored
        # like this: {provider: [{name: "publisher name", ...}], ...}
        if len(article["provider"]) < 1:
            continue
        if not "name" in article["provider"][0]:
            continue
        
        search_results.append({
            "datePublished": article["datePublished"],
            "headline": article["name"],
            "blurb": article["description"],
            "url": article["url"],
            "publisher": article["provider"][0]["name"]
        })
    return search_results