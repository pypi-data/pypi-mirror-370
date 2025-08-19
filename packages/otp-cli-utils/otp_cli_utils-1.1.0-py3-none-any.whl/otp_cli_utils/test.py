import sys

import typer

app = typer.Typer(
    name="otp-cli-utils",
    help="cli tool for OTP",
)


@app.command(help="validate otp")
def validate(
    otp: str = typer.Argument(help="The OTP code to validate"),
    secret: str = typer.Argument(help="OTP secret"),
):
    """
    Validate if the provided OTP matches the expected value for the given secret
    """
    print(otp + secret)


@app.command("get-otp", help="get otp code")
def get_otp(secret: str = typer.Argument(help="OTP secret")):
    """
    Get the current OTP code for the given secret
    """
    print(secret)


def main():
    app()


if __name__ == "__main__":
    main()
