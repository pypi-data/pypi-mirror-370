import click
from making_with_code_cli.teach.student.create import create_student
from making_with_code_cli.teach.student.update import update_student

@click.group()
def student():
    "Manage students"

student.add_command(create_student)
student.add_command(update_student)
