from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"👋 Hello {user_name}! Welcome to **Word Guess Bot** 🎉\n\n"
        "🔠 **How to Play:**\n"
        "1️⃣ Start a new game using /new\n"
        "2️⃣ Choose a word length\n"
        "3️⃣ Guess the word and get feedback with 🟩🟨🟥\n"
        "4️⃣ Score points and climb the leaderboard!\n\n"
        "🚀 Add me to a group and play with friends!"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("📜 Bot Commands", callback_data="commands")]
    ])
    
    await message.reply_photo(
        photo="https://files.catbox.moe/x4w7h1.jpg",  # Replace with an actual image URL
        caption=welcome_text,
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex("^commands$"))
async def show_commands(client, callback_query):
    commands_text = (
        "📜 **Bot Commands:**\n\n"
        "🎮 /new - Start a new game\n"
        "📊 /leaderboard - View global leaderboard\n"
        "🏆 /chatleaderboard - View chat leaderboard\n"
        "ℹ️ /start - Show this message again\n"
    )
    
    await callback_query.message.edit_text(commands_text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ]))

@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start(client, callback_query):
    await start_command(client, callback_query.message)
