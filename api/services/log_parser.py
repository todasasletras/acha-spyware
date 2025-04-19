import os
import re
import json
from typing import List

from api.exceptions import (
    PatternFileNotFound,
    InvalidPatternFormat,
    NoPatternMatchError,
)
from api.models.types.schemas import MessageLogType, MessageEntry


class LogParser:
    def __init__(
        self,
        patterns_file: str = None,
    ):
        # Determina o diretório base (api/)
        base_dir = os.path.dirname(os.path.dirname(__file__))
        # Define arquivo padrão em api/resources
        default_file = os.path.join(base_dir, "resources", "log_message_patterns.json")
        # Usa o arquivo fornecido ou o padrão
        patterns_file = patterns_file or default_file

        if not os.path.exists(patterns_file):
            raise PatternFileNotFound(patterns_file)

        try:
            with open(patterns_file, "r", encoding="utf-8") as file:
                self.patterns: List[MessageLogType] = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não econtrado {patterns_file}")
        except FileExistsError:
            raise FileExistsError(f"Erro ao abrir o arquivo {patterns_file}")
        except json.JSONDecodeError as e:
            raise InvalidPatternFormat(f"Erro ao decodificar o JSON: {str(e)}")

    def parse(self, log_text: str):
        cleaned = self._clean_output(log_text)
        result: List[MessageEntry] = []

        for pattern in self.patterns:
            try:
                regex = re.compile(pattern["pattern"], re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                print(f"Erro no regex padrão: {e} - {pattern['pattern']}")
                continue
            for m in regex.finditer(cleaned):
                result.append(
                    {
                        "category": pattern["category"],
                        "message": pattern["message"],
                        "original_message": m.group().strip(),
                    }
                )
        if not result:
            raise NoPatternMatchError("Nenhum padrão encontrado!")

        return result

    def _clean_output(self, text: str):
        # Remover sequências ANSI
        text = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]]", "", text)

        # Normalizar quebras de linha
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" *\n *", "\n", text)

        # Limpar padrões específicos do log mvt/adb
        text = re.sub(r"(\s+)(?=\S)", " ", text)
        text = re.sub(r"\n+", " ", text)
        text = re.sub(r"(\s+)(INFO|ERROR|CRITICAL|DEBUG|WARNING)(\s+)", r" \2", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"(\s)(INFO|ERROR|CRITICAL|DEBUG|WARNING)", r"\1\n\2", text)
        return text.strip()


if __name__ == "__main__":
    parser = LogParser()
    parsed = parser.parse(
        """


        MVT - Mobile Verification Toolkit
                https://mvt.re
                Version: 2.5.4
                Version 2.6.0 is available! Upgrade mvt with `pip3 install -U mvt`
                Indicators updates checked recently, next automatic check in 10 hours


02:21:17 INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path 
                        /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_mvt-project_mvt-indicators_main_2023-06_01_operation_triangulation_operation_triangulation.stix2                        
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path 
         /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_AmnestyTech_investigations_master_2023-03-29_android_campaign_malware.stix2                                             
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_mvt-project_mvt-indicators_main_2023-04-11_quadream_kingspawn.stix2                                                     
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_AmnestyTech_investigations_master_2021-07-18_nso_pegasus.stix2                                                          
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path 
         /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_AmnestyTech_investigations_master_2024-05-02_wintego_helios_wintego_helios.stix2                                        
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_AmnestyTech_investigations_master_2024-12-16_serbia_novispy_novispy.stix2                                               
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_mvt-project_mvt-indicators_main_intellexa_predator_predator.stix2                                                       
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_AssoEchap_stalkerware-indicators_master_generated_stalkerware.stix2                                                     
02:21:20 INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_mvt-project_mvt-indicators_main_2022-06-23_rcs_lab_rcs.stix2                                                            
         INFO     [mvt.android.cmd_check_adb] Parsing STIX2 indicators file at path /home/jonas/.local/share/mvt/indicators/raw.githubusercontent.com_mvt-project_mvt-indicators_main_2023-07-25_wyrmspy_dragonegg_wyrmspy_dragonegg.stix2                                    
         INFO     [mvt.android.cmd_check_adb] Loaded a total of 10006 unique indicators                                                                                                                                                                                       
         INFO     [mvt] Checking Android device over debug bridge                                                                                                                                                                                                             
         INFO     [mvt.android.modules.adb.chrome_history] Running module ChromeHistory...                                                                                                                                                                                    
         CRITICAL [mvt.android.modules.adb.chrome_history] No device found. Make sure it is connected and unlocked.
        """
    )
    print(len(parsed))
    print(
        "\n".join(
            f"{key}: {value}"
            for p in parsed
            if p["original_message"]
            for key, value in p.items()
        ),
    )
