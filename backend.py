"""
Acha Spyware - Backend API
Requer: pip install fastapi uvicorn aiofiles mvt
Ferramentas externas: adb, androidQF, mvt-android
"""

import json
import os
import subprocess
import threading
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ── CONFIG ────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IOC_DIR = Path("/home/jonas/.local/share/mvt/indicators/")
CONFIG_FILE = BASE_DIR / "config.json"
OUTPUT_DIR.mkdir(exist_ok=True)
IOC_DIR.mkdir(exist_ok=True)

# ── ANDROIDQF: MAPAS DE MENU ────────────────────────────────────
# Número de ↓ pressionados para selecionar cada opção no menu interativo.
BACKUP_MAPS = {
    "Only SMS": 0,
    "Everything": 1,
    "No Backup": 2,
}
DOWNLOAD_MAPS = {
    "All": 0,
    "Only no-system packages": 1,
    "Do not download any": 2,
}
REMOVE_MAPS = {
    "Yes": 0,
    "No": 1,
}

# ── ANDROIDQF: TIMEOUTS ─────────────────────────────────────────
# Tempo máximo (s) aguardando cada PROMPT do menu aparecer no terminal.
# Aumente se o dispositivo for lento para iniciar o ADB.
_QF_MENU_TIMEOUT = 120

# Tempo máximo (s) para a COLETA completa rodar após a confirmação.
# Este é o valor a aumentar quando o dispositivo tem muitos dados.
# 600 = 10 min | 1800 = 30 min | 3600 = 1 hora
_QF_COLLECTION_TIMEOUT = 600

# ── STATE (em memória) ────────────────────────────────────────────
state = {
    "vt_api_key": "",
    "backup_status": {
        "done": False,
        "error": None,
        "progress": 0,
        "output_path": "",
        "message": "",
    },
    "analysis_status": {
        "done": False,
        "error": None,
        "progress": 0,
        "detections": 0,
        "results": [],
        "message": "",
    },
    "ioc_count": 0,
}


# ── HELPERS GERAIS ────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        state["vt_api_key"] = cfg.get("vt_api_key", "")


def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"vt_api_key": state["vt_api_key"]}, f)


def run_cmd(cmd: list[str], timeout=60) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except FileNotFoundError:
        return -1, "", f"Comando não encontrado: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def adb_available() -> bool:
    code, _, _ = run_cmd(["adb", "version"])
    return code == 0


def mvt_available() -> bool:
    code, _, _ = run_cmd(["mvt-android", "version"])
    return code == 0


def androidqf_available() -> bool:
    qf_path = BASE_DIR / "androidqf"
    if qf_path.exists():
        return True
    code, _, _ = run_cmd(["./androidqf", "--help"])
    return code == 0


load_config()


# ── ANDROIDQF: EXECUÇÃO INTERATIVA ──────────────────────────────
# O androidQF atual:
#   - Ignora qualquer flag (--help, --output, etc.)
#   - Cria automaticamente uma pasta UUID no diretório onde é executado
#   - Ainda exibe menus interativos que precisam de pexpect
#
# Estratégia:
#   1. Snapshot das pastas UUID em OUTPUT_DIR antes de rodar
#   2. Spawnar via pexpect com cwd=OUTPUT_DIR (pasta UUID cai aqui)
#   3. Responder os menus com setas + Enter
#   4. Aguardar EOF (processo termina)
#   5. Identificar a pasta nova por diff ou mtime

import re as _re

_UUID_RE = _re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    _re.IGNORECASE,
)


def _uuid_dirs_in(directory: Path) -> set[str]:
    """Retorna os nomes de todas as pastas UUID em `directory`."""
    return {
        p.name for p in directory.iterdir() if p.is_dir() and _UUID_RE.match(p.name)
    }


