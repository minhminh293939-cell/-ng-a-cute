import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os


# Tạo web server giả lập để Render không bị lỗi port
class SimpleHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Bot is active!")


def run_server():
  port = int(os.environ.get("PORT", 10000))
  server = HTTPServer(("0.0.0.0", port), SimpleHandler)
  server.serve_forever()


# Chạy server web ngầm ở background
threading.Thread(target=run_server, daemon=True).start()

# --- PHẦN DƯỚI NÀY LÀ CODE BOT DISCORD CŨ CỦA BẠN ---
import random
import discord
from discord.ext import commands

# Cấu hình Intent
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# Dictionary lưu số dư của người chơi
balances = {}


@bot.event
async def on_ready():
  print(f"🔥 Bot {bot.user} đã hoạt động và sẵn sàng trên server!")


# 1. Lệnh Admin tặng/cộng tiền: .cong @user số_tiền
@bot.command()
@commands.has_permissions(administrator=True)
async def cong(ctx, member: discord.Member, amount: int):
  if member.id not in balances:
    balances[member.id] = 0
  balances[member.id] += amount
  await ctx.send(
      f"✅ *Admin* đã tặng *{amount}* tiền cho {member.mention}! Số dư mới:"
      f" *{balances[member.id]}* tiền."
  )


# 2. Lệnh xem số dư: .sodu
@bot.command()
async def sodu(ctx, member: discord.Member = None):
  if member is None:
    member = ctx.author
  bal = balances.get(member.id, 0)
  await ctx.send(f"💰 Số dư của *{member.name}* là: *{bal}* tiền.")


# 3. Lệnh Tài Xỉu cược tiền thật (.tx)
@bot.command()
async def tx(ctx, lua_chon: str = None, tien_cuoc: int = 0):
  if not lua_chon or tien_cuoc <= 0:
    await ctx.send(
        "❌ *Cú pháp sai!* Dùng: .tx <t/x> <số tiền> (Ví dụ: .tx t 100)"
    )
    return

  if ctx.author.id not in balances:
    balances[ctx.author.id] = 0

  if balances[ctx.author.id] < tien_cuoc:
    await ctx.send(
        f"❌ Bạn không đủ tiền để cược! Số dư hiện tại của bạn chỉ có:"
        f" *{balances[ctx.author.id]}* tiền."
    )
    return

  # Tung 3 viên xúc xắc (1 đến 6)
  d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
  tong = d1 + d2 + d3

  ket_qua = "t" if tong >= 11 else "x"
  ten_ket_qua = "TÀI" if ket_qua == "t" else "XỈU"
  chon_clean = lua_chon.lower()[0]

  if chon_clean not in ["t", "x"]:
    await ctx.send("❌ Vui lòng chọn t (Tài) hoặc x (Xỉu)!")
    return

  # Xử lý kết quả thắng / thua
  if chon_clean == ket_qua:
    balances[ctx.author.id] += tien_cuoc
    await ctx.send(
        f"""🎲 Kết quả: *{d1} - {d2} - {d3}* (Tổng: *{tong}* - *{ten_ket_qua}*)
🎉 *{ctx.author.mention}* đã *THẮNG*
*{tien_cuoc}* tiền! Số dư mới: *{balances[ctx.author.id]}* tiền."""
    )
  else:
    balances[ctx.author.id] -= tien_cuoc
    await ctx.send(
        f"""🎲 Kết quả: *{d1} - {d2} - {d3}* (Tổng: *{tong}* - *{ten_ket_qua}*)
💸 *{ctx.author.mention}* đã *THUA*
*{tien_cuoc}* tiền! Số dư mới: *{balances[ctx.author.id]}* tiền."""
    )


# 4. Lệnh quản lý server: Xóa tin nhắn (.clear)
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
  await ctx.channel.purge(limit=amount + 1)
  await ctx.send(f"🧹 Đã xóa {amount} tin nhắn!", delete_after=3)


# Token thật của bot Ong Dia
TOKEN ="MTU2MjcwNDA4MjU0MjUyNjQ2NA.GhDxoT.beW8DQZFQwI4dGO808urZ-zXKz2jwAffplpgoI"
bot.run(TOKEN)
