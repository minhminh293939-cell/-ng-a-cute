import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord
from discord.ext import commands


# 1. Web server giả lập để Render không bị kill port
class SimpleHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Bot Ong Dia is running!")


def run_server():
  port = int(os.environ.get("PORT", 10000))
  server = HTTPServer(("0.0.0.0", port), SimpleHandler)
  server.serve_forever()


threading.Thread(target=run_server, daemon=True).start()

# 2. Khai báo Cấu hình Intents cho Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# Dictionary lưu số dư tài khoản người chơi
balances = {}


@bot.event
async def on_ready():
  print(f"🔥 Bot {bot.user} đã kết nối thành công và đang hoạt động!")


# --- LỆNH 1: ADMIN CỘNG TIỀN (.cong) ---
@bot.command(name="cong")
@commands.has_permissions(administrator=True)
async def cong(ctx, member: discord.Member, amount: int):
  if amount <= 0:
    await ctx.send("❌ Số tiền cộng phải lớn hơn 0!")
    return

  balances[member.id] = balances.get(member.id, 0) + amount
  await ctx.send(
      f"✅ **Admin** đã cộng **{amount:,}** tiền cho {member.mention}!\n"
      f"💰 Số dư mới: **{balances[member.id]:,}** tiền."
  )


@cong.error
async def cong_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("❌ Bạn không có quyền Administrator để dùng lệnh này!")
  elif isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(
        "❌ **Thiếu thông tin!** Cú pháp đúng: `.cong @tên_user <số_tiền>`"
    )
  elif isinstance(error, commands.BadArgument):
    await ctx.send("❌ **Sai định dạng!** Hãy tag đúng user và nhập số tiền dạng số nguyên.")
  else:
    await ctx.send(f"⚠️ Lỗi lệnh `.cong`: {error}")


# --- LỆNH 2: XEM SỐ DƯ (.sodu) ---
@bot.command(name="sodu")
async def sodu(ctx, member: discord.Member = None):
  target = member or ctx.author
  bal = balances.get(target.id, 0)
  await ctx.send(f"💰 Số dư hiện tại của **{target.name}** là: **{bal:,}** tiền.")


@sodu.error
async def sodu_error(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send("❌ Không tìm thấy người dùng này!")
  else:
    await ctx.send(f"⚠️ Lỗi lệnh `.sodu`: {error}")


# --- LỆNH 3: TÀI XỈU (.tx) ---
@bot.command(name="tx")
async def tx(ctx, lua_chon: str = None, tien_cuoc: int = 0):
  if not lua_chon or tien_cuoc <= 0:
    await ctx.send(
        "❌ **Cú pháp chưa chuẩn!** Sử dụng: `.tx <t/x> <số tiền>`\n"
        "👉 Ví dụ đặt Tài 1000: `.tx t 1000`\n"
        "👉 Ví dụ đặt Xỉu 1000: `.tx x 1000`"
    )
    return

  user_id = ctx.author.id
  current_bal = balances.get(user_id, 0)

  if current_bal < tien_cuoc:
    await ctx.send(
        f"❌ **Không đủ tiền!** Số dư hiện tại của bạn là **{current_bal:,}** tiền, "
        f"không đủ để cược **{tien_cuoc:,}** tiền."
    )
    return

  chon_clean = lua_chon.lower()[0]
  if chon_clean not in ["t", "x"]:
    await ctx.send("❌ Vui lòng chọn **t** (Tài) hoặc **x** (Xỉu)!")
    return

  # Đổ 3 viên xí ngầu (1 đến 6)
  d1, d2, d3 = random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)
  tong = d1 + d2 + d3

  ket_qua = "t" if tong >= 11 else "x"
  ten_ket_qua = "TÀI" if ket_qua == "t" else "XỈU"

  if chon_clean == ket_qua:
    balances[user_id] += tien_cuoc
    await ctx.send(
        f"🎲 Xúc xắc: **{d1} - {d2} - {d3}** (Tổng: **{tong}** ➔ **{ten_ket_qua}**)\n"
        f"🎉 {ctx.author.mention} đã **THẮNG {tien_cuoc:,}** tiền!\n"
        f"💰 Số dư mới: **{balances[user_id]:,}** tiền."
    )
  else:
    balances[user_id] -= tien_cuoc
    await ctx.send(
        f"🎲 Xúc xắc: **{d1} - {d2} - {d3}** (Tổng: **{tong}** ➔ **{ten_ket_qua}**)\n"
        f"💸 {ctx.author.mention} đã **THUA {tien_cuoc:,}** tiền!\n"
        f"💰 Số dư mới: **{balances[user_id]:,}** tiền."
    )


@tx.error
async def tx_error(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send("❌ Số tiền cược phải là một con số nguyên hợp lệ!")
  else:
    await ctx.send(f"⚠️ Lỗi lệnh `.tx`: {error}")


# --- LỆNH 4: XÓA TIN NHẮN (.clear) ---
@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
  await ctx.channel.purge(limit=amount + 1)
  await ctx.send(f"🧹 Đã dọn dẹp **{amount}** tin nhắn!", delete_after=3)


@clear.error
async def clear_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("❌ Bạn cần có quyền `Manage Messages` để xóa tin nhắn!")
  else:
    await ctx.send(f"⚠️ Lỗi lệnh `.clear`: {error}")


# --- CHẠY BOT ---
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
