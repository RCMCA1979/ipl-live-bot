import os, threading, asyncio
from flask import Flask, jsonify, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN  = "6050076233:AAHTfZpIWvzuQfZWA20uBSqYQpzvI1ozoyU"
CHANNEL_ID = "-1001919117846"
ADMIN_ID   = 587231038

STREAM = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
MATCH  = {"teams":"CSK vs MI","score":"CSK: 97/2 (10 ov)","status":"LIVE"}

flask_app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>IPL Live</title>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#0d0d0d;color:white;font-family:sans-serif;}
.hdr{background:#1a1a2e;padding:12px 16px;display:flex;
justify-content:space-between;align-items:center;
border-bottom:2px solid #e63946;}
.badge{background:#e63946;padding:3px 10px;border-radius:4px;
font-size:11px;font-weight:bold;animation:blink 1.2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:0.3;}}
.teams{color:#ffd700;font-size:15px;font-weight:bold;}
video{width:100%;background:#000;display:block;}
.card{background:#1a1a2e;margin:10px;padding:14px;
border-radius:12px;border:1px solid #333;}
.score{font-size:22px;font-weight:bold;margin-top:6px;}
.st{color:#4cc9f0;font-size:13px;margin-top:4px;}
.btn{background:#e63946;border:none;color:white;padding:11px;
width:calc(100% - 20px);margin:8px 10px 16px;
border-radius:8px;font-size:14px;font-weight:bold;display:block;}
</style></head><body>
<div class="hdr">
<span class="teams">{{ teams }}</span>
<span class="badge">LIVE</span>
</div>
<video id="v" controls autoplay muted playsinline></video>
<div class="card">
<div style="color:#ffd700;font-size:14px;">IPL 2026 - Live Score</div>
<div class="score" id="sc">{{ score }}</div>
<div class="st" id="st">{{ status }}</div>
</div>
<button class="btn" onclick="location.reload()">Refresh</button>
<script>
var v=document.getElementById("v");
var url="{{ stream_url }}";
if(Hls.isSupported()){
  var h=new Hls();
  h.loadSource(url);
  h.attachMedia(v);
  h.on(Hls.Events.MANIFEST_PARSED,function(){v.play().catch(function(){});});
}else if(v.canPlayType("application/vnd.apple.mpegurl")){
  v.src=url;v.play().catch(function(){});
}
setInterval(function(){
  fetch("/update").then(function(r){return r.json();})
  .then(function(d){
    document.getElementById("sc").textContent=d.score;
    document.getElementById("st").textContent=d.status;
  }).catch(function(){});
},30000);
</script>
</body></html>"""

@flask_app.route("/")
def index():
    return render_template_string(HTML, stream_url=STREAM,
        teams=MATCH["teams"],score=MATCH["score"],status=MATCH["status"])

@flask_app.route("/update")
def upd(): return jsonify(MATCH)

@flask_app.route("/health")
def health(): return "OK",200

def run_flask():
    flask_app.run(host="0.0.0.0",port=5000,use_reloader=False,debug=False)

async def cmd_live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    url = "http://"+ip+":5000"
    kb = [[InlineKeyboardButton("LIVE Dekho", url=url)]]
    await update.message.reply_text(
        "*IPL LIVE*
"+MATCH["teams"]+"
"+MATCH["score"],
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown")

async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Sirf Admin!")
        return
    import socket
    ip = socket.gethostbyname(socket.gethostname())
    url = "http://"+ip+":5000"
    kb = [[InlineKeyboardButton("LIVE Dekho", url=url)]]
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="*LIVE - "+MATCH["teams"]+"*
"+MATCH["score"],
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown")
    await update.message.reply_text("Channel par post!
URL: "+url)

def run_bot():
    async def bot_main():
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("live", cmd_live))
        app.add_handler(CommandHandler("post", cmd_post))
        print("Bot ready! /live /post")
        await app.run_polling(drop_pending_updates=True)
    asyncio.run(bot_main())

if __name__ == "__main__":
    threading.Thread(target=run_flask,daemon=True).start()
    import time; time.sleep(1)
    print("Open: http://127.0.0.1:5000")
    run_bot()