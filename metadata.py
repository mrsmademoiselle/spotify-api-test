import csv
import json
import base64
import os
from requests import post,get
import string
from concurrent.futures import ThreadPoolExecutor,as_completed
import time

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
spotify_token_address = 'https://accounts.spotify.com/api/token'
spotify_search_address = 'https://api.spotify.com/v1/search?type=track&limit=50'
alphabet = list(string.ascii_lowercase)
workers = os.getenv('WORKERS')

try:
    workers = int(workers)
except ValueError:
    print(f"Error: 'WORKERS' value '{workers}' is not a valid integer. Using default value.")
    workers = 5

def collect_metadata():
    start_time = time.time()

    token = get_token()
    print()
    songs = get_songs(token)
    print()
    write_to_file(songs)

    print("--- %s seconds ---" % (time.time() - start_time))

def get_auth_header(token):
    return {"Authorization":"Bearer "+token}

def get_token():
    print('Fetching Spotify API token...')
    auth_string = client_id + ':'+client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes),'utf-8')

    url = spotify_token_address
    headers = {
        "Authorization":"Basic "+auth_base64,
        "Content-Type":"application/x-www-form-urlencoded",
    }
    data = {"grant_type":"client_credentials"}

    result = post(url, headers=headers,data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]

    return token

def get_songs(token):
    all_songs = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_letter = {executor.submit(get_songs_for_letter, letter, token): letter for letter in alphabet}

        for future in as_completed(future_to_letter):
            letter = future_to_letter[future]
            try:
                songs = future.result()
                all_songs.extend(songs)
            except Exception as exc:
                print(f'Error fetching songs for letter {letter}: {exc}')

    return all_songs

def get_songs_for_letter(letter,token):
    print(f"Getting songs for letter {letter}")
    query = f"q={letter}"
    header = get_auth_header(token)
   
    pages = range(0,100)
    songs_of_all_pages = []

    for page_number in pages:
        offset = f'offset={page_number}'
        url = spotify_search_address + '&'+query+'&'+offset

        result = get(url, headers=header)

        json_result = json.loads(result.content)["tracks"]["items"]
        songs_of_all_pages.extend(json_result)

    return songs_of_all_pages

def write_to_file(songs):
    print(f"Writing {len(songs)} songs to file")
    directory = os.getenv('CSV_DIRECTORY')
    file_path = directory + '/metadata5.csv'

    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Name', 'Artists', 'Artist Genres', 'Duration', 'Explicit', 'Popularity'])

        for song in songs:
            song_name = song["name"]
            artists_string = ''
            artists_genres = ''

            for artist in song["artists"]:
                artists_string += artist["name"] + ' '
                if 'genres' in artist:
                    artists_genres += ' '.join(artist["genres"]) + ' '

            csv_writer.writerow(
                [song_name, artists_string, artists_genres, song["duration_ms"], song["explicit"], song["popularity"]])


    print("Done.")