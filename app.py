import streamlit as st 
import pandas as pd   #excel file lai manipulate garney
import requests      
import pickle
import base64
import os
import hashlib
from datetime import datetime
from textblob import TextBlob

API_KEY = "your_tmdb_api_key"  #add you own APi from TMDb website 
background_image_path = "1_qR08Jxq0IHdvFtBsUhCe3Q.jpg"

# Sentiment Analysis Functions
def analyze_sentiment(text):
    if pd.isna(text) or not isinstance(text, str) or not text.strip():
        return "Neutral", 0.0
     #If the text is missing, or not a string, or just blank/empty, then skip it and return Neutral.
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        if polarity > 0.1:
            return "Positive", polarity
        elif polarity < -0.1:
            return "Negative", polarity
        return "Neutral", polarity
    except:
        return "Neutral", 0.0

def get_sentiment_emoji(sentiment):
    if sentiment == "Positive":
        return "😊"
    elif sentiment == "Negative":
        return "😞"
    return "😐"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists("users.csv"):   #look os.path for users.csv
        return pd.read_csv("users.csv")   #if exists look for csv files
    return pd.DataFrame(columns=["username", "password"])   #if not exist make a frame for new register

def save_user(username, password):
    users = load_users()
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv("users.csv", index=False)
    return True

def authenticate(username, password):
    users = load_users()
    if username in users["username"].values:
        hashed = users.loc[users["username"] == username, "password"].values[0]
        return hashed == hash_password(password)   
    return False

def save_feedback(username, movie_title, feedback):
    file_path = "feedback.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=["username", "movie_title", "feedback"])
    
    mask = (df["username"] == username) & (df["movie_title"] == movie_title)
    if mask.any():
        df.loc[mask, "feedback"] = feedback   #df.loc select and update the data in dataframe
    else:
        new_row = pd.DataFrame([[username, movie_title, feedback]], columns=["username", "movie_title", "feedback"])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(file_path, index=False)

def save_user_review(username, movie_title, review_text, rating):
    file_path = "user_reviews.csv"
    sentiment, polarity = analyze_sentiment(review_text)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:
        df = pd.DataFrame(columns=["username", "movie_title", "review_text", "rating", "date", "sentiment", "polarity"])
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")#################### real Time ################# 
    new_row = pd.DataFrame([[username, movie_title, review_text, rating, current_date, sentiment, polarity]], 
                         columns=["username", "movie_title", "review_text", "rating", "date", "sentiment", "polarity"])
    df = pd.concat([df, new_row], ignore_index=True)   #concat reset prvious index and ignore index makes sure there is no duplicate index
    df.to_csv(file_path, index=False)

def update_user_review(username, movie_title, review_text, rating, review_index):
    file_path = "user_reviews.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if review_index < len(df):    # 0
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sentiment, polarity = analyze_sentiment(review_text)
            df.loc[review_index, "review_text"] = review_text
            df.loc[review_index, "rating"] = rating
            df.loc[review_index, "date"] = current_date
            df.loc[review_index, "sentiment"] = sentiment
            df.loc[review_index, "polarity"] = polarity
            df.to_csv(file_path, index=False)
            return True
    return False

def delete_user_review(review_index):
    file_path = "user_reviews.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if review_index < len(df):
            df = df.drop(review_index).reset_index(drop=True)#drop means delete the rows and reset.index means rearrnage the index
            df.to_csv(file_path, index=False)
            return True
    return False

def load_user_reviews(movie_title):###################to show review################## 
    if os.path.exists("user_reviews.csv"):
        df = pd.read_csv("user_reviews.csv")
        return df[df["movie_title"] == movie_title].to_dict('records')####Creates a filter to select only rows whereThe "movie_title" column matches the input movie_title and Converts the filtered results to a list of dictionaries each dictionary represents one review
    return []
#############################################################################################################


def get_recommendations(title):
    try:
        idx = movies[movies["title"] == title].index[0]   #Finds the index position of the requested movie in the DataFrame
        sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)[1:11]
        #enumerate(cosine_sim[idx]): Gets similarity scores for all movies 