def _run_androidqf(
    serial: str | None = None,
    backup_options: str = "Everything",
    download_options: str = "Only no-system packages",
    remove_options: str = "Yes",
    status_callback=None,
) -> tuple[bool, str, str]:
    """
    Executa o androidQF respondendo automaticamente aos menus interativos
    via pexpect, com cwd=OUTPUT_DIR para que a pasta UUID seja criada lá.

    Retorna (sucesso: bool, mensagem: str, caminho_da_pasta: str).
    """
    import pexpect

    def cb(msg: str, progress: int | None = None):
        if status_callback:
            status_callback(msg, progress)

    # ── Binário ───────────────────────────────────────────────────
    qf_bin = (
        str(BASE_DIR / "androidqf")
        if (BASE_DIR / "androidqf").exists()
        else "androidqf"
    )
    cmd_parts = [qf_bin]
    if serial:
        cmd_parts += ["-serial", serial]
    command_str = " ".join(cmd_parts)
    cb(f"Executando: {command_str}", 28)

    # ── Snapshot antes ────────────────────────────────────────────
    dirs_before = _uuid_dirs_in(OUTPUT_DIR)

    # ── Sequência de menus ────────────────────────────────────────
    steps = [
        {
            "expect": "Backup",
            "send": "\x1b[B" * BACKUP_MAPS[backup_options] + "\r",
            "label": f"Menu Backup → {backup_options}",
            "progress": 40,
        },
        {
            "expect": "Download",
            "send": "\x1b[B" * DOWNLOAD_MAPS[download_options] + "\r",
            "label": f"Menu Download → {download_options}",
            "progress": 50,
        },
        {
            "expect": "Remove",
            "send": "\x1b[B" * REMOVE_MAPS[remove_options] + "\r",
            "label": f"Menu Remove → {remove_options}",
            "progress": 55,
        },
        {
            "expect": "Enter",
            "send": "\r",
            "label": "Confirmando início da coleta",
            "progress": 60,
        },
    ]

    try:
        child = pexpect.spawn(
            command_str,
            cwd=str(OUTPUT_DIR),  # ← pasta UUID cai aqui
            encoding="utf-8",
            codec_errors="replace",
            timeout=_QF_MENU_TIMEOUT,  # timeout por prompt de menu
        )

        # Navegar pelos menus
        for step in steps:
            cb(step["label"], step["progress"])
            idx = child.expect([step["expect"], pexpect.EOF, pexpect.TIMEOUT])
            if idx == 1:
                tail = (child.before or "")[-300:]
                return (
                    False,
                    f"androidQF encerrou antes de '{step['expect']}'. Saída: {tail}",
                    "",
                )
            if idx == 2:
                return (
                    False,
                    f"Timeout ({_QF_MENU_TIMEOUT}s) aguardando menu '{step['expect']}'",
                    "",
                )
            child.send(step["send"])

        # Coleta em andamento — aguardar EOF com timeout generoso
        cb("Coleta em andamento...", 65)
        progress = 65
        while True:
            idx = child.expect(
                [r".+", pexpect.EOF, pexpect.TIMEOUT], timeout=_QF_COLLECTION_TIMEOUT
            )
            if idx == 0:
                line = (child.after or "").strip()
                if line:
                    progress = min(progress + 1, 92)
                    cb(line, progress)
            elif idx == 1:
                break  # processo terminou normalmente
            else:
                child.close(force=True)
                return False, f"Timeout: coleta excedeu {_QF_COLLECTION_TIMEOUT}s", ""

        exit_status = child.wait()

    except pexpect.exceptions.ExceptionPexpect as e:
        return False, f"Erro pexpect: {e}", ""
    except Exception as e:
        return False, f"Erro inesperado: {e}", ""

    # ── Localizar pasta UUID criada ───────────────────────────────
    dirs_after = _uuid_dirs_in(OUTPUT_DIR)
    new_dirs = dirs_after - dirs_before

    if not new_dirs:
        # Fallback: pasta UUID mais recente por mtime
        candidates = sorted(
            [p for p in OUTPUT_DIR.iterdir() if p.is_dir() and _UUID_RE.match(p.name)],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            new_dirs = {candidates[0].name}
        else:
            return (
                False,
                "androidQF não criou nenhuma pasta de aquisição em OUTPUT_DIR",
                "",
            )

    acq_folder = OUTPUT_DIR / sorted(new_dirs)[0]

    if exit_status != 0:
        # Dados parciais ainda são úteis
        return (
            False,
            f"androidQF terminou com código {exit_status} (dados parciais disponíveis)",
            str(acq_folder),
        )

    return True, "Coleta concluída com sucesso", str(acq_folder)


# ── BACKUP THREAD ─────────────────────────────────────────────────
def _run_backup(
    serial: str | None = None,
    backup_options: str = "Everything",
    download_options: str = "Only no-system packages",
    remove_options: str = "Yes",
):
    s = state["backup_status"]

    def update(msg: str, progress: int | None = None):
        s["message"] = msg
        if progress is not None:
            s["progress"] = progress

    s.update(
        {
            "done": False,
            "error": None,
            "progress": 10,
            "message": "Verificando pré-requisitos...",
        }
    )

    # ── Checar androidQF ─────────────────────────────────────────
    if not androidqf_available():
        s["error"] = (
            "androidQF não encontrado. Baixe em: github.com/botherder/androidqf"
        )
        s["done"] = True
        return

    # ── Checar dispositivo ADB ────────────────────────────────────
    update("Verificando dispositivo ADB...", 15)
    code, out, _ = run_cmd(["adb", "devices"])
    connected = [
        l
        for l in out.splitlines()
        if "device" in l
        and "List" not in l
        and "offline" not in l
        and "unauthorized" not in l
    ]
    if not connected:
        s["error"] = "Nenhum dispositivo ADB conectado"
        s["done"] = True
        return

    detected_serial = serial or connected[0].split()[0]
    update(f"Dispositivo: {detected_serial}", 20)

    # ── Executar androidQF ────────────────────────────────────────
    update("Iniciando androidQF...", 25)
    success, message, acq_path = _run_androidqf(
        serial=detected_serial,
        backup_options=backup_options,
        download_options=download_options,
        remove_options=remove_options,
        status_callback=update,
    )

    if not success and not acq_path:
        s["error"] = message
        s["progress"] = 0
        s["done"] = True
        return

    # androidQF pode retornar código != 0 mas ter coletado dados parciais
    if not success:
        update(f"Aviso: {message} — dados parciais em {acq_path}", 95)

    s.update(
        {
            "progress": 100,
            "message": f"Extração concluída → {Path(acq_path).name}",
            "output_path": acq_path,
            "done": True,
        }
    )


# ── APP ──────────────────────────────────────────────────────────
app = FastAPI(title="Acha Spyware API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── MODELS ───────────────────────────────────────────────────────
class VTKeyRequest(BaseModel):
    api_key: str


class BackupRequest(BaseModel):
    serial: str | None = None
    backup_options: str = "Everything"
    download_options: str = "Only no-system packages"
    remove_options: str = "Yes"


class AnalysisRequest(BaseModel):
    use_virustotal: bool = False


# ── ROUTES: CONFIG ────────────────────────────────────────────────
@app.post("/api/config/virustotal")
def set_vt_key(req: VTKeyRequest):
    state["vt_api_key"] = req.api_key.strip()
    save_config()
    return {"ok": True}


@app.get("/api/config")
def get_config():
    return {"vt_key_set": bool(state["vt_api_key"])}


# ── ROUTES: DEVICE ───────────────────────────────────────────────
@app.get("/api/device/check")
def check_device():
    if not adb_available():
        raise HTTPException(400, "ADB não encontrado. Instale o Android Debug Bridge.")

    code, out, err = run_cmd(["adb", "devices"])
    if code != 0:
        raise HTTPException(500, f"Erro ADB: {err}")

    lines = [
        l.strip() for l in out.splitlines() if l.strip() and "List of devices" not in l
    ]
    connected = [
        l
        for l in lines
        if "device" in l and "offline" not in l and "unauthorized" not in l
    ]

    if not connected:
        return {"connected": False}

    serial = connected[0].split()[0]

    def adb_prop(prop):
        _, o, _ = run_cmd(["adb", "-s", serial, "shell", "getprop", prop])
        return o.strip()

    model = adb_prop("ro.product.model")
    brand = adb_prop("ro.product.brand")
    android = adb_prop("ro.build.version.release")

    return {
        "connected": True,
        "serial": serial,
        "model": f"{brand} {model}".strip() or serial,
        "android_version": android,
    }


# ── ROUTES: IOC ───────────────────────────────────────────────────
@app.post("/api/ioc/update")
def update_iocs():
    if not mvt_available():
        raise HTTPException(400, "MVT não encontrado. Instale com: pip install mvt")

    code, out, err = run_cmd(["mvt-android", "download-iocs"], timeout=120)
    if code != 0:
        raise HTTPException(500, f"Erro ao atualizar IOCs: {err or out}")

    count = len(list(IOC_DIR.glob("*.stix2"))) + len(list(IOC_DIR.glob("*.json")))
    state["ioc_count"] = count
    return {"ok": True, "count": count, "path": str(IOC_DIR)}


# ── ROUTES: BACKUP ───────────────────────────────────────────────
@app.post("/api/backup/start")
def start_backup(req: BackupRequest):
    state["backup_status"] = {
        "done": False,
        "error": None,
        "progress": 0,
        "output_path": "",
        "message": "",
    }
    t = threading.Thread(
        target=_run_backup,
        kwargs={
            "serial": req.serial,
            "backup_options": req.backup_options,
            "download_options": req.download_options,
            "remove_options": req.remove_options,
        },
        daemon=True,
    )
    t.start()
    return {"ok": True, "message": "Extração iniciada em background"}


@app.get("/api/backup/status")
def backup_status():
    return state["backup_status"]


# ── ROUTES: APK ──────────────────────────────────────────────────
@app.post("/api/apk/extract")
def extract_apks():
    if not adb_available():
        raise HTTPException(400, "ADB não disponível")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    apk_dir = OUTPUT_DIR / f"apks_{ts}"
    apk_dir.mkdir(parents=True, exist_ok=True)

    code, out, err = run_cmd(
        ["adb", "shell", "pm", "list", "packages", "-f"], timeout=30
    )
    if code != 0:
        raise HTTPException(500, f"Erro ao listar pacotes: {err}")

    packages = [l.strip() for l in out.splitlines() if l.strip()]
    count = 0

    for pkg_line in packages[:200]:
        if "=" not in pkg_line or ":" not in pkg_line:
            continue
        path = pkg_line.split("package:")[1].split("=")[0].strip()
        name = pkg_line.split("=")[-1].strip()
        dest = apk_dir / f"{name}.apk"
        pull_code, _, _ = run_cmd(["adb", "pull", path, str(dest)], timeout=30)
        if pull_code == 0:
            count += 1

    return {"ok": True, "count": count, "output_path": str(apk_dir)}


# ── ROUTES: ANALYSIS ─────────────────────────────────────────────
def _run_analysis(use_vt: bool):
    s = state["analysis_status"]
    s.update(
        {
            "done": False,
            "error": None,
            "progress": 5,
            "message": "Procurando backup mais recente...",
        }
    )

    backups = sorted(OUTPUT_DIR.glob("backup_*"), reverse=True)
    if not backups:
        s["error"] = "Nenhum backup encontrado. Execute a extração primeiro."
        s["done"] = True
        return

    backup_path = backups[0]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_out = OUTPUT_DIR / f"analysis_{ts}"
    analysis_out.mkdir(parents=True, exist_ok=True)

    if not mvt_available():
        s["error"] = "MVT não encontrado. Instale com: pip install mvt"
        s["done"] = True
        return

    s.update({"progress": 20, "message": f"Analisando backup: {backup_path.name}..."})

    cmd = [
        "mvt-android",
        "check-backup",
        "--output",
        str(analysis_out),
        str(backup_path),
    ]

    if state["ioc_count"] > 0:
        cmd += ["--iocs", str(IOC_DIR)]

    if use_vt and state["vt_api_key"]:
        cmd += ["--virustotal"]
        os.environ["VTAPIKEY"] = state["vt_api_key"]

    s.update({"progress": 40, "message": "MVT analisando dados (pode demorar)..."})
    code, out, err = run_cmd(cmd, timeout=1200)
    s.update({"progress": 80, "message": "Processando resultados..."})

    results = []
    for rf in analysis_out.glob("*.json"):
        try:
            with open(rf) as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if item.get("detected"):
                        results.append(
                            {
                                "name": item.get("package", item.get("name", rf.stem)),
                                "detail": item.get(
                                    "description",
                                    item.get(
                                        "matched_indicator", "Indicador detectado"
                                    ),
                                ),
                                "severity": "critical"
                                if item.get("matched_indicator")
                                else "warning",
                            }
                        )
        except Exception:
            pass

    if not results and "detected" in out.lower():
        for line in out.splitlines():
            if "detected" in line.lower() or "found" in line.lower():
                results.append(
                    {
                        "name": "Detecção MVT",
                        "detail": line.strip(),
                        "severity": "warning",
                    }
                )

    if not results and code == 0:
        results.append(
            {
                "name": "Verificação concluída",
                "detail": f"Nenhum indicador de comprometimento encontrado em {backup_path.name}",
                "severity": "clean",
            }
        )

    if code != 0 and not results:
        s["error"] = f"Erro MVT: {err[:200] if err else out[:200]}"
        s["done"] = True
        return

    s.update(
        {
            "progress": 100,
            "message": f"Análise finalizada — {len([r for r in results if r['severity'] != 'clean'])} detecções",
            "detections": len([r for r in results if r["severity"] != "clean"]),
            "results": results,
            "done": True,
            "output_path": str(analysis_out),
        }
    )


@app.post("/api/analysis/run")
def run_analysis(req: AnalysisRequest):
    state["analysis_status"] = {
        "done": False,
        "error": None,
        "progress": 0,
        "detections": 0,
        "results": [],
        "message": "",
    }
    t = threading.Thread(target=_run_analysis, args=(req.use_virustotal,), daemon=True)
    t.start()
    return {"ok": True, "message": "Análise iniciada"}


@app.get("/api/analysis/status")
def analysis_status():
    return state["analysis_status"]


@app.post("/api/analysis/report")
def export_report():
    s = state["analysis_status"]
    if not s.get("done") or not s.get("results"):
        raise HTTPException(400, "Nenhuma análise concluída para exportar")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = OUTPUT_DIR / f"relatorio_{ts}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "generated_at": datetime.now().isoformat(),
                "detections": s["detections"],
                "results": s["results"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return {"ok": True, "path": str(report_path)}


# ── ROUTES: SYSTEM ───────────────────────────────────────────────
@app.post("/api/system/open-output-folder")
def open_output_folder():
    import platform

    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(OUTPUT_DIR))
        elif system == "Darwin":
            subprocess.Popen(["open", str(OUTPUT_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True, "path": str(OUTPUT_DIR)}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "adb": adb_available(),
        "mvt": mvt_available(),
        "androidqf": androidqf_available(),
        "output_dir": str(OUTPUT_DIR),
    }


# Servir frontend estático (deve ser montado por último)
if (BASE_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(BASE_DIR), html=True), name="static")


# ── MAIN ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("  Acha Spyware - Backend iniciado")
    print("  Interface: http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
