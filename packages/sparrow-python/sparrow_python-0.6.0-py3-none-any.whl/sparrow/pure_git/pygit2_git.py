import pygit2

class PyGit2Git:
    @staticmethod
    def clone(repo_url, path):
        """克隆仓库"""
        return pygit2.clone_repository(repo_url, path)

    @staticmethod
    def pull(path, remote_name='origin', branch='master', user_name=None, user_email=None):
        """拉取远程更新并合并到本地分支"""
        repo = pygit2.Repository(f'{path}/.git')
        remote = repo.remotes[remote_name]
        remote.fetch()
        remote_branch = f'refs/remotes/{remote_name}/{branch}'
        remote_branch_id = repo.lookup_reference(remote_branch).target
        repo.merge(remote_branch_id)
        if repo.index.conflicts is not None:
            raise Exception('有冲突需要解决')
        user = pygit2.Signature(user_name or 'User', user_email or 'user@example.com')
        repo.index.write()
        tree = repo.index.write_tree()
        repo.create_commit(
            'HEAD',
            user,
            user,
            'Merge remote-tracking branch',
            tree,
            [repo.head.target]
        )
        repo.state_cleanup()

    @staticmethod
    def push(path, remote_name='origin', branch='master', username=None, password=None):
        """推送到远程"""
        repo = pygit2.Repository(f'{path}/.git')
        remote = repo.remotes[remote_name]
        if username and password:
            credentials = pygit2.UserPass(username, password)
            callbacks = pygit2.RemoteCallbacks(credentials=credentials)
        else:
            callbacks = None
        remote.push([f'refs/heads/{branch}'], callbacks=callbacks)

    @staticmethod
    def rebase(path, upstream_branch='origin/master', user_name=None, user_email=None):
        """rebase 本地分支到远程分支"""
        repo = pygit2.Repository(f'{path}/.git')
        rebase = repo.rebase_init(
            repo.head.target,
            repo.lookup_reference(f'refs/remotes/{upstream_branch}').target,
            None
        )
        while True:
            operation = rebase.next()
            if operation is None:
                break
            # 这里可以处理冲突
        rebase.finish() 