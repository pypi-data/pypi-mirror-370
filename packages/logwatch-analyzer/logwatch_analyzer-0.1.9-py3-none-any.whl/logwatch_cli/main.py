import yaml
import subprocess
import json
import requests
import sys
import argparse
import shlex
import os
import platform
import importlib.resources
import time
import random
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

console = Console()

# ------------------------------- 
# LLM Wrapper Module
# ------------------------------- 
def analyze_log_messages(messages, task, provider_config):
    '''
    Analizza i log utilizzando un LLM, gestendo grandi volumi tramite riassunti intermedi.
    '''
    if not messages:
        return "Nessun messaggio da analizzare."

    CHUNK_SIZE = 50  # Numero di messaggi per blocco

    # Se i messaggi sono pochi, esegui lanalisi diretta
    if len(messages) <= CHUNK_SIZE:
        prompt = build_prompt(messages, task)
        response = call_llm_api(prompt, provider_config)
        if response is None:
            # Se la chiamata API fallisce, restituisce None per far gestire il fallback alla funzione chiamante
            return None
        return response

    # Se i messaggi sono troppi, applica la strategia di riassunto a blocchi
    console.print(f"[yellow]Rilevati {len(messages)} log. Verrà usata la modalità di analisi a blocchi per evitare di superare la context window del modello.[/yellow]")
    
    summaries = []
    task_summarize_chunk = """
    Sei un assistente per lanalisi dei log. Riassumi gli eventi chiave nel seguente blocco di log.
    Sii conciso e concentrati solo sulle informazioni più importanti. Elenca gli eventi chiave come punti elenco.
    """

    for i in range(0, len(messages), CHUNK_SIZE):
        chunk = messages[i:i + CHUNK_SIZE]
        console.print(f"Analisi del blocco {i//CHUNK_SIZE + 1}/{(len(messages) + CHUNK_SIZE - 1)//CHUNK_SIZE}...")
        
        prompt = build_prompt(chunk, task_summarize_chunk)
        summary = call_llm_api(prompt, provider_config)
        
        if summary:
            summaries.append(summary)
        else:
            # Se una chiamata API fallisce, lo segnaliamo ma continuiamo
            summaries.append(f"Errore nellanalisi del blocco {i//CHUNK_SIZE + 1}.")

    # Unisci i riassunti e crea il report finale
    console.print("Creazione del report finale basato sui riassunti intermedi...")
    
    final_prompt_messages = ["Di seguito sono riportati i riassunti dei blocchi di log analizzati:"] + summaries
    final_prompt = build_prompt(final_prompt_messages, task)
    
    final_report = call_llm_api(final_prompt, provider_config)
    
    if final_report is None:
        return "Errore durante la generazione del report finale."
        
    return final_report

def build_prompt(messages, task):
    return f"{task}:\n" + "\n".join(messages)

