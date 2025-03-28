# 🕸️ Sitemap Inspector & Submitter — Google Search Console API

A Python script to **inspect, validate, and resubmit sitemaps** listed in a sitemap index, using the Google Search Console API.

Built for SEO engineers, devops, and web teams who need automated insight into their sitemap structure and proactive handling of broken or pending sitemaps.

---

## 🚀 Features

- Fetches and parses any sitemap index (XML)
- Checks each child sitemap using the GSC API
- Displays:
  - Last submitted & downloaded dates
  - Errors, warnings, pending status
  - Number of discovered URLs
- Automatically "pings" (submits) broken or pending sitemaps
- Generates a complete CSV report (`sitemap_report.csv`)

---

## 🛠️ Requirements

- Python 3.7+
- A valid **Google Search Console Service Account**
- The site must be added and verified in your GSC account

---

## 📦 Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/sitemap-monitor.git
cd sitemap-monitor
pip install -r requirements.txt
