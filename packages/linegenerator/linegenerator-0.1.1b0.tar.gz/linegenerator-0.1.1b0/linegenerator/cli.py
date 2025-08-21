import typer
from faker import Faker
from linegenerator.generator import Generators, LinesGenerator

app = typer.Typer(
    name="linegenerator-cli",
    help="Synthetic data line generator",
    add_completion=True,
)


@app.command()
def main(
        template: str = typer.Option("Hello, {name}!", "--template", "-t", help="Line template"),
        count: int = typer.Option(1, "--count", "-n", help="Numbers of lines"),
        help_generators: bool = typer.Option(False, "-help-generators", help="Show list default generators")
):
    faker = Faker()
    faker_gen = Generators(faker)
    lines_gen = LinesGenerator(template, faker_gen, count)

    if help_generators:
        typer.secho("Available generators:", bold=True, fg=typer.colors.BLUE)
        # TODO: add generators description
        for field in sorted(faker_gen.get_all_generators()):
            typer.echo(f"  {{{field}}}")
        raise typer.Exit()

    for line in lines_gen.lines_generator():
        print(line)


if __name__ == "__main__":
    app()
