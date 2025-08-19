#!/usr/bin/env python3

# Copyright (c) 2025 Marcelão Dev <eu@marcelao.dev>
# MIT License
# (see LICENSE or https://opensource.org/licenses/MIT)

"""
Append some string to a MkDocs page's <head>.
"""

from mkdocs.config.config_options import Type
from mkdocs.config import Config
from mkdocs.plugins import BasePlugin


class MkAppendToHead(BasePlugin):

    config_scheme = (
        ('append_str', Type(str, default='')),
        ('pages', Type(list, default=[])),
    )

    def on_post_page(self, output_content: str, page, config: Config):
        if (not self.config["pages"] or page.title in self.config["pages"]):
            output_content = output_content.replace("</head>", '  ' + self.config["append_str"] + '\n  </head>')

        return output_content

