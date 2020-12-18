print("Empezando imports (transcripción)...")
from argparse import ArgumentParser
from pydub import AudioSegment
from numpy import array
import speech_recognition as sp_recon
from speech_recognition import Recognizer

from urllib.request import Request
import json
import sys

from io import BytesIO
from multiprocessing import Pool, cpu_count, Manager
print("FIN (transcripción)")

def default(p):
    print(f"Handling {p[0]}:")
    
    with open(p[0], 'rb') as audio_file:
        if(not p[2]):
            p[1].append(text_from_audio(audio_from_video(audio_file)))
        else:
            p[1].append(text_from_audio(audio_file))

def main():
    #if(len(argv) > 1):
    args = __create_parser()
    #else:
     #   class args:
      #      audio:bool=False
       #     Archivos:list=[input("File name: ") or "TestEsAudio.wav"]
        #    verbose:bool=True
         #   proc_num:int=8

    results = Manager().list()
    
    
    print(f"Starting pool of {(num_proc := min(cpu_count(), args.proc_num, len(args.Archivos)))} process to "
            f"handle {len(args.Archivos)} {'audio' if args.audio else 'video'} files")
    
    with Pool(num_proc) as p:
        p.map_async(default, ({0:f, 1:results, 2:args.audio} for f in args.Archivos)).get()
        #control.wait()

    print(results)


def text_from_audio(audio:"Audio[FileIO]") -> str:
    print("Extracting text...")
    recognizer = sp_recon.Recognizer()

    with sp_recon.AudioFile(audio) as audio_wrapper:
        return recognizer.recognize_sphinx(recognizer.record(audio_wrapper), language="es-ES", show_all=False)
            

def audio_from_video(video:"Video[FileIO]") -> "Audio[FileIO]":
    print("Extracting audio...", end=' > ')
    file = AudioSegment.from_file_using_temporary_files(video).export(BytesIO(), format="wav")
    file.seek(0)

    return file


def __create_parser():
    ### Any functionality will be added as needed

    description = """
        Transcribe a partir de un video o audio, mediante reconocimiento del lenguaje natural
        """

    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--audio", "-a",
        action="store_true",
        help="Indica que los archivos son audio, en vez de video (por defecto:video)")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Muestra por pantalla información adicional")
    parser.add_argument(
        "-p", "--proc_num",
        type=int,
        default=1,
        help="Límite de procesos a lanzar"
    )
    parser.add_argument(
        dest="Archivos",
        nargs='+',
        type=str,
        help="Los archivos a partir de los cuales transcribir el audio"
    )

    return parser.parse_args()

if __name__ == "__main__":
    main()