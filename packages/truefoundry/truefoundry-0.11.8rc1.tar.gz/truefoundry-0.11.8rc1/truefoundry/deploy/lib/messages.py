TFY = "TFY"

# TODO: probably create another `rich_messages.py` and apply all formatting there
PROMPT_LOGOUT_SUCCESSFUL = """[green bold]Logged Out![/]"""
PROMPT_ALREADY_LOGGED_OUT = """[yellow]You are already logged out[/]"""
PROMPT_CREATING_NEW_WORKSPACE = """[yellow]Creating a new workspace {!r}[/]"""
PROMPT_DELETED_WORKSPACE = """[green]Deleted workspace {!r}[/]"""
PROMPT_DELETED_APPLICATION = """[green]Deleted Application {!r}[/]"""
PROMPT_NO_WORKSPACES = f"""[yellow]No workspaces found. Either cluster name is wrong, or your cluster doesn't contain any workspaces. You can create one with [bold]{TFY} create workspace[/][/]"""
PROMPT_NO_APPLICATIONS = f"""[yellow]No applications found. You can create one with [bold]{TFY} deploy[/] from within your application folder"""
PROMPT_NO_VERSIONS = """[yellow]No application versions found."""
PROMPT_APPLYING_MANIFEST = """[yellow]Applying manifest for file {!r}[/]"""
PROMPT_DELETING_MANIFEST = """[yellow]Deleting manifest for file {!r}[/]"""
