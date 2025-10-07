import os
import telebot
import openai
import base64
from dotenv import load_dotenv

# --- 1. تحميل الإعدادات ومفاتيح الـ API ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("الرجاء التأكد من وضع مفاتيح API في ملف .env")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- 2. نص الأمر التحليلي ---
# --- 2. نص الأمر التحليلي (نسخة محسنة للخيارات الثنائية) ---
# --- 2. نص الأمر التحليلي (نسخة مطورة لدمج المؤشرات) ---
PROMPT_TEXT = """
أنت محلل فني خبير ومهمتك هي إصدار إشارات دقيقة لتداول الخيارات الثنائية على إطار زمني 5 دقائق.

**عملية التحليل (اتبع هذه الخطوات بالترتيب):**

**الخطوة 1: تحليل المؤشرات الفنية (الأولوية القصوى)**
- ابحث بتركيز في الصورة عن أي مؤشرات فنية (مثل RSI, MACD, Stochastic, Bollinger Bands, Moving Averages).
- حلل حالة كل مؤشر. هل هو في منطقة تشبع بيع (Oversold)؟ أم تشبع شراء (Overbought)؟ هل هناك تقاطع (Cross)؟ هل هناك تباعد (Divergence) بين المؤشر والسعر؟

**الخطوة 2: تحليل حركة السعر (لتأكيد إشارة المؤشرات)**
- حلل الشموع اليابانية الأخيرة. هل هناك نماذج انعكاسية (مثل شمعة ابتلاعية، مطرقة) أو استمرارية؟
- حدد أقرب مستويات دعم ومقاومة قوية.
اعتمد على مناطق الدعم والمقاومة الدخلية
**الخطوة 3: إصدار التوصية النهائية**
- ادمج نتائج الخطوتين 1 و 2. يجب أن تكون التوصية النهائية مدعومة بقوة من المؤشرات وحركة السعر معًا.
- إذا كانت المؤشرات وحركة السعر متعارضتين، اذكر ذلك وقلل من قوة الإشارة.

**تنسيق الرد المطلوب (مهم جدًا وموجز):**

**الصفقة:** [صعود (CALL) أو هبوط (PUT)]
**قوة الإشارة:** [تقييم من 1 إلى 10، حيث 10 هي الأقوى والأكثر تأكيدًا]
ولا تذكر سبب الاشارة او تحليل الذي استنتجته
"""


# --- 3. معالج الرسائل التي تحتوي على صور ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "لقد استلمت الصورة، جاري تحليلها... 🤖")

        # تنزيل الصورة
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # تحويل الصورة إلى Base64
        base64_image = base64.b64encode(downloaded_file).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{base64_image}"

        print("กำลังส่ง الطلب إلى OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT_TEXT},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1000
        )
        print("تم استلام الرد من OpenAI.")

        # إرسال الرد للمستخدم
        analysis_result = response.choices[0].message.content
        bot.reply_to(message, analysis_result)

    except Exception as e:
        print(f"حدث خطأ: {e}")
        bot.reply_to(message, "عذرًا، حدث خطأ ما أثناء تحليل الصورة. الرجاء المحاولة مرة أخرى.")

# --- 4. تشغيل البوت ---
print("البوت قيد التشغيل الآن...")
bot.polling()
