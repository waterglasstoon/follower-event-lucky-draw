#!/usr/bin/env python3

import requests
import time
import random
import sys

# target instagram post id obtained by facebook api
POST_ID = "POST_ID_HERE"

# facebook graph api access token
ACCESS_TOKEN = "ACCESS_TOKEN_HERE"

# draw configs
DRAWS = [
    {"name": "셔츠", "count": 1, "excluded": set([])},
    {"name": "쿠키", "count": 4, "excluded": set([])}
]


def get_comment_users(post_id, access_token, interval_sec=1):
    all_users = set([])
    params = {
        "fields": "username",
        "limit": 50,
        "access_token": access_token
    }
    param_str = "&".join(map(lambda a: f"{a[0]}={a[1]}", params.items()))
    url = f"https://graph.facebook.com/{post_id}/comments?{param_str}"

    # iterate until no more item left
    while True:
        res = requests.get(url)
        res.raise_for_status()
        body = res.json()
        for item in body["data"]:
            all_users.add(item["username"])
        if "paging" not in body:
            break
        url = body["paging"]["next"]
        time.sleep(interval_sec)

    return all_users


def run_draws(draws, users):
    results = []
    already_won = set([])
    for draw in draws:
        candids = set(filter(lambda id: id not in draw["excluded"] and id not in already_won, users))
        won_users = random.sample(candids, draw["count"])
        results.append({"name": draw["name"], "users": won_users})
        already_won.update(won_users)
    return results


if __name__ == "__main__":
    # version check
    MIN_PYTHON = (3, 6)
    if sys.version_info < MIN_PYTHON:
        sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)

    print("Fetch all users in comment (except for re-reply)...")
    users = get_comment_users(POST_ID, ACCESS_TOKEN)

    print("Done. Now pick users")
    draw_results = run_draws(DRAWS, users)
    print("=======================================================================================")
    for result in draw_results:
        print(f"{result['name']}: {', '.join(result['users'])}")
    print("=======================================================================================")
