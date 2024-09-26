import requests


def get_first_sentence_and_link(keyword):
    url = "https://en.wikipedia.org/w/api.php"

    # Параметры для основного запроса
    params = {
        "action": "query",
        "format": "json",
        "titles": keyword,
        "prop": "extracts|info",
        "exintro": True,
        "explaintext": True,
        "redirects": 1,
        "inprop": "url"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        pages = data['query']['pages']

        for page_id, page in pages.items():
            if 'extract' in page and 'may refer to' not in page['extract']:
                extract = page['extract']
                first_sentence = extract.split('\n')[0] + '.'
                article_title = page['title']
                article_url = f"https://en.wikipedia.org/wiki/{article_title.replace(' ', '_')}"

                print(keyword,  article_url)
                return first_sentence, article_url

            # Если статья не найдена, выполняем поиск
            else:
                related_keyword = get_related_articles(keyword)
                if related_keyword:
                    return get_first_sentence_and_link(related_keyword)

    else:
        return None


def get_related_articles(keyword):
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "opensearch",
        "search": keyword,
        "limit": 3,
        "namespace": 0,
        "format": "json"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if len(data[1]) > 0:
            related_title = data[1][1 if len(data[1]) > 0 else 0]
            return related_title

    return None
#
# first_sentence, article_link = get_first_sentence_and_link('Python')
# print("First sentence:", first_sentence)
# print("Article link:", article_link)
