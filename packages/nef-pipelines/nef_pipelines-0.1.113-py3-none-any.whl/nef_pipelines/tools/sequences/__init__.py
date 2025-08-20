import typer

from nef_pipelines import nef_app

sequences_app = typer.Typer()


if nef_app.app:
    nef_app.app.add_typer(
        sequences_app, name="sequences", help="- import and manage sequences from various formats"
    )

    # import of specific importers must be after app creation to avoid circular imports
    import nef_pipelines.tools.sequences.ucbshift  # noqa: F401