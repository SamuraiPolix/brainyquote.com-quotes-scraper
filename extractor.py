import requests
from lxml import html
import json
import io
from lxml.html.clean import unicode


def extract(author: str, chars_limit):
    # Define empty lists to store extracted data
    quotes = list()
    authors = list()

    author_for_url = author.replace(" ", "-")
    author_for_url += "-quotes"

    count_skipped = 0       # Skipped quotes because of chars_limit
    print(f"Scraping \"{author}\" from BrainyQuote.com ...")
    # Define URL to fetch data from
    base_url = f"https://www.brainyquote.com/authors"

    pages = get_number_of_pages(base_url, author_for_url)

    print(pages)

    for page in range(1, pages+1, 1):
        count_scraped_page = 0
        print(f"\nScraping quotes by {author}, Page: {page}/{pages}...")
        tmp_url: str = f'{author_for_url}_{page}'
        # Fetch the HTML content from the URL
        headers = {
            'authority': 'www.brainyquote.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en,en-US;q=0.9,he-IL;q=0.8,he;q=0.7',
            'referer': f'{base_url}/{tmp_url}',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = requests.get(f'{base_url}/{tmp_url}', headers=headers)
        html_str = response.text

        # Convert HTML content to lxml tree object
        tree = html.fromstring(html_str)

        # Extract quote
        div_elements = tree.xpath("//div[@class='grid-item qb clearfix bqQt']")
        for div_element in div_elements:
            count_scraped_page += 1
            p_text = ''.join(div_element.xpath('.//a//div//text()')).replace('\t', '').replace('\n', '')
            quotes.append(p_text)
            authors.append(author)

        print(f"Scraped {count_scraped_page} quotes by {author} from Page {page}/{pages}")

    # Remove quotes that are too long (if limit is not -1)
    if chars_limit != -1:
        for i in range(len(quotes)-1, -1, -1):
            if len(quotes[i]) > chars_limit:
                count_skipped += 1
                del quotes[i]
                del authors[i]

    # Write extracted data to a JSON file
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    data = []
    for i in range(0, len(quotes)):
        quote_dict: dict
        quote_dict['quote'] = quotes[i]
        quote_dict['author'] = authors[i]
        data.append(quote_dict)

    with io.open(f'{author}_data.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data, ensure_ascii=False, indent=4)
        outfile.write(to_unicode(str_))

    if chars_limit != -1:
        print(f"skipped {count_skipped} quotes that exceeded {chars_limit} chars.")
    return outfile.name, len(quotes)


def get_number_of_pages(base_url, author_for_url):
    # Fetch the HTML content from the URL
    headers = {
        'authority': 'www.brainyquote.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en,en-US;q=0.9,he-IL;q=0.8,he;q=0.7',
        'referer': f'{base_url}/{author_for_url}',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    response = requests.get(f'{base_url}/{author_for_url}', headers=headers)
    html_str = response.text

    # Convert HTML content to lxml tree object
    tree = html.fromstring(html_str)

    pages: int = 1

    # Extract pages items
    div_elements = tree.xpath("//li[@class='page-item']")
    for div_element in div_elements:
        p_text = ''.join(div_element.xpath('.//a//text()')).replace('\t', '').replace('\n', '')
        if p_text.isnumeric() and int(p_text) > pages:
            pages = int(p_text)

    return pages
