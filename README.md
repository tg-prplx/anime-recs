![New Project 5  97DAAF6](https://github.com/user-attachments/assets/5c194461-99f5-4cda-a739-2e61df29f149)

# ARecs (Preview) — Anime Recommender in Telegram

A simple Telegram bot built with [aiogram 3](https://docs.aiogram.dev/) for keeping a personal list of watched anime and getting awesome recommendations based on your tastes.  
Works with a local (offline) database (anime, genres, tags) — private, fast, and supports images 😊

## Features
- Saves your anime list (even after restarts!)
- Personalized recommendations based on what you’ve watched
- Anime search with typo correction
- Anime preview cards with poster, genres, description, and status
- Extremely user-friendly UX with interactive buttons

## Getting Started
1. **Clone the repo and open it**
2. **Create a `.env` file**
   ```
   BOT_TOKEN=your_bot_token
   ANIME_DB_PATH=app/anime-offline-database.json
   USER_DATA_PATH=users.json
   ```
3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
5. **Run the bot!**
    ```bash
    python app/app.py
    ```

## Project Structure
```
app/
⎿ app.py                       # main bot file
⎿ anime-offline-database.json  # anime database
⎿ bot/
   ⎿ kb.py                     # keyboards
   ⎿ handlers.py               # handlers
   ⎿ utils.py                  # extra bot utilities
⎿ recs/
  ⎿ tag_freq.py                # recommendation engine dependency
  ⎿ tag_genres.py              # recommendation engine
  ⎿ fuzzy_search.py            # fuzzy search function (typos, synonyms)
.env
prototype.py                   # prototype implementation
users.json                     # user favorite anime list
```

## Screenshots
![image](https://github.com/user-attachments/assets/f0131f0e-f241-44b9-9868-99bbbc98e58d)
![image](https://github.com/user-attachments/assets/54056420-f9e9-4997-ae2e-4d99f601667c)

## How to Add/Search Anime
- The ➕ Add watched anime button — you can enter multiple titles comma-separated or partially, the bot will suggest matches!
- "🔥 Get recommendations" — you’ll get a selection of suggestions tailored to your tastes (click anime for details and quick add).
- Everything is saved, you can view or clear your list at any time.

---

**Open Source forever! Love anime? Fork the bot 🙃**  
Contacts and ideas: [tg @prplx](https://t.me/prplx)  
Database taken from https://github.com/manami-project/anime-offline-database
