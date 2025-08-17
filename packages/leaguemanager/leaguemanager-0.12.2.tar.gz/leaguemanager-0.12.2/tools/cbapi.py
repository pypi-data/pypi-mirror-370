import importlib
import json
import os
from typing import Annotated, Optional

import typer
from attrs import asdict, define, field
from httpx import Client, Headers, Response
from rich import print


@define
class Release:
    tag_name: str
    name: str
    body: str
    draft: bool = False
    prerelease: bool = False
    hide_archive_links: bool = True


@define
class ReleaseBody:
    text: str = "# Highlights\r\n"

    def add_line(self, line: str):
        self.text += f"{line}\n"


@define
class CBAPI:
    cb_api_key: str = field(default=(os.getenv("CODEBERG_API_KEY")))
    user: str = field(default=(os.getenv("CODEBERG_REPO_USER")))
    repo: str = field(default="leaguemanager")
    base_url: str = field()
    headers: Headers = field()
    client: Client = field()

    @base_url.default
    def _default_base_url(self) -> str:
        return f"https://codeberg.org/api/v1/repos/{self.user}/{self.repo}"

    @headers.default
    def _default_headers(self) -> Headers:
        headers = Headers({"Authorization": f"token {self.cb_api_key}", "Content-Type": "application/json"})
        return headers

    @client.default
    def _default_client(self) -> Client:
        return Client(base_url=self.base_url, headers=self.headers)

    @property
    def current_version(self) -> str:
        return importlib.import_module("leaguemanager").__version__

    def get_relases(self) -> Response:
        return self.client.get("releases")

    def get_latest_release(self) -> Response:
        return self.client.get("releases/latest")

    def create_release(self, data: dict) -> Response:
        # test_data = {
        #     "body": "Add CLI for auto release.",
        #     "draft": True,
        #     "hide_archive_links": True,
        #     "name": "v0.5.4",
        #     "prerelease": False,
        #     "tag_name": "v0.5.4",
        #     "target_commitish": "string",
        # }
        return self.client.post("releases", json=data)


app = typer.Typer(no_args_is_help=True)
cb = CBAPI()


def _release_body(create: bool) -> ReleaseBody:
    if not create:
        return
    body = ReleaseBody()
    current_version = cb.current_version

    line = typer.prompt("Input release line: ")
    body.add_line(line)
    more = typer.confirm("Add more release lines?")
    while more:
        line = typer.prompt("Input release line: ")
        body.add_line(line)
        more = typer.confirm("Add more release lines?")
    release = Release(
        tag_name=f"v{current_version}",
        name=f"v{current_version}",
        body=body.text,
    )
    typer.confirm("Publish to Codeberg?")
    return asdict(release)


@app.callback(no_args_is_help=True)
def main():
    return


@app.command()
def releases(
    create: bool = typer.Option(
        False, "--create", "-c", is_flag=True, callback=_release_body, help="Create a release."
    ),
    latest: bool = typer.Option(False, "--latest", "-l", is_flag=True, help="Get the latest release."),
) -> None:
    """Release commands."""
    if latest:
        latest_release = cb.get_latest_release().json()
        print(json.dumps(latest_release, indent=4))
        return
    if create:
        _ = cb.create_release(data=create)
        print(f"Created Release v{cb.current_version} in Codeberg.")
        return

    releases = cb.get_relases().json()
    print(json.dumps(releases, indent=4))
    return


if __name__ == "__main__":
    app(prog_name="cbapi")
