import random
from pyrogram import Client, filters
from pyrogram.types import Message

# List of 5-letter words for the game
word_list = ["apple", "grape", "melon", "peach", "plums", "mango", "berry", "lemon"]

# Dictionary to store ongoing games for groups
group_games = {}
group_scores = {}  # Stores scores per group
global_scores = {}  # Stores scores globally

# Bot credentials
API_ID = "20222660"
API_HASH = "5788f1f4a93f2de28835a0cf1b0ebae4"
BOT_TOKEN = "7560532835:AAE5yA7zLwHrkJQK0VYeGeCR-Db6Jhqzvpo"

app = Client("word_guess_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Function to start a new game
def start_new_game():
    return random.choice(word_list)

# Function to check the user's guess
def check_guess(guess, word_to_guess):
    feedback = []
    word_to_guess_list = list(word_to_guess)  # Convert to list to track used letters
    
    # First pass: Check for correct positions (green)
    for i in range(5):
        if guess[i] == word_to_guess[i]:
            feedback.append("🟩")
            word_to_guess_list[i] = None  # Mark letter as used
        else:
            feedback.append(None)  # Placeholder for later updates
    
    # Second pass: Check for correct letters in wrong positions (yellow)
    for i in range(5):
        if feedback[i] is None and guess[i] in word_to_guess_list:
            feedback[i] = "🟨"
            word_to_guess_list[word_to_guess_list.index(guess[i])] = None  # Mark letter as used
        elif feedback[i] is None:
            feedback[i] = "🟥"
    
    return ''.join(feedback)

# Start new game command for groups
@app.on_message(filters.command("new"))
async def new_game(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in group_games:
        word_to_guess = start_new_game()
        group_games[chat_id] = {"word": word_to_guess, "history": []}
        await message.reply("A new game has started! Guess a 5-letter word.")
    else:
        await message.reply("A game is already running! Keep guessing.")

# Handle guesses from all users in the group
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
    
    if len(guess) != 5:
        return  # Ignore incorrect-length guesses

    feedback = check_guess(guess, word_to_guess)
    
    # Store the group's guess history
    group_games[chat_id]["history"].append(f"{feedback}")
    guess_history = "\n".join(group_games[chat_id]["history"])
    
    await message.reply(guess_history)
    
    # If the player guessed correctly, end the game and update scores
    if guess == word_to_guess:
        group_scores.setdefault(chat_id, {})
        global_scores.setdefault(user_id, 0)
        
        group_scores[chat_id][user_id] = group_scores[chat_id].get(user_id, 0) + 1
        global_scores[user_id] += 1
        
        del group_games[chat_id]
        
        await message.reply(f"🎉 {user_name} guessed the word correctly! The word was {word_to_guess} 🎉\n\n🏆 Group Score: {group_scores[chat_id][user_id]}\n🌍 Global Score: {global_scores[user_id]}")

# Run the bot
app.run()

