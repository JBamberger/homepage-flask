def handle_github_hook(headers, json):
    if headers is None:
        raise ValueError
    if json is None:
        raise ValueError

    if headers["X-GitHub-Event"] is not None:
        event = headers["X-GitHub-Event"]
    else:
        event = "unknown"

    if "sender" in json:
        user = json["sender"]
        if "login" in user:
            user = user["login"]
        else:
            user = "unknown"
    else:
        user = "unknown"
    if "repository" in json:
        repo = json["repository"]
        if "full_name" in repo:
            repo = repo["full_name"]
        else:
            repo = "unknown"
    else:
        repo = "unknown"

    return user, event, repo
