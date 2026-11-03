#!/usr/bin/env bash
# Train and test all seven ML projects, then write one coverage report.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "$#" -ne 7 ]]; then
  echo "Pass all 7 project directory names. Got $#." >&2
  exit 1
fi
PROJECTS=("$@")

DATA_DIR="$ROOT/.coverage-data"
rm -rf "$DATA_DIR" "$ROOT/htmlcov" "$ROOT/coverage.xml" "$ROOT/coverage.json" "$ROOT/.coverage"
mkdir -p "$DATA_DIR"

for project in "${PROJECTS[@]}"; do
  echo "========== $project =========="
  project_dir="$ROOT/projects/$project"
  if [[ ! -d "$project_dir/tests" ]]; then
    echo "Missing tests directory: $project_dir/tests" >&2
    exit 1
  fi
  (
    cd "$project_dir"
    if [[ -f src/generate_data.py ]]; then
      python -m src.generate_data
    fi
    if [[ -f src/train.py ]]; then
      python -m src.train
    elif [[ -f train.py ]]; then
      python train.py
    else
      echo "No training entrypoint in $project" >&2
      exit 1
    fi
    sources="src"
    if [[ -f app.py ]]; then
      sources="src,app"
    fi
    # Measure the same commands CI runs: generate, train, then pytest.
    # Later commands append so a module executed only by the CLI is not
    # reported as uncovered. The first command must not pass --append.
    data_file="$DATA_DIR/.coverage.$project"
    append=()
    run_cov() {
      python -m coverage run "${append[@]}" \
        --data-file="$data_file" \
        --source="$sources" \
        "$@"
      append=(--append)
    }
    if [[ -f src/generate_data.py ]]; then
      run_cov -m src.generate_data
    fi
    if [[ -f src/train.py ]]; then
      run_cov -m src.train
    elif [[ -f train.py ]]; then
      run_cov -m train
    fi
    run_cov -m pytest -q
  )
done

python -m coverage combine --data-file="$ROOT/.coverage" "$DATA_DIR"/.coverage.*
python -m coverage html --data-file="$ROOT/.coverage" -d "$ROOT/htmlcov"
python -m coverage xml --data-file="$ROOT/.coverage" -o "$ROOT/coverage.xml"
python -m coverage json --data-file="$ROOT/.coverage" -o "$ROOT/coverage.json"
python -m coverage report --data-file="$ROOT/.coverage" -m --fail-under=70
python "$ROOT/scripts/write_coverage_docs.py"
echo "All 7 projects passed."
