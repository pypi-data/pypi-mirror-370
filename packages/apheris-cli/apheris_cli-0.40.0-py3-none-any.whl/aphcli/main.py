import typer
from typing_extensions import Annotated

from aphcli.utils import get_login_status

from . import compute, datasets, job, models
from .version import __version__

app = typer.Typer(no_args_is_help=True)

app.add_typer(
    datasets.app,
    name="datasets",
    help=("Use the sub-commands to interact with datasets."),
)
app.add_typer(
    compute.app,
    name="compute",
    help=("Use the sub-commands to interact with Compute Specs."),
)

app.add_typer(
    job.app,
    name="job",
    help=("Use the sub-commands to interact with jobs."),
)

app.add_typer(
    models.app,
    name="models",
    help="Interact with the Apheris Registry.",
)


@app.command(
    help="Interactive login to Apheris. You will be forwarded to a website. "
    "For machine to machine applications (m2m), make sure the environment variables "
    "`APH_SERVICE_USER_CLIENT_ID` and `APH_SERVICE_USER_CLIENT_SECRET` are set. "
    "Call `apheris login status` to check your login status."
)
def login(
    command: Annotated[
        str,
        typer.Argument(help="Call `apheris login status` to show your login status."),
    ] = None,
):
    import apheris_auth

    if command == "status":
        is_logged_in, email, organization, env = get_login_status()
        if is_logged_in:
            print(
                f"You are logged in:"
                f"\n\te-mail:\t\t{email}"
                f"\n\torganization:\t{organization}"
                f"\n\tenvironment:\t{env}"
            )
        else:
            print("You are not logged in.")

    elif not command:
        apheris_auth.login(login_mode="sso")
        login(command="status")
    else:
        print(f"Unknown command: {command}")
        raise typer.Exit(code=2)


@app.command(help="Log out of Apheris.")
def logout():
    import apheris_auth

    apheris_auth.logout()


@app.command(help="Print the version of the Apheris CLI.")
def version():
    print(__version__)


def main():
    app()
