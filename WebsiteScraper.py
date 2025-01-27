import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from collections import Counter
import re
import os

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
        structured_data_list = []
        for idx, script in enumerate(json_ld, start=1):
            try:
                data = json.loads(script.string)
                structured_data_list.append(data)
                print(f"{idx}: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"{idx}: Invalid JSON-LD script")

        # Extract contact information (emails and phone numbers)
        print("\nContact Information:")
        emails = set(re.findall(r'[\w\.]+@[\w\.]+', page_text))
        phones = set(re.findall(r'\+?\d[\d\s().-]{7,}\d', page_text))
        print(f"Emails: {', '.join(emails) if emails else 'None found'}")
        print(f"Phone Numbers: {', '.join(phones) if phones else 'None found'}")

        # Extract headings (h1, h2, h3, etc.)
        print("\nHeadings:")
        headings = {}
        for i in range(1, 7):
            tag = f'h{i}'
            headings[tag] = [heading.get_text(strip=True) for heading in soup.find_all(tag)]
            print(f"{tag.upper()}:")
            for heading in headings[tag]:
                print(f"  - {heading}")

        # Extract tables and their contents
        print("\nTables:")
        tables = soup.find_all('table')
        table_list = []
        for idx, table in enumerate(tables, start=1):
            rows = table.find_all('tr')
            table_data = []
            for row in rows:
                cells = row.find_all(['td', 'th'])
                cell_data = [cell.get_text(strip=True) for cell in cells]
                table_data.append(cell_data)
            table_list.append(table_data)
            print(f"Table {idx}:")
            for row in table_data:
                print(f"  {row}")

        # Extract forms and their input fields
        print("\nForms:")
        forms = soup.find_all('form')
        form_list = []
        for idx, form in enumerate(forms, start=1):
            form_details = {
                "action": form.get('action', 'No action'),
                "method": form.get('method', 'GET').upper(),
                "inputs": []
            }
            inputs = form.find_all('input')
            for input_tag in inputs:
                input_details = {
                    "name": input_tag.get('name', 'No name'),
                    "type": input_tag.get('type', 'text'),
                    "value": input_tag.get('value', '')
                }
                form_details["inputs"].append(input_details)
            form_list.append(form_details)
            print(f"Form {idx}: Action: {form_details['action']}, Method: {form_details['method']}")
            for input_field in form_details['inputs']:
                print(f"  Input: {input_field}")

        # Save results to a JSON file in the same directory as the script
        result = {
            "title": site_title,
            "articles": article_list,
            "images": image_list,
            "hyperlinks": hyperlink_list,
            "word_frequency": sorted_word_count,
            "meta_description": meta_description['content'] if meta_description and 'content' in meta_description.attrs else None,
            "meta_keywords": meta_keywords['content'] if meta_keywords and 'content' in meta_keywords.attrs else None,
            "structured_data": structured_data_list,
            "contact_information": {
                "emails": list(emails),
                "phone_numbers": list(phones)
            },
            "headings": headings,
            "tables": table_list,
            "forms": form_list
        }
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, 'scraped_data.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print(f"\nResults saved to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")

if __name__ == "__main__":
    # Ask the user for the website URL
    website_url = input("Enter the website URL to scrape: ")
    scrape_website(website_url)