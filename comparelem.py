#!/usr/bin/env python3

import argparse
import pandas as pd
import os
from collections import defaultdict as dd

OUTPUT_DIR = 'output'


def get_dataframe(io_file, texts=[]):
    underscores_freq = pd.read_csv(io_file, sep='\t')
    if 'word_lemma_id' not in underscores_freq:
        raise "csv file should have a column named \"word_lemma_id\"."
    underscores = underscores_freq.drop('F', axis=1).word_lemma_id.values
    del underscores_freq
    underscores = [u.split("_") for u in underscores]
    original = [(u[0], u[1:-4], u[-3])
                for u in underscores for x in u[1:-4]]
    underscores = [(u[0], x, u[-3]) for u in underscores for x in u[1:-4]]
    df = pd.DataFrame(underscores, columns=['word', 'lemmas', 'text_name'])
    original = pd.DataFrame(original, columns=['word', 'lemmas', 'text_name'])
    if texts != []:
        df = df[df.text_name.isin(texts)]
        original = original[original.text_name.isin(texts)]
    df.to_csv(f'debug_{os.path.basename(io_file.name)}', index=False)
    return df, original


def compare_lemmas(first, second, o_first, o_second):
    ret = dd(lambda: {'common_lemma': '',
                      'forms_1': set(),
                      'forms_2': set(),
                      'id_text': set(),
                      'count_first': 0,
                      'count_second': 0})
    for word_1, lemma_1, text_name_1 in first.values:
        for word_2, lemma_2, text_name_2 in second.values:
            if lemma_1 == lemma_2:
                ret[lemma_1]['common_lemma'] = lemma_1
                ret[lemma_1]['id_text'].add(text_name_1)
                ret[lemma_1]['id_text'].add(text_name_2)
                if word_1 not in ret[lemma_1]['forms_1']:
                    ret[lemma_1]['count_first'] += len(
                        o_first[o_first.word == word_1])
                if word_2 not in ret[lemma_1]['forms_2']:
                    ret[lemma_1]['count_second'] += len(
                        o_second[(o_second.word == word_2)])
                ret[lemma_1]['forms_1'].add(word_1)
                ret[lemma_1]['forms_2'].add(word_2)
    return pd.DataFrame([ret[k]for k in ret])


def save_output(commons_lemmas, save_output_format, texts, output_name):
    def print_msg(filename):
        print(f"Create : {filename}")
    here = os.path.dirname(__file__)
    os.makedirs(os.path.join(here, OUTPUT_DIR), exist_ok=True)
    output_name = [output_name] if output_name != '' else []
    basenamefile = os.path.join(
        here, OUTPUT_DIR, f"{'_'.join(output_name + texts)}")
    if 'csv' in save_output_format:
        csv = basenamefile + '.csv'
        commons_lemmas.to_csv(csv, index=False)
        print_msg(csv)
    if 'txt' in save_output_format:
        txt = basenamefile + '.txt'
        commons_lemmas.to_csv(txt, index=False, sep='\t')
        print_msg(txt)
    if 'xlsx' in save_output_format:
        xlsx = basenamefile + '.xlsx'
        writer = pd.ExcelWriter(xlsx, engine='xlsxwriter')
        commons_lemmas.to_excel(writer, index=False)
        writer.save()
        print_msg(xlsx)


def main(args):
    first, o_first = get_dataframe(args.files[0], args.texts)
    second, o_second = get_dataframe(args.files[1], args.texts)
    commons_lemmas = compare_lemmas(first, second, o_first, o_second)
    save_output(commons_lemmas, args.save_output_format,
                args.texts, args.output_name)


def get_args():
    parser = argparse.ArgumentParser(
        "Find forms that have common lemmas between two files.")
    parser.add_argument('files',
                        type=argparse.FileType("r"),
                        nargs=2,
                        help="Lemmas files with and without schwa.",
                        metavar="FILE_WITH[OUT]_SCHWA"
                        )
    parser.add_argument('-t', '--texts',
                        default=[],
                        nargs='+',
                        help="Restrict output to certain text(s)." +
                        "(Default do all texts.)"
                        )
    # parser.add_argument('-p', '--POS',
    #                     action='store_true',
    #                     default=False,
    #                     help="Boolean value : " +
    #                     "is common only if common POS too"
    #                     )
    parser.add_argument('-S', '--save_output_format', nargs='+',
                        help='save output in a file with one of the ' +
                        'following format' +
                        ' \'csv\' or \'xlsx\' or \'txt\'',
                        choices=['csv', 'xlsx', 'txt'],
                        metavar='format',
                        default=['xlsx'])
    parser.add_argument('-O', '--output_name',
                        type=str,
                        default='')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    ARGS = get_args()
    main(ARGS)
