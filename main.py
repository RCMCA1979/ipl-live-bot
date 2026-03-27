# ================================================================
#   IPL LIVE STREAM BOT â€” PyTgCalls
#   Group mein LIVE badge + Join button + TV player
#   Deploy: Render (Linux) ya Termux
#   Install: pyrogram, pytgcalls, python-telegram-bot, flask
# ================================================================

import asyncio
import threading
import os
import json
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, MediaStreamType
from pytgcalls.types.stream import AudioQuality, VideoQuality

from flask import Flask, jsonify

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#   APNI DETAILS YAHAN BHARO
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
API_ID    = 25326160               # my.telegram.org se lo
API_HASH  = "ef5debe0996ef03ed9357225ccda478a"   # my.telegram.org se lo
BOT_TOKEN = "6050076233:AAHTfZpIWvzuQfZWA20uBSqYQpzvI1ozoyU"  # BotFather se lo
GROUP_ID  = -1001919117846         # Aapka Group ID

# Free test streams (legal, open source)
STREAMS = {
    "test1": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
    "test2": "https://bitdash-a.akamaihd.net/content/sintel/hls/playlist.m3u8",
    "test3": "https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8",
}
CURRENT = STREAMS["test1"]
IS_LIVE  = False

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#   FLASK â€” Health check for Render
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return jsonify({"status": "running", "live": IS_LIVE})

@flask_app.route("/health")
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port, use_reloader=False, debug=False)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#   PYROGRAM CLIENT (User Account)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
user_client = Client(
    "ipl_stream_session",
    api_id=API_ID,
    api_hash=API_HASH,
)
tgcalls = PyTgCalls(user_client)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#   BOT CLIENT (Commands ke liye)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
bot = Client(
    "ipl_bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#   COMMANDS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@bot.on_message(filters.command("live") & filters.private)
async def cmd_live(client, message: Message):
    global IS_LIVE
    if IS_LIVE:
        await message.reply("Stream pehle se chal rahi hai! /stop se band karo.")
        return
    await message.reply("Stream shuru ho rahi hai...")
    try:
        await tgcalls.play(
            GROUP_ID,
            MediaStream(
                CURRENT,
                video_flags=MediaStreamType.IGNORE,   # sirf audio test
            )
        )
        IS_LIVE = True
        await message.reply(
            "LIVE ho gaya!\n"
            "Group mein jao - LIVE badge dikhega!\n"
            "Members Join karenge to stream sunenge.\n\n"
            "Video bhi chahiye? /livevideo try karo.\n"
            "Band karna ho: /stop"
        )
    except Exception as e:
        await message.reply("Error: " + str(e))

@bot.on_message(filters.command("livevideo") & filters.private)
async def cmd_livevideo(client, message: Message):
    global IS_LIVE
    IS_LIVE = True
    await message.reply("Video+Audio stream shuru ho rahi hai...")
    try:
        await tgcalls.play(
            GROUP_ID,
            MediaStream(CURRENT)   # audio + video dono
        )
        await message.reply(
            "LIVE VIDEO ho gaya!\n"
            "Group mein jao - LIVE badge dikhega!\n"
            "Join karo - Video player khulega (TV jaisa!)\n\n"
            "/stop se band karo."
        )
    except Exception as e:
        await message.reply("Error: " + str(e))

@bot.on_message(filters.command("stop") & filters.private)
async def cmd_stop(client, message: Message):
    global IS_LIVE
    try:
        await tgcalls.leave_call(GROUP_ID)
        IS_LIVE = False
        await message.reply("Stream band ho gaya.")
    except Exception as e:
        await message.reply("Error: " + str(e))

@bot.on_message(filters.command("change") & filters.private)
async def cmd_change(client, message: Message):
    global CURRENT
    args = message.text.split()
    options = ", ".join(STREAMS.keys())
    if len(args) < 2 or args[1] not in STREAMS:
        await message.reply("Options: " + options + "\nUsage: /change test1")
        return
    CURRENT = STREAMS[args[1]]
    await message.reply("Stream badal gaya: " + args[1] + "\n/livevideo se start karo.")

@bot.on_message(filters.command("status") & filters.private)
async def cmd_status(client, message: Message):
    status = "LIVE chal rahi hai" if IS_LIVE else "Koi stream nahi"
    await message.reply(
        "Status: " + status + "\n"
        "Group ID: " + str(GROUP_ID) + "\n"
        "Stream: " + CURRENT
    )

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#   MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
async def main():
    print("=" * 45)
    print("  IPL LIVE STREAM BOT")
    print("=" * 45)

    # Flask background mein start karo (Render ke liye)
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    print("Flask health server ready.")

    # PyTgCalls + User client start karo
    await user_client.start()
    await tgcalls.start()
    me = await user_client.get_me()
    print("User account: " + me.first_name + " (@" + (me.username or "no_username") + ")")

    # Bot start karo
    await bot.start()
    bot_me = await bot.get_me()
    print("Bot: @" + (bot_me.username or "no_username"))

    print("=" * 45)
    print("Commands (Bot ko DM mein bhejo):")
    print("  /live       - Audio stream shuru karo")
    print("  /livevideo  - Video+Audio stream (TV jaisa!)")
    print("  /stop       - Stream band karo")
    print("  /change     - Stream URL badlo")
    print("  /status     - Status dekho")
    print("=" * 45)
    print("Ready! Ctrl+C se band karo.")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