def call_llm_api(prompt, provider_config):
    provider_type = provider_config.get("type")
    timeout = provider_config.get("timeout", 60)  # Default a 60 secondi

    # Configura la strategia di retry
    retry_strategy = Retry(
        total=5,
        backoff_factor=2, # Aumentato per gestire meglio il rate limiting
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    response = None
    try:
        if provider_type == "ollama":
            response = session.post(
                provider_config["api_url"],
                json={
                    "model": provider_config["model"],
                    "prompt": prompt,
                    "stream": False
                },
                timeout=timeout
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()

        elif provider_type == "gemini":
            api_key_env = provider_config.get("api_key_env")
            api_key = os.getenv(api_key_env)
            if not api_key:
                console.print(f"[bold red]Errore: La variabile d'ambiente '{api_key_env}' non è impostata.[/bold red]")
                return None
            
            url = f"{provider_config['api_url']}?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            response = session.post(url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text'].strip()

        elif provider_type == "openrouter":
            api_key_env = provider_config.get("api_key_env")
            api_key = os.getenv(api_key_env)
            if not api_key:
                console.print(f"[bold red]Errore: La variabile d'ambiente '{api_key_env}' non è impostata.[/bold red]")
                return None

            api_url = provider_config["api_url"].rstrip('/')
            if not api_url.endswith('/chat/completions'):
                api_url += "/chat/completions"

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/levigross/logwatch", # Opzionale
                "X-Title": "LogWatch" # Opzionale
            }
            data = {
                "model": provider_config["model"],
                "messages": [{"role": "user", "content": prompt}]
            }

            response = session.post(api_url, headers=headers, json=data, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()

        else:
            console.print(f"[bold red]Errore: Provider LLM '{provider_type}' non supportato.[/bold red]")
            return None

    except requests.exceptions.RequestException as e:
        # Logga l'errore finale dopo che tutti i tentativi sono falliti
        console.print(f"[bold red]Errore di connessione al provider LLM '{provider_type}' dopo multipli tentativi.[/bold red]")
        console.print(f"Dettagli: {e}")
        return None
    except (KeyError, IndexError) as e:
        console.print(f"[bold red]Errore nella struttura della risposta dal provider '{provider_type}': {e}[/bold red]")
        if response:
            console.print(f"Risposta ricevuta: {response.text}")
        return None


# ------------------------------- 
# Log Parsers
# ------------------------------- 

def ssh_parser(entries):
    return [e for e in entries if "Failed password" in e.get("MESSAGE", "")]

def kernel_parser(entries):
    return [e for e in entries if "error" in e.get("MESSAGE", "").lower()]

def llm_parser(entries, provider_config, task_info):
    messages = [e.get("MESSAGE", "") for e in entries if e.get("MESSAGE")]
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    os_info = " ".join(platform.uname())
    log_command = task_info.get("command", "N/A")

    default_task = f"""
    Sei un esperto sistemista. Stai operando su un sistema con le seguenti caratteristiche: `{os_info}`.
    Analizza i seguenti log, ottenuti tramite il comando `{log_command}`, e genera un report tecnico conciso in formato Markdown.
    Il report è stato generato il {current_time}.

    Il report deve includere:
    1.  **Sommario Esecutivo**: Una sintesi di 1-2 frasi degli eventi principali.
    2.  **Eventi Rilevanti**: Una lista puntata degli eventi specifici trovati nei log.
    3.  **Criticità**: Una valutazione del livello di criticità (Info, Basso, Medio, Alto, Critico).

    **Regole importanti:**
    - Basa la tua analisi **esclusivamente** sui log forniti.
    - Non inventare o ipotizzare eventi non presenti nel testo.
    - Se non ci sono eventi significativi, indicalo chiaramente.
    """
    
    analysis_result = analyze_log_messages(messages, default_task, provider_config)
    
    if analysis_result is None:
        return entries
    
    return analysis_result

# ------------------------------- 
# Utility and Display Functions
# ------------------------------- 

def pre_filter_logs(logs, log_type, custom_filters):
    if not logs:
        return []

    critical_patterns = {
        "SSH Failed Logins": ["Failed password"],
        "Sudo Usage": ["authentication failure"],
    }
    must_show_patterns = critical_patterns.get(log_type, [])
    
    filtered_logs = []
    for log in logs:
        message = log.get("MESSAGE", "")
        is_critical = any(pattern in message for pattern in must_show_patterns)
        is_irrelevant = any(pattern in message for pattern in custom_filters)

        if is_critical or not is_irrelevant:
            filtered_logs.append(log)
            
    return filtered_logs

def load_config():
    """
    Carica la configurazione cercando in percorsi predefiniti.
    
    Ordine di priorità:
    1. ~/.config/logwatch/config.yaml (configurazione utente)
    2. config.yaml (directory corrente, per sviluppo)
    3. File config.yaml di default incluso nel pacchetto (fallback)
    """
    user_config_path = os.path.expanduser("~/.config/logwatch/config.yaml")
    local_config_path = "config.yaml"
    
    config_path_to_use = None
    
    if os.path.exists(user_config_path):
        config_path_to_use = user_config_path
    elif os.path.exists(local_config_path):
        config_path_to_use = local_config_path

    try:
        if config_path_to_use:
            with open(config_path_to_use, "r") as f:
                return yaml.safe_load(f)
        else:
            # Fallback: usa il file di configurazione di default dal pacchetto
            console.print("[yellow]Nessun file di configurazione locale trovato. Uso la configurazione di default.[/yellow]")
            console.print("Per personalizzare, copia il file in '~/.config/logwatch/config.yaml'")
            with importlib.resources.open_text("logwatch_cli", "config.yaml") as f:
                return yaml.safe_load(f)

    except FileNotFoundError:
        console.print(f"[bold red]Errore critico:[/bold red] Impossibile trovare qualsiasi file di configurazione.")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[bold red]Errore nel parsing del file YAML: {e}[/bold red]")
        sys.exit(1)

def get_log_entries(command):
    try:
        args = shlex.split(command)
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            if "No entries" not in result.stderr:
                 console.print(f"[yellow]Attenzione eseguendo '{command}':\n{result.stderr}[/yellow]")
            return []

        entries = []
        for line in result.stdout.splitlines():
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # If it's not a JSON object, treat it as a raw log message.
                    entries.append({"MESSAGE": line})
        return entries
    except FileNotFoundError:
        console.print(f"[bold red]Errore:[/bold red] Comando '{args[0]}' non trovato. Assicurati che sia installato e nel PATH.")
        return []

def display_results(title, results, output_file=None):
    console.print(f"[bold cyan]Risultati per: {title}[/bold cyan]")

    if isinstance(results, str):
        console.print(Markdown(results))
        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(results)
                console.print(f"\n[bold green]Report salvato in '{output_file}'[/bold green]")
            except IOError as e:
                console.print(f"[bold red]Errore durante il salvataggio del file:[/bold red] {e}")

    elif isinstance(results, list) and results:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Log Entry", style="dim")
        for r in results:
            message = r.get("MESSAGE", "Evento senza messaggio.") if isinstance(r, dict) else r
            table.add_row(str(message))
        console.print(table)
    else:
        console.print("Nessun risultato significativo trovato.")

# ------------------------------- 
# Main CLI Execution
# ------------------------------- 

def main():
    parser = argparse.ArgumentParser(
        description="LogWatch: uno strumento da CLI per analizzare i log di sistema.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--task", type=str, help="Esegue solo un task di analisi specificato per nome.")
    parser.add_argument("--list", action="store_true", help="Elenca tutti i task di analisi disponibili dalla configurazione.")
    parser.add_argument("--since", type=str, help="Sovrascrive la finestra temporale per l'analisi (es. '1 hour ago', '2 days ago').")
    parser.add_argument("--output", "-o", type=str, help="Salva il report in un file (preferibilmente .md).")
    args = parser.parse_args()

    config = load_config()
    
    active_provider_name = config.get("active_llm_provider")
    llm_providers = config.get("llm_providers", {})
    provider_config = llm_providers.get(active_provider_name)
    
    log_tasks = config.get("logs", [])

    if args.list:
        table = Table(title="[bold]Task di Analisi Disponibili[/bold]")
        table.add_column("Nome Task", style="cyan")
        table.add_column("Comando", style="magenta")
        table.add_column("Parser", style="green")
        for task in log_tasks:
            table.add_row(task.get('name'), task.get('command'), task.get('parser'))
        console.print(table)
        sys.exit(0)

    if args.task:
        log_tasks = [t for t in log_tasks if t.get("name") == args.task]
        if not log_tasks:
            console.print(f"[bold red]Errore:[/bold red] Task '{args.task}' non trovato in config.yaml.")
            sys.exit(1)

    for task in log_tasks:
        command = task.get("command")
        if args.since:
            command = ' '.join(command.split('--since')[0].strip().split()) + f" --since '{args.since}'"

        task['command'] = command

        entries = get_log_entries(command)
        custom_filters = task.get("filters", [])
        filtered_entries = pre_filter_logs(entries, task.get("name"), custom_filters)
        
        parser_name = task.get("parser")
        parser_func = globals().get(parser_name)
        
        if not parser_func:
            console.print(f"[yellow]Parser '{parser_name}' non trovato.[/yellow]")
            continue
        
        if parser_name == "llm_parser":
            if not provider_config:
                console.print(f"[bold red]Salto del task '{task.get('name')}' perché il provider LLM '{active_provider_name}' non è configurato.[/bold red]")
                continue
            results = parser_func(filtered_entries, provider_config, task)
        else:
            results = parser_func(filtered_entries)
            
        display_results(task.get("name"), results, args.output)

if __name__ == "__main__":
    main()