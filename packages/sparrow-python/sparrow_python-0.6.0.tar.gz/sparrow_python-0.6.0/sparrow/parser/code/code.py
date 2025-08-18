import os
from fnmatch import fnmatch
from typing import List, Tuple
import pathspec

lang_map = {
    '.py': 'python',
    '.js': 'javascript',
    '.html': 'html',
    '.css': 'css',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.sh': 'bash',
    '.rb': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.yml': 'yaml',
    '.yaml': 'yaml',
    '.toml': 'toml',
    # '.json': 'json',
    '.md': 'markdown',
    'Dockerfile': 'dockerfile',
}


def read_gitignore(gitignore_path: str) -> List[str]:
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if not line.startswith('#') and line.strip()]
    except Exception as e:
        print(f"Read gitignore Error: {e}")
        return []


def adjust_gitignore_patterns(gitignore_patterns: List[str], gitignore_path: str, extract_dir: str) -> List[str]:
    adjusted_patterns = []

    # Calculate the relative path from the directory of gitignore to extract_dir
    gitignore_dir = os.path.dirname(os.path.abspath(gitignore_path))
    extract_dir = os.path.abspath(extract_dir)

    relative_path = os.path.relpath(extract_dir, gitignore_dir)

    # If the relative path is '.', then the gitignore is in the same directory as extract_dir
    # So, we don't need to adjust the patterns
    if relative_path == '.':
        return gitignore_patterns

    # Otherwise, we adjust the patterns
    for pattern in gitignore_patterns:
        if pattern.startswith(relative_path):
            adjusted_pattern = pattern[len(relative_path) + 1:]  # +1 to remove the leading '/'
            if adjusted_pattern.startswith('./'):
                adjusted_pattern = adjusted_pattern[2:]  # Remove the leading './'
            adjusted_patterns.append(adjusted_pattern)
        else:
            adjusted_patterns.append(pattern)

    return adjusted_patterns


def should_ignore(file_path: str, spec=None) -> bool:
    """Check if a given file or directory should be ignored."""
    assert spec is not None
    if spec.match_file(file_path):
        return True
    return False


def generate_tree(directory: str, project_root: str, padding: str = '', spec=None) -> Tuple[
    List[str], int, int]:
    tree_str, folder_count, file_count = [], 0, 0
    sorted_files_dirs = sorted(os.listdir(directory))
    for file in sorted_files_dirs:
        path = os.path.join(directory, file)
        relative_path = os.path.relpath(path, project_root)

        if should_ignore(relative_path, spec):
            continue

        new_padding = padding + ('└── ' if file == sorted_files_dirs[-1] else '├── ')

        if os.path.isdir(path):
            subtree, sub_folders, sub_files = generate_tree(
                path, project_root, padding + ('    ' if file == sorted_files_dirs[-1] else '│   '), spec=spec
            )
            if sub_folders > 0 or sub_files > 0:
                tree_str.append(f"{new_padding}{file}/")
                tree_str.extend(subtree)
                folder_count += sub_folders + 1
                file_count += sub_files
        else:
            tree_str.append(f"{new_padding}{file}")
            file_count += 1

    return tree_str, folder_count, file_count


def generate_markdown(startpath: str, project_root: str, ignore_patterns: List[str], line_number: bool = False) -> str:
    spec = pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns)
    tree_str, folder_count, file_count = generate_tree(startpath, project_root, spec=spec)
    tree_str = [f"{line}\n" for line in tree_str]
    md_content = [
        f"# Project Overview\n",
        f"Total folders: {folder_count}  \n",
        f"Total files: {file_count}  \n",
        "\n# Project Directory Tree\n",
        f"```bash\n{os.path.basename(os.path.abspath(startpath))}/\n",
        *tree_str,
        "```\n",
        "\n# Code Files\n"
    ]

    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if
                   not should_ignore(os.path.relpath(os.path.join(root, d), project_root), spec=spec)]

        for file in sorted(files):
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, project_root)

            if should_ignore(relative_path, spec):
                continue

            md_content.append(f"\n## {relative_path}\n")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    md_content.append(f"```{lang_map.get(os.path.splitext(file)[-1], 'text')}\n")
                    for i, line in enumerate(f, 1):
                        if line_number:
                            md_content.append(f"{i:4} {line.rstrip()}\n")
                        else:
                            md_content.append(f"{line.rstrip()}\n")
                    md_content.append("```\n")
            except UnicodeDecodeError:
                md_content.append("This file could not be read as it contains non-UTF-8 encoded characters.\n")

    return ''.join(md_content)


def extract_to_md(extract_dir: str, gitignore_path: str = None,
                  target: str = './project_overview.md', line_number: bool = False) -> str:
    if os.path.exists(target):
        os.remove(target)

    default_ignore_patterns = ['.git', '*.gitignore', '.github', '__pycache__', 'venv', '*.png', "*.jpg", "*.svg"]
    if gitignore_path is None:
        gitignore_path = '.gitignore'
    ignore_patterns = read_gitignore(gitignore_path)

    # print(f"{ignore_patterns=},{gitignore_path=}, {extract_dir=}")

    ignore_patterns = adjust_gitignore_patterns(ignore_patterns, gitignore_path, extract_dir)
    ignore_patterns += default_ignore_patterns

    md_content = generate_markdown(extract_dir, extract_dir, ignore_patterns, line_number)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(md_content)
    return md_content


# Example usage:
# extract_to_md(extract_dir='./vector_search', gitignore_path='.gitignore')

# def refactor(extract_dir, target='./refactor_project_overview.txt'):
#     if os.path.exists(target):
#         os.remove(target)
#     content = (f"I will provide you with a project code description file next,"
#                f" including the directory tree of the project and the project code "
#                f"(which might also include some description files). "
#                f"Please help me refactor the project code for greater logic and readability."
#                f" If you identify any obvious errors in the code, please assist in correcting "
#                f"them and indicate in comments. The following is the description of my project code. "
#                f"\n")
#     md_content = generate_markdown(extract_dir, line_number=False)
#     content += md_content
#     with open(target, 'w', encoding='utf-8') as f:
#         f.write(content)
