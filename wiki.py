import asyncio
import aiohttp

async def get_first_sentence_and_link_async(session, keyword):
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "titles": keyword,
        "prop": "extracts|info",
        "exintro": "1",
        "explaintext": "1",
        "redirects": "1",
        "inprop": "url"
    }

    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            pages = data['query']['pages']

            for page_id, page in pages.items():
                if 'extract' in page and 'may refer to' not in page['extract']:
                    extract = page['extract']
                    first_sentence = '.'.join(extract.split('.')[:2]) + '.'
                    article_title = page['title']
                    article_url = f"https://en.wikipedia.org/wiki/{article_title.replace(' ', '_')}"
                    print(keyword, article_url)
                    return first_sentence, article_url
                else:
                    related_keyword = await get_related_articles_async(session, keyword)
                    if keyword == related_keyword:
                        return None
                    if related_keyword:
                        return await get_first_sentence_and_link_async(session, related_keyword)
        return None


async def get_related_articles_async(session, keyword):
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "opensearch",
        "search": keyword,
        "limit": 3,
        "namespace": 0,
        "format": "json"
    }

    async with session.get(url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            if len(data[1]) > 0:
                related_title = data[1][1 if len(data[1]) > 1 else 0]
                return related_title
        return None