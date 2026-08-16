# BSS Reunion — Update Package

এই zip-এ শুধু **পরিবর্তিত ও নতুন ফাইলগুলো** আছে। আপনার `.env`, `db.sqlite3`,
`migrations/`, `media/` — এগুলো এখানে নেই, তাই কিছু হারানোর ভয় নেই।

## কীভাবে অ্যাপ্লাই করবেন (PowerShell)

```powershell
# 1) প্রজেক্ট ফোল্ডারে যান
cd D:\bssreunion\bssreunion

# 2) (রেকমেন্ডেড) আগে ব্যাকআপ / git commit করে নিন
git add -A ; git commit -m "before update"

# 3) zip টা প্রজেক্ট রুটে এক্সট্র্যাক্ট করুন (ফাইলগুলো ওভাররাইট হবে)
Expand-Archive -Path "D:\Download chrome\bssreunion-update.zip" -DestinationPath "$env:TEMP\bssupd" -Force
Copy-Item -Path "$env:TEMP\bssupd\bssreunion-update\*" -Destination . -Recurse -Force

# 4) নতুন প্যাকেজ ইনস্টল করুন  ← এবার এই ধাপটা লাগবেই
pip install -r requirements.txt

# 5) সার্ভার চালান
python manage.py runserver
```

ব্রাউজারে **Ctrl + F5** দিয়ে hard refresh করুন।

> **নতুন dependency:** Excel ডাউনলোডের জন্য `openpyxl` লেগেছে, সেটা
> `requirements.txt`-এ যোগ করা আছে। ধাপ ৪ বাদ দিলে ডাউনলোড বাটনে ক্লিক করলে
> "openpyxl দরকার" মেসেজ দেখাবে (সাইট ক্র্যাশ করবে না)।
>
> **কোনো নতুন migration লাগবে না** — ডেটাবেজ মডেলে কিছু বদলায়নি।

প্রোডাকশনে ডিপ্লয়ের আগে: `python manage.py collectstatic --noinput`

---

## এই আপডেটে কী কী বদলেছে

### ১. হোম পেজের ট্যাগলাইন
- ট্যাগলাইনের সাইজ বড় করা হয়েছে (আগের চেয়ে প্রায় ৪০% বড়)
- ডান পাশে দ্বিতীয় ট্যাগলাইন যোগ: **"আবার ফিরি প্রিয় বিদ্যালয়ে"**
- দুটো পাশাপাশি বসে; মোবাইলে জায়গা না হলে নিচে নেমে যায়
- দ্বিতীয়টা একটু হালকা স্টাইলে, যাতে দুটো একসাথে জোড়া হিসেবে পড়া যায় — একটা আরেকটার সাথে প্রতিযোগিতা না করে

### ২. লোকেশন (সব জায়গায়)
নতুন ঠিকানা: **Vill: Baraibunia, Post: Tarabunia, P.S.: Nazirpur, Dist: Pirojpur**

এটা এখন `settings.py`-তে **একটা জায়গায়** (`EVENT_LOCATION`) আছে, আর সেখান থেকেই
সব জায়গায় যাচ্ছে — হোম পেজের হিরো, Location কার্ড, টিকিট পেজ, টিকিট ইমেইল,
আর PDF টিকিট। ভবিষ্যতে ঠিকানা বদলাতে চাইলে শুধু ওই এক লাইন বদলালেই হবে।

### ৩. তারিখ ও রেজিস্ট্রেশন উইন্ডো
- "To be announced" → **December 25 and 26** (`settings.py` → `EVENT_DATE_TEXT`)
- Registration window → **August - October 2026** (`settings.py` → `REGISTRATION_WINDOW_TEXT`)

### ৪. হিরোর লেখা
"...is happening **once more**" → "...is happening **for the first time**"

### ৫. Sovereign → Souvenir
টিকিট বেনিফিটের নাম সব জায়গায় বদলেছে — হোম পেজ, টিকিট পেজ, টিকিট ইমেইল, PDF টিকিট।

### ৬. Blood Group ড্রপডাউন
টেক্সট বক্সের বদলে এখন ড্রপডাউন: A+, A−, B+, B−, AB+, AB−, O+, O−
(অপশনাল, তাই খালি রাখা যাবে)। সার্ভার সাইডেও ভ্যালিডেশন আছে।

### ৭. অ্যাডমিন ড্যাশবোর্ড
- **SSC Batch ফিল্টার** যোগ হয়েছে (টাইপ করে সার্চ করা যায়), Status ফিল্টারের পাশে
- **Reset** বাটন — সব ফিল্টার একবারে ক্লিয়ার
- ফিল্টার চালু থাকলে উপরে ট্যাগ আকারে দেখায় কোন কোন ফিল্টার লেগে আছে ও কয়টা ম্যাচ করেছে
- **⤓ Download Excel** বাটন:
  - ফিল্টার দেওয়া থাকলে শুধু ফিল্টার করা লিস্ট নামবে (বাটনে "(filtered)" লেখা দেখাবে)
  - ফিল্টার না দিলে পুরো লিস্ট নামবে
  - স্ক্রিনে যা দেখছেন, ঠিক তা-ই নামবে — এক্সপোর্ট আর ড্যাশবোর্ড একই ফিল্টার লজিক ব্যবহার করে
