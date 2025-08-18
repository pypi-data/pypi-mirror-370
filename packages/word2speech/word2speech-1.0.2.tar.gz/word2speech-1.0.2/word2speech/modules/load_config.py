"""
Carga la configuración de múltiples ubicaciones.
"""

from pathlib import Path

import yaml

from .utilities import validate_config_file


def load_config(log=None):
    """
    Busca y carga la configuración con la siguiente prioridad:
    1. ~/.word2speech/config.yml (configuración global del usuario)
    2. .word2speech/config.yml (configuración local del proyecto)
    """

    user_config = Path.home().joinpath(".word2speech", "config.yml")
    local_config = Path.cwd().joinpath(".word2speech", "config.yml")

    # Cargamos configuraciones en caso que existan
    for config_file in [local_config, user_config]:
        if config_file.is_file():
            try:
                with open(config_file, "r", encoding="utf-8") as file:
                    config = yaml.load(file, yaml.Loader)
                    validate_config_file(config)
                    if log:
                        log.info(f'Configuración cargada desde: "{config_file}"')

                    return config
            except Exception as error:
                raise SystemExit(
                    f'Error al cargar la configuración desde: "{config_file}": error: {error}'
                )

    return {}


def create_config():
    """
    Crea un template del fichero de configuración en la ruta ~/.word2speech/config.yml si no existe
    """
    config_dir = Path.home() / ".word2speech"
    config_file = config_dir / "config.yml"

    if not config_dir.exists():
        config_dir.mkdir(exist_ok=True)

        template_config = """# Parámetros obligatorios.
token: "tu_token"
email: "tu_email@domain.com"
voice: Alvaro

# Parámetros opcionales.
# Formato del fichero resultante, default=mp3.
# (mp3, wav, ogg)
# format: mp3

# Velocidad de reproducción, default=1.
# (rango de 0.1 a 2.0)
# speed: 1

# Tono de voz, default=0.
# (rango de -20 a 20)
# pitch: 0

# Emoción de la voz, default=good.
# (good, evil, neutral)
# emotion: good

# Tiempo de pausa entre frases.
# pause_sentence: 300

# Tiempo de pausa entre párrafos.
# pause_paragraph: 400

# Tasa de muestro.
# (rango de 8000 a 192000 Hz)
# bitrate: 48000

# Detalle de entonación de la palabra, se pueden escoger hasta 5 puntos.
#     x - Porcentaje de duración de la palabra (0 a 100)
#     y - Procentaje de entonación (-100 a 100)
# contour:
#   - 100,50 # punto1
#   - 40,-20 # punto2
"""

        with open(config_file, "w", encoding="utf-8") as fd:
            fd.write(template_config)
        print(f'[INFO] Fichero de configuración creado en: "{config_file}"')
        return True

    return False
