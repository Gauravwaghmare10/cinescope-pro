import streamlit as st
import pandas as pd
import requests
import re

# 🌍 OMDb API credentials
OMDB_API_KEY = "26a45e26"
OMDB_URL = "http://www.omdbapi.com/"

# Page configuration
st.set_page_config(page_title="🎬 Movie Recommender Deluxe", layout="wide")

# App Header
st.markdown(
    """
    <h1 style='text-align: center; color: #e50914;'>🍿 Movie Explorer Deluxe</h1>
    <p style='text-align:center; color: #444;'>Discover movies effortlessly — with posters, genres, ratings and more.</p>
    <hr style='margin-top:10px; margin-bottom:30px;'>
    """,
    unsafe_allow_html=True
)

def clean_title(title):
    match = re.match(r"^(.*?)\s*\((\d{4})\)", title)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return title.strip(), None

@st.cache_data
def load_movies():
    df = pd.read_csv("movies.csv")
    df = df[df["genres"].notna()]
    df["year"] = df["title"].apply(lambda x: re.findall(r"\((\d{4})\)", x))
    df["year"] = df["year"].apply(lambda x: int(x[0]) if x else None)
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df.drop_duplicates(subset=["movieId"])
    return df

@st.cache_data
def get_all_genres(df):
    return sorted({g for genres in df["genres"].str.split("|") for g in genres if g})

@st.cache_data(show_spinner=False)
def fetch_movie_info(title, year):
    params = {
        "apikey": OMDB_API_KEY,
        "t": title,
        "y": year
    }
    try:
        response = requests.get(OMDB_URL, params=params, timeout=5)
        data = response.json()
        poster = data.get("Poster", "")
        if not poster or poster == "N/A":
            poster = "https://via.placeholder.com/200x300?text=No+Image"
        ratings = data.get("Ratings", [])
        if ratings:
            ratings_str = "<br>".join([f"<b>{r['Source']}</b>: {r['Value']}" for r in ratings])
        else:
            ratings_str = "<span style='color:#999;'>No ratings available.</span>"
        return poster, ratings_str
    except:
        return "https://via.placeholder.com/200x300?text=No+Image", "<span style='color:#999;'>No ratings available.</span>"

# Load and prepare data
movies_df = load_movies()
all_genres = get_all_genres(movies_df)
all_years = sorted(movies_df["year"].unique())

# Sidebar filters
st.sidebar.markdown(
    "<div style='padding:20px 10px; background-color:#f9f9f9; border-radius:10px;'>"
    "<h3 style='margin-bottom:0;'>🔍 Filter Movies</h3>",
    unsafe_allow_html=True
)
selected_genres = st.sidebar.multiselect("🎭 Select Genres", options=all_genres)
selected_years = st.sidebar.multiselect("📅 Select Year(s)", options=all_years)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Show recommendations
if st.sidebar.button("🎥 Show Recommendations"):
    with st.spinner("⏳ Fetching movies..."):
        filtered = movies_df.copy()
        if selected_genres:
            filtered = filtered[filtered["genres"].apply(lambda g: all(genre in g for genre in selected_genres))]
        if selected_years:
            filtered = filtered[filtered["year"].isin(selected_years)]

        filtered = filtered.drop_duplicates("title").sort_values(by=["year", "title"])
        st.subheader(f"{len(filtered)} movie(s) found")

        if filtered.empty:
            st.warning("🙁 No movies match your filters.")
        else:
            for _, movie in filtered.head(30).iterrows():
                clean_name, clean_year = clean_title(movie["title"])
                poster_url, omdb_ratings = fetch_movie_info(clean_name, clean_year)

                st.markdown(f"""
                <div style='display:flex; gap: 20px; margin-bottom:30px; padding:15px;
                            border-radius:15px; background: #ffffff; box-shadow:0 4px 12px rgba(0,0,0,0.08);'>
                    <div style='flex-shrink:0'>
                        <img src="{poster_url}" width='120' style='border-radius:10px; object-fit:cover;' />
                    </div>
                    <div>
                        <h3 style='margin-bottom:4px;'>🎬 {movie['title']}</h3>
                        <div style='color:#555; margin-bottom:10px; font-size:15px;'>
                            📅 <b>Year:</b> {movie['year']} &nbsp; | &nbsp; 🎭 <b>Genres:</b> {movie['genres']}
                        </div>
                        <div style='font-size:15px;'>
                            <b>🌐 OMDb Ratings:</b><br>{omdb_ratings}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
