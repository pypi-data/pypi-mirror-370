from sparrow.string.color_string import rgb_string, color_const
from git import Repo, RemoteProgress
import os
from sparrow.utils.cursor import Cursor

cursor = Cursor()


class CloneProgress(RemoteProgress):
    MESSAGE = ''

    def update(self, op_code, cur_count, max_count=None, message=""):
        percent = cur_count / (max_count or 100.0) * 100
        self.MESSAGE = message if message != "" else self.MESSAGE
        print(f"\r{int(cur_count)}|{int(max_count)} {self.MESSAGE} PERCENT:{percent:.0f}% {cursor.EraseLine(0)} ",
              end='', flush=True)


def clone(url: str, save_path=None, branch=None, proxy=False):
    url = url.strip()
    repo_name = url.split('/')[-1][:-len('.git')]
    if url.startswith('git'):
        git_proxy_dir = url.strip()
    else:
        # git_proxy_dir = f"https://ghproxy.com/{url.strip()}" if gh_proxy else url.strip()
        if proxy:
            git_proxy_dir = f"{url.strip()}".replace("https://github.com", "https://github.kunyuan.sh.cn")
            git_proxy_dir = f"{git_proxy_dir}".replace("https://huggingface.co", "https://huggingface.kunyuan.sh.cn")
        else:
            git_proxy_dir = url.strip()
    print(rgb_string(f"Cloning into '{repo_name}' ...", color=color_const.green))
    to_path = save_path if save_path else repo_name
    print(f"{git_proxy_dir=}")
    Repo.clone_from(git_proxy_dir, to_path=to_path, branch=branch, progress=CloneProgress())


def clone_cmd(url: str, save_path=None, gh_proxy=False):
    to_path = save_path if save_path else ""
    url = url.strip()
    gh_url = f"https://ghproxy.com/{url}" if gh_proxy else url
    os.system(f"git clone {gh_url} {to_path}")


if __name__ == "__main__":
    clone("https://github.com/beidongjiedeguang/beidongjiedeguang.git")
    # clone_cmd("https://github.com/beidongjiedeguang/beidongjiedeguang.git")
