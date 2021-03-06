""" Generic mamba server command interface """


class MambaCommand:
    """ Mamba server command interface """
    @staticmethod
    def syntax():
        """
        Command syntax (preferably one-line). Do not include command name.
        """
        return ""

    @staticmethod
    def short_desc():
        """
        A short description of the command
        """
        return ""

    @staticmethod
    def long_desc():
        """A long description of the command. Return short description when not
        available. It cannot contain newlines, since contents will be formatted
        by optparser which removes newlines and wraps text.
        """
        return MambaCommand.short_desc()

    @staticmethod
    def help():
        """An extensive help for the command. It will be shown when using the
        "help" command. It can contain newlines, since no post-formatting will
        be applied to its contents.
        """
        return MambaCommand.long_desc()

    @staticmethod
    def add_arguments(parser):
        """
        Populate option parse with options available for this command
        """
        pass

    @staticmethod
    def run(args, mamba_dir, project_dir):
        """
        Entry point for running commands
        """
        raise NotImplementedError
