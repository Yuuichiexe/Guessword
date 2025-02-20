import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Word lists based on length
word_lists = {
    4: ["pear", "lime", "kiwi", "figs", "blue", "palm", "corn", "salt", "fish", "bark", "milk", "gold", "iron", "leaf", "dust", "rose", "star", "moon", "mars", "coal", "vine", "wind", "seed", "root", "flax", "wool", "wave", "beet", "toad", "fern", "reed", "rice", "lily", "foam", "ruby", "opal", "zinc", "tide", "sand", "snow", "haze", "mist", "echo", "lava", "silt", "clay", "lead", "bron", "acme", "crux", "limb", "husk", "twig", "raze", "zest", "loam", "moss", "peat", "plow", "spur", "cane", "hail", "dune", "vibe", "flux", "fume", "grit", "jade", "mule", "opal", "perch", "quilt", "silk", "twine"],
    5: ["apple", "grape", "melon", "peach", "plums", "mango", "berry", "lemon", "chess", "brick", "sword", "glass", "sugar", "cloud", "storm", "river", "plain", "ocean", "music", "torch", "flame", "quilt", "beach", "zebra", "dwarf", "smoke", "grape", "slate", "marsh", "chime", "quark", "plume", "brisk", "fable", "linen", "wheat", "spine", "flint", "charm", "thorn", "swirl", "ranch", "bison", "clove", "vivid", "glyph", "frost", "chest", "drift", "bloom", "steed", "fjord", "quake", "spurt", "prism", "scarf", "vexed", "brink", "froze", "creek", "fizzy", "skunk", "pouch", "badge", "glint", "brood", "quest", "fluke", "crisp", "shard", "plush", "dwell", "vigor", "whisk", "flair"],
    6: ["banana", "orange", "tomato", "carrot", "cheese", "breeze", "forest", "desert", "canyon", "beacon", "flight", "pillar", "castle", "shadow", "lantern", "ripple", "pebble", "marble", "zigzag", "brandy", "whisky", "sandal", "cactus", "rocket", "carpet", "purple", "violet", "tundra", "relief", "thrift", "plunge", "glisten", "zephyr", "coarse", "mellow", "jungle", "tropic", "glider", "warble", "prance", "ransom", "beacon", "sizzle", "piston", "cradle", "wisped", "luster", "spigot", "jester", "freeze", "plated", "ranger", "guzzle", "jumble", "kettle", "mingle", "dazzle", "nibble", "blithe", "quiver", "throat", "murmur", "scurry", "puzzle", "jumper", "tangle", "wholly", "gossip", "morsel", "brisket", "cuddle", "snappy", "cranky", "whizzy"],
    7: ["pumpkin", "avocado", "spinach", "broccoli", "lantern", "chimney", "warrior", "buffalo", "diamond", "emerald", "curtain", "sunrise", "monarch", "horizon", "pioneer", "whisper", "cushion", "glimmer", "twinkle", "stencil", "passion", "gingham", "glacier", "granite", "journey", "whiskey", "quilted", "victory", "torpedo", "symphon", "vortex", "blazing", "curtain", "phoenix", "twisted", "tundras", "skylark", "rooster", "nostalg", "justice", "harmony", "pulsate", "spectra", "scaling", "balloon", "mystery", "arizona", "morning", "orchard", "plutoid", "vintage", "jeopard", "wrinkle", "seismic", "zealous", "stealth", "flicker", "chateau", "clovera", "horizon", "painter", "ballast", "paradox", "neptune", "quicken", "sunbeam", "warlock", "vividly", "radiate", "furnace", "blossom", "banquet", "cypress", "glisten", "bizarre", "sunfish", "torment"]
}

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
def start_new_game(word_length):
    return random.choice(word_lists[word_length])

# Function to check the user's guess
def check_guess(guess, word_to_guess):
    feedback = []
    word_to_guess_list = list(word_to_guess)  # Convert to list to track used letters
    
    # First pass: Check for correct positions (green)
    for i in range(len(word_to_guess)):
        if guess[i] == word_to_guess[i]:
            feedback.append("🟩")
            word_to_guess_list[i] = None  # Mark letter as used
        else:
            feedback.append(None)  # Placeholder for later updates
    
    # Second pass: Check for correct letters in wrong positions (yellow)
    for i in range(len(word_to_guess)):
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
    chat_id = callback_query.message.chat.id
    word_length = int(callback_query.data.split("_")[1])
    
    word_to_guess = start_new_game(word_length)
    group_games[chat_id] = {"word": word_to_guess, "history": []}
    
    await callback_query.message.edit_text(f"A new {word_length}-letter game has started! Guess a word.")

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
    
    if len(guess) != len(word_to_guess):
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
        
        await message.reply(f"🎉 {user_name} guessed the word correctly! The word was {word_to_guess} 🎉\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n🏆 Group Score: {group_scores[chat_id][user_id]}\n🌍 Global Score: {global_scores[user_id]}")

# Show group leaderboard
@app.on_message(filters.command("chatleaderboard"))
async def group_leaderboard(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in group_scores or not group_scores[chat_id]:
        await message.reply("No scores recorded for this group yet.")
        return
    
    leaderboard = "🏆 Group Leaderboard:\n" + "\n".join([f"{user_id}: {score}" for user_id, score in sorted(group_scores[chat_id].items(), key=lambda x: x[1], reverse=True)])
    await message.reply(leaderboard)

# Show global leaderboard
@app.on_message(filters.command("leaderboard"))
async def global_leaderboard(client: Client, message: Message):
    if not global_scores:
        await message.reply("No global scores recorded yet.")
        return
    
    leaderboard = "🌍 Global Leaderboard:\n" + "\n".join([f"{user_id}: {score}" for user_id, score in sorted(global_scores.items(), key=lambda x: x[1], reverse=True)])
    await message.reply(leaderboard)

# Run the bot
app.run()
