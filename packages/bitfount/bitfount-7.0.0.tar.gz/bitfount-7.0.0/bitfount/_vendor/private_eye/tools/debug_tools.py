import click


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_path", type=click.Path(dir_okay=False))
def histogram(input_path: str, output_path: str) -> None:
    from .histogram import create_histogram

    create_histogram(input_path, output_path)


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_folder", type=click.Path(file_okay=False, dir_okay=True))
@click.option("-s", "--series-id", type=int, default=-1)
def heidelberg(input_path: str, output_folder: str, series_id: int) -> None:
    from .heidelberg.deconstruct import deconstruct

    deconstruct(input_path, output_folder, series_id)


@cli.command(context_settings=dict(max_content_width=120))
@click.argument("parser")
@click.argument("input_path", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_folder", type=click.Path(file_okay=False, dir_okay=True))
def contours(parser: str, input_path: str, output_folder: str) -> None:
    """
    \b
        Dump CSV files containing contour information for all b-scans in the input file.

    \b
        A quick and dirty way of displaying the contours on the appropriate b-scan:
        1. Run 'pe-convert' using raw_images mode to export all b-scans as PNGs
        2. Run this command
        3. Open the CSV for a b-scan with a given ID in Excel
        4. Create a line graph using all data in the CSV. Each column should be titled with the name of the layer
        5. Adjust the y-scale to be between 0 and the height of the b-scan
        6. Format the plot area, select 'Fill', 'Picture or Gradient', and select the appropriate b-scan from step 1.
    """
    from .contours import dump_contours

    dump_contours(parser, input_path, output_folder)
