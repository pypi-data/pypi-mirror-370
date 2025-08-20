#!/usr/bin/env python3
# -*- coding: utf-8 -*-

extensions = [
    "sphinx.ext.doctest",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]

source_suffix = ".rst"

master_doc = "index"

project = "waflibs"
copyright = "2019, Felix Wong"
author = "Felix Wong"

version = open("VERSION").read().strip()
release = version

language = None

exclude_patterns = []

pygments_style = "sphinx"

todo_include_todos = True

html_theme = "alabaster"

html_static_path = ["_static"]

htmlhelp_basename = "waflibsdoc"

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "figure_align": "htbp",
}

latex_documents = [
    (
        master_doc,
        "waflibs.tex",
        "waflibs Documentation",
        "Felix Wong",
        "manual",
    ),
]

man_pages = [(master_doc, "waflibs", "waflibs Documentation", [author], 1)]

texinfo_documents = [
    (
        master_doc,
        "waflibs",
        "waflibs Documentation",
        author,
        "waflibs",
        "One line description of project.",
        "Miscellaneous",
    ),
]
