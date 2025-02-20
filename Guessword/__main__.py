import random
from pyrogram import Client, filters
from pyrogram.types import Message

# List of 5-letter words for the game
word_list = ["apple", "grape", "melon", "peach", "plums", "mango", "berry", "lemon"]

# Dictionary to store ongoing games for groups
group_games = {}

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
    for i in range(5):
        if guess[i] == word_to_guess[i]:
            feedback.append("🟩")  # Correct letter and position
        elif guess[i] in word_to_guess:
            feedback.append("🟨")  # Correct letter, wrong position
        else:
            feedback.append("🟥")  # Incorrect letter
    return ''.join(feedback)

# Start new game command for groups
@app.on_message(filters.command("new"))
async def new_game(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in group_games:
        word_to_guess = start_new_game()
        group_games[chat_id] = {"word": word_to_guess, "players": {}}
        await message.reply("A new game has started! Guess a 5-letter word.")
    else:
        await message.reply("A game is already running! Keep guessing.")

# Handle guesses from all users in the group
@app.on_message(filters.text & ~filters.command("new"))
async def guess_word(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if chat_id not in group_games:
        await message.reply("No active game. Type /new to start.")
        return

    word_to_guess = group_games[chat_id]["word"]
    guess = message.text.strip().lower()
    
    if len(guess) != 5:
        return  # Ignore incorrect-length guesses

    feedback = check_guess(guess, word_to_guess)
    
    # Store the player's guess history
    if user_id not in group_games[chat_id]["players"]:
        group_games[chat_id]["players"][user_id] = []
    group_games[chat_id]["players"][user_id].append(feedback)
    
    # Display the player's previous guesses as blocks only
    guess_history = "\n".join(group_games[chat_id]["players"][user_id])
    await message.reply(guess_history)
    
    # If the player guessed correctly, end the game
    if guess == word_to_guess:
        del group_games[chat_id]
        await message.reply(f"🎉 Correct! The word was {word_to_guess} 🎉")

# Run the bot
app.run()
