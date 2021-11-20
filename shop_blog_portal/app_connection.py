#!/usr/bin/env python3

import json
import click

import shopify


class PrivateApp:
    def __init__(self, shop: str, api_key: str, password: str) -> None:
        self.shop = shop
        self.api_key = api_key
        self.password = password
        self.shop_url = f"https://{api_key}:{password}@{shop}.myshopify.com/admin"

    def connect(self) -> None:
        shopify.ShopifyResource.set_site(self.shop_url)  # type: ignore

    def get_blogs(self):
        return shopify.Blog.find()

    def export_blogs(self, output_file: str) -> None:
        blogs = self.get_blogs()

        for b in blogs:
            b.attributes["articles"] = b.articles()

        blogs_export = [b.to_dict() for b in blogs]
        with open(output_file, "w") as f:
            json.dump(blogs_export, f, indent=4)

    def import_blogs(self, file: str) -> None:
        pass


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--store-name",
    prompt="Enter store name",
    help="Store to export from.",
)
@click.option(
    "--api-key",
    prompt="Enter private app api_key",
    help="Private app API key.",
)
@click.option(
    "--password",
    prompt="Enter private app password",
    hide_input=True,
    help="Private app password.",
)
@click.option(
    "--output-file",
    type=click.Path(dir_okay=False, writable=True, readable=False),
    default="blog_export.json",
    help="Output file path.",
)
def export(store_name: str, api_key: str, password: str, output_file: str):
    app = PrivateApp(
        shop=store_name,
        api_key=api_key,
        password=password,
    )

    app.connect()
    app.export_blogs(output_file)


if __name__ == "__main__":
    cli()
