"""The main sight-words entry-point."""
import itertools
import pathlib

import click
import pyttsx3

from sight_words import data_utils, ml, reports, data_rep


@click.group()
def main():
    pass


@main.command("new_data_file")
@click.argument("file_path", type=click.Path())
@click.argument("grade", type=int)
@click.option("--past_grade_success_incr", type=int, default=1)
@click.option("--text_name", type=str, default="p_and_p")
def new_data_file(file_path, grade, past_grade_success_incr, text_name):
    """Initializes a datafile for a new student"""
    click.secho(f"Creating new data file for grade {grade}.")
    words = data_utils.build_new_dataset(
        max_grade=grade, past_grade_success_incr=past_grade_success_incr
    )
    dataset = data_rep.DataSet(
        spelling_words=words, reading_words=words, text=text_name
    )
    click.secho(f"Saving data file at {file_path}.")
    data_utils.save_dataset(pathlib.Path(file_path), dataset)
    click.secho(f"Done.")


@main.command("parse_new_text")
@click.argument("text", type=click.Path())
@click.argument("name", type=str)
@click.option("--max_length", type=int, default=100)
def parse_new_text(text, name, max_length):
    """Parses a new text file for sentences"""
    click.secho(f"Parsing the text {text}.")
    dataset = data_utils.build_new_sentence_file(text, name, max_length=max_length)
    click.secho(f"Saved under {name}.")


@main.command("read")
@click.argument("data_file", type=click.Path())
@click.option("--inv_temp", type=float, default=1)
@click.option("--inv_grade_temp", type=float, default=1)
def read(data_file, inv_temp, inv_grade_temp):
    """Tests reading"""
    data_file = pathlib.Path(data_file)
    dataset = data_utils.load_dataset(data_file)
    success_str = None
    while success_str != "\quit":
        word = ml.choose_word(
            dataset.reading_words, inv_temp=inv_temp, inv_grade_temp=inv_grade_temp
        )
        click.secho("Please read:\n\n")
        click.secho(word)
        click.secho("\n")
        capture = False
        while not capture:
            success_str = input("Successful (y/n/\quit)? ")
            if success_str.lower()[0] == "y":
                dataset = data_utils.update_dataset(
                    dataset, reading_word=word, successes=1, failures=0
                )
                capture = True
            elif success_str.lower()[0] == "n":
                dataset = data_utils.update_dataset(
                    dataset, reading_word=word, successes=0, failures=1
                )
                capture = True
            elif success_str == "\quit":
                capture = True
        data_utils.save_dataset(data_file, dataset)


@main.command("spell")
@click.argument("data_file", type=click.Path())
@click.option("--inv_temp", type=float, default=1)
@click.option("--inv_grade_temp", type=float, default=1)
@click.option("--spoken/--silent", type=bool, default=True)
def spell(data_file, inv_temp, inv_grade_temp, spoken):
    """Tests spelling"""
    if spoken:
        engine = pyttsx3.init()
    else:
        engine = None
    data_file = pathlib.Path(data_file)
    dataset = data_utils.load_dataset(data_file)
    texts = [data_utils.get_indexed_sentences(text) for text in dataset.text]
    attempt = None

    while attempt != "\quit":
        word = ml.choose_word(
            dataset.spelling_words, inv_temp=inv_temp, inv_grade_temp=inv_grade_temp
        )
        sentence = None
        for text in texts:
            sentence = text.get_sentence(word)
            if sentence:
                break

        phrase = f"Please spell {word}"
        if sentence:
            phrase += f", as in: {sentence}. {word}."
        if engine:
            engine.say(phrase)
            engine.runAndWait()
        else:
            print(phrase)

        attempt = input("spelling (or \quit): ")
        if attempt == "\quit":
            click.secho("Quitting...")
            pass
        else:
            if attempt.lower().strip() == word.lower().strip():
                success = 1
                failure = 0
                click.secho("Correct!")
            else:
                success = 0
                failure = 1
                click.secho(f"{word} is the correct spelling.")
            dataset = data_utils.update_dataset(
                dataset, spelling_word=word, successes=success, failures=failure
            )
        data_utils.save_dataset(data_file, dataset)


@main.command("report")
@click.argument("data_file", type=click.Path())
@click.option("--n_worst", type=int, default=10)
def report(data_file, n_worst):
    """Get a performance report"""
    data_file = pathlib.Path(data_file)
    dataset = data_utils.load_dataset(data_file)

    click.secho("Spelling Grades:")
    for grade, mark in reports.marks_by_grade(dataset.spelling_words).items():
        click.secho(f"\t{mark}% in Grade {grade}")
    click.secho("Reading Grades:")
    for grade, mark in reports.marks_by_grade(dataset.reading_words).items():
        click.secho(f"\t{mark}% in Grade {grade}")

    click.secho("\n\nSpelling challenge words:")
    sorted_marks = reports.marks_by_word(dataset.spelling_words).items()
    for word, score in itertools.islice(sorted_marks, n_worst):
        click.secho(f"\t{word} (misspelt {100-score}%)")

    click.secho("\n\nReading challenge words:")
    sorted_marks = reports.marks_by_word(dataset.reading_words).items()
    for word, score in itertools.islice(sorted_marks, n_worst):
        click.secho(f"\t{word} (misspelt {100-score}%)")


if __name__ == "__main__":
    main()