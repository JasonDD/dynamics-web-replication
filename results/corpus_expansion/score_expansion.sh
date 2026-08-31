#!/bin/bash
# Sample-score each expansion corpus on the 8 DWEB axes via the shared 7B on :8301.
# Caps to 300 rows/corpus, WORKERS=6 to stay polite behind the running score job. Resumable.
set -u
cd /mnt/nas/kronaxis/corpora
CORPORA="fw2_indonesian fw2_thai fw2_vietnamese fw2_filipino fw2_kazakh fw2_uzbek fw2_samoan fw2_maori fw2_fijian fw2_amharic fw2_somali twitter_sentiment140 mastodon_toots telegram_channels youtube_comments gutenberg_english"
for n in $CORPORA; do
  in="$n/$n.jsonl"; cap="$n/score_in.jsonl"; out="$n/char.jsonl"
  [ -f "$in" ] || { echo "MISS $n"; continue; }
  head -150 "$in" > "$cap"
  echo "=== scoring $n ($(wc -l < $cap) rows) $(date -u +%H:%M:%S)Z ==="
  INPUT="$cap" OUT="$out" WORKERS=6 BODYMAX=6000 python3 score_turns.py 2>>score_expansion.err
done
echo "ALL DONE $(date -u +%H:%M:%S)Z"
