Here’s a clean, well-structured **README.md** style arrangement for GitHub that makes your Movie Recommendation System look professional and easy to follow:

---

# 🎬 Movie Recommendation System with Sentiment Analysis

A **Streamlit** web app that recommends movies using **Cosine Similarity** and analyzes user reviews with **TextBlob Sentiment Analysis**.
*(Tip: Use Dark Mode on your PC for the best UI experience!)*

---

## 🚀 Features

* **Content-based movie recommendations** using cosine similarity
* **Sentiment analysis** on user reviews with TextBlob
* Fetches movie details, posters, and cast from **TMDB API**
* Stylish **dark-themed UI** with custom CSS

---

## 📦 Installation & Setup

### 1️⃣ Install Python & Extensions

* Install [Python](https://www.python.org/downloads/)
* Install **Python** and **Jupyter** extensions in VS Code

---

### 2️⃣ Install Required Packages

Open a terminal in your project folder and run:

```bash
pip install streamlit pandas requests textblob
```

---

### 3️⃣ Get TMDB API Key

* Sign up at [TMDB](https://www.themoviedb.org/settings/api)
* Or follow this YouTube tutorial: [TMDB API Key Guide](https://youtu.be/FvuaZOK2grY?si=TuU6-Rd-GO6ALXmE)
* Paste your API key in `app.py` **line 11**:

```python
API_KEY = "your_key_here"
```

---

### 4️⃣ Generate Movie Data

Run the `Movie_Recommendation_System.ipynb` file in Jupyter to create:

```
movie_data.pkl
```

---

### 5️⃣ Run the Application

```bash
streamlit run app.py
```

---



Do you want me to prepare it in **GitHub-optimized README format** with badges and extra styling?
