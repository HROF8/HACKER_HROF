import asyncio, json, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest, Forbidden
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
BOT_TOKEN = "7803560556:AAG3TYXAYks6WBCxcc7q03o4_QSN7i0Vbck"
API_KEY = "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM"
BASE_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty"

# --- قاموس الترجمة المحدث ---
LANGS = {
    "ar": {"start": "👑 أهلاً بك في بوت 'حروف الموت' - أبو علي 👑\nاستخدم /login لبدء الإدارة / المالك @HACKER_HROF.", "email": "أدخل البريد الإلكتروني:", "pass": "أدخل كلمة المرور:", "success": "تم تسجيل الدخول بنجاح! اختر العملية:", "change_email": "تغيير البريد", "change_pass": "تغيير كلمة السر", "new_val": "أدخل القيمة الجديدة:", "done": "✅ تم التغيير بنجاح", "fail": "❌ لم ينجح التغيير", "error": "خطأ في البيانات!"},
    "en": {"start": "👑 Welcome to 'Death Letters' bot - Abu Ali 👑\nUse /login to start management / Owner @HACKER_HROF.", "email": "Enter email:", "pass": "Enter password:", "success": "Login successful! Choose action:", "change_email": "Change Email", "change_pass": "Change Password", "new_val": "Enter new value:", "done": "✅ Changed successfully", "fail": "❌ Failed to change", "error": "Data error!"},
    "tr": {"start": "👑 'Ölüm Harfleri' botuna hoş geldiniz - Abu Ali 👑\nYönetimi başlatmak için /login kullanın / Sahibi @HACKER_HROF.", "email": "E-posta girin:", "pass": "Şifre girin:", "success": "Giriş başarılı! İşlem seçin:", "change_email": "E-postayı Değiştir", "change_pass": "Şifreyi Değiştir", "new_val": "Yeni değeri girin:", "done": "✅ Başarıyla değiştirildi", "fail": "❌ Değiştirilemedi", "error": "Veri hatası!"},
    "ja": {"start": "👑 '死の文字'ボットへようこそ - Abu Ali 👑\n管理を開始するには /login を使用してください / オーナー @HACKER_HROF。", "email": "メールアドレスを入力:", "pass": "パスワードを入力:", "success": "ログイン成功！操作を選択:", "change_email": "メールを変更", "change_pass": "パスワードを変更", "new_val": "新しい値を入力:", "done": "✅ 正常に変更されました", "fail": "❌ 変更に失敗しました", "error": "データエラー!"},
    "ko": {"start": "👑 '죽음의 글자' 봇에 오신 것을 환영합니다 - Abu Ali 👑\n관리를 시작하려면 /login을 사용하세요 / 소유자 @HACKER_HROF.", "email": "이메일 입력:", "pass": "비밀번호 입력:", "success": "로그인 성공! 작업 선택:", "change_email": "이메일 변경", "change_pass": "비밀번호 변경", "new_val": "새 값 입력:", "done": "✅ 성공적으로 변경됨", "fail": "❌ 변경 실패", "error": "데이터 오류!"},
    "hi": {"start": "👑 'Death Letters' बॉट में आपका स्वागत है - Abu Ali 👑\nप्रबंधन शुरू करने के लिए /login का उपयोग करें / मालिक @HACKER_HROF।", "email": "ईमेल दर्ज करें:", "pass": "पासवर्ड दर्ज करें:", "success": "लॉगिन सफल! कार्रवाई चुनें:", "change_email": "ईमेल बदलें", "change_pass": "पासवर्ड बदलें", "new_val": "नया मान दर्ज करें:", "done": "✅ सफलतापूर्वक बदल दिया गया", "fail": "❌ बदलने में विफल", "error": "डेटा त्रुटि!"},
    "ur": {"start": "👑 'Death Letters' بوٹ میں خوش آمدید - ابو علی 👑\nانتظام شروع کرنے کے لیے /login استعمال کریں / مالک @HACKER_HROF۔", "email": "ای میل درج کریں:", "pass": "پاس ورڈ درج کریں:", "success": "لاگ ان کامیاب! عمل منتخب کریں:", "change_email": "ای میل تبدیل کریں", "change_pass": "پاس ورڈ تبدیل کریں", "new_val": "نئی قدر درج کریں:", "done": "✅ کامیابی کے ساتھ تبدیل کر دیا گیا", "fail": "❌ تبدیل کرنے میں ناکامی", "error": "ڈیٹا کی غلطی!"},
    "ru": {"start": "👑 Добро пожаловать в бот 'Письма смерти' - Abu Ali 👑\nИспользуйте /login для начала управления / Владелец @HACKER_HROF.", "email": "Введите email:", "pass": "Введите пароль:", "success": "Вход выполнен! Выберите действие:", "change_email": "Изменить email", "change_pass": "Изменить пароль", "new_val": "Введите новое значение:", "done": "✅ Успешно изменено", "fail": "❌ Ошибка изменения", "error": "Ошибка данных!"},
    "fa": {"start": "👑 به ربات 'نامه های مرگ' خوش آمدید - ابوعلی 👑\nبرای شروع مدیریت از /login استفاده کنید / مالک @HACKER_HROF.", "email": "ایمیل را وارد کنید:", "pass": "رمز عبور را وارد کنید:", "success": "ورود موفق! عملیات را انتخاب کنید:", "change_email": "تغییر ایمیل", "change_pass": "تغییر رمز عبور", "new_val": "مقدار جدید را وارد کنید:", "done": "✅ با موفقیت تغییر کرد", "fail": "❌ تغییر ناموفق بود", "error": "خطای داده!"},
    "id": {"start": "👑 Selamat datang di bot 'Surat Kematian' - Abu Ali 👑\nGunakan /login untuk memulai manajemen / Pemilik @HACKER_HROF.", "email": "Masukkan email:", "pass": "Masukkan kata sandi:", "success": "Login berhasil! Pilih tindakan:", "change_email": "Ubah Email", "change_pass": "Ubah Kata Sandi", "new_val": "Masukkan nilai baru:", "done": "✅ Berhasil diubah", "fail": "❌ Gagal diubah", "error": "Kesalahan data!"}
}

