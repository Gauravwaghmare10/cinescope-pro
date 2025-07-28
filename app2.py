import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="CineScope Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .movie-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
OMDB_API_KEY = "26a45e26"  # Your OMDb API key
OMDB_URL = "http://www.omdbapi.com/"

def search_movies_omdb(query, max_results=3):
    """Search for movies using OMDb API and return top 3 highest rated"""
    movies = []
    page = 1
    
    while len(movies) < max_results and page <= 10:  # Limit pages to avoid infinite loop
        try:
            params = {
                'apikey': OMDB_API_KEY,
                's': query,
                'type': 'movie',
                'page': page
            }
            
            response = requests.get(OMDB_URL, params=params, timeout=10)
            data = response.json()
            
            if data.get('Response') == 'True' and 'Search' in data:
                for movie in data['Search']:
                    # Get detailed info for rating
                    detailed_info = get_movie_details(movie['imdbID'])
                    if detailed_info and detailed_info.get('imdbRating') != 'N/A':
                        try:
                            rating = float(detailed_info['imdbRating'])
                            movie['imdbRating'] = rating
                            movies.append(movie)
                        except (ValueError, TypeError):
                            continue
                
                page += 1
            else:
                break
                
        except requests.exceptions.RequestException:
            break
    
    # Sort by IMDb rating (highest first) and return top 3
    movies.sort(key=lambda x: x.get('imdbRating', 0), reverse=True)
    return movies[:3]

def get_movie_details(imdb_id):
    """Get detailed movie information"""
    try:
        params = {
            'apikey': OMDB_API_KEY,
            'i': imdb_id,
            'plot': 'full'
        }
        
        response = requests.get(OMDB_URL, params=params, timeout=10)
        return response.json()
    except requests.exceptions.RequestException:
        return None

