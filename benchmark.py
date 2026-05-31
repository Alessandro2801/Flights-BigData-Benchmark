#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Automated Benchmark Execution Pipeline")
    parser.add_argument("job", type=str, choices=["job_1", "job_2"], help="Job name (matching script prefix)")
    parser.add_argument("master", type=str, choices=["local[*]", "yarn"], help="Master type execution environment")
    parser.add_argument("--fractions", type=str, default="0.01 0.2 0.5 0.7", help="Fractions of dataset to use")
    args = parser.parse_args()

    # Configurazione automatica della directory di destinazione sicura
    master_dir = "local" if "local" in args.master else "yarn"

    # Le tre cartelle reali presenti nel tuo progetto Flight
    tools = ["spark-core", "spark-sql", "hive"]

    # Traduzione delle frazioni decimali nei nomi dei file effettivi su HDFS
    fraction_values = list(map(float, args.fractions.split()))
    fractions = [f"flights_{int(x * 100)}" for x in fraction_values] + ["flights_cleaned"]

    # Dizionario per memorizzare i tempi di esecuzione per i grafici
    execution_data = {tool: [] for tool in tools}
    
    # Memorizziamo solo le frazioni che hanno avuto successo per ciascun tool (evita disallineamenti sull'asse X)
    successful_fractions = {tool: [] for tool in tools}

    for tool in tools:
        for fraction in fractions:
            print(f"[BENCHMARK] Avvio {tool} -> {args.job} su dataset: {fraction} ({args.master})")
            
            start = time.time()
            
            # Esecuzione nativa entrando nella cartella specifica (cwd) della tecnologia
            process = subprocess.run(
                ["bash", "run.sh", args.job, fraction, args.master],
                cwd=tool,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            end = time.time()
            exec_time = end - start

            # Creazione dinamica della struttura dei log divisa per master (local/yarn)
            output_path = os.path.join("logs", master_dir, tool, args.job)
            os.makedirs(output_path, exist_ok=True)
            
            # Salvataggio del file di log di output standard
            with open(os.path.join(output_path, f"stdout-{fraction}.txt"), "wb") as f:
                f.write(process.stdout)

            # Se il processo termina correttamente con exit code 0, salviamo il tempo per i grafici
            if process.returncode == 0:
                print(f"[BENCHMARK] Completato {tool}#{args.job} per \"{fraction}\" in {exec_time:.2f} secondi")
                execution_data[tool].append(exec_time)
                successful_fractions[tool].append(fraction)
            else:
                print(f"[⚠️ ERRORE CRITICO] {tool} ha fallito su {fraction}. Controlla stderr-{fraction}.txt")
                with open(os.path.join(output_path, f"stderr-{fraction}.txt"), "wb") as f:
                    f.write(process.stderr)

    # --- GENERAZIONE GRAFICI CON MATPLOTLIB ---
    plt.figure(figsize=(11, 6))

    # Definizione colori accattivanti e coerenti con le cartelle reali
    colors = {
        "hive": "red",
        "spark-core": "green",
        "spark-sql": "blue"
    }

    # Disegna le linee sul grafico in modo dinamico
    for tool in tools:
        if execution_data[tool]:
            x_pos = list(range(len(successful_fractions[tool])))
            plt.plot(
                x_pos,
                execution_data[tool],
                marker='o',
                linestyle='-',
                linewidth=2,
                label=tool,
                color=colors.get(tool, "black")
            )

    # Definizione pulita delle etichette dell'asse X basata sulla pianificazione teorica iniziale
    full_x_labels = [f.replace("flights_", "") + "%" if "cleaned" not in f else "100% (Cleaned)" for f in fractions]
    plt.xticks(list(range(len(fractions))), full_x_labels)
    
    plt.xlabel('Dimensione Dataset (% su scala reale)', fontsize=11, fontweight='bold')
    plt.ylabel('Tempo di esecuzione (Secondi)', fontsize=11, fontweight='bold')
    plt.title(f'Benchmark Execution Time ({master_dir.upper()} Mode) - {args.job.upper()}', fontsize=13, fontweight='bold', pad=15)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()

    # Salvataggio automatico del grafico nella cartella del rispettivo master
    graph_folder = os.path.join("logs", master_dir)
    os.makedirs(graph_folder, exist_ok=True)
    output_graph = os.path.join(graph_folder, f"benchmark_{args.job}.png")
    
    plt.savefig(output_graph, dpi=300)
    print(f"\n[BENCHMARK EXECUTOR] Esperimento completato! Grafico salvato in: {output_graph}\n")

if __name__ == "__main__":
    main()