class GithubRepo:
    def __init__(self, name, description="", url="", language="", updated="", default_branch="main"):
        self.name = name
        self.description = description
        self.url = url
        self.language = language
        self.updated = updated
        self.default_branch = default_branch
