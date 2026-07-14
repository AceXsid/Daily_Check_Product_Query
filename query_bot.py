import requests
from bs4 import BeautifulSoup
import os
import time

# ==============================
# 🔐 CONFIGURATION
# ==============================

CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")

# ONE GLOBAL SEEN FILE
SEEN_FILE = "seen_support_queries.txt"

# 🔥 Add all your products here
PRODUCTS = [
    {
        "name": "The Plus Addons",
        "url": "https://wordpress.org/support/plugin/the-plus-addons-for-elementor-page-builder/",
        "clickup_list_id": "901607047583",
        # "clickup_list_id": "901607808438",
        "assignees": [176552817, 94892542, 94894039]
    },
    {
        "name": "Nexter Extension",
        "url": "https://wordpress.org/support/plugin/nexter-extension/",
        "clickup_list_id": "901606860254",
        "assignees": [94894033, 94893994]
    },
    {
        "name": "WDesignKit",
        "url": "https://wordpress.org/support/plugin/wdesignkit/",
        "clickup_list_id": "901607048102",
        "assignees": [176552723, 94894049, 94893993]
    },
    {
        "name": "Nexter Blocks",
        "url": "https://wordpress.org/support/plugin/the-plus-addons-for-block-editor/",
        "clickup_list_id": "901606860254",
        "assignees": [94894033, 94893991]
    },
     {
        "name": "Sticky Header",
        "url": "https://wordpress.org/support/plugin/sticky-header-effects-for-elementor/",
        "clickup_list_id": "901607050738",
        "assignees": [176552817, 94892542]
    },
      {
        "name": "OhhBoi",
        "url": "https://wordpress.org/support/plugin/ooohboi-steroids-for-elementor/",
        "clickup_list_id": "901606984097",
        "assignees": [94894039]
    },
    {
        "name": "Uichemy",
        "url": "https://wordpress.org/support/plugin/uichemy/",
        "clickup_list_id": "901606862007",
        "assignees": [94894033, 94896099]
    },
    {
        "name": "Nexter Theme",
        "url": "https://wordpress.org/support/theme/nexter/",
        "clickup_list_id": "901606860254",
        "assignees": [94894033, 94893994]
    },
        {
        "name": "SproutOS",
        "url": "https://wordpress.org/support/plugin/sproutos/",
        "clickup_list_id": "901615868228",
        "assignees": [94894049, 94892542 , 176552817]
    }
]

# ==============================
# 📂 LOAD & SAVE SEEN FILE
# ==============================

def load_seen_queries():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(line.strip() for line in f)


def save_seen_query(url):
    with open(SEEN_FILE, "a") as f:
        f.write(url + "\n")


# ==============================
# 🔎 GET SUPPORT TOPICS
# ==============================

def get_support_topics(base_url, limit=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    topics = []
    topic_links = soup.select("a.bbp-topic-permalink")

    for topic in topic_links[:limit]:
        title = topic.get_text(strip=True)
        url = topic["href"]
        topics.append((title, url))

    return topics


# ==============================
# 📄 GET FULL TOPIC CONTENT
# ==============================

def get_topic_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    content_div = soup.find("div", class_="bbp-topic-content")

    if content_div:
        return content_div.get_text(strip=True)

    return "[No content found]"


# ==============================
# 📌 CREATE CLICKUP TASK
# ==============================

def create_clickup_task(product_name, list_id, title, topic_url, topic_content, assignees):
    api_url = f"https://api.clickup.com/api/v2/list/{list_id}/task"

    headers = {
        "Authorization": CLICKUP_API_TOKEN,
        "Content-Type": "application/json"
    }

    payload = {
        "name": f" ORG Ticket | Support Query: {title}",
        "description": f"""🔗 Support URL:
{topic_url}

📝 Query Details:
{topic_content}
""",
        "status": "NEW TICKET",
        "assignees": assignees
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        print(f"✅ Task created: {title}")
        return True
    else:
        print(f"❌ Failed: {title}")
        print("Response:", response.text)
        return False


# ==============================
# 🚀 MAIN RUNNER
# ==============================

if __name__ == "__main__":

    print("🔍 Checking all products for new support queries...\n")

    seen_queries = load_seen_queries()
    total_new = 0

    for product in PRODUCTS:

        print(f"🔎 Scanning: {product['name']}")

        topics = get_support_topics(product["url"], limit=15)

        for title, link in topics:

            if link in seen_queries:
                print(f"⏩ Already processed: {title}")
                continue

            print(f"🆕 New query found: {title}")

            content = get_topic_content(link)

            success = create_clickup_task(
                product_name=product["name"],
                list_id=product["clickup_list_id"],
                title=title,
                topic_url=link,
                topic_content=content,
                assignees=product["assignees"]
            )
            # success = "done"

            if success:
                save_seen_query(link)
                seen_queries.add(link)  # 🔥 important to prevent duplicates in same run
                total_new += 1

            time.sleep(2)

        print()

    print(f"✅ Done. Total new tasks created: {total_new}")