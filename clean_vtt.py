from sys import argv

import re
import spacy
from spacy.symbols import (DET, ADP, INTJ, CCONJ, SCONJ, X, PUNCT, SPACE, NUM, SYM)
from typing import Pattern
from unidecode import unidecode


NON_ALPHA:Pattern = re.compile(r"[^a-zA-Z]")
MAIL:Pattern = re.compile(r"[^\s]+?@[^\s]+?\.[^\s]+")
URLs:Pattern = re.compile(r"(https?://)?([^\s]+?\.)+?[^.\s]+(\/.*)?")
DROP_TOKENS:set = {DET, ADP, INTJ, CCONJ, SCONJ, X, PUNCT, SPACE, NUM, SYM}


nlp = spacy.load("es_core_news_sm")

def main():
    extract:Pattern = re.compile("-->.*?\n(.+?)\n\n", re.S)

    for fname in argv[1:]:
        with open(fname, 'r') as file:
            text = NON_ALPHA.sub(' ', URLs.sub(' ', MAIL.sub(' ', unidecode(
                            ' '.join(tok.lemma_ 
                            for tok in nlp(
                                ' '.join(map(lambda m:m.group(1), extract.finditer(file.read()))))
                                    if tok.pos not in DROP_TOKENS
                            )
            ))))

        with open(fname[:-4]+"_clean.txt", 'w') as file:
            file.write(text)

if __name__ == "__main__":
    main()