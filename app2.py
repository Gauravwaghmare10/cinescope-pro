import streamlit as st
import os
import pandas as pd
import requests
import re
import time

# 🌍 OMDb API credentials
OMDB_API_KEY = os.getenv("OMDB_API_KEY")  # Set this on Streamlit Cloud
OMDB_URL = "http://www.omdbapi.com/"

# Page configuration with custom theme
st.set_page_config(
    page_title="🎬 CineScope Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Global Styles */
    .main {
        padding-top: 2rem;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        color: rgba(255,255,255,0.9);
        font-weight: 300;
        margin-bottom: 0;
    }
    
    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .filter-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .filter-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Movie Card Styling */
    .movie-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        border: 1px solid #f1f5f9;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .movie-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .movie-content {
        display: flex;
        gap: 1.5rem;
        align-items: flex-start;
    }
    
    .movie-poster {
        flex-shrink: 0;
        position: relative;
    }
    
    .poster-image {
        width: 140px;
        height: 200px;
        border-radius: 12px;
        object-fit: cover;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
    }
    
    .poster-image:hover {
        transform: scale(1.05);
    }
    
    .movie-info {
        flex: 1;
        min-width: 0;
    }
    
    .movie-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.8rem;
        line-height: 1.3;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .movie-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: #f8fafc;
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #4a5568;
        border: 1px solid #e2e8f0;
    }
    
    .meta-label {
        font-weight: 600;
        color: #2d3748;
    }
    
    .ratings-container {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    
    .ratings-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .ratings-content {
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Stats Banner */
    .stats-banner {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.3);
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .empty-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #4a5568;
        margin-bottom: 0.5rem;
    }
    
    .empty-subtitle {
        font-family: 'Inter', sans-serif;
        color: #718096;
        font-size: 1rem;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Loading Spinner */
    .stSpinner {
        color: #667eea !important;
    }
    
    /* Progress Bar Styling */
    .stProgress .st-bo {
        background-color: #667eea;
    }
    
    /* Rating Badge */
    .rating-badge {
        font-size: 0.9rem;
        padding: 0.3rem 0.6rem;
        border-radius: 8px;
        font-weight: 600;
        margin-left: 1rem;
        color: white;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .movie-content {
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        
        .movie-meta {
            justify-content: center;
        }
        
        .movie-title {
            justify-content: center;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced header
st.markdown("""
<div class="main-header">
    <div class="main-title">🎬 CineScope Pro</div>
    <div class="main-subtitle">Discover exceptional cinema with intelligent recommendations and detailed insights</div>
</div>
""", unsafe_allow_html=True)

def clean_title(title):
    """Extract clean title and year from movie title string"""
    match = re.match(r"^(.*?)\s*\((\d{4})\)", title)
    if match:
        return match.group(1).strip(), int(match.group(2))
    return title.strip(), None

@st.cache_data
def load_movies():
    """Load and preprocess movies data"""
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
    """Extract all unique genres from the dataset"""
    return sorted({g for genres in df["genres"].str.split("|") for g in genres if g})

@st.cache_data(show_spinner=False)
def fetch_movie_info_with_rating(title, year):
    """Fetch movie info from OMDb API and return poster, ratings display, and numeric score"""
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
            poster = "https://via.placeholder.com/140x200/667eea/ffffff?text=No+Image"
        
        ratings = data.get("Ratings", [])
        numeric_rating = 0
        
        if ratings:
            rating_items = []
            for r in ratings:
                source = r['Source']
                value = r['Value']
                
                # Extract numeric value for sorting
                if 'Internet Movie Database' in source:
                    rating_match = re.search(r'(\d+\.?\d*)', value)
                    if rating_match:
                        numeric_rating = max(numeric_rating, float(rating_match.group(1)))
                    rating_items.append(f"<span style='color:#f39c12;'>⭐ IMDb:</span> <strong>{value}</strong>")
                elif 'Rotten Tomatoes' in source:
                    rating_match = re.search(r'(\d+)', value)
                    if rating_match:
                        rt_score = float(rating_match.group(1)) / 10  # Convert to 10-point scale
                        numeric_rating = max(numeric_rating, rt_score)
                    rating_items.append(f"<span style='color:#e74c3c;'>🍅 RT:</span> <strong>{value}</strong>")
                elif 'Metacritic' in source:
                    rating_match = re.search(r'(\d+)', value)
                    if rating_match:
                        meta_score = float(rating_match.group(1)) / 10  # Convert to 10-point scale
                        numeric_rating = max(numeric_rating, meta_score)
                    rating_items.append(f"<span style='color:#9b59b6;'>📊 Meta:</span> <strong>{value}</strong>")
                else:
                    rating_items.append(f"<span style='color:#34495e;'>📈 {source}:</span> <strong>{value}</strong>")
            
            ratings_str = "<br>".join(rating_items)
        else:
            ratings_str = "<span style='color:#95a5a6;'>📭 No ratings available</span>"
        
        return poster, ratings_str, numeric_rating
    except Exception as e:
        return "https://via.placeholder.com/140x200/667eea/ffffff?text=No+Image", "<span style='color:#95a5a6;'>📭 No ratings available</span>", 0

def get_rating_color(rating):
    """Return color based on rating score"""
    if rating >= 7:
        return "#27ae60"  # Green for high ratings
    elif rating >= 5:
        return "#f39c12"  # Orange for medium ratings
    else:
        return "#e74c3c"  # Red for low ratings

# Load and prepare data
movies_df = load_movies()
all_genres = get_all_genres(movies_df)
all_years = sorted(movies_df["year"].unique())

# Enhanced sidebar filters
st.sidebar.markdown("""
<div class="filter-container">
    <div class="filter-title">🎯 Smart Filters</div>
</div>
""", unsafe_allow_html=True)

selected_genres = st.sidebar.multiselect(
    "🎭 Choose Genres", 
    options=all_genres,
    help="Select one or more genres to filter movies"
)

selected_years = st.sidebar.multiselect(
    "📅 Select Years", 
    options=all_years,
    help="Choose specific years or leave empty for all years"
)

# Add sorting options
st.sidebar.markdown("<br>", unsafe_allow_html=True)
sort_option = st.sidebar.selectbox(
    "🏆 Sort Movies By",
    options=["Default (Year & Title)", "Highest Rated First", "Lowest Rated First"],
    help="Choose how to sort the movie results"
)

# Add number of results limit
max_results = st.sidebar.slider(
    "📊 Number of Results",
    min_value=10,
    max_value=100,
    value=30,
    step=10,
    help="Maximum number of movies to display"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Enhanced recommendation button and results
if st.sidebar.button("🚀 Discover Movies", help="Click to find movies based on your filters"):
    with st.spinner("🔍 Analyzing your preferences and fetching movie data..."):
        filtered = movies_df.copy()
        
        # Apply filters
        if selected_genres:
            filtered = filtered[filtered["genres"].apply(lambda g: all(genre in g for genre in selected_genres))]
        
        if selected_years:
            filtered = filtered[filtered["year"].isin(selected_years)]

        filtered = filtered.drop_duplicates("title")
        
        if filtered.empty:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🎭</div>
                <div class="empty-title">No Movies Found</div>
                <div class="empty-subtitle">Try adjusting your filters to discover more movies</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Fetch ratings for all movies if sorting by rating
            if sort_option in ["Highest Rated First", "Lowest Rated First"]:
                movie_data = []
                total_movies = min(len(filtered), max_results * 2)  # Fetch more to account for movies without ratings
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, (_, movie) in enumerate(filtered.head(total_movies).iterrows()):
                    status_text.text(f"🎬 Fetching ratings... ({idx + 1}/{total_movies})")
                    progress_bar.progress((idx + 1) / total_movies)
                    
                    clean_name, clean_year = clean_title(movie["title"])
                    poster_url, omdb_ratings, numeric_rating = fetch_movie_info_with_rating(clean_name, clean_year)
                    
                    movie_data.append({
                        'movie': movie,
                        'poster_url': poster_url,
                        'omdb_ratings': omdb_ratings,
                        'numeric_rating': numeric_rating
                    })
                    
                    # Small delay to avoid API rate limits
                    time.sleep(0.1)
                
                progress_bar.empty()
                status_text.empty()
                
                # Sort by rating
                if sort_option == "Highest Rated First":
                    movie_data.sort(key=lambda x: x['numeric_rating'], reverse=True)
                else:  # Lowest Rated First
                    movie_data.sort(key=lambda x: x['numeric_rating'])
                    
            else:
                # Default sorting
                filtered = filtered.sort_values(by=["year", "title"])
                movie_data = []
                for _, movie in filtered.head(max_results).iterrows():
                    clean_name, clean_year = clean_title(movie["title"])
                    poster_url, omdb_ratings, numeric_rating = fetch_movie_info_with_rating(clean_name, clean_year)
                    movie_data.append({
                        'movie': movie,
                        'poster_url': poster_url,
                        'omdb_ratings': omdb_ratings,
                        'numeric_rating': numeric_rating
                    })

            # Stats banner with sorting info
            sort_info = ""
            if sort_option == "Highest Rated First":
                sort_info = " • Sorted by Highest Ratings 📈"
                if movie_data:
                    avg_rating = sum(item['numeric_rating'] for item in movie_data if item['numeric_rating'] > 0) / len([item for item in movie_data if item['numeric_rating'] > 0])
                    sort_info += f" • Avg: {avg_rating:.1f}⭐"
            elif sort_option == "Lowest Rated First":
                sort_info = " • Sorted by Lowest Ratings 📉"
                
            st.markdown(f"""
            <div class="stats-banner">
                🎯 Found {len(movie_data)} movies matching your criteria{sort_info}
            </div>
            """, unsafe_allow_html=True)

            # Display movies (limit to max_results)
            displayed_count = 0
            for item in movie_data:
                if displayed_count >= max_results:
                    break
                    
                movie = item['movie']
                poster_url = item['poster_url']
                omdb_ratings = item['omdb_ratings']
                numeric_rating = item['numeric_rating']
                
                # Split genres for better display
                genres_list = movie["genres"].split("|")
                genres_html = " ".join([f"<span style='background:#e2e8f0; color:#4a5568; padding:0.2rem 0.5rem; border-radius:6px; font-size:0.8rem; margin-right:0.3rem;'>{genre}</span>" for genre in genres_list])
                
                # Add rating badge if available
                rating_badge = ""
                if numeric_rating > 0:
                    color = get_rating_color(numeric_rating)
                    rating_badge = f"<span class='rating-badge' style='background:{color};'>⭐ {numeric_rating:.1f}</span>"

                st.markdown(f"""
                <div class="movie-card">
                    <div class="movie-content">
                        <div class="movie-poster">
                            <img src="{poster_url}" class="poster-image" alt="{movie['title']} poster" />
                        </div>
                        <div class="movie-info">
                            <div class="movie-title">
                                <span>{movie['title']}</span>
                                {rating_badge}
                            </div>
                            <div class="movie-meta">
                                <div class="meta-item">
                                    <span>📅</span>
                                    <span class="meta-label">Year:</span>
                                    <span>{movie['year']}</span>
                                </div>
                                <div class="meta-item">
                                    <span>🎭</span>
                                    <span class="meta-label">Genres:</span>
                                </div>
                            </div>
                            <div style="margin-bottom: 1rem;">
                                {genres_html}
                            </div>
                            <div class="ratings-container">
                                <div class="ratings-title">
                                    <span>🌟</span>
                                    <span>Ratings & Reviews</span>
                                </div>
                                <div class="ratings-content">
                                    {omdb_ratings}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                displayed_count += 1

# Footer
st.markdown("""
<br><br>
<div style="text-align: center; padding: 2rem; color: #718096; font-family: 'Inter', sans-serif;">
    <p>Built with ❤️ using Streamlit • Powered by OMDb API</p>
    <p style="font-size: 0.9rem; margin-top: 0.5rem;">
        🎬 Discover • 🌟 Rate • 📱 Share • 🍿 Enjoy
    </p>
</div>
""", unsafe_allow_html=True)
