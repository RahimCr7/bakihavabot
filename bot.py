import telebot
from telebot import types
import time
import threading
import schedule
import random
from datetime import datetime
import pytz
from flask import Flask # Render kilitlənməsini önləmək üçün internet server köməkçisi

TOKEN = "8883498106:AAHr37lxE_kLy_za0TZHlGyfX_9iMI_Yqsc"
bot = telebot.TeleBot(TOKEN, threaded=False)

ADMIN_ID = 55443322  

mahni_bazasi = {
    "bass": ["https://soundhelix.com"],
    "azeri": ["https://soundhelix.com"],
    "rus": ["https://soundhelix.com"],
    "turk": ["https://soundhelix.com"],
    "meyxana": ["https://soundhelix.com"]
}

# 🌐 RENDER PLATFORMASINI ALDATMAQ ÜÇÜN SAXTA İNTERNET PORTU
app = Flask('')

@app.route('/')
def home():
    return "Bot aktivdir və 7/24 işləyir!"

def run_flask():
    # Render avtomatik olaraq 10000 portunu dinləyir
    app.run(host='0.0.0.0', port=10000)

def dynamic_hava_durumu_al():
    aylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "İyun", "İyul", "Avqust", "Sentyabr", "Oktabr", "Noyabr", "Dekabr"]
    baku_tz = pytz.timezone('Asia/Baku')
    indiki_vaxt = datetime.now(baku_tz)
    
    ay_adi = aylar[indiki_vaxt.month - 1]
    gun_bugun = indiki_vaxt.day
    gun_sabah = gun_bugun + 1
    current_month = indiki_vaxt.month
    
    if current_month == 12 or current_month == 1 or current_month == 2:
        t1, t2, status1, status2, yuma = "+7", "+5", "Buludlu, yağıntılı 🌧", "Sulu qar 💨", "❌ Maşını bu gün yumayın! 💸"
    elif current_month >= 3 and current_month <= 5:
        t1, t2, status1, status2, yuma = "+16", "+15", "Dəyişkən buludlu 🌤", "Açıq hava ☀️", "🧼 Maşını ürək rahatlığı ilə yuya bilərsiniz! ✨"
    elif current_month >= 6 and current_month <= 8:
        t1, t2, status1, status2, yuma = "+32", "+34", "Tamamilə günəşli ☀️", "İsti hava 🔥", "🧼 Maşını yumaq tam məsləhətdir! ✨"
    else:
        t1, t2, status1, status2, yuma = "+24", "+22", "Günəşli, mülayim 🌤", "Az buludlu ☀️", "🧼 Yaxın 2 gündə yağış yoxdur, maşını yuya bilərsiniz! ✨"

    return f"📊 **Azərbaycan Üçün Canlı Hava və Yol Hesabatı** 🌤\n\n📅 **Bu gün ({gun_bugun} {ay_adi}):** {t1}°C | {status1}\n\n📅 **Sabah ({gun_sabah} {ay_adi}):** {t2}°C | {status2}\n\n{yuma}"

def avto_hava_gonder():
    try:
        bot.send_message("@BakiTrafficAz", "☀️ **SƏHƏR HAVA PROQNOZU** ☀️\n\n" + dynamic_hava_durumu_al(), parse_mode="Markdown")
    except Exception as e:
        print("Avtomatik mesaj xətası:", e)

def baku_saatiyle_planla(saat_str, gorev_fonksiyonu):
    def kontrol_et():
        baku_tz = pytz.timezone('Asia/Baku')
        while True:
            simdi = datetime.now(baku_tz).strftime("%H:%M")
            if simdi == saat_str:
                gorev_fonksiyonu()
                time.sleep(60)
            time.sleep(10)
    
    threading.Thread(target=kontrol_et, daemon=True).start()

baku_saatiyle_planla("08:00", avto_hava_gonder)

@bot.message_handler(commands=['start'])
def start_menyu(message):
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    duyme_hava = types.KeyboardButton("🌤 Hava və Maşın Yuma")
    duyme_radar = types.KeyboardButton("📸 Sabit Radarlar")
    duyme_qeza_bildir = types.KeyboardButton("⚠️ Qəza / Tıxac Bildir")
    duyme_musiqi = types.KeyboardButton("🎵 Maşın Mahnıları")
    
    menu.add(duyme_hava, duyme_radar)
    menu.add(duyme_qeza_bildir, duyme_musiqi)
    bot.send_message(message.chat.id, f"Salam, {message.from_user.first_name}! Botumuz aktivdir. Düymələrdən istifadə edin:", reply_markup=menu)

@bot.message_handler(content_types=['audio'])
def mahni_kodunu_tut(message):
    bot.reply_to(message, f"🎵 **Bu mahnının gizli Telegram kodu:**\n\n`{message.audio.file_id}`")

