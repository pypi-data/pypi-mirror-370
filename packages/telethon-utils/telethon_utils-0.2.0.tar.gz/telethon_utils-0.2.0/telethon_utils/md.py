def link(text: str, link: str) -> str:
    return f"[{text}]({link})"


def inline_code(text: str) -> str:
    return f"`{text}`"


def code_block(text: str) -> str:
    return f"```{text}```"


def bold(text: str) -> str:
    return f"**{text}**"
