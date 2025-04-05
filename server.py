from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime
from collections import Counter
from flask_cors import CORS
from routes.LeetCode_data_fetcher import get_user_profile, get_solved_stats, get_topic_wise_stats, get_contest_history, get_badges, get_language_stats

app = Flask(__name__)
CORS(app)

import requests
from collections import Counter

def fetch_github_data(username):
    user_api = f"https://api.github.com/users/{username}"
    repos_api = f"https://api.github.com/users/{username}/repos?per_page=100"
    contrib_api = f"https://api.github.com/users/{username}/events/public"

    try:
        # Fetch User Profile Data
        user_response = requests.get(user_api)
        if user_response.status_code != 200:
            return {"error": f"GitHub profile not found (Status code: {user_response.status_code})"}

        user_data = user_response.json()

        # Fetch Repositories Data
        repos_response = requests.get(repos_api)
        if repos_response.status_code != 200:
            return {"error": f"Failed to fetch repositories (Status code: {repos_response.status_code})"}

        all_repos = repos_response.json()
        repos_data = []
        languages = []

        for repo in all_repos:
            languages.append(repo.get("language"))
            repos_data.append({
                "name": repo.get("name"),
                "description": repo.get("description"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "language": repo.get("language"),
                "repo_url": repo.get("html_url")
            })

        # Find Top 5 Most Used Languages
        language_count = Counter(languages)
        top_5_languages = [lang for lang, _ in language_count.most_common(5)]

        # Fetch Contributions (Recent Public Events)
        contrib_response = requests.get(contrib_api)
        total_contributions = 0
        if contrib_response.status_code == 200:
            events = contrib_response.json()
            total_contributions = len(events)

        # Final Response
        return {
            "name": user_data.get("name", ""),
            "bio": user_data.get("bio", ""),
            "followers": user_data.get("followers", 0),
            "following": user_data.get("following", 0),
            "public_repos": user_data.get("public_repos", 0),
            "profile_url": user_data.get("html_url", ""),
            "company": user_data.get("company", ""),
            "location": user_data.get("location", ""),
            "blog": user_data.get("blog", ""),
            "created_at": user_data.get("created_at", ""),
            "updated_at": user_data.get("updated_at", ""),
            "most_used_languages": top_5_languages,
            "total_contributions": total_contributions,
            "repositories": repos_data
        }

    except Exception as e:
        return {"error": f"Error fetching GitHub data: {str(e)}"}


def fetch_leetcode_data(username):
    leetcode_api = f"https://leetcode-stats-api.herokuapp.com/{username}"
    try:
        profile = get_user_profile(username)
        solved_stats = get_solved_stats(username)
        topics = get_topic_wise_stats(username)
        contests = get_contest_history(username)
        badges = get_badges(username)
        languages = get_language_stats(username)

        return {
            "profile": profile,
            "solved_stats": solved_stats,
            "topics": topics,
            "contest_history": contests,
            "badges": badges,
            "language_stats": languages
        }

    except Exception as e:
        return {"error": f"Error fetching LeetCode data: {str(e)}"}
    
def save_data_to_json(data, github_username, leetcode_username):
    if not os.path.exists('api_data'):
        os.makedirs('api_data')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_data/{github_username}_{leetcode_username}_{timestamp}.json"
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)
    return filename

@app.route('/api', methods=['GET'])
def get_data():
    github_username = request.args.get('github_username')
    leetcode_username = request.args.get('leetcode_username')

    if not github_username or not leetcode_username:
        return jsonify({"error": "Both github_username and leetcode_username are required"}), 400

    github_data = fetch_github_data(github_username)
    leetcode_data = fetch_leetcode_data(leetcode_username)

    analysis = {
        "github_analysis": github_data,
        "leetcode_analysis": leetcode_data
    }

    save_data_to_json(analysis, github_username, leetcode_username)

    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True)
