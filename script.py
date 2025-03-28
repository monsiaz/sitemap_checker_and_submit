import requests
import xml.etree.ElementTree as ET
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import csv

SERVICE_ACCOUNT_FILE = '/Users/simonazoulay/API-SC/winged-helper-454920-c3-92bae76aea5e.json'
SCOPES = ['https://www.googleapis.com/auth/webmasters']
SITE_URL = 'sc-domain:wenony.fr'
SITEMAP_INDEX_URL = 'https://sitemaps.wenony.fr/sitemap/index.xml'
CSV_OUTPUT = 'sitemap_report.csv'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('searchconsole', 'v1', credentials=credentials)

def fetch_sitemap_urls(index_url):
    print(f"\n📥 Downloading sitemap index: {index_url}")
    response = requests.get(index_url)

    if response.status_code != 200:
        print(f"❌ Download failed with status code: {response.status_code}")
        return []

    root = ET.fromstring(response.content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('ns:sitemap/ns:loc', ns)]
    print(f"✅ Found {len(urls)} child sitemaps in the index.\n")
    return urls

def check_and_ping_sitemaps(sitemap_urls):
    rows = []

    for url in sitemap_urls:
        print(f"🔎 Checking sitemap: {url}")

        row = {
            "sitemap_url": url,
            "last_submitted": "",
            "last_downloaded": "",
            "errors": "",
            "warnings": "",
            "is_pending": "",
            "discovered_urls": "",
            "ping_attempted": "No",
            "ping_status": "",
            "sitemap_status": ""
        }

        try:
            sitemap = service.sitemaps().get(siteUrl=SITE_URL, feedpath=url).execute()

            row["last_submitted"] = sitemap.get('lastSubmitted', 'N/A')
            row["last_downloaded"] = sitemap.get('lastDownloaded', 'N/A')
            row["errors"] = int(sitemap.get('errors', 0))
            row["warnings"] = int(sitemap.get('warnings', 0))
            row["is_pending"] = sitemap.get('isPending', False)

            print(f"   - 📅 Last submitted    : {row['last_submitted']}")
            print(f"   - 📥 Last downloaded   : {row['last_downloaded']}")
            print(f"   - 🧨 Errors            : {row['errors']}")
            print(f"   - ⚠️  Warnings          : {row['warnings']}")
            print(f"   - ⏳ Pending           : {'Yes' if row['is_pending'] else 'No'}")

            total_submitted = 0
            if sitemap.get("contents"):
                for content in sitemap["contents"]:
                    if content.get("type") == "web":
                        submitted = content.get("submitted", 0)
                        try:
                            total_submitted += int(submitted)
                        except (ValueError, TypeError):
                            print(f"   ⚠️  Invalid 'submitted' value: {submitted}")
            row["discovered_urls"] = total_submitted
            print(f"   - 🌐 Discovered URLs   : {total_submitted}")

            if row["errors"] > 0 or row["is_pending"]:
                row["ping_attempted"] = "Yes"
                print("   🚀 Submitting sitemap...")
                try:
                    service.sitemaps().submit(siteUrl=SITE_URL, feedpath=url).execute()
                    row["ping_status"] = "Submitted successfully"
                    row["sitemap_status"] = "Submitted"
                    print("   ✅ Submission succeeded\n")
                except Exception as e:
                    row["ping_status"] = f"Submit failed: {e}"
                    row["sitemap_status"] = "Submission error"
                    print(f"   ❌ Submission failed: {e}\n")
            else:
                row["ping_status"] = "Not needed"
                row["sitemap_status"] = "OK"
                print("   ✔️ No issues found.\n")

        except Exception as e:
            row["ping_status"] = f"API error: {e}"
            row["sitemap_status"] = "API error"
            print(f"   ❌ Failed to fetch sitemap info: {e}\n")

        rows.append(row)

    print("📝 Exporting CSV...")
    with open(CSV_OUTPUT, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Export completed: {CSV_OUTPUT}\n")

if __name__ == '__main__':
    sitemap_urls = fetch_sitemap_urls(SITEMAP_INDEX_URL)
    check_and_ping_sitemaps(sitemap_urls)
