Here's the clean, markdown-formatted README text for you to copy-paste:

```markdown
# Movie Recommendation System with Sentiment Analysis

A Streamlit web app that recommends movies using cosine similarity and analyzes reviews with TextBlob sentiment analysis.

## Features
- 🎬 Personalized movie recommendations
- 😊 Sentiment analysis of user reviews
- 👍 Like/favorite system
- ✍️ Review writing with ratings
- 🎥 Movie details & cast info

## Requirements
- Python 3.7+
- TMDB API key (free)

## Installation
1. Clone repo:
```bash
git clone https://github.com/your-username/Movie-Recommendation-system.git
cd Movie-Recommendation-system
```

2. Install packages:
```bash
pip install streamlit pandas requests textblob
```

## Setup
1. Get API key from [TMDB](https://www.themoviedb.org/settings/api) or go to youtube https://youtu.be/FvuaZOK2grY?si=TuU6-Rd-GO6ALXmE and follow the instruction
2. Paste it in `app.py` line 11:
```python
API_KEY = "your_key_here"  # Replace this
```

3. Generate data:
- Run `Movie_Recommendation_System.ipynb` to create `movie_data.pkl`

## Run the App
```bash
streamlit run app.py
```

## File Structure
```
app.py                    - Main application
movie_data.pkl            - Processed movie data
users.csv                 - User accounts (auto-created) 
feedback.csv              - Liked movies (auto-created)
user_reviews.csv          - Reviews (auto-created)
```

## How It Works
1. **Recommendations**: Cosine similarity on movie overviews
2. **Sentiment**: TextBlob analyzes review emotions
3. **TMDB Integration**: Fetches posters, cast details

