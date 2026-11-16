import telebot
import requests
import schedule
import time
import threading

# ۱. توکن ربات خودت رو اینجا بذار
TOKEN = "9195172603:AAEe1QMvLKJU_Ihc_REzHm3O6PjeQn1YYaM" 
bot = telebot.TeleBot(TOKEN)

# متغیری برای ذخیره آیدی چت
CHAT_ID = None

# تابعی که آگهی‌ها رو از جاب‌ویژن می‌گیره
def fetch_jobs():
    url = "https://candidateapi.jobvision.ir/api/v1/JobPost/List"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://jobvision.ir",
        "Referer": "https://jobvision.ir/",
        "clientId": "65305799",
        "Page-Route": "https://jobvision.ir/jobs/keyword/python",
        "ngsw-bypass": "true"
    }
    
    payload = {"keyword": "python", "page": 1, "pageSize": 5}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            jobs = response.json()['data']['jobPosts']
            msg = "📋 ۵ آگهی جدید پایتون (گزارش خودکار):\n\n"
            for i, job in enumerate(jobs, 1):
                title = job.get('title', 'بدون عنوان')
                company_data = job.get('company', {})
                company = company_data.get('nameFa', 'نامشخص') if company_data else 'نامشخص'
                location = job.get('location', {})
                city_data = location.get('city', {})
                city = city_data.get('titleFa', 'نامشخص') if city_data else 'نامشخص'
                region_data = location.get('region', {})
                region = region_data.get('titleFa', '') if region_data else ''
                
                msg += f"{i}. {title}\n"
                msg += f"🏢 شرکت: {company}\n"
                msg += f"📍 موقعیت: {city} {('، ' + region) if region else ''}\n"
                msg += f"🔗 https://jobvision.ir/jobs/{job.get('id')}\n\n"
            return msg
        else:
            return "خطا در دریافت اطلاعات."
    except Exception as e:
        return f"خطای غیرمنتظره: {e}"

# دستور start: ذخیره آیدی و راهنمایی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global CHAT_ID
    CHAT_ID = str(message.chat.id) # ذخیره آیدی چت
    print(f"✅ CHAT_ID ذخیره شد: {CHAT_ID}")
    bot.reply_to(message, "سلام! آیدی شما ذخیره شد. من هر روز ساعت ۹ صبح آگهی‌های جدید پایتون رو براتون می‌فرستم.")

# دستور دستی برای گرفتن آگهی‌ها
@bot.message_handler(commands=['jobs'])
def get_jobs(message):
    bot.reply_to(message, "دارم آگهی‌های جدید رو می‌گیرم...")
    msg = fetch_jobs()
    bot.reply_to(message, msg)

# تابعی که پیام خودکار می‌فرسته
def send_daily_report():
    global CHAT_ID
    if CHAT_ID is None:
        print("⚠️ هنوز کسی به ربات /start نداده است.")
        return
    
    print("در حال ارسال گزارش خودکار...")
    msg = fetch_jobs()
    try:
        bot.send_message(CHAT_ID, msg)
        print("✅ پیام خودکار با موفقیت ارسال شد.")
    except Exception as e:
        print(f"❌ خطا در ارسال پیام خودکار: {e}")

# ۲. زمان‌بندی: هر روز ساعت ۹ صبح
schedule.every().day.at("09:00").do(send_daily_report)

# حلقه اجرای زمان‌بندی در پس‌زمینه
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# اجرای زمان‌بندی در یک ترد جداگانه
threading.Thread(target=run_schedule, daemon=True).start()

print("Bot is running... (Daily report scheduled at 09:00)")
bot.infinity_polling()