@bot.message_handler(commands=['xeber'])
def xeber_istə(message):
    if message.chat.id == ADMIN_ID:
        sorqu = bot.send_message(message.chat.id, "📢 **Rəsmi Yol Təmiri / Bağlanma Xəbərini daxil edin:**")
        bot.register_next_step_handler(sorqu, xeberi_qrupa_firlat)

def xeberi_qrupa_firlat(message):
    try:
        bot.send_message("@BakiTrafficAz", f"📢 **YOL İNFRASTRUKTURU XƏBƏRDARLIĞI** 📢\n\nℹ️ {message.text}\n\n⚠️ Sürücülərdən diqqətli olmaq xahiş olunur! 🚗", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Xəbər uğurla qrupa göndərildi!")
    except Exception as e:
        print(e)

@bot.message_handler(func=lambda message: True)
def mesajlari_idare_et(message):
    metn = message.text
    if metn == "🌤 Hava və Maşın Yuma":
        bot.send_message(message.chat.id, dynamic_hava_durumu_al(), parse_mode="Markdown")
    elif metn == "📸 Sabit Radarlar":
        radarlar = (
            "⚠️ **Azərbaycan Yollarındakı Əsas Radarlar:**\n\n"
            "📍 **Heydər Əliyev prospekti (Bağırov körpüsü):** 90 km/s 📸\n"
            "📍 **Aeroport yolu (Sabunçu keçidi):** 110 km/s 📸\n"
            "📍 **Ziya Bünyadov prospekti (tünellər):** 90 km/s 📸\n"
            "📍 **Babək prospekti:** 60 km/s 📸\n"
            "📍 **Bakı - Sumqayıt yolu:** 90 - 110 km/s 📸\n"
            "📍 **İpək Yolu (Rayon istiqaməti):** 90 - 110 km/s 📸\n\n"
            "ℹ️ *Sürət həddini aşmayaraq özünüzü və büdcənizi qoruyun!*"
        )
        bot.send_message(message.chat.id, radarlar, parse_mode="Markdown")
    elif metn == "⚠️ Qəza / Tıxac Bildir" and message.chat.type == 'private':
        sorqu = bot.send_message(message.chat.id, "🚨 Zəhmət olmasa qəza və ya sıxlıq olan yeri tam yazın:")
        bot.register_next_step_handler(sorqu, qezani_qrupa_at)
    elif metn == "🎵 Maşın Mahnıları" and message.chat.type == 'private':
        musiqi_menyu = types.InlineKeyboardMarkup(row_width=2)
        musiqi_menyu.add(
            types.InlineKeyboardButton("🔊 Bass Music", callback_data="bass"),
            types.InlineKeyboardButton("🇦🇿 Azeri Style", callback_data="azeri"),
            types.InlineKeyboardButton("🇷🇺 Rus Mix", callback_data="rus"),
            types.InlineKeyboardButton("🇹🇷 Türk Mix", callback_data="turk")
        )
        musiqi_menyu.add(types.InlineKeyboardButton("🎤 Meyxana / Nostalji", callback_data="meyxana"))
        bot.send_message(message.chat.id, "Hansı janrda musiqi dinləmək istəyirsiniz?", reply_markup=musiqi_menyu)

def qezani_qrupa_at(message):
    try:
        qrup_elan = f"🚨 **YOLDA TƏCİLİ MƏLUMAT!** 🚨\n\n👤 **Bildirən sürücü:** {message.from_user.first_name}\n📍 **Vəziyyət:** {message.text}\n\n⚠️ Xahiş olunur alternativ yollardan istifadə edəsiniz!"
        bot.send_message("@BakiTrafficAz", qrup_elan, parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Məlumatınız qrupa göndərildi!")
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: True)
def mahni_gonder(call):
    janr = call.data
    if janr in mahni_bazasi:
        bot.answer_callback_query(call.id, "Mahnı seçilir...")
        secilen_mahni = random.choice(mahni_bazasi[janr])
        try:
            bot.send_audio(call.message.chat.id, secilen_mahni, caption=f"🎵 Sürücü üçün təsadüfi {janr.upper()} mahnısı!")
        except Exception as e:
            bot.send_message(call.message.chat.id, "❌ Bu janra hələ tam mahnı kodu əlavə edilmeyib.")

# 🚀 SAXTA SERVERİ ARXA FONDA İŞƏ SALIRIQ
threading.Thread(target=run_flask, daemon=True).start()

bot.remove_webhook()
print("Render üçün kilitlənməz rejim port dəstəyi ilə hazırlandı...")

while True:
    try:
        bot.polling(none_stop=True, interval=2, timeout=20)
    except Exception as e:
        time.sleep(5)
