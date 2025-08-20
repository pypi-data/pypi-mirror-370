from __future__ import annotations

import git
import os
import time


def is_repo_empty(repository):
    return not repository.heads


def get_repo(repo_path):
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        repo = git.Repo.init(repo_path)
        print(f"Initialized a new repository at {repo_path}")
    return repo


def start_watcher(
        repo_path='.',
        remote_repo_name: str | None = None,
        name="K.Y.Bot", email="beidongjiedeguang@gmail.com",
        interval=60
):
    repo = get_repo(repo_path)

    author = git.Actor(name=name, email=email)
    # use the active branch name
    branch_name = repo.active_branch.name

    # Setup remote
    if 'origin' in [remote.name for remote in repo.remotes]:
        remote = repo.remotes.origin
    else:
        assert remote_repo_name
        remote_url = f'git@guang:KenyonY/{remote_repo_name}.git'
        remote = repo.create_remote('origin', remote_url)

    # Fetch the remote repository if it exists
    try:
        remote.fetch()
        print(f"Fetched changes from remote repository: {remote_repo_name}")

        # Pull changes from the remote repo to local
        repo.git.pull(remote.name, branch_name)
        print("Pulled changes from remote repository!")
    except git.GitCommandError as e:
        print(f"Failed to fetch from remote repository. Reason: {e}")

    # Setup branch
    if branch_name in repo.heads:
        print("branch already exists")
    else:
        if is_repo_empty(repo):
            print("Initializing empty repository...")
            with open(os.path.join(repo_path, 'sparrow_conf.md'), 'w') as f:
                f.write('Initial commit.')

            repo.index.add(['sparrow_conf.md'])
            repo.index.commit('Initial commit', author=author)
            repo.create_head(branch_name, commit='HEAD')
        else:
            print("branch not exists, create a new one")
            repo.create_head(branch_name, commit='HEAD')

    repo.heads[branch_name].checkout()

    try:
        while True:
            print("Checking for changes...")
            time.sleep(interval)

            if repo.is_dirty(untracked_files=True):
                repo.git.add(A=True)
                repo.index.commit('Automatic commit', author=author)
                remote.push(branch_name)
                print("Committed and pushed changes!")
    except KeyboardInterrupt:
        if repo.is_dirty(untracked_files=True):
            repo.git.add(A=True)
            repo.index.commit('Automatic commit', author=author)
            remote.push(branch_name)
            print("Committed and pushed changes!")

# 存在问题，在push的时候无法识别我的ssh的github.com的别名
# import pygit2
# import os
# import time
#
#
# def is_repo_empty(repository):
#     try:
#         repository.head
#         return False
#     except pygit2.GitError:
#         return True
#
#
# def has_uncommitted_changes(repo):
#     status = repo.status()
#     return bool(status)  # True if there are changes, False otherwise
#
#
# def get_repo(repo_path):
#     try:
#         repo = pygit2.Repository(repo_path)
#         return repo
#     except pygit2.GitError:
#         repo = pygit2.init_repository(repo_path)
#         print(f"Initialized a new repository at {repo_path}")
#         return repo
#
#
# def credentials_callback(url, username_from_url, allowed_types):
#     # This will rely on default credentials. For example, SSH keys in default paths
#     # or credentials stored in a git credential helper.
#     return pygit2.KeypairFromAgent(username_from_url)
#
#
# def start_watcher(repo_path='.', remote_repo_name: str | None = None):
#     repo = get_repo(repo_path)
#
#     author = pygit2.Signature('K.Y.Bot', 'beidongjiedeguang@gmail.com')
#     branch_name = 'dev'
#     ref = f'refs/heads/{branch_name}'
#
#     if 'origin' in repo.remotes.names():
#         remote = repo.remotes['origin']
#     else:
#         assert remote_repo_name
#         remote_url = f'git@guang:KenyonY/{remote_repo_name}.git'
#         remote = repo.remotes.create('origin', remote_url)
#
#     branch = repo.lookup_branch(branch_name)
#     if branch:
#         print("branch already exists")
#     elif not branch:
#         print("branch NOT exists")
#         if is_repo_empty(repo):
#             print("Initializing empty repository...")
#
#             # Create an initial commit if the repository is empty
#             config_file = "sparrow_conf.yaml"
#             with open(os.path.join(repo_path, 'sparrow_conf.md'), 'w') as f:
#                 f.write('Initial commit.')
#
#             index = repo.index
#             index.add(config_file)
#             index.write()
#
#             tree = index.write_tree()
#             commit_oid = repo.create_commit("HEAD", author, author, 'Initial commit', tree, [])
#             repo.create_branch(branch_name, repo.head.peel())
#             branch = repo.lookup_branch(branch_name)
#         else:
#             print("branch not exists, create a new one")
#             repo.create_branch(branch_name, repo.head.peel())
#             branch = repo.lookup_branch(branch_name)
#
#     repo.checkout(branch)
#
#     # callbacks = pygit2.RemoteCallbacks(credentials=credentials_callback)
#
#     def commit():
#         index = repo.index
#         index.add_all()
#         index.write()
#         tree = index.write_tree()
#         commit = repo.create_commit(ref, author, author, 'Automatic commit', tree, [repo.head.target])
#         print("Committed changes!")
#
#     def push():
#         remote.push([ref])
#
#     try:
#         while True:
#             print("Checking for changes...")
#             time.sleep(3)
#
#             if has_uncommitted_changes(repo):
#                 commit()
#                 push()
#     except KeyboardInterrupt:
#         commit()
#         push()
