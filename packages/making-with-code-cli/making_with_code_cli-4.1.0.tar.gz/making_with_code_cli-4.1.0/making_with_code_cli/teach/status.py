import click
from csv import DictWriter
from collections import defaultdict
from tabulate import tabulate
from making_with_code_cli.settings import read_settings
from making_with_code_cli.teach.setup import check_required_teacher_settings
from making_with_code_cli.teach.student_repos import StudentRepos
from making_with_code_cli.helpers import date_string
from making_with_code_cli.teach.student_repo_functions import (
    count_commits,
    count_changed_py_lines,
    count_changed_md_lines,
    module_completion,
)
from making_with_code_cli.styles import (
    address,
    question,
    info,
    debug as debug_fmt,
    confirm,
    error,
)

measures = {
    "commits": ("Counting commits", count_commits),
    "py-lines": ("Counting changed lines in Python files", count_changed_py_lines),
    "md-lines": ("Counting changed lines in Markdown files", count_changed_md_lines),
    "completion": ("Running tests", module_completion),
}

@click.command()
@click.option("--config", help="Path to config file (default: ~/.mwc)")
@click.option("-s", "--section", help="Filter by section name/slug")
@click.option("-c", "--course", help="Filter by course name")
@click.option("-u", "--user", help="Filter by username")
@click.option("-n", "--unit", help="Filter by unit name/slug")
@click.option("-m", "--module", help="Filter by module name/slug")
@click.option("-v", "--measure", default="commits", type=click.Choice(measures.keys()), 
        help="Measure to show")
@click.option("-a", "--anonymous", is_flag=True, help="Hide usernames")
@click.option("-x", "--short", is_flag=True, help="Show short module names")
@click.option("-o", "--outfile", help="Save results as csv")
@click.option('-U', "--update", is_flag=True, help="Update repos first")
@click.option('-t', "--threads", type=int, default=8, help="Maximum simultaneous threads")
@click.option('-B', "--begin", type=date_string, help="Begin date")
@click.option('-C', "--end", type=date_string, help="End date")
def status(config, section, course, user, unit, module, measure, anonymous, short, 
        outfile, update, threads, begin, end):
    "Show status of student repos by module"
    if update:
        from making_with_code_cli.teach.update import update as update_task
        update_task.callback(config, section, course, user, unit, module, threads)
    settings = read_settings(config)
    if not check_required_teacher_settings(settings):
        return
    repos = StudentRepos(settings, threads)
    measure_status_message, measure_fn = measures[measure]
    results = repos.apply(
        measure_fn, 
        section=section, 
        course=course, 
        user=user, 
        unit=unit, 
        module=module, 
        begin=begin,
        end=end,
        status_message=measure_status_message
    )
    recursive_dict = lambda: defaultdict(recursive_dict)
    results_dict = recursive_dict()
    for r in results:
        s = r['section']['name'] + ' | ' + r['section']['course_name']
        results_dict[s][r['username']][r['module']] = r['score']
    all_scores = []
    for section, users in results_dict.items():
        if users:
            headers = ['username'] + sorted(next(iter(users.values())).keys())
            section_scores = format_user_scores(users, anonymous, short)
            all_scores += section_scores
            if not outfile:
                click.echo(address(section))
                click.echo(address(tabulate(section_scores, headers='keys'), 
                        preformatted=True))
    if outfile and all_scores:
        with open(outfile, 'w') as fh:
            writer = DictWriter(fh, headers)
            writer.writeheader()
            writer.writerows(all_scores)

def shorten_module_name(name):
    return name.replace("lab_", "").replace("project_", "").replace("problemset_", "")

def format_user_scores(scores, anonymous=False, short=False):
    formatted_scores = []
    for i, (username, user_scores) in enumerate(scores.items()):
        if anonymous: 
           username_dict  = {"username": f"student_{i}"}
        else:
            username_dict = {"username": username}
        if short: 
            formatted_user_scores = {
                shorten_module_name(k): v 
                for k, v in user_scores.items()
            }
        else:
            formatted_user_scores = user_scores
        formatted_scores.append(username_dict | formatted_user_scores)
    return sorted(formatted_scores, key=lambda user_scores_dict: user_scores_dict['username'])
    


