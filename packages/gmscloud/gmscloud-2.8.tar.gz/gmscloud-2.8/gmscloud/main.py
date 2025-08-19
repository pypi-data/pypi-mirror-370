import win32print
import sys
import os

# Menambahkan direktori tempat file main.py berada ke sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from beautifultable import BeautifulTable
from print_faktur_rekening_utils import print_faktur_rekening 
from print_faktur_rekening_tanda_tangan_utils import print_faktur_rekening_tanda_tangan 
from print_faktur_group_utils import print_faktur_group 
from print_faktur_group_tanda_tangan_utils import print_faktur_group_tanda_tangan 
from print_surat_jalan_ttbk_utils import print_surat_jalan_ttbk
from print_surat_jalan_harga_utils import print_surat_jalan_harga
from print_surat_jalan_harga_ttbk_utils import print_surat_jalan_harga_ttbk
from print_surat_jalan_harga_driver_utils import print_surat_jalan_harga_driver
from print_surat_jalan_no_tabung_utils import print_surat_jalan_no_tabung
from print_surat_jalan_utils import print_surat_jalan
from print_titipan_utils import print_titipan
from print_ttbk_utils import print_ttbk
from print_ttd_utils import print_ttd
from print_gaji_utils import print_gaji
from do_print_utils import do_print 
from get_app_info import get_app_info
# ANSI escape codes for colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"

def select_printer():
    # Mengambil daftar printer lokal
    printer_list = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
    printer_names = [printer_info[2] for printer_info in printer_list]
    return printer_names

def print_ascii_art():
    art = r"""
  ____                   ____  _                    _ 
 / ___| _ __ ___   ___  / ___|| |  ___   _   _   __| |
| |  _ | '_ ` _ \ / __|| |    | | / _ \ | | | | / _` |
| |_| || | | | | |\__ \| |___ | || (_) || |_| || (_| |
 \____||_| |_| |_||___/ \____||_| \___/  \__,_| \__,_|                                                                        
    """
    print(art)
    print(get_app_info())

def print_separator():
    print("\n" + "=" * 50 + "\n")

def main():
    print_ascii_art()

    # Daftar kode perusahaan yang valid
    valid_company_codes = ["golden", "stargas", "bgs", "sga","mbg","localhost","demo"]

    kode = BeautifulTable()
    kode.columns.header = ["Nama Perusahaan","Kode Perusahaan"]
    kode.rows.append(["PT. BUMI GASINDO SUMATERA", "bgs"])
    kode.rows.append(["CV. SUMBER GASINDO ABADI", "sga"])
    kode.rows.append(["PT. GOLDEN ISLAND GROUP", "golden"])
    kode.rows.append(["PT. STARGAS INTI PERKASA", "stargas"])
    kode.rows.append(["PT. MINANG BERSAUDARA GAS", "mbg"])
    kode.set_style(BeautifulTable.STYLE_BOX)
    kode.columns.alignment = BeautifulTable.ALIGN_CENTER

    print(kode)

    while True:
        company_code = input(f"Masukkan Kode Perusahaan Anda: ")
        if company_code in valid_company_codes:
            print(f"Kode Perusahaan yang dimasukkan: {company_code}")
            break
        else:
            print(f"Kode perusahaan tidak valid. Silakan coba lagi.")

    print_separator()

    printers = select_printer()

    # Pilih printer
    print(f"Pilih Printer:")
    for idx, printer in enumerate(printers):
        print(f"{idx + 1}. {printer}")

    printer_choice = int(input(f"Masukkan nomor printer yang dipilih: ")) - 1
    selected_printer = printers[printer_choice]

    while True:
        print_separator()

        # Masukkan ID Dokumen
        doc_id = input(f"Masukkan ID Dokumen (atau ketik 'exit' untuk keluar): ")
        if doc_id.lower() == 'exit':
            print(f"Terima kasih telah menggunakan aplikasi ini!")
            break

        # Pilih jenis tombol print
        print("Pilih jenis print:")
        print("** Surat Jalan")
        print("1. Surat Jalan")
        print("2. Surat Jalan & TTBK")
        print("3. Surat Jalan & Harga")
        print("4. Surat Jalan & Harga + TTBK")
        print("5. Surat Jalan & Harga + Driver")
        print("6. Surat Jalan & Nomor Tabung")
        print("7. TTBK")
        print("** Faktur")
        print("8. Faktur")
        print("9. Faktur Grup Total Barang")
        print("10. Faktur + Tanda Tangan Penerima")
        print("11. Faktur Grup Total Barang + Tanda Tangan Penerima")
        print("** Titipan")
        print("12. Titipan")
        print("** Lainnya")
        print("13. Tanda Terima Dokumen")
        print("14. Gaji")
        
        # Tambahkan opsi lainnya sesuai kebutuhan

        print_choice = int(input(f"Masukkan nomor jenis print yang dipilih: "))

        # Proses pencetakan berdasarkan pilihan
        print(f"Printer yang dipilih: {selected_printer}")

        if print_choice == 1:
            print_surat_jalan(doc_id, selected_printer, company_code)  
        elif print_choice == 2:
            print_surat_jalan_ttbk(doc_id, selected_printer, company_code)
        elif print_choice == 3:
            print_surat_jalan_harga(doc_id, selected_printer, company_code)
        elif print_choice == 4:
            print_surat_jalan_harga_ttbk(doc_id, selected_printer, company_code)
        elif print_choice == 5:
            print_surat_jalan_harga_driver(doc_id, selected_printer, company_code)
        elif print_choice == 6:
            print_surat_jalan_no_tabung(doc_id, selected_printer, company_code)
        elif print_choice == 7:
            print_ttbk(doc_id, selected_printer, company_code)
        elif print_choice == 8:
            print_faktur_rekening(doc_id, selected_printer, company_code)
        elif print_choice == 9:
            print_faktur_group(doc_id, selected_printer, company_code)
        elif print_choice == 10:
            print_faktur_rekening_tanda_tangan(doc_id, selected_printer, company_code)
        elif print_choice == 11:
            print_faktur_group_tanda_tangan(doc_id, selected_printer, company_code)
        elif print_choice == 12:
            print_titipan(doc_id, selected_printer, company_code)
        elif print_choice == 13:
            print_ttd(doc_id, selected_printer, company_code)
        elif print_choice == 14:
            print_gaji(doc_id, selected_printer, company_code)
        else:
            print(f"Pilihan tidak valid!")

if __name__ == "__main__":
    main()
