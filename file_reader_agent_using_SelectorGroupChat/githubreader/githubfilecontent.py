class GithubFileContent:
    def __init__(self, name, path, size, url, sha, html_url, download_url, type, content):
        self.name = name
        self.path = path
        self.size = size
        self.sha = sha
        self.url = url
        self.download_url = download_url
        self.html_url = html_url
        self.type = type
        self.content = content