# sorted(..., reverse=True): Sorts by similarity (most similar first)
# [1:11]: Skips first result (itself) and takes next 10

        movie_indices = [i[0] for i in sim_scores]
        return movies.iloc[movie_indices]
    except IndexError:
        st.error(f"Movie '{title}' not found in our database.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return pd.DataFrame()

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(url).json()
        return f"https://image.tmdb.org/t/p/w500{response.get('poster_path', '')}" if response.get("poster_path") else "https://via.placeholder.com/500x750?text=No+Image"
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {str(e)}")
        return "https://via.placeholder.com/500x750?text=No+Image"

def fetch_movie_details_by_id(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
        response = requests.get(url).json()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return {}

def fetch_cast(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
        response = requests.get(url).json()
        cast_list = []
        for c in response.get("cast", [])[:10]:
            person_url = f"https://api.themoviedb.org/3/person/{c['id']}?api_key={API_KEY}"
            person_response = requests.get(person_url).json()
            cast_list.append({
                "id": c["id"],
                "name": c["name"],
                "character": c.get("character", "N/A"),
                "profile_path": f"https://image.tmdb.org/t/p/w500{c.get('profile_path', '')}" if c.get('profile_path') else "https://via.placeholder.com/150x200?text=No+Image",
                "biography": person_response.get("biography", "No biography available."),
                "birthday": person_response.get("birthday", "N/A"),
                "place_of_birth": person_response.get("place_of_birth", "N/A"),
                "known_for_department": person_response.get("known_for_department", "N/A")
            })
        return cast_list
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching cast: {str(e)}")
        return []

def fetch_reviews(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={API_KEY}"
        response = requests.get(url).json()
        reviews = response.get("results", [])
        
        for review in reviews:
            if review.get('author_details', {}).get('avatar_path'):
                avatar_path = review['author_details']['avatar_path']
                if avatar_path.startswith('/http'):
                    review['author_details']['avatar_url'] = avatar_path[1:]
                else:
                    review['author_details']['avatar_url'] = f"https://image.tmdb.org/t/p/w45{avatar_path}" if avatar_path else None
            else:
                review['author_details']['avatar_url'] = None
            review['type'] = 'professional'
        return reviews
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching reviews: {str(e)}")
        return []

def get_base64_of_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("CSS file not found. Using default styles.")

def load_liked_movies(username):
    if os.path.exists("feedback.csv"):
        df = pd.read_csv("feedback.csv")
        liked = df[(df["username"] == username) & (df["feedback"] == "Like")]
        return liked["movie_title"].tolist()
    return []

# Load movie data
try:
    with open("movie_data.pkl", "rb") as file:
        movies, cosine_sim = pickle.load(file)
except FileNotFoundError:
    st.error("Movie data file not found. Please ensure 'movie_data.pkl' exists.")
    st.stop()
except Exception as e:
    st.error(f"Error loading movie data: {str(e)}")
    st.stop()

# UI Setup
background_base64 = get_base64_of_image(background_image_path)
st.set_page_config(page_title="Movie Recommender", layout="wide", page_icon="")
local_css("style.css")

if background_base64:
    st.markdown(f"""
        <style>
            .stApp {{
                background: url("data:image/jpeg;base64,{background_base64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .sentiment-positive {{
                color: #4CAF50;
                font-weight: bold;
            }}
            .sentiment-negative {{
                color: #F44336;
                font-weight: bold;
            }}
            .sentiment-neutral {{
                color: #FFC107;
                font-weight: bold;
            }}
        </style>
    """, unsafe_allow_html=True)

# Session State
if 'current_movie' not in st.session_state:
    st.session_state.current_movie = movies["title"].values[0] if not movies.empty else ""
if 'get_recs' not in st.session_state:
    st.session_state.get_recs = False
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'editing_review' not in st.session_state:
    st.session_state.editing_review = None
if 'show_review_form' not in st.session_state:
    st.session_state.show_review_form = False

# Sidebar
with st.sidebar:
    st.markdown("## User Login / Signup")

    if st.session_state.authenticated:
        st.success(f"Logged in as {st.session_state.username}")
        page = st.radio("Navigation", ["Home", "Liked Movies"])##############################################################liked movies##########################
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.get_recs = False
            st.session_state.editing_review = None
            st.session_state.show_review_form = False
            st.rerun()
    else:
        menu = st.radio("Choose", ["Login", "Signup"])
        page = "Home"

        if menu == "Signup":
            new_user = st.text_input("New Username")
            new_pass = st.text_input("New Password", type="password")######################eye########
            if st.button("Create Account"):
                if save_user(new_user, new_pass):
                    st.success("Account created successfully. Please login now.")
                else:
                    st.error("Username already exists.")####

        elif menu == "Login":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

# Main Content
if st.session_state.authenticated:
    if page == "Home":
        st.markdown("<h1 class='title-text'> Movie Recommendation System using Sentiment Analysis</h1>", unsafe_allow_html=True)####################################################
        
        movie_titles = movies["title"].values.tolist() if not movies.empty else []
        current_index = movie_titles.index(st.session_state.current_movie) if st.session_state.current_movie in movie_titles else 0
        selected_movie = st.selectbox("Select a movie", movie_titles, index=current_index, key='movie_select')

        if selected_movie != st.session_state.current_movie:
            st.session_state.current_movie = selected_movie
            st.session_state.get_recs = False
            st.session_state.editing_review = None
            st.session_state.show_review_form = False

        if st.button("Get Recommendations") or st.session_state.get_recs: ############################################################################button for#
            st.session_state.get_recs = True

            try:
                selected_movie_row = movies[movies["title"] == st.session_state.current_movie]
                if selected_movie_row.empty:
                    st.error(f"Movie '{st.session_state.current_movie}' not found in our database.")
                    st.stop()
                
                selected_movie_row = selected_movie_row.iloc[0]
                selected_movie_id = selected_movie_row["movie_id"]
                selected_details = fetch_movie_details_by_id(selected_movie_id)
                recs = get_recommendations(st.session_state.current_movie)

                if recs.empty:
                    st.error("No recommendations found for this movie.")
                    st.stop()

                st.markdown(f"<h2 class='title-text'> {st.session_state.current_movie} Details</h2>", unsafe_allow_html=True)######movie details
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown(f"<img class='poster-img' src='{fetch_poster(selected_movie_id)}' />", unsafe_allow_html=True)
                    st.markdown(f"<p class='recommendation-title'>{st.session_state.current_movie}</p>", unsafe_allow_html=True)

                    if st.button(" Like this movie"): #################################################like this movie################################3
                        save_feedback(st.session_state.username, st.session_state.current_movie, "Like")
                        st.success("Added to your liked movies!")

                with col2:
                    st.markdown(f"""
                        <div class="movie-container">
                            <p> <b>Rating:</b> {selected_details.get('vote_average', 'N/A')}</p>
                            <p> <b>Release Date:</b> {selected_details.get('release_date', 'N/A')}</p>
                            <p><b>Overview:</b></p>
                            <div class="overview-box">{selected_details.get('overview', 'No overview available.')}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div class='spacer-large'></div>", unsafe_allow_html=True)
                st.markdown("<h3 class='title-text'> Top Cast</h3>", unsafe_allow_html=True)############################cast
                cast_info = fetch_cast(selected_movie_id)
                cast_rows = [cast_info[i:i+5] for i in range(0, len(cast_info),5)]

                for row in cast_rows:
                    cols = st.columns(len(row))
                    for col, cast in zip(cols, row):
                        with col:
                            st.markdown(f"<img class='cast-img' src='{cast['profile_path']}' alt='{cast['name']}' />", unsafe_allow_html=True)
                            st.markdown(f"<p class='cast-name'>{cast['name']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='color: #ddd; text-align: center; font-size: 14px;'>as {cast['character']}</p>", unsafe_allow_html=True)

                            with st.expander("View Details", expanded=False):############button
                                st.markdown(f"""
                                    <div style="padding: 10px;">
                                        <p><b>Known For:</b> <span style="color: #ffcc00;">{cast['known_for_department']}</span></p>
                                        <p><b>Born:</b> {cast['birthday']} in {cast['place_of_birth']}</p>
                                        <hr style="border-color: rgba(255,255,255,0.2);">
                                        <h4 style="color: #ffcc00;">Biography</h4>
                                        <p style="font-size: 15px;">{cast['biography']}</p>
                                    </div>
                                """, unsafe_allow_html=True)

                st.markdown("<div class='spacer-large'></div>", unsafe_allow_html=True)
                st.markdown("<h3 class='title-text'> More Recommended Movies</h3>", unsafe_allow_html=True)##############################

                for i in range(0, min(10, len(recs)), 5):
                    cols = st.columns(5)
                    for j in range(i, min(i + 5, len(recs))):
                        movie = recs.iloc[j]
                        with cols[j % 5]:
                            st.markdown(
                                f"<div class='recommendation-card'>"
                                f"<img src='{fetch_poster(movie['movie_id'])}'/>"
                                f"<p class='recommendation-title'>{movie['title']}</p>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                            
                            if st.button(
                                "Get Recommendations",########################################################################
                                key=f"rec_button_{movie['movie_id']}",
                                help=f"Get recommendations similar to {movie['title']}"
                            ):
                                st.session_state.current_movie = movie['title']
                                st.session_state.get_recs = True
                                st.rerun()

                st.markdown("<div class='spacer-large'></div>", unsafe_allow_html=True)
                st.markdown("<h3 class='title-text'> Movie Reviews</h3>", unsafe_allow_html=True)  ###########################

                # Check if user has already reviewed this movie
                user_reviews = load_user_reviews(st.session_state.current_movie)
                user_has_reviewed = any(review['username'] == st.session_state.username for review in user_reviews)
                
                # Review form section
                if not user_has_reviewed or st.session_state.editing_review is not None:
                    with st.expander("Write Your Review", expanded=st.session_state.show_review_form):##########
                        if st.session_state.editing_review is not None:
                            df = pd.read_csv("user_reviews.csv") if os.path.exists("user_reviews.csv") else pd.DataFrame()
                            if not df.empty and st.session_state.editing_review < len(df):
                                review_data = df.iloc[st.session_state.editing_review]
                                
                                with st.form("edit_review_form"):
                                    review_text = st.text_area("Your Review", value=review_data["review_text"], height=150)
                                    rating = st.slider("Rating (1-10)", 1, 10, int(review_data["rating"]))################
                                    submitted = st.form_submit_button("Update Review")
                                    cancel = st.form_submit_button("Cancel")
                                    
                                    if submitted:
                                        if review_text.strip():
                                            success = update_user_review(
                                                st.session_state.username,
                                                st.session_state.current_movie,
                                                review_text,
                                                rating,
                                                st.session_state.editing_review
                                            )
                                            if success:
                                                st.success("Review updated successfully!")
                                                st.session_state.editing_review = None
                                                st.session_state.show_review_form = False
                                                st.rerun()
                                            else:
                                                st.error("Failed to update review.")
                                        else:
                                            st.warning("Please write your review before submitting.")
                                    if cancel:
                                        st.session_state.editing_review = None
                                        st.session_state.show_review_form = False
                                        st.rerun()
                            else:
                                st.error("Review not found. Creating a new review instead.")
                                st.session_state.editing_review = None
                                st.session_state.show_review_form = True
                        else:
                            with st.form("review_form"):
                                review_text = st.text_area("Your Review", height=150)
                                rating = st.slider("Rating (1-10)", 1, 10, 5)
                                submitted = st.form_submit_button("Submit Review")
                                
                                if submitted:
                                    if review_text.strip():
                                        save_user_review(
                                            st.session_state.username,
                                            st.session_state.current_movie,
                                            review_text,
                                            rating
                                        )
                                        st.success("Thank you for your review!")
                                        st.session_state.show_review_form = False
                                        st.rerun()
                                    else:
                                        st.warning("Please write your review before submitting.")

                # Get all reviews and display with sentiment analysis
                professional_reviews = fetch_reviews(selected_movie_id)
                user_reviews = load_user_reviews(st.session_state.current_movie)
                
                # Prepare all reviews with sentiment
                all_reviews = []
                
                # Current user's review first
                current_user_review = next((r for r in user_reviews if r['username'] == st.session_state.username), None)
                if current_user_review:
                    all_reviews.append({
                        'author': current_user_review['username'],
                        'content': current_user_review['review_text'],
                        'rating': current_user_review['rating'],
                        'date': current_user_review['date'],
                        'type': 'user',
                        'is_current_user': True,
                        'sentiment': str(current_user_review.get('sentiment', 'Neutral')),
                        'polarity': float(current_user_review.get('polarity', 0))
                    })
                
                # Other user reviews
                for review in user_reviews:
                    if review['username'] != st.session_state.username:
                        all_reviews.append({
                            'author': review['username'],
                            'content': review['review_text'],
                            'rating': review['rating'],
                            'date': review['date'],
                            'type': 'user',
                            'is_current_user': False,
                            'sentiment': str(review.get('sentiment', 'Neutral')),
                            'polarity': float(review.get('polarity', 0))
                        })
                
                # Professional reviews
                for review in professional_reviews:
                    content = review.get('content', 'No review text available')##########################
                    sentiment, polarity = analyze_sentiment(content)
                    
                    all_reviews.append({
                        'author': review.get('author', 'Anonymous'),
                        'content': content,
                        'rating': review.get('author_details', {}).get('rating', 'N/A'),
                        'date': review.get('created_at', '')[:10],
                        'type': 'professional',
                        'is_current_user': False,
                        'avatar_url': review.get('author_details', {}).get('avatar_url'),
                        'sentiment': str(sentiment),
                        'polarity': float(polarity)
                    })

                # Display sentiment statistics
                if all_reviews:
                    sentiment_df = pd.DataFrame(all_reviews)
                    pos_count = len(sentiment_df[sentiment_df['sentiment'] == 'Positive'])
                    neg_count = len(sentiment_df[sentiment_df['sentiment'] == 'Negative'])
                    neu_count = len(sentiment_df[sentiment_df['sentiment'] == 'Neutral'])
                    
                    st.markdown("### Sentiment Analysis Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive Reviews", f"{pos_count} ")
                    with col2:
                        st.metric("Neutral Reviews", f"{neu_count} ")
                    with col3:
                        st.metric("Negative Reviews", f"{neg_count} ")
                    
                    st.markdown("---")
                
                # Display all reviews
                if not all_reviews:
                    st.markdown("<p>No reviews available for this movie yet.</p>", unsafe_allow_html=True)
                else:
                    df = pd.read_csv("user_reviews.csv") if os.path.exists("user_reviews.csv") else pd.DataFrame()
                    
                    for i, review in enumerate(all_reviews):
                        sentiment_class = str(review.get('sentiment', 'Neutral')).lower()
                        emoji = get_sentiment_emoji(review.get('sentiment', 'Neutral'))
                        
                        if review['type'] == 'user' and review['is_current_user']:
                            mask = (df['username'] == st.session_state.username) & \
                                   (df['movie_title'] == st.session_state.current_movie)
                            matching_indices = df.index[mask].tolist()
                            
                            if matching_indices:
                                actual_index = matching_indices[0]
                                stars = " " * int(review['rating'])
                                formatted_date = datetime.strptime(review['date'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y") if 'date' in review else "Date not available"
                                
                                col1, col2 = st.columns([4, 1])
                                with col1:
                                    st.markdown(f"""
                                        <div class="review-card">
                                            <div class="review-header">
                                                <div class="review-author">
                                                    <p class="review-name">{review['author']} (You) {emoji}</p>
                                                    <p>{formatted_date}</p>
                                                </div>
                                            </div>
                                            <div class="review-content">
                                                <p>{review['content']}</p>
                                            </div>
                                            <p class="review-rating">{stars} ({review['rating']}/10)</p>
                                            <p class="sentiment-{sentiment_class}">Sentiment: {review.get('sentiment', 'Neutral')}</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    if st.button("Edit", key=f"edit_{i}"):
                                        st.session_state.editing_review = actual_index
                                        st.session_state.show_review_form = True
                                        st.rerun()
                                    if st.button("Delete", key=f"delete_{i}"):
                                        if delete_user_review(actual_index):
                                            st.success("Review deleted successfully!")
                                            st.session_state.editing_review = None
                                            st.session_state.show_review_form = False
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete review.")
                        else:
                            stars = " " * int(review['rating']) if isinstance(review['rating'], (int, float)) else ""
                            rating_display = f"{stars} ({review['rating']}/10)" if isinstance(review['rating'], (int, float)) else "Rating: N/A"
                            
                            if review['type'] == 'professional':
                                avatar_url = review.get('avatar_url', None)
                                default_avatar = "https://via.placeholder.com/45?text=No+Photo"
                                st.markdown(f"""
                                    <div class="review-card">
                                        <div class="review-header">
                                            <img src="{avatar_url if avatar_url else default_avatar}" class="review-avatar">
                                            <div>
                                                <p><b>{review['author']}</b> <span style="color: #ffcc00;">(Critic)</span> {emoji}</p>
                                                <p><i>{review['date']}</i></p>
                                            </div>
                                        </div>
                                        <div class="review-content">
                                            <p>{review['content']}</p>
                                            <p><i>{rating_display}</i></p>
                                            <p class="sentiment-{sentiment_class}">Sentiment: {review.get('sentiment', 'Neutral')}</p>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                formatted_date = datetime.strptime(review['date'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y") if 'date' in review else "Date not available"
                                st.markdown(f"""
                                    <div class="review-card">
                                        <div class="review-header">
                                            <div class="review-author">
                                                <p class="review-name">{review['author']} {emoji}</p>
                                                <p>{formatted_date}</p>
                                            </div>
                                        </div>
                                        <div class="review-content">
                                            <p>{review['content']}</p>
                                        </div>
                                        <p class="review-rating">{rating_display}</p>
                                        <p class="sentiment-{sentiment_class}">Sentiment: {review.get('sentiment', 'Neutral')}</p>
                                    </div>
                                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error loading recommendations: {str(e)}")

    elif page == "Liked Movies":
        st.markdown("<h1 class='title-text'>Your Liked Movies</h1>", unsafe_allow_html=True)
        liked_movies = load_liked_movies(st.session_state.username)

        if liked_movies:
            st.markdown(f"<div class='liked-count'>You have {len(liked_movies)} liked movie(s)</div>", unsafe_allow_html=True)
            
            for i in range(0, len(liked_movies), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(liked_movies):
                        movie_title = liked_movies[i + j]
                        movie_data = movies[movies["title"] == movie_title]
                        if not movie_data.empty:
                            movie_id = movie_data.iloc[0]["movie_id"]
                            poster_url = fetch_poster(movie_id)
                            with cols[j]:
                                st.markdown(
                                    f"""
                                    <div class="liked-movie-card">
                                        <img src="{poster_url}" class="liked-poster"/>
                                        <p class="liked-movie-title">{movie_title}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
        else:
            st.markdown("""
                <div class="no-liked-movies">
                    <h3>No liked movies yet</h3>
                    <p>Like some movies to see them here!</p>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("<h1 class='title-text'> Movie Recommendation System using sentiment analysis</h1>", unsafe_allow_html=True)
    st.markdown("<div class='login-prompt'>Please login or sign up to access the movie recommendations</div>", unsafe_allow_html=True)