- **পেজিনেশন** এখন অনেক পরিষ্কার: "Showing 1–20 of 55", First / Prev / পেজ নম্বর / Next / Last

  > একটা বাগও ঠিক হয়েছে: আগে পেজ ২-তে গেলে ফিল্টার হারিয়ে যেত (লিংকে শুধু `?page=2`
  > থাকত)। এখন ফিল্টার সব পেজে ধরে রাখে।

### ৮. Excel ফরম্যাট
- টাইটেল রো + কোন ফিল্টার লেগেছে, কয়টা রেকর্ড, কখন জেনারেট হয়েছে
- নেভি হেডার, সাদা বোল্ড লেখা; এক লাইন পরপর হালকা ব্যান্ডিং
- Payment Status রঙে আলাদা (Paid সবুজ, Pending হলুদ, Failed লাল, Cancelled ধূসর)
- Freeze panes (হেডার + প্রথম ৩ কলাম আটকানো), AutoFilter, ঠিকঠাক কলাম width
- নিচে Amount-এর TOTAL (এক্সেল ফর্মুলা, তাই ফিল্টার করলেও ঠিক থাকে)
- ২০টা কলাম — ফোন, WhatsApp, ইমেইল, ব্যাচ, ব্লাড গ্রুপ, টি-শার্ট সাইজ, ঠিকানা,
  ট্রানজেকশন আইডি, চেক-ইন সহ সব তথ্য
- ল্যান্ডস্কেপ প্রিন্ট সেটআপ, প্রতি পেজে হেডার রিপিট — গেটে প্রিন্ট করে নিলে কাজে লাগবে

---

## আগের আপডেটগুলোও এই zip-এ আছে

- **নতুন লোগো** (transparent PNG) + ফেভিকন, সব পেজ ও অ্যাডমিন প্যানেলে
- **হোম পেজের ব্যানার** — স্কুলের ছবি হিরোর ব্যাকগ্রাউন্ডে, লেখা তার উপরে,
  বাঁ দিকে navy wash যাতে লেখা পরিষ্কার থাকে
- **SSC Batch / Passing Year** — ১৯৬৩–২০৩২ সার্চ করা যায় এমন ড্রপডাউন
- ফি ক্যালকুলেশন: বছর সিলেক্ট না করা পর্যন্ত `৳---`

---

## টিউন করতে চাইলে

| কী | কোথায় |
|---|---|
| ঠিকানা | `bssreunion/settings.py` → `EVENT_LOCATION` |
| ইভেন্টের তারিখ | `bssreunion/settings.py` → `EVENT_DATE_TEXT` |
| রেজিস্ট্রেশন উইন্ডো | `bssreunion/settings.py` → `REGISTRATION_WINDOW_TEXT` |
| ট্যাগলাইনের লেখা | `templates/registration/home.html` → `.tagline-row` |
| ট্যাগলাইনের সাইজ | `static/css/main.css` → `.hero .eyebrow.eyebrow-bn` এর `font-size` |
| ব্যানার কতটা গাঢ় | `static/css/main.css` → `.hero-photo::before` এর alpha মান |
| ব্যানারের উচ্চতা | `static/css/main.css` → `.hero.has-photo` এর `min-height` |
| প্রতি পেজে কয়টা রো | `registration/views.py` → `Paginator(qs..., 20)` |
| Excel-এর কলাম | `registration/export_utils.py` → `COLUMNS` লিস্ট |
| ব্লাড গ্রুপের অপশন | `registration/forms.py` → `BLOOD_GROUP_CHOICES` |
| বছরের রেঞ্জ | `registration/forms.py` → `SSC_YEAR_MIN` / `SSC_YEAR_MAX` |

---

## ফাইল লিস্ট

```
requirements.txt                                   (পরিবর্তিত — openpyxl যোগ)
bssreunion/settings.py                             (পরিবর্তিত)
registration/context_processors.py                 (পরিবর্তিত)
registration/export_utils.py                       (নতুন — Excel জেনারেটর)
registration/forms.py                              (পরিবর্তিত)
registration/ticket_utils.py                       (পরিবর্তিত)
registration/urls.py                               (পরিবর্তিত)
registration/views.py                              (পরিবর্তিত)
static/css/main.css                                (পরিবর্তিত)
static/img/bss-logo.png                            (নতুন)
static/img/favicon.png                             (নতুন)
static/img/school-campus.jpg                       (নতুন)
static/js/searchable-select.js                     (নতুন)
templates/registration/base.html                   (পরিবর্তিত)
templates/registration/home.html                   (পরিবর্তিত)
templates/registration/register.html               (পরিবর্তিত)
templates/registration/special_funding.html        (পরিবর্তিত)
templates/registration/ticket_view.html            (পরিবর্তিত)
templates/registration/email/ticket_email.html     (পরিবর্তিত)
templates/registration/admin_panel/dashboard.html  (পরিবর্তিত)
templates/registration/admin_panel/detail.html     (পরিবর্তিত)
templates/registration/admin_panel/login.html      (পরিবর্তিত)
```
