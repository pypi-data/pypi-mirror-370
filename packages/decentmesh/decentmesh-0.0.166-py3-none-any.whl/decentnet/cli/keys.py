import asyncio

import click
import rich
from rich.console import Console
from rich.table import Table

from decentnet.interface.alias_resolver import AliasResolver
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.utils.key_tools import generate_impl


@click.group()
def key():
    pass


@key.command()
@click.option('--private-key-file', '-p', default=None,
              help='Filename for the private key')
@click.option('--public-key-file', '-u', default=None,
              help='Filename for the public key')
@click.option("--description", "-d", default="", help="Description of the key")
@click.option("--sign", "-s", default=False, type=bool, help="Signing keys or Encryption",
              is_flag=True)
@click.option("--alias", "-a", default=None, help="Alias of the key", type=str)
def generate(private_key_file, public_key_file, description, sign, alias):
    """
    Generate SSH key pair.
    """
    suc = asyncio.run(generate_impl(description, private_key_file, public_key_file, sign, alias))
    if not suc:
        rich.print("[red]Failed to generate keys.[/red]")
        return
    rich.print("[green]Generated new keys and saved to database[/green]")


@key.command()
def list():
    keys = asyncio.run(KeyManager.get_all_keys())

    table = Table(title="Owned Keys")

    # Define columns
    table.add_column("Alias", justify="left", style="cyan", no_wrap=True)
    table.add_column("Public Key", justify="left", style="magenta")
    table.add_column("Description", justify="left", style="green")
    table.add_column("Can Encrypt", justify="center", style="bold yellow")

    # Add rows to the table
    for key in keys:
        table.add_row(
            key.alias,
            key.public_key,
            key.description,
            "Yes" if key.can_encrypt else "No"
        )

    # Display the table
    console = Console()
    console.print(table)


@key.command()
@click.option("--alias-sign", "-s", required=True, help="Alias of the key for signing")
@click.option("--alias-enc", "-e", required=True, help="Alias of the key for encryption")
@click.option('--qr', is_flag=True, help='Generate a QR code for the keys')
def share(alias_sign: str, alias_enc: str, qr: bool):
    akey, _ = AliasResolver.get_key_by_alias(alias_sign)
    aenc, _ = AliasResolver.get_key_by_alias(alias_enc)
    if qr:
        import qrcode
        keys_qr = qrcode.make(akey + aenc)
        keys_qr.show()
    else:
        print(f"{akey}.{aenc}")


@key.command("import")
@click.argument('private_key_path', type=click.Path(exists=True))
@click.argument('public_key_path', type=click.Path(exists=True))
def do_import(private_key_path, public_key_path):
    """
    Import SSH key pair from files.
    """
    private_key_obj, public_key_obj = KeyManager.import_ssh_key_pair(private_key_path,
                                                                     public_key_path)
    private_key, public_key = KeyManager.export_ssh_key_pair(private_key_obj,
                                                             public_key_obj)
    click.echo(f'Private Key:\n{private_key}\n')
    click.echo(f'Public Key:\n{public_key}\n')