# --- الوظائف ---
def firebase_request(endpoint, payload):
    url = f"{BASE_URL}/{endpoint}?key={API_KEY}"
    return requests.post(url, json=payload).json()

def get_text(context, key):
    lang = context.user_data.get("lang", "ar")
    return LANGS.get(lang, LANGS["ar"]).get(key, "Error")

async def start(update, context):
    kb = [
        [InlineKeyboardButton("العربية", callback_data="lang_ar"), InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Türkçe", callback_data="lang_tr"), InlineKeyboardButton("日本語", callback_data="lang_ja")],
        [InlineKeyboardButton("한국어", callback_data="lang_ko"), InlineKeyboardButton("हिन्दी", callback_data="lang_hi")],
        [InlineKeyboardButton("اردو", callback_data="lang_ur"), InlineKeyboardButton("Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("فارسی", callback_data="lang_fa"), InlineKeyboardButton("Indonesia", callback_data="lang_id")]
    ]
    await update.message.reply_text("يرجى اختيار لغتك / Please select your language:", reply_markup=InlineKeyboardMarkup(kb))

async def login_start(update, context):
    context.user_data["step"] = "email"
    await update.message.reply_text(get_text(context, "email"))

async def button_handler(update, context):
    q = update.callback_query
    try: await q.answer()
    except: pass
    
    try:
        if q.data.startswith("lang_"):
            context.user_data["lang"] = q.data.split("_")[1]
            await q.edit_message_text(get_text(context, "start"))
        elif q.data in ["change_email", "change_pass"]:
            context.user_data["action"] = q.data
            context.user_data["step"] = "new_value"
            await q.edit_message_text(get_text(context, "new_val"))
    except Exception as e:
        print(f"Error: {e}")

async def handle_text(update, context):
    step = context.user_data.get("step")
    if step == "email":
        context.user_data["email"] = update.message.text
        context.user_data["step"] = "password"
        await update.message.reply_text(get_text(context, "pass"))
    elif step == "password":
        res = firebase_request("verifyPassword", {"email": context.user_data["email"], "password": update.message.text, "returnSecureToken": True})
        if "idToken" in res:
            context.user_data.update({"idToken": res["idToken"], "localId": res["localId"]})
            kb = [[InlineKeyboardButton(get_text(context, "change_email"), callback_data="change_email")],
                  [InlineKeyboardButton(get_text(context, "change_pass"), callback_data="change_pass")]]
            await update.message.reply_text(get_text(context, "success"), reply_markup=InlineKeyboardMarkup(kb))
        else:
            await update.message.reply_text(get_text(context, "error"))
        context.user_data["step"] = None
    elif step == "new_value":
        payload = {"idToken": context.user_data["idToken"], ("email" if context.user_data["action"] == "change_email" else "password"): update.message.text}
        res = firebase_request("setAccountInfo", payload)
        await update.message.reply_text(get_text(context, "done") if "localId" in res else get_text(context, "fail"))
        context.user_data["step"] = None

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login_start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()
