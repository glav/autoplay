import asyncio

from github import Repository
from github.AuthenticatedUser import AuthenticatedUser
from github.Organization import Organization

from .namedbytesio import NamedBytesIO
from .githubelement import GithubElement
from .githubfilecontent import GithubFileContent
from .githubrepo import GithubRepo


class GithubRepoReader:
    __instance = object()
    __repository: Repository = None

    def __init__(self, org: Organization, user: AuthenticatedUser, instance: object):
        assert GithubRepoReader.__instance == instance, "Only create this object using the create method"
        self.org: Organization = org
        self.user: AuthenticatedUser = user

    @classmethod
    async def create(self, org: Organization, user: AuthenticatedUser, githubRepo: GithubRepo):
        repo_reader = GithubRepoReader(org, user, self.__instance)
        await repo_reader.__set_repo_async(githubRepo)

        return repo_reader

    async def __set_repo_async(self, githubRepo: GithubRepo):
        print(f"Getting repo {githubRepo.name}...")
        if self.org is not None:
            repo_thread = asyncio.to_thread(self.org.get_repo, githubRepo.name)
        else:
            repo_thread = asyncio.to_thread(self.user.get_repo, githubRepo.name)
        repo = await repo_thread
        self.__repository = repo

    def map_file_content(self, file_content) -> GithubFileContent:
        """
        Maps the Github repository object to a simpler object
        """
        return GithubFileContent(
            name=file_content.name,
            path=file_content.path,
            size=file_content.size,
            sha=file_content.sha,
            url=file_content.url,
            html_url=file_content.html_url,
            download_url=file_content.download_url,
            type=file_content.type,
            content= NamedBytesIO(file_content.name, file_content.decoded_content),
        )

    def map_git_element(self, git_element) -> GithubElement:
        """
        Maps the Github repository object to a simpler object
        """
        return GithubElement(
            path=git_element.path,
            size=git_element.size,
            sha=git_element.sha,
            url=git_element.url,
            mode=git_element.mode,
            type=git_element.type,
        )

    async def get_repo_contents_async(self):
        repo_contents_thread = asyncio.to_thread(self.__repository.get_contents, "")
        repo_contents = await repo_contents_thread
        file_contents = []
        while repo_contents:
            file_content = repo_contents.pop(0)
            if file_content.type == "dir":
                dir_contents_thread = asyncio.to_thread(self.__repository.get_contents, file_content.path)
                repo_contents.extend(await dir_contents_thread)
            else:
                file_contents.append(file_content)
        mapped_content = map(self.map_file_content, file_contents)

        return mapped_content

    async def get_repo_content_async(self, path: str):
        """
        Gets the repository content for a given organisation within Github using a path
        """

        repo_contents_thread = asyncio.to_thread(self.__repository.get_contents, path)
        repo_content = await repo_contents_thread

        if isinstance(repo_content, list):
            raise ValueError(f"Expected a single file but got a list of files for path {path}")

        mapped_content = self.map_file_content(repo_content)

        return mapped_content

    async def get_repo_paths_async(self, githubRepo: GithubRepo, recursive: bool = True):
        """
        Gets the repository files list for a given organisation within Github using a Personal Access Token (PAT)
        """
        if self.org is not None:
            repo_thread = asyncio.to_thread(self.org.get_repo, githubRepo.name)
        else:
            repo_thread = asyncio.to_thread(self.user.get_repo, githubRepo.name)

        # repo_thread = asyncio.to_thread(self.org.get_repo, githubRepo.name)
        repo = await repo_thread

        repo_tree_thread = asyncio.to_thread(repo.get_git_tree, githubRepo.default_branch, recursive=recursive)
        repo_tree = await repo_tree_thread

        mapped_content = map(self.map_git_element, repo_tree.tree)

        return mapped_content
