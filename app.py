from datetime import datetime
from io import BytesIO
import os
import threading
from urllib.parse import quote

import pandas as pd
from flask import Flask, flash, redirect, render_template, send_file, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-for-local-use")

KEYWORDS = ["KMA", "날씨", "기상청", "태풍", "폭염", "강풍"]
COLUMNS = ["keyword", "title", "url", "collected_at"]
results = []
last_updated = None
refresh_lock = threading.Lock()


def fetch_cafe_results():
    """Collect visible Naver search results for each keyword using Edge."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,1000")

    driver_path = os.environ.get("EDGE_DRIVER_PATH")
    if driver_path:
        from selenium.webdriver.edge.service import Service
        driver = webdriver.Edge(service=Service(executable_path=driver_path), options=options)
    else:
        # Selenium Manager attempts to locate/download a compatible EdgeDriver.
        driver = webdriver.Edge(options=options)

    rows = []
    try:
        for keyword in KEYWORDS:
            url = f"https://search.naver.com/search.naver?where=article&query={quote(keyword)}"
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(By.CSS_SELECTOR, "a")
                )
            except Exception:
                pass

            # Naver selectors may change; gather links conservatively.
            links = driver.find_elements(By.CSS_SELECTOR, "a")
            seen = set()
            for link in links:
                try:
                    title = (link.text or "").strip()
                    href = link.get_attribute("href") or ""
                    if not title or not href.startswith("http"):
                        continue
                    if "cafe.naver.com" not in href and "search.naver.com" not in href:
                        continue
                    key = (title, href)
                    if key in seen:
                        continue
                    seen.add(key)
                    rows.append({
                        "keyword": keyword,
                        "title": title,
                        "url": href,
                        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    })
                except Exception:
                    continue
    finally:
        driver.quit()
    return rows


@app.get("/")
def index():
    keyword_filter = ( __import__("flask").request.args.get("keyword") or "").strip()
    query = ( __import__("flask").request.args.get("q") or "").strip().lower()
    filtered = [
        row for row in results
        if (not keyword_filter or row["keyword"] == keyword_filter)
        and (not query or query in row["title"].lower() or query in row["url"].lower())
    ]
    return render_template(
        "index.html",
        rows=filtered,
        keywords=KEYWORDS,
        keyword_filter=keyword_filter,
        query=query,
        total=len(results),
        last_updated=last_updated,
    )


@app.post("/refresh")
def refresh():
    global results, last_updated
    if not refresh_lock.acquire(blocking=False):
        flash("수집이 이미 진행 중입니다. 잠시 후 확인해 주세요.", "warning")
        return redirect(url_for("index"))
    try:
        fresh_rows = fetch_cafe_results()
        results = fresh_rows
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if fresh_rows:
            pd.DataFrame(fresh_rows, columns=COLUMNS).to_excel(
                "my_2nd_crawling.xlsx", index=False
            )
        flash(f"수집이 완료되었습니다. {len(fresh_rows)}건을 확인했습니다.", "success")
    except Exception as exc:
        flash(f"수집 중 오류가 발생했습니다: {exc}", "danger")
    finally:
        refresh_lock.release()
    return redirect(url_for("index"))


@app.get("/download")
def download():
    if not results:
        flash("다운로드할 데이터가 없습니다. 먼저 새로고침을 눌러 수집해 주세요.", "warning")
        return redirect(url_for("index"))
    buffer = BytesIO()
    pd.DataFrame(results, columns=COLUMNS).to_excel(buffer, index=False)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="my_2nd_crawling.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
