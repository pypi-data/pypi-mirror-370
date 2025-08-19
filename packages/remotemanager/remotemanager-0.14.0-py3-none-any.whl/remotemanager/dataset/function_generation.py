from remotemanager.dataset.repo import date_format


def create_run_function(
    submitter: str,
    manifest_filename: str,
    script_run: bool = False,
    add_docstring: bool = True,
) -> str:
    """
    Generates a submission function for submitter

    script_run should be used if the target function (or script) does not
    log its output to the manifest (as is the case with None as the function)

    $1 is the runner short_uuid
    $2 is the path to the jobscript
    $3 is the path to the error file
    $4 is the path to the result file

    Args:
        submitter: submitter to generate for
        manifest_filename: path to manifest file
        script_run: handle completed and failed status updates in the function
        add_docstring: adds docstring to function if True
    """
    template = f"""{{docstring}}
submit_job_{{submitter_cmd}} () {{
    echo "$(date -u +'{date_format}') [$1] submitted" >> \
$sourcedir/{{manifest_filename}}
    {{submission_section}}
}}"""

    submission_normal = f"""{{submitter}} $2 2> $3 ||
    echo "$(date -u +'{date_format}') [$1] failed" >> \
$sourcedir/{{manifest_filename}}
"""
    submission_script = f"""if {{submitter}} $2 > $4 2> $3 ; then
        echo "$(date -u +'{date_format}') [$1] completed" >> \
$sourcedir/{{manifest_filename}}
    else
        echo "$(date -u +'{date_format}') [$1] failed" >> \
$sourcedir/{{manifest_filename}}
    fi"""

    if script_run:
        template = template.replace("{submission_section}", submission_script)
    else:
        template = template.replace("{submission_section}", submission_normal)
    template = template.replace("{manifest_filename}", manifest_filename)
    template = template.replace("{submitter}", submitter)

    # strip any flags from the cmd
    template = template.replace("{submitter_cmd}", submitter.split(" ", maxsplit=1)[0])

    docstring = """# This function handles the running of jobs
# Arguments:
#   $1 is the runner short_uuid
#   $2 is the path to the jobscript
#   $3 is the path to the error file
#   $4 is the path to the result file"""

    if add_docstring:
        template = template.replace("{docstring}", docstring)
    else:
        template = template.replace("{docstring}", "")

    return template
