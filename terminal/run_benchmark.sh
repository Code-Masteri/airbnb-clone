#!/bin/bash

export GROQ_API_KEY=$(cat .env | grep GROQ_API_KEY | cut -d'=' -f2 | tr -d '"')

ROUNDS=5
WAIT_MINUTES=65  # 65 mins to let daily limit breathe

for i in $(seq 1 $ROUNDS); do
    echo ""
    echo "========================================"
    echo "ROUND $i of $ROUNDS — $(date)"
    echo "========================================"

    echo "--- Running Oracle ---"
    harbor run -p "./distributed_job_queue" -a oracle

    echo "--- Running AI Agent ---"
    harbor run -p "./distributed_job_queue" \
        -a terminus-2 \
        --model groq/moonshotai/kimi-k2-instruct-0905 \
        -k 10 -n 1

    if [ $i -lt $ROUNDS ]; then
        echo ""
        echo "Waiting $WAIT_MINUTES minutes before next round..."
        echo "Next run at: $(date -v +${WAIT_MINUTES}M)"
        sleep ${WAIT_MINUTES}m
    fi
done

echo ""
echo "All $ROUNDS rounds complete!"
