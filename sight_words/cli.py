"""The main sight-words entry-point."""
import itertools
import pathlib

import blessed
import click

from sight_words.games import stacking, tetris
from sight_words import data_utils, ml, reports, data_rep, io, game


@click.group()
def main():
    """The Word Practice program. Please choose spell, read, or
    add a new student, parse a new text, or generate a report"""
    pass


@main.command("new_data_file")
@click.argument("file_path", type=click.Path())
@click.argument("grade", type=int)
@click.option("--past_grade_success_incr", type=int, default=1)
@click.option("--text_name", type=str, multiple=True, default=("p_and_p",))
def new_data_file(file_path, grade, past_grade_success_incr, text_name):
    """Initializes a datafile for a new student"""
    click.secho(f"Creating new data file for grade {grade}.")
    words = data_utils.build_new_dataset(
        max_grade=grade, past_grade_success_incr=past_grade_success_incr
    )
    dataset = data_rep.DataSet(
        spelling_words=words, reading_words=words, text=list(text_name)
    )
    click.secho(f"Saving data file at {file_path}.")
    data_utils.save_dataset(pathlib.Path(file_path), dataset)
    click.secho("Done.")


@main.command("parse_new_text")
@click.argument("text", type=click.Path())
@click.argument("name", type=str)
@click.option("--max_length", type=int, default=100)
def parse_new_text(text, name, max_length):
    """Parses a new text file for sentences"""
    click.secho(f"Parsing the text {text}.")
    data_utils.build_new_sentence_file(text, name, max_length=max_length)
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
            io.flush_input()
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
@click.option("--target_accuracy", type=float, default=0.75)
def spell(data_file, inv_temp, inv_grade_temp, spoken, target_accuracy):
    """Tests spelling"""
    if spoken:
        engine = io.OutputEngine(output_type=io.OutputType.SPOKEN)
    else:
        engine = io.OutputEngine(output_type=io.OutputType.SILENT)
    data_file = pathlib.Path(data_file)
    dataset = data_utils.load_dataset(data_file)
    text = data_utils.get_indexed_sentences(*dataset.text)

    game_state = tetris.Tetris()
    ui = blessed.Terminal()

    # Use a jeffrey's prior:
    session_successes = 0.5
    session_failures = 0.5

    quit_ = False
    while not quit_:
        hook = game_state.play(ui)
        if not isinstance(hook, game.GameOver):
            word = ml.choose_word_for_target_accuracy(
                dataset.spelling_words,
                inv_grade_temp=inv_grade_temp,
                inv_temp=inv_temp,
                target_accuracy=target_accuracy,
                session_successes=session_successes,
                session_failures=session_failures,
            )
            sentence = text.get_sentence(word)

            phrase = f"Please spell {word}"
            if sentence:
                phrase += f", as in: {sentence}. {word}."
            engine.output(phrase)

            io.flush_input()
            attempt = input("spelling (or \quit): ")
            if attempt == "\quit":
                click.secho("Quitting...")
                quit_ = True
            else:
                if attempt.lower().strip() == word.lower().strip():
                    success = 1
                    failure = 0
                    engine.output("Correct!")
                    event = game.SightWordTestEvent(
                        word, 1, game.TestQuestionResult.PASS
                    )
                else:
                    success = 0
                    failure = 1
                    click.secho(f"{word} is the correct spelling.")
                    if spoken:
                        engine.output(
                            f"Sorry! The correct spelling is: {', '.join(word)}."
                        )
                    event = game.SightWordTestEvent(
                        word, 1, game.TestQuestionResult.FAIL
                    )
                session_successes += success
                session_failures += failure
                dataset = data_utils.update_dataset(
                    dataset, spelling_word=word, successes=success, failures=failure
                )
                game_state = hook(event)
        else:
            quit_ = True
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
