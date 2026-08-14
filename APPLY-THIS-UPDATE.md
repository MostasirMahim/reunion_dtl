# BSS Reunion — Update Package

এই zip-এ শুধু **পরিবর্তিত ও নতুন ফাইলগুলো** আছে। আপনার প্রজেক্টের অন্য কোনো ফাইল
(`.env`, `db.sqlite3`, `migrations/`, `settings.py` ইত্যাদি) এখানে নেই, তাই কিছু হারানোর ভয় নেই।

## কীভাবে অ্যাপ্লাই করবেন (PowerShell)

```powershell
# 1) প্রজেক্ট ফোল্ডারে যান
cd D:\bssreunion\bssreunion

# 2) (রেকমেন্ডেড) আগে ব্যাকআপ / git commit করে নিন
git add -A ; git commit -m "before logo + UI update"

# 3) zip টা প্রজেক্ট রুটে এক্সট্র্যাক্ট করুন (ফাইলগুলো ওভাররাইট হবে)
Expand-Archive -Path "D:\Download chrome\bssreunion-update.zip" -DestinationPath "$env:TEMP\bssupd" -Force
Copy-Item -Path "$env:TEMP\bssupd\bssreunion-update\*" -Destination . -Recurse -Force

# 4) সার্ভার চালান
python manage.py runserver
```

ব্রাউজারে **Ctrl + F5** দিয়ে hard refresh করুন (পুরনো CSS/লোগো ক্যাশ থাকতে পারে)।

প্রোডাকশনে (Vercel/সার্ভার) ডিপ্লয়ের আগে:

```powershell
python manage.py collectstatic --noinput
```

> কোনো নতুন migration লাগবে না — ডেটাবেজ মডেলে কিছু বদলায়নি, শুধু ফর্মের widget বদলেছে।

---

## কী কী বদলেছে

### ১. লোগো
- নতুন লোগো: `static/img/bss-logo.png` (ব্যাকগ্রাউন্ড রিমুভ করা transparent PNG)
- ফেভিকন: `static/img/favicon.png`
- সব টেমপ্লেটে পুরনো `bss-logo.jpg` রেফারেন্স নতুন `.png`-এ বদলানো হয়েছে
- `.brand-mark` CSS গোল (circle) থেকে বদলে rectangular logo-র জন্য ঠিক করা হয়েছে

পুরনো `bss-logo.jpg` ফাইলটা এখন আর কোথাও ব্যবহার হচ্ছে না — চাইলে ডিলিট করে দিতে পারেন।

### ২. হোম পেজে স্কুলের ছবি (ব্যানার)
- `static/img/school-campus.jpg` যোগ করা হয়েছে
- হিরো সেকশনের **পুরো ব্যাকগ্রাউন্ড** হিসেবে ছবিটা বসেছে, লেখাগুলো তার উপরে
- বাঁদিক থেকে ডানদিকে navy gradient wash — যেখানে লেখা আছে সেদিকটা গাঢ়, ডানদিকে ক্যাম্পাস স্পষ্ট দেখা যায়
- উপরে-নিচে আলাদা fade, তাই navbar আর পরের সেকশনের সাথে সুন্দরভাবে মিশে যায়
- মোবাইলে wash উপর-নিচমুখী হয়ে যায়, যাতে ছোট স্ক্রিনেও লেখা পুরোপুরি পড়া যায়

### ৩. SSC Batch / SSC Passing Year — search & select
- টেক্সট ইনপুটের বদলে এখন **১৯৬৩ থেকে ২০৩২** পর্যন্ত dropdown
- নতুন ফাইল `static/js/searchable-select.js` — টাইপ করলে ফিল্টার হয়, তারপর সিলেক্ট
- Arrow key / Enter / Esc / মাউস ক্লিক — সবই কাজ করে; মোবাইলে numeric keyboard আসে
- JavaScript বন্ধ থাকলেও সাধারণ dropdown হিসেবে কাজ করবে
- Special Funding পেজের SSC Batch ফিল্ডেও একই জিনিস
- সার্ভার সাইডেও year range ভ্যালিডেশন যোগ করা হয়েছে (কেউ range-এর বাইরে পাঠাতে পারবে না)
- ফি ক্যালকুলেশন: বছর সিলেক্ট না করা পর্যন্ত `৳---` দেখাবে (আগে ভুলভাবে ৳1500 দেখাতো)

### ৪. ট্যাগলাইন
- "Once a Baraibunian, always a Baraibunian" → **"যেখানে স্বপ্নের শুরু, সেখানেই একসাথে"**
- বাংলার জন্য আলাদা স্টাইল (আগের uppercase + wide letter-spacing বাংলা যুক্তাক্ষর ভেঙে দিত)

---

## ফাইল লিস্ট

```
registration/forms.py                              (পরিবর্তিত)
static/css/main.css                                (পরিবর্তিত)
static/img/bss-logo.png                            (নতুন)
static/img/favicon.png                             (নতুন)
static/img/school-campus.jpg                       (নতুন)
static/js/searchable-select.js                     (নতুন)
templates/registration/base.html                   (পরিবর্তিত)
templates/registration/home.html                   (পরিবর্তিত)
templates/registration/register.html               (পরিবর্তিত)
templates/registration/special_funding.html        (পরিবর্তিত)
templates/registration/admin_panel/dashboard.html  (পরিবর্তিত)
templates/registration/admin_panel/detail.html     (পরিবর্তিত)
templates/registration/admin_panel/login.html      (পরিবর্তিত)
```

## টিউন করতে চাইলে

- **ব্যানার কতটা গাঢ়:** `static/css/main.css` → `.hero-photo::before` এর gradient-এর alpha মানগুলো
  (`0.95 / 0.88 / 0.66 / 0.42`)। মান বাড়ালে ছবি আরও চাপা পড়বে, কমালে ছবি স্পষ্ট হবে।
- **ব্যানারের উচ্চতা:** `.hero.has-photo` এর `min-height: min(84vh, 760px)`
- **ছবির কোন অংশ দেখাবে:** `.hero-photo img` এর `object-position: 55% 60%`
- **হেডারে লোগোর সাইজ:** `.brand-mark` এর `height: 52px`
- **বছরের রেঞ্জ:** `registration/forms.py` → `SSC_YEAR_MIN` / `SSC_YEAR_MAX`
