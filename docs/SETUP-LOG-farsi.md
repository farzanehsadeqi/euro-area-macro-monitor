# گزارش فاز ۰ — ساخت اسکلت پروژه

پروژه: `euro-area-macro-monitor`
خط لولهٔ ETL خودکار برای شاخص‌های کلان و مالی از ECB، Eurostat و FRED.
زبان: پایتون. مسیر: `C:\Users\farza\projects\euro-area-macro-monitor`

---

## چرا این پروژه، و چرا اول

هدف: اثبات اینکه می‌توان یک جریان دادهٔ تولیدی ساخت که بدون دخالت دستی کار کند.
این با «یک نوت‌بوک که داده را یک‌بار گرفت» فرق دارد و در آگهی‌های شغلی زیر عنوان
ETL و automation می‌آید.

چرا اول از این شروع شد، نه از پروژهٔ بزرگ‌تر برق آلمان: **اولین مخزن جایی است که
همهٔ اشتباهات مخزن‌داری رخ می‌دهد.** بهتر است روی پروژه‌ای که یک هفته طول می‌کشد
رخ بدهد. ضمناً لایهٔ دریافت داده‌اش بعداً در پروژهٔ برق قابل استفادهٔ مجدد است.

---

## تصمیم‌های طراحی و دلیلشان

**پایتون، نه R.** دوره R بود، ولی این پروژه مهندسی داده است و اکوسیستم
زمان‌بندی و CI در پایتون بالغ‌تر است.

**سه منبع داده عمدی.** ECB و Eurostat کلید نمی‌خواهند، FRED می‌خواهد.
وجود یک منبع کلیددار اجباری می‌کند که مدیریت اسرار درست انجام شود
(متغیر محیطی در توسعه، GitHub Secrets در اجرای خودکار) — و همین در رزومه ارزش دارد.
دو منبع بی‌کلید باعث می‌شود هر کسی مخزن را clone کرد، بیشتر پروژه بدون ثبت‌نام کار کند.

**Parquet در گیت، DuckDB نه.**
- Parquet افزایشی و فشرده است → commit می‌شود، مخزن را بازتولیدپذیر می‌کند.
- DuckDB فایل باینری است و هر اجرا کل فایل را عوض می‌کند → گیت هر بار یک نسخهٔ
  کامل جدید ذخیره می‌کند و ظرف یک ماه مخزن گیگابایتی می‌شود. از روی Parquet ساخته می‌شود.
- `data/raw/` (JSON خام) نادیده گرفته می‌شود چون دوباره قابل دریافت است و حجیم.

**پروژه بیرون از OneDrive.** OneDrive با پوشهٔ `.git` و محیط مجازی تداخل دارد:
قفل‌شدن فایل، نسخهٔ تکراری، و گاهی خرابی مخزن.

---

## گام‌هایی که برداشتیم

### ۱. بررسی پیش‌نیازها
```bash
git --version      # 2.54.0.windows.1
python --version   # 3.14.5
```
نکته: پایتون ۳٫۱۴ تازه است و ممکن است بعضی بسته‌ها نسخهٔ سازگار نداشته باشند.
در عمل مشکلی پیش نیامد.

### ۲. بررسی مخزن قبلی
```bash
find /c/Users/farza -maxdepth 4 -type d -name ".git" 2>/dev/null
```
خروجی خالی → هیچ مخزن گیتی روی سیستم نبود، پس بحث پاک‌سازی منتفی شد.
(هر مخزن گیت یک پوشهٔ مخفی `.git` در ریشه دارد؛ این فرمان دنبال همان می‌گردد.)

### ۳. پوشه و محیط مجازی
```bash
mkdir -p /c/Users/farza/projects
cd /c/Users/farza/projects
mkdir euro-area-macro-monitor
cd euro-area-macro-monitor

python -m venv .venv
source .venv/Scripts/activate
```
در ویندوز `python` درست است نه `python3`، و مسیر `Scripts` است نه `bin`.

بررسی اینکه محیط واقعاً فعال است:
```bash
python -c "import sys; print(sys.prefix)"
# → C:\Users\farza\projects\euro-area-macro-monitor\.venv
```
اگر مسیر پایتون سیستمی را نشان بدهد، محیط فعال نشده.

### ۴. `.gitignore` — پیش از `git init`

**قاعده‌ای که باید درونی شود: `.gitignore` روی فایلی که قبلاً ردیابی شده اثر ندارد.**
اگر یک‌بار فایل سنگینی commit شود، افزودنش به `.gitignore` هیچ کاری نمی‌کند و آن فایل
تا ابد در تاریخچه می‌ماند — حتی بعد از حذف. پس باید قبل از اولین commit نوشته شود.

```
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/
.env
data/raw/
*.duckdb
*.duckdb.wal
output/*
!output/.gitkeep
```

### ۵. ساختار پوشه
```bash
mkdir -p src/monitor/sources data/raw data/processed output tests .github/workflows
touch src/monitor/__init__.py src/monitor/sources/__init__.py
touch data/raw/.gitkeep data/processed/.gitkeep output/.gitkeep
```
- `__init__.py` به پایتون می‌گوید این پوشه یک بسته است تا بتوان از آن import کرد.
- `.gitkeep` لازم است چون **گیت پوشهٔ خالی را ذخیره نمی‌کند** — فقط فایل‌ها را می‌بیند.

