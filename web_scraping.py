import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
import os
import re

# =========================
# تنظيف اسم النادي (حل نهائي)
# =========================
def clean_team_name(text):
    """
    يحذف تكرار اسم الفريق بالكامل
    مثال:
    ريال مدريد ريال مدريد -> ريال مدريد
    برشلونة برشلونة -> برشلونة
    """
    text = " ".join(text.split())  # تنظيف المسافات الزائدة

    pattern = r"^(.+?)\s+\1$"
    match = re.match(pattern, text)

    if match:
        return match.group(1)

    return text

# =========================
# الدالة الأساسية
# =========================
def update_laliga_standings():

    URL = "https://www.kooora.com/%D9%83%D8%B1%D8%A9-%D8%A7%D9%84%D9%82%D8%AF%D9%85/%D9%85%D8%B3%D8%A7%D8%A8%D9%82%D8%A9/%D8%A7%D9%84%D9%88%D8%B1%D9%8A-%D8%A7%D9%84%D8%A7%D9%95%D8%B3%D8%A8%D8%A7%D9%86%D9%8A/%D8%AC%D8%AF%D9%88%D9%84/34pl8szyvrbwcmfkuocjm3r6t"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")

    headers = [th.get_text(strip=True) for th in table.find_all("th")]

    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue

        row = []
        for i, td in enumerate(tds):
            text = td.get_text(" ", strip=True)

            # تنظيف اسم النادي (عمود الفريق)
            if i == 1:
                text = clean_team_name(text)

            row.append(text)

        rows.append(row)

    df = pd.DataFrame(rows, columns=headers)

    # =========================
    # حذف العمود A و B
    # =========================
    df = df.iloc[:, 2:]

    # =========================
    # حفظ ملف Excel
    # =========================
    file_path = os.path.join(os.getcwd(), "LaLiga_Standings.xlsx")
    df.to_excel(file_path, index=False)

    print("✅ تم تحديث الترتيب بنجاح")
    print(file_path)

# =========================
# تشغيل فوري
# =========================
update_laliga_standings()

# =========================
# جدولة كل يوم اثنين
# =========================
schedule.every().monday.at("09:00").do(update_laliga_standings)

print("⏳ السكربت يعمل وسيحدّث كل يوم اثنين الساعة 09:00")

while True:
    schedule.run_pending()
    time.sleep(60)
