from requests import session
from time import sleep
from sys import argv
from math import ceil

GITHUB_API_RROT = "https://api.github.com"
SEARCH_REPO_ENDPOINT = "/search/repositories"

if __name__ == '__main__':
    to_fetch = int(argv[1])
    output_fp = argv[2]
    pages_needed = ceil(to_fetch / 100)
    results = []
    s = session()
    for page in range(1, pages_needed + 1):
        print(page)
        response = s.get(GITHUB_API_RROT + SEARCH_REPO_ENDPOINT,
                         params={"sort": "stars", "order": "desc", "q": "stars:>=20", "per_page": 100, "page": page},
                         )
        if int(response.headers['X-RateLimit-Remaining']) < 3:
            sleep(60)
        response_items = response.json()
        repos = response_items['items']
        results += repos

    results = results[:to_fetch]

    with open(output_fp, "w") as output_file:
        for repo in results:
            print(repo['full_name'], file=output_file)
