import requests
import math as Math

# Function to fetch OSSF score
def get_ossf_score(organization, repository):
    url = f"https://api.securityscorecards.dev/projects/github.com/{organization}/{repository}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['score']
    else:
        return None

# Function to report OSSF scores for multiple repositories
def report_ossf_scores(repositories):
    scores = {}
    for repo in repositories:
        organization, repository = repo.split('/')
        score = get_ossf_score(organization, repository)
        if score is not None:
            scores[repo] = score
        else:
            scores[repo] = Math.nan
    return scores

# Function to fetch repositories for an organization
def fetch_repositories(organization):
    url = f"https://api.github.com/orgs/{organization}/repos?per_page=100"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        repositories = [repo['full_name'] for repo in data]
        return repositories
    else:
        return []
