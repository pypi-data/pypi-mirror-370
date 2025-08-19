import click

from mosamatic.commands import (
    calculatescores,
    copyfiles,
    decompressdicomfiles,
    rescaledicomfiles,
    segmentmusclefatl3,
    segmentmusclefatl3tensorflow,
    runpipeline,
)
from mosamatic.utils import show_doc_command


class CustomHelpGroup(click.Group):
    def format_commands(self, ctx, formatter):
        commands = self.list_commands(ctx)
        with formatter.section('Commands'):
            for command_name in commands:
                command = self.get_command(ctx, command_name)
                if command is None or command.hidden:
                    continue
                help_text = command.get_short_help_str()
                formatter.write_text(f'{command_name:15} {help_text}')


@click.group(cls=CustomHelpGroup)
def cli():
    pass


cli.add_command(calculatescores.calculatescores)
cli.add_command(copyfiles.copyfiles)
cli.add_command(decompressdicomfiles.decompressdicomfiles)
cli.add_command(rescaledicomfiles.rescaledicomfiles)
cli.add_command(segmentmusclefatl3.segmentmusclefatl3)
cli.add_command(segmentmusclefatl3tensorflow.segmentmusclefatl3tensorflow)
cli.add_command(runpipeline.runpipeline)

cli.add_command(show_doc_command(cli)) # Special command to show long description for command