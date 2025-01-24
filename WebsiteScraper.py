import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from collections import Counter

def scrape_website(url):
    try:
        # Send an HTTP request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the website's HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract website title
        site_title = soup.title.string if soup.title else "No title found"
        print(f"Website Title: {site_title}\n")

        # Find all article titles (update the tag and class based on the website's structure)
        articles = soup.find_all('h2', class_='article-title')  # Example: update 'h2' and 'article-title'

        article_list = []
        print("Articles:")
        for idx, article in enumerate(articles, start=1):
            title = article.get_text(strip=True)
            link = article.find('a')['href'] if article.find('a') else "No link"
            full_link = urljoin(url, link)  # Ensure the link is absolute
            article_list.append({"title": title, "link": full_link})
            print(f"{idx}. {title}")
            print(f"   Link: {full_link}")

        # Find all images on the page
        images = soup.find_all('img')
        image_list = []
        print("\nImages:")
        for idx, img in enumerate(images, start=1):
            img_src = urljoin(url, img.get('src', 'No source'))
            img_alt = img.get('alt', 'No alt text')
            image_list.append({"src": img_src, "alt": img_alt})
            print(f"{idx}. Source: {img_src}")
            print(f"   Alt Text: {img_alt}")

        # Find all hyperlinks on the page
        links = soup.find_all('a')
        hyperlink_list = []
        print("\nHyperlinks:")
        for idx, link in enumerate(links, start=1):
            href = urljoin(url, link.get('href', 'No href'))
            text = link.get_text(strip=True)
            hyperlink_list.append({"text": text, "url": href})
            print(f"{idx}. Text: {text if text else 'No text'}")
            print(f"   URL: {href}")

        # Count and display word frequency in the page's content
        print("\nWord Frequency:")
        page_text = soup.get_text()
        words = page_text.split()
        word_count = Counter(word.strip().lower() for word in words if word.strip())
        sorted_word_count = word_count.most_common(10)
        print(json.dumps(sorted_word_count, indent=2))

        # Extract meta description and keywords
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        print("\nMeta Information:")
        print(f"Description: {meta_description['content'] if meta_description and 'content' in meta_description.attrs else 'No description'}")
        print(f"Keywords: {meta_keywords['content'] if meta_keywords and 'content' in meta_keywords.attrs else 'No keywords'}")

        # Find structured data (JSON-LD)
        print("\nStructured Data (JSON-LD):")
        json_ld = soup.find_all('script', type='application/ld+json')
        for idx, script in enumerate(json_ld, start=1):
            try:
                data = json.loads(script.string)
                print(f"{idx}: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"{idx}: Invalid JSON-LD script")

        # Save results to a JSON file
        result = {
            "title": site_title,
            "articles": article_list,
            "images": image_list,
            "hyperlinks": hyperlink_list,
            "word_frequency": sorted_word_count,
            "meta_description": meta_description['content'] if meta_description and 'content' in meta_description.attrs else None,
            "meta_keywords": meta_keywords['content'] if meta_keywords and 'content' in meta_keywords.attrs else None
        }
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print("\nResults saved to scraped_data.json")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")

if __name__ == "__main__":
    # Replace with the website URL you want to scrape
    website_url = "https://example.com/news"
    scrape_website(website_url)