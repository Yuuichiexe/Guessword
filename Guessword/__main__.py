import random
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Fallback words in case the API fails
fallback_words = {
    4: ["play", "word", "game", "chat", "test", "love", "cool", "hard"],
    5: ["guess", "brain", "smart", "think", "score", "solve", "happy", "lucky"],
    6: ["random", "puzzle", "letter", "breeze", "player", "winner", "pencil", "bottle"],
    7: ["amazing", "thought", "journey", "fantasy", "mystery", "fortune", "complex", "victory"]
}

# Function to fetch words from Datamuse API
def fetch_words(word_length, max_words=100000):
    try:
        response = requests.get(f"https://api.datamuse.com/words?sp={'?' * word_length}&max={max_words}")
        response.raise_for_status()  # Raise an error if request fails (4xx, 5xx)
        words = [word["word"] for word in response.json()]
        return words if words else fallback_words[word_length]
    except requests.RequestException as e:
        print(f"Error fetching {word_length}-letter words: {e}")
        return fallback_words[word_length]  # Use fallback words

# Fetch words for different lengths
word_lists = {
    4: fetch_words(4),
    5: fetch_words(5),
    6: fetch_words(6),
    7: fetch_words(7),
}

# Dictionary to store game data
group_games = {}
group_scores = {}  # Stores scores per group
global_scores = {}  # Stores scores globally

# Secure Bot Credentials (Use environment variables for safety)
API_ID = int(os.getenv("API_ID", "20222660"))  # Replace with your API_ID
API_HASH = os.getenv("API_HASH", "5788f1f4a93f2de28835a0cf1b0ebae4")  # Replace with your API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7560532835:AAE5yA7zLwHrkJQK0VYeGeCR-Db6Jhqzvpo")  # Replace with your actual bot token

app = Client("word_guess_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Function to start a new game
def start_new_game(word_length):
    return random.choice(word_lists[word_length])

# Function to check if a word is in the English dictionary
def is_valid_english_word(word):
    try:
        response = requests.get(f"https://api.datamuse.com/words?sp={word}&max=1")
        response.raise_for_status()
        words = [w["word"] for w in response.json()]
        return word in words
    except requests.RequestException:
        return False

# Function to check the user's guess
def check_guess(guess, word_to_guess):
    feedback = []
    word_to_guess_list = list(word_to_guess)

    # First pass: Check for correct positions (🟩 Green)
    for i in range(len(word_to_guess)):
        if guess[i] == word_to_guess[i]:
            feedback.append("🟩")
            word_to_guess_list[i] = None  
        else:
            feedback.append(None)  

    # Second pass: Check for correct letters in wrong positions (🟨 Yellow)
    for i in range(len(word_to_guess)):
        if feedback[i] is None and guess[i] in word_to_guess_list:
            feedback[i] = "🟨"
            word_to_guess_list[word_to_guess_list.index(guess[i])] = None  
        elif feedback[i] is None:
            feedback[i] = "🟥"
    
    return ''.join(feedback)

# Start new game command for groups
@app.on_message(filters.command("new"))
async def new_game(client: Client, message: Message):
    chat_id = message.chat.id
    buttons = [
        [InlineKeyboardButton("4 Letters", callback_data="start_4")],
        [InlineKeyboardButton("5 Letters", callback_data="start_5")],
        [InlineKeyboardButton("6 Letters", callback_data="start_6")],
        [InlineKeyboardButton("7 Letters", callback_data="start_7")]
    ]
    await message.reply("Choose a word length to start the game:", reply_markup=InlineKeyboardMarkup(buttons))

# Handle word length selection
@app.on_callback_query()
async def select_word_length(client, callback_query):
    await callback_query.answer()  # Acknowledge callback query
    chat_id = callback_query.message.chat.id
    word_length = int(callback_query.data.split("_")[1])
    
    word_to_guess = start_new_game(word_length)
    group_games[chat_id] = {"word": word_to_guess, "history": [], "used_words": set()}
    
    await callback_query.message.edit_text(f"A new {word_length}-letter game has started! Guess a word.")

# Handle guesses
@app.on_message(filters.text & ~filters.command("new"))
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
        await message.reply(f"❌ {user_name}, this word is not in the English dictionary. Try another one!")
        return

    if guess in group_games[chat_id]["used_words"]:
        await message.reply(f"🔄 {user_name}, you already used this word! Try a different one.")
        return

    group_games[chat_id]["used_words"].add(guess)
    feedback = check_guess(guess, word_to_guess)
    
    group_games[chat_id]["history"].append(f"{feedback} → {guess}")
    guess_history = "\n".join(group_games[chat_id]["history"])
    
    await message.reply(guess_history)

    if guess == word_to_guess:
        group_scores.setdefault(chat_id, {})
        global_scores.setdefault(user_id, 0)
        
        group_scores[chat_id][user_id] = group_scores[chat_id].get(user_id, 0) + 1
        global_scores[user_id] += 1
        
        del group_games[chat_id]
        
        await message.reply(f"🎉 {user_name} guessed the word correctly! The word was {word_to_guess} 🎉\n"
                            f"🏆 Group Score: {group_scores[chat_id].get(user_id, 0)}\n"
                            f"🌍 Global Score: {global_scores[user_id]}")

# Run the bot
app.run()
