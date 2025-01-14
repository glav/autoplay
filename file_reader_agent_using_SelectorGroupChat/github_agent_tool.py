import config
from githubreader.githubreader import GithubReader
from githubreader.githubrepo import GithubRepo
from githubreader.githubreporeader import GithubRepoReader

async def get_repository_files() -> str:
    """Get all the file names within a Github repository."""
    if not config.GITHUB_TOKEN:
        raise ValueError("No GITHUB_TOKEN defined in the environment.")

    github_reader = await GithubReader.create(config.GITHUB_TOKEN, config.GITHUB_ORG)
    repo = GithubRepo(config.GITHUB_REPONAME)
    repo_reader = await GithubRepoReader.create(github_reader.org_to_use, github_reader.user, repo)

    # Get the repo contents as context
    repo_contents = await repo_reader.get_repo_contents_async()
    context = ""
    for file in repo_contents:
        context += f"FilePath: {file.name}\n"
        #print(f"File: {file.name}")
    return context

