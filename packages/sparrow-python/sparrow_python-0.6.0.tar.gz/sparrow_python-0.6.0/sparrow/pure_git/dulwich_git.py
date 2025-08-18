from dulwich import porcelain

class DulwichGit:
    user_name = None
    user_email = None

    @classmethod
    def set_user(cls, name, email):
        cls.user_name = name
        cls.user_email = email

    @classmethod
    def clone(cls, repo_url, path, username=None, password=None):
        """克隆仓库，支持用户名密码认证"""
        return porcelain.clone(repo_url, path, username=username, password=password)

    @classmethod
    def pull(cls, path, remote='origin', username=None, password=None):
        """拉取远程更新，支持认证"""
        return porcelain.pull(path, remote, username=username, password=password)

    @classmethod
    def push(cls, path, remote='origin', ref='refs/heads/master', username=None, password=None):
        """推送到远程，支持认证"""
        return porcelain.push(path, remote, ref, username=username, password=password)

    @classmethod
    def init(cls, path):
        """初始化仓库"""
        return porcelain.init(path)

    @classmethod
    def add(cls, path, paths):
        """添加文件到暂存区"""
        return porcelain.add(path, paths)

    @classmethod
    def commit(cls, path, message):
        """提交更改，自动带上类属性 user_name 和 user_email"""
        author = None
        if cls.user_name and cls.user_email:
            author = f"{cls.user_name} <{cls.user_email}>".encode('utf-8')
        return porcelain.commit(path, message.encode('utf-8'), author=author)

    @classmethod
    def status(cls, path):
        """查看仓库状态"""
        return porcelain.status(path)

    @classmethod
    def log(cls, path, max_entries=10):
        """查看提交日志"""
        return porcelain.log(path, max_entries=max_entries)

    @classmethod
    def branch_list(cls, path):
        """列出分支"""
        return porcelain.branch_list(path)

    @classmethod
    def branch_create(cls, path, branch):
        """创建分支"""
        return porcelain.branch_create(path, branch)

    @classmethod
    def checkout(cls, path, branch):
        """切换分支"""
        return porcelain.checkout(path, branch)

    @classmethod
    def merge(cls, path, branch):
        """合并分支"""
        return porcelain.merge(path, branch)

    @classmethod
    def tag_create(cls, path, tag, message=None):
        """创建标签"""
        return porcelain.tag_create(path, tag, message=message)

    @classmethod
    def fetch(cls, path, remote='origin', username=None, password=None):
        """拉取远程分支"""
        return porcelain.fetch(path, remote, username=username, password=password)

    @classmethod
    def remote_add(cls, path, name, url):
        """添加远程仓库"""
        return porcelain.remote_add(path, name, url)

    @classmethod
    def remote_list(cls, path):
        """列出远程仓库"""
        return porcelain.remote_list(path)

    @classmethod
    def ls_remote(cls, repo_url, username=None, password=None):
        """列出远程仓库引用"""
        return porcelain.ls_remote(repo_url, username=username, password=password)

    @classmethod
    def rebase(cls, *args, **kwargs):
        """预留 rebase 接口，Dulwich 暂无直接支持"""
        raise NotImplementedError('Dulwich 暂不支持 rebase，可自行实现') 