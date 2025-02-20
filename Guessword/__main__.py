import random
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Fallback words in case the API fails
fallback_words = {
    4: ["play", "word", "game", "chat"],
    5: ["guess", "brain", "smart", "think"],
    6: ["random", "puzzle", "letter", "breeze"],
    7: ["amazing", "thought", "journey", "fantasy"]
}

# Function to fetch words from Datamuse API
def fetch_words(word_length, max_words=100000):
    try:
        response = requests.get(f"https://api.datamuse.com/words?sp={'?' * word_length}&max={max_words}")
        response.raise_for_status()
        words = [word["word"] for word in response.json()]
        return words if words else fallback_words[word_length]
    except requests.RequestException:
        return fallback_words[word_length]

# Fetch words for different lengths
word_lists = {length: fetch_words(length) for length in fallback_words}

# Game data storage
group_games = {}
group_scores = {}
global_scores = {}

# Bot credentials
API_ID = int(os.getenv("API_ID", "20222660"))
API_HASH = os.getenv("API_HASH", "5788f1f4a93f2de28835a0cf1b0ebae4")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7560532835:AAE5yA7zLwHrkJQK0VYeGeCR-Db6Jhqzvpo")

app = Client("word_guess_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Start a new game
def start_new_game(word_length):
    return random.choice(word_lists[word_length])

# Check if a word is valid
def is_valid_english_word(word):
    try:
        response = requests.get(f"https://api.datamuse.com/words?sp={word}&max=1")
        response.raise_for_status()
        return word in [w["word"] for w in response.json()]
    except requests.RequestException:
        return False

# Check a user's guess
def check_guess(guess, word_to_guess):
    feedback = []
    word_to_guess_list = list(word_to_guess)
    
    for i in range(len(word_to_guess)):
        if guess[i] == word_to_guess[i]:
            feedback.append("🟩")
            word_to_guess_list[i] = None  
        else:
            feedback.append(None)
    
    for i in range(len(word_to_guess)):
        if feedback[i] is None and guess[i] in word_to_guess_list:
            feedback[i] = "🟨"
            word_to_guess_list[word_to_guess_list.index(guess[i])] = None  
        elif feedback[i] is None:
            feedback[i] = "🟥"
    
    return ''.join(feedback)

@app.on_message(filters.command("new"))
async def new_game(client: Client, message: Message):
    chat_id = message.chat.id

    # Ensure the group has a score entry before starting a new game
    if chat_id not in group_scores:
        group_scores[chat_id] = {}
        
    buttons = [[InlineKeyboardButton(f"{i} Letters", callback_data=f"start_{i}")] for i in range(4, 8)]
    await message.reply("Choose a word length to start the game:", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query()
async def select_word_length(client, callback_query):
    await callback_query.answer()
    chat_id = callback_query.message.chat.id
    word_length = int(callback_query.data.split("_")[1])
    
    word_to_guess = start_new_game(word_length)
    group_games[chat_id] = {"word": word_to_guess, "history": [], "used_words": set()}
    
    await callback_query.message.edit_text(f"A new {word_length}-letter game has started! Guess a word.")

@app.on_message(filters.text)
async def guess_word(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    if chat_id not in group_games:
        await message.reply("No active game. Type /new to start.")
        return

    word_to_guess = group_games[chat_id]["word"]
    guess = message.text.strip().lower()

    if len(guess) != len(word_to_guess):
        return  

    if not is_valid_english_word(guess):
        await message.reply(f"❌ {user_name}, this word is not valid. Try another one!")
        return

    if guess in group_games[chat_id]["used_words"]:
        await message.reply(f"🔄 {user_name}, you already used this word! Try a different one.")
        return

    group_games[chat_id]["used_words"].add(guess)
    feedback = check_guess(guess, word_to_guess)
    
    group_games[chat_id]["history"].append(f"{feedback} → {guess.upper()}")
    guess_history = "\n".join(group_games[chat_id]["history"])
    
    await message.reply(guess_history)

    if guess == word_to_guess:
        group_scores.setdefault(chat_id, {}).setdefault(user_id, 0)
        global_scores.setdefault(user_id, 0)
        
        group_scores[chat_id][user_id] += 1
        global_scores[user_id] += 1
        
        del group_games[chat_id]
        
        await message.reply(f"🎉 {user_name} guessed the word correctly! The word was {word_to_guess.upper()} 🎉\n"
                            f"🏆 Group Score: {group_scores[chat_id][user_id]}\n"
                            f"🌍 Global Score: {global_scores[user_id]}")
        

@app.on_message(filters.command("leaderboard"))
async def leaderboard(client: Client, message: Message):
    if not global_scores:
        await message.reply("No scores recorded yet.")
        return

    leaderboard_text = "🌍 **Global Leaderboard:**\n"
    sorted_scores = sorted(global_scores.items(), key=lambda x: x[1], reverse=True)

    for rank, (user_id, score) in enumerate(sorted_scores, start=1):
        leaderboard_text += f"**{rank}.** User {user_id} → {score} points\n"

    print(f"Global Leaderboard Retrieved: {global_scores}")  # Debugging print
    await message.reply(leaderboard_text)


@app.on_message(filters.command("chatleaderboard"))
async def chat_leaderboard(client: Client, message: Message):
    chat_id = message.chat.id

    # Ensure the group chat has a score entry before checking leaderboard
    if chat_id not in group_scores:
        group_scores[chat_id] = {}  # Initialize empty scores

    if not group_scores[chat_id]:
        await message.reply("No scores recorded in this chat yet.")
        return

    leaderboard_text = "🏆 **Chat Leaderboard:**\n"
    sorted_scores = sorted(group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)

    for rank, (user_id, score) in enumerate(sorted_scores, start=1):
        leaderboard_text += f"**{rank}.** User {user_id} → {score} points\n"

    print(f"Chat Leaderboard Retrieved for {chat_id}: {group_scores[chat_id]}")  # Debugging print
    await message.reply(leaderboard_text)


app.run()
