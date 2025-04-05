import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json
from datetime import datetime, timedelta

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

def fetch_all_leetcode_data(username):
    profile = get_user_profile(username)
    solved_stats = get_solved_stats(username)
    topics = get_topic_wise_stats(username)
    contests = get_contest_history(username)
    badges = get_badges(username)
    languages = get_language_stats(username)

    result = {
        "profile": profile,
        "solved_stats": solved_stats,
        "topics": topics,
        "contest_history": contests,
        "badges": badges,
        "language_stats": languages
    }

    # Save to JSON
    with open(f"{username}_leetcode_data.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ All data saved to {username}_leetcode_data.json")

# Usage
fetch_all_leetcode_data("mandartule")
