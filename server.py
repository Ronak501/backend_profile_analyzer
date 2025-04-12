from flask import Flask, request, jsonify, send_from_directory
import requests
import json
import os
from collections import Counter
from flask_cors import CORS
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

# Enhanced CORS configuration for both development and production
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://*.onrender.com", "https://*.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["*"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "Authorization"],
        "max_age": 86400
    }
})

@app.after_request
def after_request(response):
    # Get the origin from the request
    origin = request.headers.get('Origin')
    
    # If origin is in our allowed list, set it as the allowed origin
    if origin and origin in ["http://localhost:3000", "https://*.onrender.com", "https://*.vercel.app"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        # In production, allow any origin
        response.headers.add('Access-Control-Allow-Origin', '*')
    
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

def get_readme_exists(username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    res = requests.get(url, headers=headers)
    return res.status_code == 200
  
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
    
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com"
}

GRAPHQL_URL = "https://leetcode.com/graphql"

def graphql_query(query, variables):
    try:
        response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables}, headers=HEADERS)
        return response.json()
    except Exception as e:
        print(f"GraphQL Error: {e}")
        return {}

def get_user_profile(username):
    query = """
    query getUserProfile($username: String!) {
      matchedUser(username: $username) {
        username
        profile {
          realName
          aboutMe
          countryName
          ranking
          reputation
        }
      }
    }
    """
    return graphql_query(query, {"username": username})

def get_solved_stats(username):
    query = """
    query userProblemsSolved($username: String!) {
      allQuestionsCount { difficulty count }
      matchedUser(username: $username) {
        submitStatsGlobal {
          acSubmissionNum { difficulty count }
        }
      }
    }
    """
    return graphql_query(query, {"username": username})

def get_topic_wise_stats(username):
    query = """
    query userProblemsSolved($username: String!) {
      matchedUser(username: $username) {
        tagProblemCounts {
          advanced { tagName problemsSolved }
          intermediate { tagName problemsSolved }
          fundamental { tagName problemsSolved }
        }
      }
    }
    """
    return graphql_query(query, {"username": username})

def get_contest_history(username):
    query = """
    query userContestRankingInfo($username: String!) {
      userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
        totalParticipants
        topPercentage
      }
      userContestRankingHistory(username: $username) {
        contest {
          title
          startTime
        }
        ranking
        score
        attended
        problemsSolved
        totalProblems
      }
    }
    """
    return graphql_query(query, {"username": username})

def get_badges(username):
    query = """
    query userBadges($username: String!) {
      matchedUser(username: $username) {
        badges {
          id
          name
          shortName
          displayName
          creationDate
        }
      }
    }
    """
    return graphql_query(query, {"username": username})

def get_language_stats(username):
    query = """
    query languageStats($username: String!) {
      matchedUser(username: $username) {
        languageProblemCount {
          languageName
          problemsSolved
        }
      }
    }
    """
    return graphql_query(query, {"username": username})


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

def fetch_linkedin_data(username):
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    linkedin_profile_url = f'https://www.linkedin.com/in/{username}/'
    api_key = "zZe8tR05rWiFuLY9NRDgzA"  # Use environment variable with fallback
    headers = {'Authorization': 'Bearer ' + api_key}

    try:
        response = requests.get(
            api_endpoint, 
            params={'url': linkedin_profile_url, 'skills': 'include'}, 
            headers=headers
        )
        
        if response.status_code != 200:
            return {"error": f"LinkedIn profile not found or API error (Status code: {response.status_code})"}
        
        profile_data = response.json()
        
        # Extract the most relevant information
        return {
            "profile_info": {
                "full_name": profile_data.get("full_name", ""),
                "headline": profile_data.get("headline", ""),
                "summary": profile_data.get("summary", ""),
                "occupation": profile_data.get("occupation", ""),
                "profile_pic_url": profile_data.get("profile_pic_url", ""),
                "location": {
                    "country": profile_data.get("country", ""),
                    "city": profile_data.get("city", ""),
                    "state": profile_data.get("state", "")
                },
                "connections": profile_data.get("connections", 0)
            },
            "experiences": profile_data.get("experiences", []),
            "education": profile_data.get("education", []),
            "skills": profile_data.get("skills", []),
            "certifications": profile_data.get("certifications", []),
            "languages": profile_data.get("languages", []),
            "volunteer_work": profile_data.get("volunteer_work", []),
            "accomplishments": {
                "publications": profile_data.get("accomplishment_publications", []),
                "honors_awards": profile_data.get("accomplishment_honors_awards", []),
                "patents": profile_data.get("accomplishment_patents", []),
                "courses": profile_data.get("accomplishment_courses", []),
                "projects": profile_data.get("accomplishment_projects", []),
                "organizations": profile_data.get("accomplishment_organisations", [])
            }
        }
    except Exception as e:
        return {"error": f"Error fetching LinkedIn data: {str(e)}"}
    
@app.route('/api', methods=['GET', 'OPTIONS'])
def get_data():
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight CORS check'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

    github_username = request.args.get('github_username')
    leetcode_username = request.args.get('leetcode_username')
    linkedin_username = request.args.get('linkedin_username')

    if not github_username and not leetcode_username and not linkedin_username:
        return jsonify({"error": "At least one username is required"}), 400

    analysis = {}
    
    if github_username:
        github_data = fetch_github_data(github_username)
        analysis["github_analysis"] = github_data
    
    if leetcode_username:
        leetcode_data = fetch_leetcode_data(leetcode_username)
        analysis["leetcode_analysis"] = leetcode_data
        
    if linkedin_username:
        linkedin_data = fetch_linkedin_data(linkedin_username)
        analysis["linkedin_analysis"] = linkedin_data

    return jsonify(analysis)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({
        "error": "Not Found",
        "message": "The requested URL was not found on the server.",
        "available_endpoints": [
            "/ - API documentation",
            "/api - Analyze profiles",
            "/health - Health check"
        ]
    }), 404

@app.route('/', methods=['GET'])
def index():
    # Assuming your TypeScript file is in a 'static' directory
    # You may need to adjust the path based on your project structure
    return send_from_directory('static', 'app.ts', mimetype='application/typescript')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
