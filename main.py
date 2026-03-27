import asyncio, threading, os
from flask import Flask, jsonify
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, VideoPiped, HighQualityAudio, HighQualityVideo

API_ID    = int(os.environ.get("25326160","0"))
API_HASH  = os.environ.get("ef5debe0996ef03ed9357225ccda478a","")
BOT_TOKEN = os.environ.get("6050076233:AAHTfZpIWvzuQfZWA20uBSqYQpzvI1ozoyU","")
GROUP_ID  = int(os.environ.get("-1001919117846","0"))

STREAM   = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
IS_LIVE  = False

flask_app = Flask(__name__)

@flask_app.route("/")
def home(): return jsonify({"status":"running","live":IS_LIVE})

@flask_app.route("/health")
def health(): return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False)

user_client = Client("session", api_id=API_ID, api_hash=API_HASH)
tgcalls     = PyTgCalls(user_client)
bot         = Client("bot_s", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("livevideo") & filters.private)
async def cmd_livevideo(c, m: Message):
    global IS_LIVE
    IS_LIVE = True
    await m.reply("Starting LIVE stream...")
    try:
        await tgcalls.join_group_call(
            GROUP_ID,
            AudioPiped(STREAM, HighQualityAudio()),
            video=VideoPiped(STREAM, HighQualityVideo()),
        )
        await m.reply("LIVE ho gaya!
Group mein LIVE badge dikhega!
/stop se band karo.")
    except Exception as e:
        IS_LIVE = False
        await m.reply("Error: "+str(e))

@bot.on_message(filters.command("stop") & filters.private)
async def cmd_stop(c, m: Message):
    global IS_LIVE
    try:
        await tgcalls.leave_group_call(GROUP_ID)
        IS_LIVE = False
        await m.reply("Stream band ho gaya.")
    except Exception as e:
        await m.reply("Error: "+str(e))

@bot.on_message(filters.command("status") & filters.private)
async def cmd_status(c, m: Message):
    await m.reply("LIVE: "+str(IS_LIVE))

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    await user_client.start()
    await tgcalls.start()
    await bot.start()
    me = await bot.get_me()
    print("Bot ready: @"+(me.username or "bot"))
    await asyncio.Event().wait()

if __name__=="__main__":
    asyncio.run(main())
