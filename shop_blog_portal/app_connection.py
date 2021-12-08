#!/usr/bin/env python3

import json
import click
from typing import List, Dict

import shopify


class PrivateApp:
    def __init__(self, shop: str, api_key: str, password: str) -> None:
        self.shop = shop
        self.api_key = api_key
        self.password = password
        self.shop_url = f"https://{api_key}:{password}@{shop}.myshopify.com/admin"

    def connect(self) -> None:
        shopify.ShopifyResource.set_site(self.shop_url)  # type: ignore

    def get_posted_blogs(self) -> Dict[str, shopify.Blog]:
        return {b.attributes["handle"]: b for b in shopify.Blog.find()}

    def export_blogs(self, output_file: str) -> None:
        posted_blogs = self.get_posted_blogs()

        for handle, blog in posted_blogs.items():
            blog.attributes["articles"] = blog.articles()
            posted_blogs[handle] = blog.to_dict()

        with open(output_file, "w") as f:
            json.dump(posted_blogs, f, indent=4)

    def post_article(self, blog_id: str, article: shopify.Article) -> None:
        a = {
            "blog_id": blog_id,
            "title": article["title"],
            "handle": article["handle"],
            "author": article.get("author"),
            "tags": article.get("tags"),
            "body_html": article.get("body_html"),
            "image": article.get("image"),
        }
        shopify.Article.create(a)
        print("Added: ", article.get("handle"))

    def import_posted_blog(self, posted_blog: shopify.Blog, exported_articles: List[shopify.Article]) -> None:
        posted_articles = set(a.to_dict().get("handle") for a in posted_blog.articles())
        for article in exported_articles:
            if article["handle"] not in posted_articles:
                self.post_article(posted_blog.id, article)

    def import_new_blog(self, blog: shopify.Blog, exported_articles: List[shopify.Article]) -> None:
        b = {
            "title": blog["title"],
            "handle": blog["handle"],
        }
        new_blog = shopify.Blog.create(b)
        for article in exported_articles:
            self.post_article(new_blog.id, article)

    def import_blogs(self, input_file: str) -> None:
        posted_blogs = self.get_posted_blogs()

        with open(input_file, "r") as f:
            exported_blogs = json.load(f)

        for handle, blog in exported_blogs.items():
            exported_articles = blog["articles"]
            posted_blog = posted_blogs.get(handle)

            if posted_blog:
                # print(handle, "blog exists: importing only new articles")
                self.import_posted_blog(posted_blog, exported_articles)
            else:
                # print(handle, "blog does not exist: importing entire blog, including all articles")
                self.import_new_blog(blog, exported_articles)


@click.group()
def cli():
    pass


@cli.command(name="export")
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
def export_blogs(store_name: str, api_key: str, password: str, output_file: str):
    app = PrivateApp(
        shop=store_name,
        api_key=api_key,
        password=password,
    )

    app.connect()
    app.export_blogs(output_file)


@cli.command(name="import")
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
    "--input-file",
    type=click.Path(dir_okay=False, writable=False, readable=True),
    default="blog_export.json",
    help="Input file path.",
)
def import_blogs(store_name: str, api_key: str, password: str, input_file: str):
    app = PrivateApp(
        shop=store_name,
        api_key=api_key,
        password=password,
    )

    app.connect()
    app.import_blogs(input_file)


if __name__ == "__main__":
    cli()
