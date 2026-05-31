#!/bin/bash

# Controllo formale dell'argomento passato da terminale
if [ "$1" != "local[*]" ] && [ "$1" != "yarn" ]; then
    echo "Errore: Argomento master non valido o mancante."
    echo "Uso correttot ./experiments.sh local[*]"
    echo "              ./experiments.sh yarn"
    exit 1
fi

echo "================================================================="
echo " AVVIO PIPELINE AUTOMATICA DI BENCHMARK - MODALITA': ${1^^} "
echo "================================================================="

# Avvio del Benchmark sequenziale per il Job 1 e il Job 2
python3 benchmark.py job_1 "$1" --fractions "0.01 0.2 0.5 0.7"
python3 benchmark.py job_2 "$1" --fractions "0.01 0.2 0.5 0.7"

echo "================================================================="
echo " PIPELINE COMPLETATA. CONTROLLA I RISULTATI NELLA DIRECTORY logs/ "
echo "================================================================="