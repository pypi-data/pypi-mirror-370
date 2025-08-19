import win32print
import sys

# ANSI escape codes for colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"

def do_print(id, selected_printer):
    if not selected_printer:
        print("Error: Pilih printer terlebih dahulu!")
        return

    with open(f'{id}.txt', 'r') as file:
        table = file.read()

    # Menentukan data yang akan dikirim ke printer
    raw_data = bytes(table, "utf-8")
    hPrinter = win32print.OpenPrinter(selected_printer)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("test of raw data", None, "RAW"))
        try:
            win32print.StartPagePrinter(hPrinter)
            win32print.WritePrinter(hPrinter, raw_data)
            win32print.EndPagePrinter(hPrinter)
        finally:
            win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)
        print(f"\n{GREEN}Dokumen telah dicetak. Kembali ke menu ID Dokumen...\n{RESET}")