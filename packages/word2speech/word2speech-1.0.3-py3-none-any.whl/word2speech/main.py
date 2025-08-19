#!/usr/bin/env python
"""
Herramienta de línea de comandos para transformar palabras
o ficheros (json) en audios.
"""

import argparse
import logging
import os
import platform
import sys
import warnings
from pathlib import Path

# Silenciamos el warning de epitran
warnings.filterwarnings("ignore", category=UserWarning, module="epitran")

import yaml
from requests.exceptions import HTTPError

from .modules import (
    IPAError,
    Normalizer,
    Word2Speech,
    create_config,
    is_valid_file_word,
    load_config,
    spell_word,
    ssml_for_word,
    validate_bitrate,
    validate_config_file,
    validate_contour_point,
    validate_emotion,
    validate_format,
    validate_pitch,
    validate_speed,
)

BASE_PATH = Path(__file__).resolve().parents[1]

log = logging.getLogger(__name__)


def set_config(file):
    """Lee el fichero de configuración."""
    config = yaml.load(file, yaml.Loader)
    validate_config_file(config)
    file.close()
    return config


def save_audio(file_name, file_content):
    """Guarda el fichero de audio descargado."""
    with open(file_name, "wb") as audio_file:
        audio_file.write(file_content)


def parse_arguments():
    """Analiza la línea de comandos para los argumentos de entrada."""
    # Primero comprobamos los subcomandos
    if len(sys.argv) > 1 and sys.argv[1] == "deletrear":
        parser = argparse.ArgumentParser(
            prog="word2speech deletrear",
            description="Genera audio deletreando palabras sílaba por sílaba con pausas entre cada sílaba",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument(
            dest="word",
            metavar="palabra",
            help="Palabra a deletrear por sílabas",
        )
        parser.add_argument(
            "--config",
            metavar="config.yml",
            type=argparse.FileType("r"),
            help="Archivo de configuración YAML",
        )
        parser.add_argument("--token", metavar="12345", help="Token de autentificación")
        parser.add_argument(
            "--email", metavar="user@domain.com", help="Correo electrónico"
        )
        parser.add_argument("--voice", metavar="Alvaro", help="Voz a utilizar")
        parser.add_argument(
            "--format",
            choices={"mp3", "wav", "ogg"},
            type=validate_format,
            help="Formato del fichero resultante (default: mp3)",
        )
        parser.add_argument(
            "--include-word",
            action="store_true",
            help="Incluye la palabra completa al final del deletreo",
        )
        parser.add_argument(
            "--pause",
            metavar="default: 250ms",
            type=int,
            default=250,
            help="Duración de la pausa entre sílabas en segundos (default: 250ms)",
        )
        parser.add_argument(
            "--speed",
            metavar="default: 1.0",
            type=validate_speed,
            help="Velocidad de reproducción (rango de 0.1 a 2.0)",
        )
        parser.add_argument(
            "--pitch",
            metavar="default: -5",
            default=-5,
            type=validate_pitch,
            help="Tono de voz (rango de -20 a 20)",
        )
        parser.add_argument(
            "--emotion",
            choices={"good", "evil", "neutral"},
            type=validate_emotion,
            help="Emoción de la voz (default: neutral)",
        )
        parser.add_argument(
            "--bitrate",
            metavar="default: 48000",
            type=validate_bitrate,
            help="Tasa de muestreo (rango de 8000 a 192000 Hz)",
        )
        parser.add_argument(
            "--contour",
            "-c",
            metavar="x,y",
            action="append",
            type=validate_contour_point,
            help="""
Detalle de entonación de la palabra, se pueden escoger hasta 5 puntos.
    x - Porcentaje de duración de la palabra (0 a 100)
    y - Procentaje de entonación (-100 a 100)
""",
        )
        parser.add_argument(
            "--outfile",
            "-o",
            metavar="fichero",
            default="out_deletreo",
            help="Guarda el audio con el nombre %(metavar)s",
        )
        args = parser.parse_args(sys.argv[2:])
        args.command = "deletrear"
        return args

    elif len(sys.argv) > 1 and sys.argv[1] == "prosodia":
        parser = argparse.ArgumentParser(
            prog="word2speech prosodia",
            description="Genera audio con prosodia mejorada usando SSML y transcripción fonética IPA",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument(
            dest="word",
            metavar="palabra",
            help="Palabra para generar con prosodia mejorada",
        )
        parser.add_argument(
            "--config",
            metavar="config.yml",
            type=argparse.FileType("r"),
            help="Archivo de configuración YAML",
        )
        parser.add_argument("--token", metavar="12345", help="Token de autentificación")
        parser.add_argument(
            "--email", metavar="user@domain.com", help="Correo electrónico"
        )
        parser.add_argument("--voice", metavar="Alvaro", help="Voz a utilizar")
        parser.add_argument(
            "--format",
            choices={"mp3", "wav", "ogg"},
            type=validate_format,
            help="Formato del fichero resultante (default: mp3)",
        )
        # TO-DO: Incluir validaciones para la opciones del subcomando prosodia
        parser.add_argument(
            "--rate",
            metavar="velocidad: medium",
            default="medium",
            help="Velocidad de habla en SSML: x-slow, slow, medium, fast, x-fast (default: medium)",
        )
        parser.add_argument(
            "--pitch-ssml",
            metavar="tono: medium",
            default="medium",
            help="Tono de voz en SSML: x-low, low, medium, high, x-high (default: medium)",
        )
        parser.add_argument(
            "--volume",
            metavar="volumen: medium",
            default="medium",
            help="Volumen en SSML: silent, x-soft, soft, medium, loud, x-loud (default: medium)",
        )
        parser.add_argument(
            "--outfile",
            "-o",
            metavar="fichero",
            default="out_prosodia",
            help="Guarda el audio con el nombre %(metavar)s",
        )
        args = parser.parse_args(sys.argv[2:])
        args.command = "prosodia"
        return args

    else:
        # Parser para funcionalidad original
        parser = argparse.ArgumentParser(
            prog="word2speech",
            description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog="""
Comandos especiales disponibles:
  deletrear             Deletrea palabras (sílaba por sílaba) y genera audio
                        Uso: python -m word2speech deletrear palabra [opciones]
  prosodia              Genera audio con prosodia mejorada usando SSML e IPA
                        Uso: python -m word2speech prosodia palabra [opciones]
""",
        )
        parser.add_argument(
            dest="word",
            metavar="palabra/fichero",
            type=is_valid_file_word,
            help="Palabra/fichero a convertir",
        )
        parser.add_argument(
            "--config",
            metavar="config.yml",
            type=argparse.FileType("r"),
            help="Archivo de configuración YAML",
        )
        parser.add_argument("--token", metavar="12345", help="Token de autentificación")
        parser.add_argument(
            "--email", metavar="user@domain.com", help="Correo electrónico"
        )
        parser.add_argument("--voice", metavar="Alvaro", help="Voz a utilizar")
        parser.add_argument(
            "--format",
            choices={"mp3", "wav", "ogg"},
            type=validate_format,
            help="Formato del fichero resultante (default: mp3)",
        )
        parser.add_argument(
            "--speed",
            metavar="default: 1.0",
            type=validate_speed,
            help="Velocidad de reproducción (rango de 0.1 a 2.0)",
        )
        parser.add_argument(
            "--pitch",
            metavar="default: 0",
            type=validate_pitch,
            help="Tono de voz (rango de -20 a 20)",
        )
        parser.add_argument(
            "--emotion",
            choices={"good", "evil", "neutral"},
            type=validate_emotion,
            help="Emoción de la voz (default: neutral)",
        )
        parser.add_argument(
            "--bitrate",
            metavar="default: 48000",
            type=validate_bitrate,
            help="Tasa de muestreo (rango de 8000 a 192000 Hz)",
        )
        parser.add_argument(
            "--contour",
            "-c",
            metavar="x,y",
            action="append",
            type=validate_contour_point,
            help="""
Detalle de entonación de la palabra, se pueden escoger hasta 5 puntos.
    x - Porcentaje de duración de la palabra (0 a 100)
    y - Procentaje de entonación (-100 a 100)
""",
        )
        parser.add_argument(
            "--outfile",
            "-o",
            metavar="fichero",
            default="out",
            help="Guarda el audio con el nombre %(metavar)s",
        )
        args = parser.parse_args()
        args.command = None
        return args


def spell_audio(args, config):
    """Genera audio deletreando una palabra por sílabas."""
    speech = Word2Speech(config)

    try:
        spelled = spell_word(args.word, args.pause)

        if args.include_word:
            spelled += f' <break time="1s"/> {args.word}'

        file_name = args.outfile
        log.info(f'Generando audio deletreado por sílabas de la palabra "{args.word}"')
        log.info(f"Texto deletreado: {spelled}")

        audio, file_format, cost, balans = speech.convert(spelled)
        log.info(
            f'Audio deletreado generado "{file_name}.{file_format}" (coste: {cost}, saldo: {balans})'
        )
        save_audio(f"{file_name}.{file_format}", audio)
    except HTTPError as error:
        raise SystemExit(error.args[0])


def prosodia_audio(args, config):
    """Genera audio con prosodia mejorada usando SSML."""
    speech = Word2Speech(config)

    try:
        ssml_text, ssml_log = ssml_for_word(
            args.word,
            rate=args.rate,
            pitch=args.pitch_ssml,
            volume=args.volume,
        )

        file_name = args.outfile
        if ssml_log:
            log.info(ssml_log)
        log.info(f'Generando audio con prosodia mejorada de la palabra "{args.word}"')
        log.info(f"SSML generado: {ssml_text}")

        audio, file_format, cost, balans = speech.convert(ssml_text)
        log.info(
            f'Audio con prosodia generado "{file_name}.{file_format}" (coste: {cost}, saldo: {balans})'
        )
        save_audio(f"{file_name}.{file_format}", audio)
    except IPAError as error:
        raise SystemExit(error)
    except HTTPError as error:
        raise SystemExit(error.args[0])


def main():
    """Ejecuta el programa de línea de comandos."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s]: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Crea el fichero de configuración global del usuario si no existe
    create_config()

    args = parse_arguments()
    # Procesar configuración común
    config = {}
    if hasattr(args, "config") and args.config:
        config = set_config(args.config)
    else:
        # Intentamos cargar la configuración local del proyecto o glabal del usuario si exiten
        config = load_config(log)

    # Aplicar argumentos de línea de comandos
    if hasattr(args, "token") and args.token:
        config.update({"token": args.token})
    elif "token" not in config:
        raise SystemError("Es obligatorio proporcionar un token válido.")
    if hasattr(args, "email") and args.email:
        config.update({"email": args.email})
    elif "email" not in config:
        raise SystemError("Es obligatorio proporcionar un email válido.")
    if hasattr(args, "voice") and args.voice:
        config.update({"voice": args.voice})
    if hasattr(args, "format") and args.format:
        config.update({"format": args.format})
    if hasattr(args, "speed") and args.speed:
        config.update({"speed": args.speed})
    if hasattr(args, "pitch") and args.pitch:
        config.update({"pitch": args.pitch})
    if hasattr(args, "emotion") and args.emotion:
        config.update({"emotion": args.emotion})
    if hasattr(args, "bitrate") and args.bitrate:
        config.update({"bitrate": args.bitrate})
    if hasattr(args, "contour") and args.contour:
        config.update({"contour": args.contour})

    # Ejecutar el comando correspondiente
    if args.command == "deletrear":
        # Subcomando deletrear
        spell_audio(args, config)
    elif args.command == "prosodia":
        # Subcomando prosodia
        prosodia_audio(args, config)
    else:
        speech = Word2Speech(config)
        try:
            if isinstance(args.word, dict):
                norm = Normalizer()
                for dirname, words in args.word.items():
                    # No lanza excepción si el directorio ya existe
                    Path(dirname).mkdir(parents=True, exist_ok=True)
                    for word in words:
                        file_name = norm.normalize(word)
                        log.info(f'Generando el audio de la palabra "{word}"')
                        audio, file_format, cost, balans = speech.convert(word)
                        log.info(
                            f'Audio generado "{dirname}/{file_name}.{file_format}" (coste: {cost}, saldo: {balans})'
                        )
                        save_audio(f"{dirname}/{file_name}.{file_format}", audio)
            else:
                file_name = args.outfile
                log.info(f'Generando el audio de la palabra "{args.word}"')
                audio, file_format, cost, balans = speech.convert(args.word)
                log.info(
                    f'Audio generado "{file_name}.{file_format}" (coste: {cost}, saldo: {balans})'
                )
                save_audio(f"{file_name}.{file_format}", audio)
        except HTTPError as error:
            raise SystemExit(error.args[0])
