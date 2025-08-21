import click
import requests
from pathlib import Path
from tqdm import tqdm
from making_with_code_cli.curriculum import get_curriculum
from making_with_code_cli.teach.check.check_module import TestMWCModule
from making_with_code_cli.styles import info, warn

@click.command()
@click.argument("url")
@click.argument("repo_dir", type=click.Path(exists=True, file_okay=False, writable=True, 
        path_type=Path))
@click.option("--course", "-c", help="Course name to check")
@click.option("--module", "-m", help="Module slug to check")
@click.option("--json", "-j", 'use_json', is_flag=True, help="JSON-structured output")
def check(url, repo_dir, course, module, use_json):
    "Test MWC curriuclum and modules"
    if course:
        courses = [get_curriculum(url, course)]
    else:
        courses = get_curriculum(url)['courses']
    test_cases = []
    for course in courses:
        for unit in course['units']:
            for mod in unit['modules']:
                if not module or mod['slug'] == module:
                    full_slug = '/'.join([course['slug'], unit['slug'], mod['slug']])
                    path = repo_dir / full_slug
                    test_cases.append((mod, path, full_slug))
    results = []
    if not module:
        test_cases = tqdm(test_cases)
    for mod, path, slug in test_cases:
        test = TestMWCModule(mod, path)
        errors = test.run()
        if errors:
            results.append((slug, errors))
    if len(test_cases) == 0:
        print(warn("No matching modules."))
    if use_json:
        print([{'module': slug, 'errors': errors} for slug, errors in results])
    else:
        for slug, errors in results:
            print(info(slug))
            for error in errors:
                print(warn(error, list_format=True))
