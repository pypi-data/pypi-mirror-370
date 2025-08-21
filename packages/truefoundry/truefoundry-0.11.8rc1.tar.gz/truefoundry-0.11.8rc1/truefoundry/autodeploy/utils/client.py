from truefoundry.autodeploy.exception import InvalidRequirementsException


def get_git_binary():
    try:
        import git

        return git
    except Exception as ex:
        raise InvalidRequirementsException(
            message="We cannot find the 'git' command. We use Git to track changes made while automatically building your project. Please install Git to use this feature or manually create a 'truefoundry.yaml' file."
        ) from ex
