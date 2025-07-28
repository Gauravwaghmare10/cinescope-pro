import streamlit as st
import os
import pandas as pd
import requests
import re
import time

# 🌍 Use OMDb API from environment variable
OMDB_API_KEY = os.getenv("OMDB_API_KEY")  # Set this in Streamlit secrets
OMDB_URL = "http://www.omdbapi.com/"

# Streamlit page config
st.set_page_config(page_title="🎬 CineScope Pro", layout="wide", initial_sidebar_state="expanded")

# Load and clean movies
@st.cache_data
def load_movies():
    df = pd.read_csv("movies.csv")
    df = df[df["genres"].notna()]
    df["year"] = df["title"].str.extract(r"\((\d{4})\)")
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df.drop_duplicates(subset=["movieId"])
    return df

@st.cache_data
def get_all_genres(df):
    return sorted({genre for sublist in df["genres"].str.split("|") for genre in sublist})

def clean_title(title):
    match = re.match(r"^(.*?)\s*\((\d{4})\)", title)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return title.strip(), None

@st.cache_data(show_spinner=False)
def fetch_movie_info_with_rating(title, year):
    params = {"apikey": OMDB_API_KEY, "t": title, "y": year}
    try:
        response = requests.get(OMDB_URL, params=params, timeout=5)
        data = response.json()
        poster = data.get("Poster", "") or "https://via.placeholder.com/140x200/667eea/ffffff?text=No+Image"
        ratings = data.get("Ratings", [])
        rating_text = []
        numeric_rating = 0

        for r in ratings:
            source, value = r["Source"], r["Value"]
            if "Internet Movie Database" in source:
                imdb = re.search(r"(\d+\.?\d*)", value)
                if imdb:
                    numeric_rating = float(imdb.group(1))
                rating_text.append(f"⭐ IMDb: {value}")
            elif "Rotten Tomatoes" in source:
                rt = re.search(r"(\d+)", value)
                if rt:
                    numeric_rating = max(numeric_rating, float(rt.group(1)) / 10)
                rating_text.append(f"🍅 RT: {value}")
            elif "Metacritic" in source:
                meta = re.search(r"(\d+)", value)
                if meta:
                    numeric_rating = max(numeric_rating, float(meta.group(1)) / 10)
                rating_text.append(f"📊 Metacritic: {value}")
            else:
                rating_text.append(f"{source}: {value}")

        return poster, ", ".join(rating_text), numeric_rating
    except:
        return "https://via.placeholder.com/140x200/667eea/ffffff?text=No+Image", "No ratings", 0

def get_rating_color(rating):
    if rating >= 7:
        return "#27ae60"
    elif rating >= 5:
        return "#f39c12"
    else:
        return "#e74c3c"

# Load data
movies_df = load_movies()
all_genres = get_all_genres(movies_df)
all_years = sorted(movies_df["year"].unique())

# Sidebar filters
st.sidebar.title("🎯 Smart Filters")
selected_genres = st.sidebar.multiselect("🎭 Choose Genres", options=all_genres)
selected_years = st.sidebar.multiselect("📅 Select Years", options=all_years)
sort_option = st.sidebar.selectbox("🏆 Sort Movies By", ["Default (Year & Title)", "Highest Rated First", "Lowest Rated First"])
max_results = st.sidebar.slider("📊 Number of Results", 10, 100, 30, 10)

# Discover button
if st.sidebar.button("🚀 Discover Movies"):
    with st.spinner("Fetching movies..."):
        filtered = movies_df.copy()
        if selected_genres:
            filtered = filtered[filtered["genres"].apply(lambda g: all(genre in g for genre in selected_genres))]
        if selected_years:
            filtered = filtered[filtered["year"].isin(selected_years)]

        if filtered.empty:
            st.error("No movies found. Try changing filters.")
        else:
            movie_data = []
            for _, row in filtered.iterrows():
                title, year = clean_title(row["title"])
                poster, ratings, score = fetch_movie_info_with_rating(title, year)
                movie_data.append((row["title"], row["genres"], row["year"], poster, ratings, score))

            if sort_option == "Highest Rated First":
                movie_data.sort(key=lambda x: x[5], reverse=True)
            elif sort_option == "Lowest Rated First":
                movie_data.sort(key=lambda x: x[5])

            st.markdown("## 🎥 Top Recommendations")
            for title, genres, year, poster, ratings, score in movie_data[:max_results]:
                st.markdown(f"### {title} ({year})")
                cols = st.columns([1, 3])
                with cols[0]:
                    st.image(poster, width=140)
                with cols[1]:
                    st.write(f"**Genres:** {genres}")
                    st.write(f"**Ratings:** {ratings}")
                    st.markdown(f"<span style='color:{get_rating_color(score)}'><b>⭐ Score:</b> {score:.1f}</span>", unsafe_allow_html=True)

# Feature Highlights Section
st.markdown("---")
st.markdown("## ✨ Features")

st.markdown("""
#### 🎯 Smart Discovery
- Filter by genre & year  
- Multiple sort options  
- Customizable results  

#### 📊 Rich Details
- IMDb ratings & votes  
- Box office data  
- Cast & crew info  

#### 🎬 Great Experience
- High-quality posters  
- Detailed plot summaries  
- Awards information  
""")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<center>Built with ❤️ using Streamlit • Powered by OMDb API</center>", unsafe_allow_html=True)
