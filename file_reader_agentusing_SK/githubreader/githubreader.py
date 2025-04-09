"""
Utility functions to retrieve Github repository information and their contents.

To get the repositories for an organisation:
```
python githubreader.py --github-pat {github_token} \
                       --organisation-name {org_name}}
```

To get the contents of a repository:
```
python githubreader.py --github-pat {github_token} \
                       --organisation-name {org_name} \
                       --get-repo-contents
                       --repo-name {repo_name}
```

If no Github Personal Access Token (PAT) is supplied then it will look for the environment variable GITHUB_PAT.
If no Github organisation name is supplied then it will look for the environment variable GITHUB_ORGNAME.
"""

import argparse
import asyncio
import os

from github import Auth, Github

from .githubrepo import GithubRepo
from .githubreporeader import GithubRepoReader


class GithubReader:
    def __init__(self, github_token: str, organisation_name: str):
        self.organisation_name = self.__use_organisation_name(organisation_name)
        self.token_to_use = self.__use_github_token(github_token)
        self.org_to_use = self.__use_organisation_name(organisation_name)
        self.githubClient = self.__get_github_client(self.token_to_use)

    @staticmethod
    async def create(github_token: str, organisation_name: str, github_client=None):
        github_reader = GithubReader(github_token, organisation_name)
        if github_client is not None:
            github_reader.githubClient = github_client
        await github_reader.__set_org_user_async()

        return github_reader

    def map_full_list(self, repo) -> GithubRepo:
        """
        Maps the Github repository object to a simpler object
        """
        return GithubRepo(
            name=repo.name,
            description=repo.description,
            url=repo.html_url,
            language=repo.language,
            updated=repo.updated_at,
            default_branch=repo.default_branch,
        )

    def __get_github_client(self, github_token: str):
        """
        Gets the Github client
        """
        auth = Auth.Token(github_token)

        # Public Web Github
        githubClient = Github(auth=auth)

        return githubClient

    def __use_github_token(self, token):
        """
        Uses the Github Personal Access Token (PAT) supplied if it is not empty
        otherwise it gets thge token from the environment
        """
        gh_token = token if token else os.environ.get("GITHUB_PAT")
        if not gh_token:
            raise ValueError("Github Personal Access Token is required. Can use GITHUB_PAT environment variable")

        return gh_token

    def __use_organisation_name(self, name):
        """
        Uses the Github organisation name supplied if it is not empty
        otherwise it gets the organisation name from the environment
        """
        org_name = name if name else os.environ.get("GITHUB_ORGNAME")
        # if not org_name:
        #     raise ValueError("Github organisation name is required. Can use GITHUB_ORGNAME environment variable")

        return org_name

    async def get_repos_async(self):
        """
        Gets all the repositories for a given organisation within Github using a Personal Access Token (PAT)
        The repositories are sorted in descending order by modification date
        """

        if self.org:
            repos_thread = asyncio.to_thread(self.org.get_repos, type="all", sort="updated", direction="desc")
            repos = await repos_thread
        else:
            repos_thread = asyncio.to_thread(self.user.get_repos)

        repos = await repos_thread

        print(f"Found {repos.totalCount} repos for organisation {self.org_to_use}")

        mapped_list = map(self.map_full_list, repos)
        return mapped_list

    async def __set_org_user_async(self):
        self.org = None
        self.user = None
        if self.org_to_use:
            org_thread = asyncio.to_thread(self.githubClient.get_organization, self.org_to_use)
            self.org = await org_thread
        else:
            user_thread = asyncio.to_thread(self.githubClient.get_user)
            self.user = await user_thread


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retrieve Github repository inforrmation and their contents.",
    )
    parser.add_argument("--github-pat", help="Github Personal Access Token")
    parser.add_argument("--organisation-name", help=" Github organisation name to query.")
    parser.add_argument(
        "--get-repo-contents",
        action="store_true",
        required=False,
        help="Get the content for a repository.",
    )
    parser.add_argument(
        "--repo-name", required=False, help="The repository name if retrieving the repository contents."
    )
    args = parser.parse_args()

    github_reader = asyncio.run(GithubReader.create(args.github_pat, args.organisation_name))

    if args.get_repo_contents:
        if args.repo_name is None:
            raise ValueError("Repository name is required when retrieving the repository contents.")

        github_repo_reader = asyncio.run(
            GithubRepoReader.create(github_reader.org, github_reader.user, GithubRepo(args.repo_name))
        )
        contents = asyncio.run(github_repo_reader.get_repo_contents_async())

        # Print out the first 10 files for convenience
        cnt = 0
        print("\nFirst 10 files....")
        print("{:30} {:>10} {:^40} {:30}".format("Path", "Size", "SHA", "Html Url"))
        for file in contents:
            cnt += 1
            if cnt > 10:
                break
            print(f"{file.path[0:29]:30} {file.size:>10} {file.sha:^40} {file.html_url:30}")
        exit()

    # default to just listing out the repos
    repos = asyncio.run(github_reader.get_repos_async())

    # Print out the first 10 list of repositories for convenience
    cnt = 0
    print("\nFirst 10 repos....")
    print("{:30} {:23} {:30}".format("Name", "Updated", "Description"))
    for repo in repos:
        cnt += 1
        if cnt > 10:
            break
        print(
            "{:30} {:23} {:30}".format(
                repo.name[0:29], str(repo.updated)[0:22] if repo.updated else "-not set-", repo.description
            )
        )
