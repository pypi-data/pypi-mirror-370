#def main():
#    print("Hello from ys-portal-gun!")
import typer

app = typer.Typer()

@app.callback()
def callback():
    """
    Aweson Portal Gun
    """


@app.command()
def shoot():
    """
    Shoot the portal gun
    """
    typer.echo("Shooting portal gun")


@app.command()
def load():
    """
    Load the portal gun
    """
    typer.echo("Loading portal gun")

