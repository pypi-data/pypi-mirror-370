import click

from vessl.cli._base import VesslGroup, vessl_argument
from vessl.cli._util import print_data, print_table
from vessl.util.fmt import format_bool
from vessl.util.prompt import prompt_choices
from vessl.cli.organization import organization_name_option
from vessl.kernel_image import list_kernel_images, read_kernel_image


def image_id_prompter(ctx: click.Context, param: click.Parameter, value: int) -> int:
    images = list_kernel_images()
    return prompt_choices("Cluster", [(x.name, x.id) for x in images])


@click.command(name="image", cls=VesslGroup)
def cli():
    pass


@cli.vessl_command()
@vessl_argument("id", type=click.INT, required=True, prompter=image_id_prompter)
@organization_name_option
def read(id: int):
    image = read_kernel_image(image_id=id)
    print_data(
        {
            "Name": image.name,
            "URL": image.image_url,
            "Type": "Managed" if image.is_savvihub_managed else "Custom",
            "Public": format_bool(image.is_public),
            "Packages": image.packages.split("\n"),
        }
    )


@cli.vessl_command()
@organization_name_option
def list():
    images = list_kernel_images()
    print_table(
        images,
        ["Name", "URL"],
        lambda x: [x.name, x.image_url],
    )
