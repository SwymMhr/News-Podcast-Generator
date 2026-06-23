from ddgs import DDGS


def _try_search(topic, region, timelimit, max_results):
    with DDGS() as ddgs:
        return list(ddgs.news(topic, region=region, timelimit=timelimit, max_results=max_results))


def _parse_results(raw):
    return [
        {
            "title": r.get("title", ""),
            "body": r.get("body", ""),
            "url": r.get("url", ""),
            "date": r.get("date", ""),
        }
        for r in raw
    ]


def search_news(topics, region="us-en", timelimit=None, max_results=5):
    news_by_topic = {}

    for topic in topics:
        articles = []
        try:
            raw = _try_search(topic, region, timelimit, max_results)
            articles = _parse_results(raw)
        except Exception:
            pass

        if not articles and region != "wt-wt":
            try:
                raw = _try_search(topic, "wt-wt", timelimit, max_results)
                articles = _parse_results(raw)
            except Exception:
                pass

        if not articles and timelimit is not None:
            try:
                raw = _try_search(topic, region if region != "us-en" else "wt-wt", None, max_results)
                articles = _parse_results(raw)
            except Exception:
                pass

        if not articles:
            try:
                raw = _try_search(topic.lower(), "wt-wt", None, max_results)
                articles = _parse_results(raw)
            except Exception:
                pass

        if articles:
            news_by_topic[topic] = articles
    return news_by_topic