### ۶. فایل‌های پایه
`requirements.txt`, `.env.example`, `README.md` با الگوی heredoc ساخته شدند:
```bash
cat > filename << 'EOF'
...متن...
EOF
```
`.env.example` commit می‌شود (الگو)، `.env` واقعی هرگز.

### ۷. نصب و قفل نسخه‌ها
```bash
pip install -r requirements.txt
pip freeze > requirements.lock.txt
```
هشدار «Cache entry deserialization failed» بی‌اهمیت بود — فقط یعنی pip از کش
قدیمی استفاده نکرد و دوباره دانلود کرد.

تقسیم کار دو فایل:
- `requirements.txt` → پروژه به چه چیزهایی نیاز دارد
- `requirements.lock.txt` → دقیقاً چه نسخه‌هایی کار کرده‌اند (معادل `renv` در R)

نسخه‌های نصب‌شده: pandas 3.0.6، pyarrow 25.0.1، duckdb 1.5.6، matplotlib 3.11.2.
توجه: pandas نسخهٔ ۳ چند تغییر رفتاری نسبت به ۲ دارد؛ اگر نمونه‌کدی از اینترنت
کار نکرد، این می‌تواند دلیلش باشد.

### ۸. اولین commit
```bash
git init
git status                 # ← قبل از add حتماً بخوانید
git add .
git status                 # ← آخرین فرصت برای دیدن محتوای commit
git commit -m "Project skeleton: structure, gitignore, dependencies"
git count-objects -vH      # → size: 1.45 KiB
```

۱٫۴۵ کیلوبایت یعنی `.venv` وارد نشده. اگر وارد شده بود، صدها مگابایت می‌دیدیم.

---

## خطاهایی که رخ داد و چطور حل شد

### خطای ۱ — `output/.gitkeep` ظاهر نمی‌شد

**علت:** وقتی گیت یک پوشه را کلاً نادیده می‌گیرد، اصلاً داخلش را نگاه نمی‌کند.
پس استثنای `!output/.gitkeep` هرگز بررسی نمی‌شد.

**راه‌حل:** `output/` به `output/*` تغییر کرد.
- `output/` یعنی «خود پوشه را نادیده بگیر»
- `output/*` یعنی «وارد پوشه شو و هر چه داخلش است را نادیده بگیر» — و چون گیت
  وارد پوشه می‌شود، استثنای خط بعدی کار می‌کند.

**چرا اصلاً مهم بود:** بدون `.gitkeep`، کسی که مخزن را clone کند پوشهٔ `output/`
را نخواهد داشت و اسکریپت هنگام نوشتن خروجی خطا می‌دهد.

### خطای ۲ — خط `EDF` اضافی در `.gitignore`

**علت:** هنگام ساخت فایل با heredoc، به‌جای `EOF` عبارت `EDF` تایپ شد.
چون پایان‌بخش مطابقت نداشت، heredoc ادامه یافت و آن خط وارد فایل شد.

**راه‌حل:** `sed -i '/^EDF$/d' .gitignore`

بی‌خطر بود (گیت آن را الگویی برای فایلی به نام EDF می‌فهمید که وجود ندارد) ولی تمیز شد.

### ابهام‌هایی که روشن شد

- **گام اول نه پایتون است نه R** — فرمان‌ها در ترمینال (Git Bash) اجرا می‌شوند، نه در ویرایشگر.
- **`(.venv)` در خروجی** بخشی از نتیجهٔ فرمان نیست؛ نشانگر خط فرمان است که
  می‌گوید محیط مجازی فعال است.
- **`ls` خالی** طبیعی بود، چون `.venv` با نقطه شروع می‌شود و با `ls` ساده دیده نمی‌شود. `ls -a` لازم است.
- **تأیید مسیر** همیشه با `pwd` — عادتی که قبل از هر فرمان سازنده یا حذف‌کننده باید تکرار شود.

---

## وضعیت فعلی

```
euro-area-macro-monitor/
├── .github/workflows/        (خالی)
├── .venv/                    (ignored)
├── data/
│   ├── raw/                  (ignored)
│   └── processed/.gitkeep
├── output/.gitkeep
├── src/monitor/
│   ├── __init__.py
│   └── sources/__init__.py
├── tests/                    (خالی)
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── requirements.lock.txt
```

فاز ۰ تمام. یک commit محلی، مخزن ۱٫۴۵ کیلوبایت.

---

## گام بعدی

۱. ساخت مخزن روی گیت‌هاب — **بدون** README، بدون gitignore، بدون license
   (چون خودمان داریمشان و تعارض ایجاد می‌شود)
۲. ```bash
   git remote add origin https://github.com/USERNAME/euro-area-macro-monitor.git
   git branch -M main
   git push -u origin main
   ```
۳. فاز ۱: اولین اتصال به API (ECB، بدون کلید) — یک شاخص، یک DataFrame.
   آزمون پذیرش: جدولی با ستون تاریخ و مقدار برمی‌گردد.
