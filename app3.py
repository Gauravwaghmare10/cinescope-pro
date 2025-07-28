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
    .discover-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 2px solid #667eea;
        border-radius: 25px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 20px 0;
    }
    .discover-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    .smart-filters-header {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
OMDB_API_KEY = "26a45e26"  # Your OMDb API key
OMDB_URL = "http://www.omdbapi.com/"

def discover_movies_by_filters(genre="", year="", sort_by="popularity", max_results=10):
    """Discover movies based on filters"""
    movies = []
    
    # Popular movie keywords by genre for discovery
    genre_keywords = {
        "Action": ["action", "adventure", "superhero", "mission"],
        "Comedy": ["comedy", "funny", "humor", "laugh"],
        "Drama": ["drama", "life", "story", "human"],
        "Horror": ["horror", "scary", "thriller", "dark"],
        "Romance": ["love", "romance", "romantic", "heart"],
        "Sci-Fi": ["science", "future", "space", "technology"],
        "Fantasy": ["magic", "fantasy", "wizard", "dragon"],
        "Crime": ["crime", "detective", "police", "murder"],
        "Documentary": ["documentary", "real", "true", "life"],
        "Animation": ["animation", "cartoon", "animated", "kids"]
    }
    
    # Use genre keyword for search if genre is selected
    search_term = "movie"
    if genre and genre != "All Genres":
        keywords = genre_keywords.get(genre, [genre.lower()])
        search_term = keywords[0]
    
    page = 1
    while len(movies) < max_results and page <= 5:
        try:
            params = {
                'apikey': OMDB_API_KEY,
                's': search_term,
                'type': 'movie',
                'page': page
            }
            
            # Add year filter if specified
            if year and year != "All Years":
                params['y'] = year
            
            response = requests.get(OMDB_URL, params=params, timeout=10)
            data = response.json()
            
            if data.get('Response') == 'True' and 'Search' in data:
                for movie in data['Search']:
                    if len(movies) < max_results:
                        # Get detailed info for sorting
                        detailed_info = get_movie_details(movie['imdbID'])
                        if detailed_info:
                            movie.update(detailed_info)
                            movies.append(movie)
                page += 1
            else:
                break
                
        except requests.exceptions.RequestException:
            break
    
    # Sort movies based on selected criteria
    if sort_by == "rating" and movies:
        movies = [m for m in movies if m.get('imdbRating') != 'N/A']
        movies.sort(key=lambda x: float(x.get('imdbRating', 0)), reverse=True)
    elif sort_by == "year" and movies:
        movies.sort(key=lambda x: int(x.get('Year', 0)), reverse=True)
    elif sort_by == "title" and movies:
        movies.sort(key=lambda x: x.get('Title', ''))
    
    return movies

def search_movies_omdb(query, max_results=10):
    """Search for movies using OMDb API"""
    movies = []
    page = 1
    
    while len(movies) < max_results and page <= 10:
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
                    if len(movies) < max_results:
                        movies.append(movie)
                page += 1
            else:
                break
                
        except requests.exceptions.RequestException:
            break
    
    return movies

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
        <p>Discover exceptional cinema with intelligent recommendations and detailed insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Smart Filters
    st.sidebar.markdown("""
    <div class="smart-filters-header">
        <h3>🎯 Smart Filters</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Genre filter
    selected_genre = st.sidebar.selectbox(
        "🎭 Genre",
        ["All Genres", "Action", "Adventure", "Animation", "Biography", "Comedy", 
         "Crime", "Documentary", "Drama", "Family", "Fantasy", "History", 
         "Horror", "Music", "Mystery", "Romance", "Sci-Fi", "Sport", 
         "Thriller", "War", "Western"],
        help="Filter movies by genre"
    )
    
    # Year filter (discrete years)
    years = ["All Years"] + [str(year) for year in range(2024, 1979, -1)]
    selected_year = st.sidebar.selectbox(
        "📅 Year",
        years,
        help="Filter movies by release year"
    )
    
    # Sort order
    sort_order = st.sidebar.selectbox(
        "📊 Sort by",
        ["popularity", "rating", "year", "title"],
        help="Choose how to sort the results"
    )
    
    # Number of results
    num_results = st.sidebar.selectbox(
        "📋 Results",
        options=[5, 10, 15, 20],
        index=1,
        help="Number of movies to display"
    )
    
    # Discover Movies Button
    st.sidebar.markdown("---")
    discover_clicked = st.sidebar.button(
        "🚀 Discover Movies",
        use_container_width=True,
        help="Find movies based on your filters"
    )
    
    # Initialize session state
    if 'selected_movie' not in st.session_state:
        st.session_state.selected_movie = None
    if 'discovered_movies' not in st.session_state:
        st.session_state.discovered_movies = []
    
    # Main content
    if st.session_state.selected_movie:
        # Show movie details
        if st.button("⬅️ Back to Results"):
            st.session_state.selected_movie = None
            st.rerun()
        
        with st.spinner("🎬 Loading movie details..."):
            movie_details = get_movie_details(st.session_state.selected_movie)
            display_movie_details(movie_details)
    
    else:
        # Handle discover button click
        if discover_clicked:
            with st.spinner("🔍 Discovering movies based on your filters..."):
                movies = discover_movies_by_filters(
                    genre=selected_genre,
                    year=selected_year,
                    sort_by=sort_order,
                    max_results=num_results
                )
                st.session_state.discovered_movies = movies
        
        # Display discovered movies
        if st.session_state.discovered_movies:
            movies = st.session_state.discovered_movies
            
            # Filter info
            filter_info = []
            if selected_genre != "All Genres":
                filter_info.append(f"Genre: {selected_genre}")
            if selected_year != "All Years":
                filter_info.append(f"Year: {selected_year}")
            filter_info.append(f"Sorted by: {sort_order}")
            
            st.success(f"✨ Found {len(movies)} movies | {' | '.join(filter_info)}")
            
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
                        st.markdown(f"### {movie['Title']} ({movie.get('Year', 'N/A')})")
                        
                        # Show rating if available
                        if movie.get('imdbRating') and movie['imdbRating'] != 'N/A':
                            st.markdown(f"**⭐ Rating:** {movie['imdbRating']}/10")
                        
                        # Show genre
                        if movie.get('Genre'):
                            st.markdown(f"**🎭 Genre:** {movie['Genre']}")
                        
                        if st.button(f"📖 View Details", key=f"details_{movie['imdbID']}"):
                            st.session_state.selected_movie = movie['imdbID']
                            st.rerun()
                    
                    st.markdown("---")
        
        else:
            # Welcome screen
            st.markdown("""
            ### 🌟 Welcome to CineScope Pro!
            
            **How to use:**
            1. 🎯 Use the Smart Filters in the sidebar to set your preferences
            2. 🚀 Click "Discover Movies" to find films matching your criteria
            3. 📖 Click "View Details" for comprehensive movie information
            4. 📊 Sort results by popularity, rating, year, or title
            
            **Smart Filters:**
            - 🎭 **Genre**: Choose from 20+ movie genres
            - 📅 **Year**: Select specific release years (1980-2024)
            - 📊 **Sort**: Order by popularity, rating, year, or title
            - 📋 **Results**: Control how many movies to display
            
            Configure your filters and click "Discover Movies" to start! 🍿
            """)
            
            # Feature highlights
            st.markdown("### ✨ Features:")
            
            feature_cols = st.columns(3)
            
            with feature_cols[0]:
                st.markdown("""
                **🎯 Smart Discovery**
                - Filter by genre & year
                - Multiple sort options
                - Customizable results
                """)
            
            with feature_cols[1]:
                st.markdown("""
                **📊 Rich Details**
                - IMDb ratings & votes
                - Box office data
                - Cast & crew info
                """)
            
            with feature_cols[2]:
                st.markdown("""
                **🎬 Great Experience**
                - High-quality posters
                - Detailed plot summaries
                - Awards information
                """)

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
