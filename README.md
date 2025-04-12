# 🔍 Backend Profile Analyzer

A Flask-based backend that analyzes GitHub and LeetCode profiles, returning detailed statistics about repositories, programming languages, solved problems, contests, and more. Designed to work with a frontend via CORS.

---

## 🚀 Features

- 🔧 GitHub API integration:
  - Profile information
  - Top 5 used languages
  - Public contributions (events)
  - Repository details (stars, forks, language, etc.)
- 🧠 LeetCode GraphQL API integration:
  - User profile data
  - Problem-solving stats (overall and topic-wise)
  - Contest participation and ratings
  - Badge and language-specific insights
- ⚙️ CORS-configured for frontend communication
- ✅ Preflight `OPTIONS` method support

---

## 🧪 API Endpoints

### `GET /api`

**Query Parameters:**

- `github_username` (required)
- `leetcode_username` (required)

**Example Request:**

- GET http://localhost:5000/api?github_username=Meet-paladiya&leetcode_username=Meet123
  **Example Response:**

```json
{
  "github_analysis": {
    "name": "Meet Paladiya",
    "bio": "...",
    "followers": 10,
    "most_used_languages": ["JavaScript", "Python", "C++"],
    ...
  },
  "leetcode_analysis": {
    "profile": {...},
    "solved_stats": {...},
    ...
  }
}
```

---

## 🛠 Setup & Run

### 🔧 Requirements

Install required dependencies:

```bash
pip install -r requirements.txt

⚙️ Environment Variable

Create a .env file in the root directory and add the following:
-FRONTEND_URL=http://localhost:3000

▶️ Run the App
Start the Flask server with:
python app.py
The server will start at: http://localhost:5000


📦 Dependencies
Major packages used in this project:

Flask
flask-cors
requests
collections
beautifulsoup4
pandas
scikit-learn
plotly

Install all dependencies using:pip install -r requirements.txt

🔒 CORS Support
Handles both actual and preflight (OPTIONS) requests with full CORS configuration:

✅ Methods: GET, POST, OPTIONS, PUT, DELETE
✅ Supports credentials and custom headers

