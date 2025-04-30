import os
import re
import json
from typing import List

from api.exceptions.log_parse_except import (
    PatternFileNotFound,
    InvalidPatternFormat,
    NoPatternMatchError,
    InvalidRegexPattern,
)
from api.exceptions.mvt_android_except import MVTAndroidException
from api.models.types.exception import APIErrorCode
from api.models.types.schemas import (
    MessageLogType,
    MessageEntry,
    LogEntry,
    LogMessageEntry,
)
from core.logger import setup_logger

logger = setup_logger()


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
        self.patterns_file = patterns_file or default_file

    def loading_json(self):
        if not os.path.exists(self.patterns_file):
            parser_error = PatternFileNotFound({"Path": self.patterns_file})
            logger.critical(parser_error.to_log())
            raise parser_error

        try:
            with open(self.patterns_file, "r", encoding="utf-8") as file:
                self.patterns: List[MessageLogType] = json.load(file)
        except json.JSONDecodeError as e:
            parser_error = InvalidPatternFormat({"error": str(e)})
            logger.critical(parser_error.to_log())
            raise parser_error

    def parse(self, log_text: str) -> LogMessageEntry:
        self.loading_json()
        cleaned = self._clean_output(log_text)
        return {
            "logs": self._extract_log(cleaned),
            "messages": self._parser_messages_from_patterns(cleaned),
        }

    def _extract_log(self, cleaned: str) -> List[LogEntry]:
        logs: List[LogEntry] = []
        log_pattern = re.compile(
            r"^((?P<status>\w+)?\[(?P<source>.*?)\]\s+)?(?P<message>.*)$",
            re.IGNORECASE | re.MULTILINE,
        )
        for match in log_pattern.finditer(cleaned):
            status = match.group("status").strip() if match.group("status") else "-"
            message = match.group("message").strip()
            logs.append(
                {
                    "id": len(logs),
                    "status": status,
                    "message": message,
                }
            )
        return logs

    def _parser_messages_from_patterns(self, cleaned: str) -> List[MessageEntry]:
        messages: List[MessageEntry] = []

        for pattern in self.patterns:
            try:
                regex = re.compile(pattern["pattern"], re.IGNORECASE | re.MULTILINE)
            except re.error as e:
                parser_error = InvalidRegexPattern(
                    {"error": str(e), "pattern": pattern["pattern"]}
                )
                logger.critical(parser_error.to_log())
                continue
            for m in regex.finditer(cleaned):
                if "error_code" in pattern:
                    try:
                        error_enum = getattr(APIErrorCode, pattern["error_code"])
                        api_error = MVTAndroidException(
                            error=error_enum, payload=pattern
                        )
                        logger.error(api_error.to_log())
                        raise api_error
                    except AttributeError as e:
                        logger.critical(str(e))

                messages.append(
                    {
                        "category": pattern["category"],
                        "message": pattern["message"],
                        "original_message": m.group().strip(),
                    }
                )
        if not messages:
            raise NoPatternMatchError({"patterns": self.patterns})

        return messages

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
            [
                f"{key}:\n\t{'\n\t'.join([f'{chave}:\n\t\t{valor}' for v in values for chave, valor in v.items()])}"
                for key, values in parsed.items()
            ]
        ),
    )
