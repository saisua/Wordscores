import os
import re
import sys
from ctypes import c_int
from multiprocessing import Pool, Manager, cpu_count
from typing import Pattern

#from pdfminer.high_level import extract_text
import pytesseract as ptss
import pdf2image
import spacy
from spacy.symbols import (DET, ADP, INTJ, CCONJ, SCONJ, X, PUNCT, SPACE, NUM, SYM)
from click import echo
from unidecode import unidecode


STORE_EVERY:int = Manager().Value(c_int, cpu_count())
counter:int = Manager().Value(c_int, 0)

NON_ALPHA:Pattern = re.compile(r"[^a-zA-Z]")
MAIL:Pattern = re.compile(r"[^\s]+?@[^\s]+?\.[^\s]+")
URLs:Pattern = re.compile(r"(https?://)?([^\s]+?\.)+?[^.\s]+(\/.*)?")
DROP_TOKENS:set = {DET, ADP, INTJ, CCONJ, SCONJ, X, PUNCT, SPACE, NUM, SYM}

nlp = spacy.load("es_core_news_sm")
stdout = sys.stdout

INPUT_FOLDER = "pdfs"
OUTPUT_FOLDER = "texts"

def main():
    MIN_TEXT_LEN = 10
    
    if(len(__file__.split("/")) > 1):
        cpath = f"{'/'.join(__file__.split('/')[:-1])}/"
    else:
        cpath = "./"

    print(f"Path: {cpath}")

    folders = ["/tests/"]#["/pp2/", "/psoe2/"]

    in_folders = tuple(f"{cpath}{INPUT_FOLDER}{fol}" for fol in folders)
    out_folders = tuple(f"{cpath}{OUTPUT_FOLDER}{fol}" for fol in folders)

    p = Pool()
    out = Manager().list()
    
    assert all(map(os.path.isdir, in_folders)), "Missing or wrong input folders"
    assert all(map(os.path.isdir, out_folders)), "Missing or wrong output folders"
    

    print(f"Working on folders {', '.join(folders)}")
    p.starmap(mproc_pdf, ((p, f, out) for p,_,fs in 
                            tuple(filter(None, (tuple(os.walk(folders)) 
                                for folders in in_folders)))[0]
                        for f in fs
                    ))

    print("Transcription ready. Dumping last files...")

    for fname, text in out:
        with open(fname, 'w') as file:
            file.write(text)


def mproc_pdf(path, filename, out):
    out.append((path.replace(INPUT_FOLDER,OUTPUT_FOLDER)+filename[:-4]+"_clean.txt", 
                        NON_ALPHA.sub(' ', URLs.sub(' ', MAIL.sub(' ', unidecode(
                        ' '.join(tok.lemma_ for page in pdf2image.convert_from_path(path+filename) 
                        for tok in nlp(ptss.image_to_string(page, lang='spa')) 
                                    if tok.pos not in DROP_TOKENS
                        )
                        ))))
                        ))

    if(len(out) >= STORE_EVERY.value):        
        STORE_EVERY.value, last_se = float('inf'), STORE_EVERY.value

        l = [out.pop(0) for _ in range(len(out))]

        STORE_EVERY.value = last_se

        for fname, text in l:
            with open(fname, 'w') as file:
                file.write(text)        

        counter.value = counter.value + len(l)    
        echo(f"Written {counter.value} (+{len(l)})"
                "                                             \r"
                , nl=False, file=stdout)


def mproc_txt(path, filename, out):
    with open((path+filename), 'r') as file:
        out.append((path.replace(INPUT_FOLDER,OUTPUT_FOLDER)+filename[:-4]+"_clean.txt", 
                            NON_ALPHA.sub(' ', URLs.sub(' ', MAIL.sub(' ', unidecode(
                            ' '.join(tok.lemma_ 
                            for tok in nlp(file.read()) 
                                    if tok.pos not in DROP_TOKENS
                            )
                            ))))
                            ))

    if(len(out) >= STORE_EVERY.value):        
        STORE_EVERY.value, last_se = float('inf'), STORE_EVERY.value

        l = [out.pop(0) for _ in range(len(out))]

        STORE_EVERY.value = last_se

        for fname, text in l:
            with open(fname, 'w') as file:
                file.write(text)        

        counter.value = counter.value + len(l)    
        echo(f"Written {counter.value} (+{len(l)})"
                "                                             \r"
                , nl=False, file=stdout)



if __name__ == "__main__":
    main()