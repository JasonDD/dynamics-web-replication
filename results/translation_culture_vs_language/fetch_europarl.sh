#!/usr/bin/env bash
set -euo pipefail
D=/mnt/nas/kronaxis/corpora/europarl_v7
mkdir -p "$D"
cd "$D"
for pr in de-en fr-en es-en it-en fi-en pl-en el-en; do
  if [ -f "europarl-v7.${pr}.en" ]; then echo "SKIP $pr (extracted)"; continue; fi
  if [ ! -f "${pr}.tgz" ]; then
    echo "GET $pr"; curl -s -m 1200 -o "${pr}.tgz" "https://www.statmt.org/europarl/v7/${pr}.tgz"
  fi
  echo "EXTRACT $pr"; tar -xzf "${pr}.tgz"
  echo "DONE $pr lines=$(wc -l < europarl-v7.${pr}.en)"
done
echo "ALL_DONE"
ls -la "$D"/europarl-v7.*.en
