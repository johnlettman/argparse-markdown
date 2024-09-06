from argparse import ArgumentParser

from markdown_helper import Document, Header, Section, Table
from rich_tools import strip_markup_tags as strip_rich
from strip_ansi import strip_ansi


def normalize_text(text: str) -> str:
    return strip_ansi(strip_rich(text))


def get_prog(parser: ArgumentParser) -> str:
    if parser.prog is None or parser.prog == "":
        prog = "prog"
    else:
        prog = normalize_text(parser.prog)

    return prog


def get_description(parser: ArgumentParser) -> str:
    if parser.description is not None and parser.description != "":
        return f"> {normalize_text(parser.description)}\n"
    else:
        return ""


def generate_usage_section(parser: ArgumentParser) -> Section:
    section = Section(Header("Usage", 2))
    usage = normalize_text(parser.format_usage())
    section.add(f"```\n{usage.strip()}\n```")
    return section


def generate_arguments_section(parser: ArgumentParser) -> Section:
    section = Section(Header("Arguments", 2))

    for group in parser._action_groups:
        title = str(group.title).title()
        if title == "Positional Arguments":
            continue

        section.add(Header(title, 3))

        if group.description is not None and group.description != "":
            section.add(f"> {normalize_text(group.description)}\n")

        options = Table(["Short", "Long", "MetaVar", "Default", "Help"])

        for action in group._group_actions:
            long = list(filter(lambda s: s.startswith("--"), action.option_strings))
            short = filter(lambda s: s not in long, action.option_strings)

            long_str = ", ".join(map(lambda s: f"`{s}`", long))
            short_str = ", ".join(map(lambda s: f"`{s}`", short))

            metavar = f"`{action.metavar}`" if action.metavar is not None else ""
            default = f"`{action.default}`" if action.default is not None else ""

            options.add_row([short_str, long_str, metavar, default, action.help])

        section.add(options)

    return section


def generate_document(parser: ArgumentParser) -> Document:
    doc = Document(get_prog(parser) + "\n" + get_description(parser), "")
    doc.add_section(generate_usage_section(parser))
    doc.add_section(generate_arguments_section(parser))
    return doc


def generate_markdown(parser: ArgumentParser) -> str:
    return str(generate_document(parser))
