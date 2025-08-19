from github import Github


class Repo:
    def git_get_license(self, owner: str, repo: str):
        g = Github()  # You can also provide a GitHub token for authentication
        repository = g.get_repo(f"{owner}/{repo}")
        license_info = repository.get_license()
        self.json["Model Details"][
            "License"
        ] = f"{license_info.license.spdx_id if license_info else 'No license info'}"

    def get_git_info(self, owner: str, repo: str):
        g = Github()  # You can also provide a GitHub token for authentication
        repository = g.get_repo(f"{owner}/{repo}")
        license_info = repository.get_license()
        self.json["Model Details"][
            "License"
        ] = f"{license_info.license.spdx_id if license_info else 'No license info'}"
        tags = repository.get_tags()
        self.json["Model Details"][
            "Version"
        ] = f"{tags[0].name if tags.totalCount > 0 else 'No releases found'}"
        repo_name = repository.name
        self.json["Model Details"]["Name"] = repo_name
        repo_url = repository.html_url
        self.json["Model Details"]["References"]["github"] = repo_url
