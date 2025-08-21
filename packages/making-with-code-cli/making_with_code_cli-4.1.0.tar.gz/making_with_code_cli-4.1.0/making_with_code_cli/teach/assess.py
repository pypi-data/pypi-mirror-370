# teach/assess.py
# ---------------
# Implements `mwc teach assess`.
# This task iterates over student repos and assesses them.
# 
# New settings:
# - I need some way of specifying a search root for assessment repos.
#   Possibly teacher_assessment_repo_dir. We would search this directory
#   for a directory having the same name as the lab being assessed. Within
#   this direcory, we would locate assessment_policy.toml and possibly
#   modules for testing. It would be recommended that assessment materials
#   not be shared with students, but instead to be kept in an assessment
#   branch of the base repos which are forked.
# Assessment: 
# - A student module (lab, project, or problem set) is assessed according
#   to a policy, which defines:
#   - A front matter comment
#   - The type of assessment (completion, points, or rubric)
#   - The method of scoring:
#     - Using a measure (e.g. number of commits, lines of code changed)
#     - Using automated tests
#     - Qualitatively through teacher interaction
# - Assessment is recorded in `assessment.md`, in a student's module repo.
#   Machine-readable information is stored in TOML-based front matter, using
#   an [[assessment]] table for each time assessment occurs. Each [[assessment]]
#   has keys for date and score. The type of score depends on the type of assessment, 
#   and could be a string (effectively an enum) representing completion, a ratio
#   (a two-integer array specifying points awarded and points possible), or 
#   a sub-table for rubric scores.
# - Assessment should be repeatable, with subsequent assessments appended to the record.
