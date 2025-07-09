
# Movie Recommendation System with Sentiment Analysis

A Streamlit web app that recommends movies using cosine similarity and analyzes reviews with TextBlob sentiment analysis.



2. Install packages: Go to terminal and paste
```bash
pip install streamlit pandas requests textblob
```

## Setup
1. Get API key from [TMDB](https://www.themoviedb.org/settings/api) or go to youtube https://youtu.be/FvuaZOK2grY?si=TuU6-Rd-GO6ALXmE and follow the instruction
2. Paste it in `app.py` line 11:
```python
API_KEY = "your_key_here"  # Replace this
```

3. Generate data: go to terminal and paste
- Run `Movie_Recommendation_System.ipynb` to create `movie_data.pkl`

## Run the App : Go to terminal and paste
```bash
streamlit run app.py
```




