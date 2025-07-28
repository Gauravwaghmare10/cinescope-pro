import pandas as pd
import requests
import re
import time
from tqdm import tqdm

OMDB_API_KEY = "26a45e26"
OMDB_URL = "http://www.omdbapi.com/"

def clean_title(title):
    match = re.match(r"^(.*?)\s*\((\d{4})\)", title)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return title.strip(), None

def get_poster_url(title, year):
    params = {"apikey": OMDB_API_KEY, "t": title}
    if year:
        params["y"] = year
    try:
        resp = requests.get(OMDB_URL, params=params, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            poster = data.get("Poster", "")
            if data.get("Response", "") == "True" and poster and poster != "N/A":
                return poster
    except Exception as e:
        print("Error:", e)
    return ""

if __name__ == "__main__":
    movies = pd.read_csv("movies.csv")
    posters = []

    for idx, row in tqdm(movies.iterrows(), total=len(movies)):
        title_raw = str(row["title"])
        movie_id = int(row["movieId"])
        genres = str(row["genres"])
        title, year = clean_title(title_raw)

        poster_url = get_poster_url(title, year)
        print(f"{title} ({year}) → {poster_url}")

        posters.append({
            "movieId": movie_id,
            "title": title_raw,
            "clean_title": title,
            "year": year,
            "genres": genres,
            "poster_url": poster_url
        })

        time.sleep(0.35)  # respect OMDb free rate

    df = pd.DataFrame(posters)
    df["poster_url"] = df["poster_url"].fillna("")  # ensure no float NaN
    df.to_csv("preloaded_posters.csv", index=False)
    print("✅ Posters saved to preloaded_posters.csv")
