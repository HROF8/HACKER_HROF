import asyncio, json, requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
BOT_TOKEN = "7803560556:AAGVUkCDp0169xM_up3PYpwbQKKoEIP9KWg"
API_KEYS = {
    "cpm1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM",
    "cpm2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}
BASE_URL = "https://www.googleapis.com/identitytoolkit/v3/relyingparty"
SECRET_CODES = ["Telegram:@HACKER_HROF", "8526555112", "25555555", "HROF15223085"]
SIGNATURE = "\n\n👑 @HACKER_HROF"

# --- الترجمات ---
MESSAGES = {
    "ar": {
        "welcome": "\n مرحباً بك في بوت حـــروف الــــمـــوت\n🔒 يرجى إدخال الرمز السري:",
        "invalid_code": "❌ الرمز السري غير صحيح!",
        "code_success": "✅ تم قبول الرمز السري! اختر إصدار اللعبة:",
        "email": "📧 الآن أرسل البريد الإلكتروني:",
        "pass": "🔑 أدخل كلمة المرور:",
        "success": "تم تسجيل الدخول بنجاح! اختر العملية:",
        "change_email": "تغيير البريد",
        "change_pass": "تغيير كلمة السر",
        "new_val": "أدخل القيمة الجديدة:",
        "done": "✅ تم التغيير بنجاح",
        "fail": "❌ لم ينجح التغيير",
        "error": " خطأ في حساب او كلمه السر!"
    },
    "en": {
        "welcome": "\n Welcome to Death Letters Bot\n🔒 Please enter the secret code:",
        "invalid_code": "❌ Invalid secret code!",
        "code_success": "✅ Code accepted! Select game version:",
        "email": "📧 Now send the email:",
        "pass": "🔑 Enter password:",
        "success": "Login successful! Choose action:",
        "change_email": "Change Email",
        "change_pass": "Change Password",
        "new_val": "Enter new value:",
        "done": "✅ Changed successfully",
        "fail": "❌ Failed to change",
        "error": "Account or password error !"
    }
}

def get_msg(context, key):
    lang = context.user_data.get("lang", "ar")
    return MESSAGES.get(lang, MESSAGES["ar"]).get(key, "Error") + SIGNATURE

# --- الوظائف ---
async def start(update, context):
    kb = [[InlineKeyboardButton("العربية", callback_data="lang_ar"), InlineKeyboardButton("English", callback_data="lang_en")]]
    await update.message.reply_text("يرجى اختيار لغتك / Please select your language:" + SIGNATURE, reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update, context):
    q = update.callback_query
    await q.answer()
    
    if q.data.startswith("lang_"):
        context.user_data["lang"] = q.data.split("_")[1]
        context.user_data["step"] = "wait_for_code"
        await q.edit_message_text(get_msg(context, "welcome"))
        
    elif q.data.startswith("ver_"):
        context.user_data["api_key"] = API_KEYS[q.data.split("_")[1]]
        context.user_data["step"] = "email"
        await q.edit_message_text(get_msg(context, "email"))
            
    elif q.data in ["change_email", "change_pass"]:
        context.user_data["action"] = q.data
        context.user_data["step"] = "new_value"
        await q.edit_message_text(get_msg(context, "new_val"))

async def handle_text(update, context):
    text = update.message.text
    step = context.user_data.get("step")
    
    if step == "wait_for_code":
        if text in SECRET_CODES:
            kb = [[InlineKeyboardButton("CPM 1", callback_data="ver_cpm1"), InlineKeyboardButton("CPM 2", callback_data="ver_cpm2")]]
            await update.message.reply_text(get_msg(context, "code_success"), reply_markup=InlineKeyboardMarkup(kb))
            context.user_data["step"] = None
        else:
            await update.message.reply_text(get_msg(context, "invalid_code"))
            
    elif step == "email":
        context.user_data["email"] = text
        context.user_data["step"] = "password"
        await update.message.reply_text(get_msg(context, "pass"))
        
    elif step == "password":
        res = requests.post(f"{BASE_URL}/verifyPassword?key={context.user_data['api_key']}", 
                            json={"email": context.user_data["email"], "password": text, "returnSecureToken": True}).json()
        if "idToken" in res:
            context.user_data.update({"idToken": res["idToken"]})
            kb = [[InlineKeyboardButton(MESSAGES[context.user_data["lang"]]["change_email"], callback_data="change_email")],
                  [InlineKeyboardButton(MESSAGES[context.user_data["lang"]]["change_pass"], callback_data="change_pass")]]
            await update.message.reply_text(get_msg(context, "success"), reply_markup=InlineKeyboardMarkup(kb))
        else:
            await update.message.reply_text(get_msg(context, "error"))
        context.user_data["step"] = None

    elif step == "new_value":
        payload = {"idToken": context.user_data["idToken"], ("email" if context.user_data["action"] == "change_email" else "password"): text}
        res = requests.post(f"{BASE_URL}/setAccountInfo?key={context.user_data['api_key']}", json=payload).json()
        await update.message.reply_text(get_msg(context, "done") if "localId" in res else get_msg(context, "fail"))
        context.user_data["step"] = None

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
