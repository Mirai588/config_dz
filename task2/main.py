import os
import zlib
import datetime
from graphviz import Digraph


def read_git_object(repo_path, object_hash):
    object_path = os.path.join(repo_path, '.git', 'objects', object_hash[:2], object_hash[2:])
    try:
        with open(object_path, 'rb') as file:
            compressed_data = file.read()
            decompressed_data = zlib.decompress(compressed_data)
            header, data = decompressed_data.split(b'\x00', 1)
            obj_type = header.split(b' ')[0].decode('utf-8')
            return obj_type, data
    except FileNotFoundError:
        return None, None


def parse_commit(repo_path, commit_hash, commits, visited=None):
    if visited is None:
        visited = set()

    if commit_hash in visited:
        return

    visited.add(commit_hash)

    obj_type, commit_data = read_git_object(repo_path, commit_hash)
    if obj_type != 'commit':
        return

    lines = commit_data.decode('utf-8').splitlines()
    parents = []
    date = None

    for line in lines:
        if line.startswith('parent '):
            parents.append(line.split(' ')[1])
        elif line.startswith('committer '):
            timestamp = int(line.split()[-2])
            date = datetime.datetime.fromtimestamp(timestamp)

    if date:
        commits.append({
            'id': commit_hash,
            'date': date,
            'parents': parents
        })

    for parent_hash in parents:
        parse_commit(repo_path, parent_hash, commits, visited)


def read_all_commits(repo_path):
    head_commit = resolve_head_commit(repo_path)
    commits = []
    parse_commit(repo_path, head_commit, commits)
    return commits


def resolve_head_commit(repo_path):
    head_path = os.path.join(repo_path, '.git', 'HEAD')
    with open(head_path, 'r') as file:
        ref = file.readline().strip()
        if ref.startswith('ref:'):
            ref_path = os.path.join(repo_path, '.git', *ref.split()[1].split('/'))
            with open(ref_path, 'r') as ref_file:
                return ref_file.readline().strip()
        return ref


def filter_commits_by_date(commits, cutoff_date):
    return [commit for commit in commits if commit['date'] <= cutoff_date]


def build_dependency_graph(commits):
    dot = Digraph(comment='Dependency Graph')
    dot.attr(rankdir='BT')

    for commit in commits:
        dot.node(commit['id'], commit['id'])
        for parent in commit['parents']:
            dot.edge(parent, commit['id'])

    return dot


def main(repo_path, output_path, cutoff_date_str):
    cutoff_date = datetime.datetime.strptime(cutoff_date_str, '%d.%m.%Y')
    commits = read_all_commits(repo_path)
    filtered_commits = filter_commits_by_date(commits, cutoff_date)
    filtered_commits.sort(key=lambda x: x['date'])
    graph = build_dependency_graph(filtered_commits)

    print("Сгенерированный код Graphviz:")
    print(graph.source)

    with open(output_path, 'w') as file:
        file.write(graph.source)
    graph.render('output', format='png', cleanup=True)

    print(f'Граф зависимостей успешно сохранен в файле {output_path} и output.png')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Визуализатор графа зависимостей коммитов Git.')
    parser.add_argument('--repo', type=str, required=True, help='Путь к анализируемому репозиторию.')
    parser.add_argument('--output', type=str, required=True, help='Путь к файлу для сохранения графа (без расширения).')
    parser.add_argument('--date', type=str, required=True, help='Дата в формате dd.mm.yyyy.')

    args = parser.parse_args()
    main(args.repo, args.output, args.date)
