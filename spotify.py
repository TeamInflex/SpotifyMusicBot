from pyrogram import Client, filters
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os
import requests

# Importing variables from config.py
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    STRING_SESSION,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
)

# Initialize Pyrogram client with string session
app = Client(":memory:", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, string_session=STRING_SESSION)

# Initialize Spotipy
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID,
                                                                client_secret=SPOTIFY_CLIENT_SECRET))

# Command to start the bot
@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("Hi! Send me a /play command followed by a song name to play music.")

# Command to play music (restricted to groups)
@app.on_message(filters.group & filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a song name.")
        return

    song_name = " ".join(message.command[1:])
    track = spotify.search(q=song_name, limit=1, type="track")
    if track and track["tracks"]["items"]:
        track_info = track["tracks"]["items"][0]
        track_name = track_info["name"]
        artists = ", ".join([artist["name"] for artist in track_info["artists"]])
        await message.reply_text(f"Now playing: {track_name} by {artists}")
        
        # Join the voice chat
        voice_chat = await app.join_chat(message.chat.id)
        await voice_chat.start_audio()
        
        # Download the audio
        audio_url = track_info["preview_url"]
        audio_file = f"{track_name}.mp3"
        with open(audio_file, "wb") as file:
            file.write(requests.get(audio_url).content)
        
        # Stream the audio
        await voice_chat.send_audio(audio_file)
        
        # Cleanup
        os.remove(audio_file)
    else:
        await message.reply_text("Sorry, I couldn't find that song.")

# Run the bot
app.run()
