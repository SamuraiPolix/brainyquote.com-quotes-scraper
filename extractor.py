# Import necessary libraries
import requests
from lxml import html
import json
import io
from lxml.html.clean import unicode


def extract(author: str, chars_limit):
    # Define empty lists to store extracted data
    quote_approve = list()
    author_approve = list()

    author_for_url = author.replace(" ", "-")
    author_for_url += "-quotes"

    count_skipped = 0       # Skipped quotes because of chars_limit
    print(f"Scraping \"{author}\" from BrainyQuote.com ...")
    # Define URL to fetch data from
    url = f"https://www.brainyquote.com/authors/{author_for_url}"

    pages = get_number_of_pages(url)

    print(pages)

    for page in range(1, pages+1, 1):
        count_scraped_page = 0
        print(f"\nScraping quotes by {author}, Page: {page}/{pages}...")
        tmp_url: str = f'{url}_{page}'
        # Fetch the HTML content from the URL
        response = requests.get(tmp_url)
        html_str = response.text

        # Convert HTML content to lxml tree object
        tree = html.fromstring(html_str)

        # Extract quote
        div_elements = tree.xpath("//div[@class='grid-item qb clearfix bqQt']")
        for div_element in div_elements:
            count_scraped_page += 1
            p_text = ''.join(div_element.xpath('.//a//div//text()')).replace('\t', '').replace('\n', '')
            quote_approve.append(p_text)
            author_approve.append(author)

        print(f"Scraped {count_scraped_page} quotes by {author} from Page {page}/{pages}")

    # Remove verses that are too long (if limit is not -1)
    if chars_limit != -1:
        for i in range(len(quote_approve)-1, -1, -1):
            if len(quote_approve[i]) > chars_limit:
                count_skipped += 1
                del quote_approve[i]
                del author_approve[i]

    # Write extracted data to a JSON file
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    with io.open(f'{author}_data.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps({'quotes': quote_approve, 'authors': author_approve}, ensure_ascii=False, indent=4)
        outfile.write(to_unicode(str_))

    # Read data from JSON file and compare with original data
    with open(f'{author}_data.json', 'r', encoding='utf-8') as data_file:
        data_loaded = json.load(data_file)

    if chars_limit != -1:
        print(f"skipped {count_skipped} quotes that exceeded {chars_limit} chars.")
    return outfile.name, len(quote_approve)


def get_number_of_pages(url):
    # Fetch the HTML content from the URL
    response = requests.get(url)
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