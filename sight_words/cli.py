"""The main sight-words entry-point."""
import pathlib

import click

from sight_words import data_utils, data_rep, ml


@click.group()
def main():
    pass


@main.command("new_data_file")
@click.argument("file_path", type=click.Path())
@click.argument("grade", type=int)
@click.option("--past_grade_success_incr", type=int, default=3)
def new_data_file(file_path, grade, past_grade_success_incr):
    """Initializes a new datafile"""
    click.secho(f"Creating new data file for grade {grade}.")
    dataset = data_utils.build_new_dataset(
        max_grade=grade, past_grade_success_incr=past_grade_success_incr
    )
    click.secho(f"Saving data file at {file_path}.")
    data_utils.save_dataset(pathlib.Path(file_path), dataset)
    click.secho(f"Done.")


@main.command("test")
@click.argument("data_file", type=click.Path())
@click.option("--inv_temp", type=float, default=1)
@click.option("--inv_grade_temp", type=float, default=1)
def test(data_file, inv_temp, inv_grade_temp):
    """Tests"""
    data_file = pathlib.Path(data_file)
    dataset = data_utils.load_dataset(data_file)
    word = ml.choose_word(dataset, inv_temp=inv_temp, inv_grade_temp=inv_grade_temp)
    click.secho(word)
    success = None
    while success is None:
        success_str = input("success (y/n)?")
        if success_str.lower()[0] == "y":
            success = True
        elif success_str.lower()[0] == "n":
            success = False
    dataset = data_utils.update_dataset(
        dataset, word=word, successes=1 if success else 0, failures=0 if success else 1
    )
    data_utils.save_dataset(data_file, dataset)


if __name__ == "__main__":
    main()