def display_movie_details(movie_data):
    """Display detailed movie information"""
    if not movie_data or movie_data.get('Response') == 'False':
        st.error("❌ Movie details not found!")
        return
    
    # Main movie info
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if movie_data.get('Poster') and movie_data['Poster'] != 'N/A':
            st.image(movie_data['Poster'], width=300)
        else:
            st.image("https://via.placeholder.com/300x450?text=No+Image", width=300)
    
    with col2:
        st.markdown(f"# {movie_data['Title']}")
        st.markdown(f"**Year:** {movie_data.get('Year', 'N/A')}")
        st.markdown(f"**Genre:** {movie_data.get('Genre', 'N/A')}")
        st.markdown(f"**Director:** {movie_data.get('Director', 'N/A')}")
        st.markdown(f"**Runtime:** {movie_data.get('Runtime', 'N/A')}")
        st.markdown(f"**Language:** {movie_data.get('Language', 'N/A')}")
        st.markdown(f"**Country:** {movie_data.get('Country', 'N/A')}")
    
    # Ratings section
    st.markdown("## 📊 Ratings & Reviews")
    
    rating_cols = st.columns(4)
    
    with rating_cols[0]:
        imdb_rating = movie_data.get('imdbRating', 'N/A')
        st.markdown(f"""
        <div class="metric-container">
            <h3>⭐ IMDb</h3>
            <h2>{imdb_rating}/10</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with rating_cols[1]:
        votes = movie_data.get('imdbVotes', 'N/A')
        st.markdown(f"""
        <div class="metric-container">
            <h3>🗳️ Votes</h3>
            <h2>{votes}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with rating_cols[2]:
        metascore = movie_data.get('Metascore', 'N/A')
        st.markdown(f"""
        <div class="metric-container">
            <h3>📈 Metascore</h3>
            <h2>{metascore}/100</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with rating_cols[3]:
        box_office = movie_data.get('BoxOffice', 'N/A')
        st.markdown(f"""
        <div class="metric-container">
            <h3>💰 Box Office</h3>
            <h2>{box_office}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Plot section
    st.markdown("## 📖 Plot")
    plot = movie_data.get('Plot', 'No plot available.')
    st.markdown(f"*{plot}*")
    
    # Cast and Crew
    st.markdown("## 👥 Cast & Crew")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Director:** {movie_data.get('Director', 'N/A')}")
        st.markdown(f"**Writer:** {movie_data.get('Writer', 'N/A')}")
    
    with col2:
        st.markdown(f"**Actors:** {movie_data.get('Actors', 'N/A')}")
    
    # Additional Info
    if movie_data.get('Awards') and movie_data['Awards'] != 'N/A':
        st.markdown("## 🏆 Awards")
        st.markdown(f"*{movie_data['Awards']}*")

# Main App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 CineScope Pro</h1>
        <p>Discover the top 3 highest-rated movies with intelligent recommendations and detailed insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## 🔧 Search Options")
    
    # Search input
    search_query = st.sidebar.text_input(
        "🔍 Search Movies",
        placeholder="Enter movie title, genre, or keyword...",
        help="Type any movie name, genre, or keyword to find top-rated movies"
    )
    
    # Genre filter
    selected_genre = st.sidebar.selectbox(
        "🎭 Filter by Genre",
        ["All Genres", "Action", "Adventure", "Animation", "Biography", "Comedy", 
         "Crime", "Documentary", "Drama", "Family", "Fantasy", "History", 
         "Horror", "Music", "Mystery", "Romance", "Sci-Fi", "Sport", 
         "Thriller", "War", "Western"]
    )
    
    # Year range
    year_range = st.sidebar.slider(
        "📅 Year Range",
        min_value=1900,
        max_value=2024,
        value=(2000, 2024),
        help="Filter movies by release year"
    )
    
    # Initialize session state
    if 'selected_movie' not in st.session_state:
        st.session_state.selected_movie = None
    
    # Main content
    if st.session_state.selected_movie:
        # Show movie details
        if st.button("⬅️ Back to Search Results"):
            st.session_state.selected_movie = None
            st.rerun()
        
        with st.spinner("🎬 Loading movie details..."):
            movie_details = get_movie_details(st.session_state.selected_movie)
            display_movie_details(movie_details)
    
    else:
        # Search functionality
        if search_query:
            with st.spinner("🔍 Searching for top-rated movies..."):
                movies = search_movies_omdb(search_query)
                
            if movies:
                st.success(f"✨ Found top 3 highest-rated movies for '{search_query}'")
                
                # Display movies
                for i, movie in enumerate(movies, 1):
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            if movie.get('Poster') and movie['Poster'] != 'N/A':
                                st.image(movie['Poster'], width=150)
                            else:
                                st.image("https://via.placeholder.com/150x225?text=No+Image", width=150)
                        
                        with col2:
                            st.markdown(f"### {i}. {movie['Title']} ({movie['Year']})")
                            st.markdown(f"**⭐ IMDb Rating:** {movie.get('imdbRating', 'N/A')}/10")
                            
                            if st.button(f"📖 View Details", key=f"details_{movie['imdbID']}"):
                                st.session_state.selected_movie = movie['imdbID']
                                st.rerun()
                        
                        st.markdown("---")
            else:
                st.warning("🔍 No movies found. Try different keywords!")
        
        else:
            # Welcome screen
            st.markdown("""
            ### 🌟 Welcome to CineScope Pro!
            
            **How to use:**
            1. 🔍 Enter a movie title, genre, or keyword in the search box
            2. 📊 Automatically get the top 3 highest-rated movies
            3. 📖 Click "View Details" for comprehensive movie information
            4. 🎭 Use filters to refine your search
            
            **Features:**
            - ⭐ Automatic sorting by IMDb ratings
            - 📈 Comprehensive movie details and ratings
            - 🎬 High-quality movie posters
            - 📊 Box office and awards information
            - 🔍 Advanced search and filtering options
            
            Start by typing a movie name in the sidebar! 🍿
            """)
            
            # Sample searches
            st.markdown("### 🎯 Try these popular searches:")
            
            sample_cols = st.columns(3)
            
            with sample_cols[0]:
                if st.button("🦸‍♂️ Superhero Movies", use_container_width=True):
                    st.session_state.search_sample = "superhero"
            
            with sample_cols[1]:
                if st.button("🚀 Sci-Fi Classics", use_container_width=True):
                    st.session_state.search_sample = "science fiction"
            
            with sample_cols[2]:
                if st.button("🎭 Oscar Winners", use_container_width=True):
                    st.session_state.search_sample = "oscar"

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>🎬 CineScope Pro - Your Ultimate Movie Discovery Platform</p>
        <p>Made with ❤️ using Streamlit and OMDb API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
