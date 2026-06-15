#!/bin/bash
echo ""
echo " ========================================================"
echo "   VAM - Voice Assistant Module"
echo "   Computer Assistant Using Python"
echo "   By Memoona Razzaq (2022-ag-6166)"
echo "   UAF Sub Campus, Toba Tek Singh"
echo " ========================================================"
echo ""
echo " [*] Installing requirements..."
pip install -r requirements.txt --quiet
echo ""
echo " [*] Starting VAM server..."
echo " [*] Open your browser at: http://127.0.0.1:5000"
echo ""

# Open browser in background
if command -v xdg-open &> /dev/null; then
    sleep 2 && xdg-open http://127.0.0.1:5000 &
elif command -v open &> /dev/null; then
    sleep 2 && open http://127.0.0.1:5000 &
fi

python app.py
