import requests
import json
from beautifultable import BeautifulTable
from do_print_utils import do_print
from get_base_url import get_base_url
from konversi_tanggal_utils import konversi_tanggal

def print_ttbk(doc_id, selected_printer, company_code):
    # Menggunakan get_base_url untuk mendapatkan domain yang sesuai
    base_url = get_base_url(company_code)

    # Menggunakan company_code untuk membangun URL
    response = requests.get(f"{base_url}/print/surat-jalan/{doc_id}")
    json_obj = json.loads(response.content)
    print(json_obj)

    relasi_name = json_obj['data'].get('relasi', {}).get('MASTER_RELASI_NAMA', '') if json_obj['data'].get('relasi') else ''
    supplier_name = json_obj['data'].get('supplier', {}).get('MASTER_SUPPLIER_NAMA', '') if json_obj['data'].get('supplier') else ''
    driver_name = json_obj['data'].get('driver', {}).get('MASTER_KARYAWAN_NAMA', '') if json_obj['data'].get('driver') else f'{relasi_name} {supplier_name}'

    header = BeautifulTable()
    header.columns.width = 40
    header.columns.header = [
        f"{json_obj['perusahaan']['PERUSAHAAN_NAMA']}\n"
        f"{json_obj['perusahaan']['PERUSAHAAN_ALAMAT']}\n"
        f"{json_obj['perusahaan']['PERUSAHAAN_TELP']}",
        f"Nomor: {json_obj['data']['SURAT_JALAN_NOMOR']}\n"
        f"Tanggal: {konversi_tanggal(json_obj['data']['SURAT_JALAN_TANGGAL'])}"
    ]
    
    header.rows.append(["", ""])
    header.set_style(BeautifulTable.STYLE_NONE)
    header.columns.alignment = BeautifulTable.ALIGN_LEFT

    table = BeautifulTable()
    barang = BeautifulTable()
    barang.columns.width = 40
    barang.columns.header = ["                 Nama Barang                ", "             QTY            "]
    for result in json_obj['barang']:
        barang.rows.append([result['barangSuratJalan']['MASTER_BARANG_NAMA'], ""])
    barang.columns.alignment = BeautifulTable.ALIGN_CENTER

    ttbk_col = BeautifulTable()
    ttbk_col.columns.width = 40
    ttbk_col.columns.header = ["   ","   ", "   ","   ", "   ","   ", "   ","   ", "   ","   ", "   ","   ", "   "]
    ttbk_col.rows.append(["   ","   ", "   ","   ", "   ","   ", "   ","   ", "   ","   ", "   ","   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.set_style(BeautifulTable.STYLE_BOX)
    ttbk_col.columns.alignment = BeautifulTable.ALIGN_CENTER

    subtable2 = BeautifulTable()
    subtable2.rows.append(["                                          "])
    subtable2.rows.append([f"{json_obj['data']['SURAT_JALAN_KETERANGAN']}"])

    table.rows.append([f"Nama : {relasi_name} {supplier_name} "])
    table.rows.append([""])
    table.set_style(BeautifulTable.STYLE_NONE)
    table.columns.alignment = BeautifulTable.ALIGN_LEFT

    ttd = BeautifulTable()
    ttd.columns.width = 25
    ttd.columns.header = ["Diketahui Oleh","Diterima Oleh","Diperiksa Oleh"]
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["                         ", "                         ", "                         "])
    ttd.rows.append([
         f"{relasi_name} {supplier_name}".strip(),
        driver_name,
        json_obj['user']['USER_NAMA']
        ])
    ttd.set_style(BeautifulTable.STYLE_NONE)
    ttd.columns.alignment = BeautifulTable.ALIGN_CENTER

    judul = BeautifulTable()
    judul.columns.width = 80
    judul.columns.header = ["TTBK SURAT JALAN\nTABUNG KOSONG"]
    judul.rows.append(["                                                                      "])
    judul.set_style(BeautifulTable.STYLE_NONE)
    judul.columns.alignment = BeautifulTable.ALIGN_CENTER
    with open(f'{doc_id}.txt', 'w') as f:
        f.write(str(header))
        f.write("\n")
        f.write(str(judul))
        f.write("\n")
        f.write(str(table))
        f.write("\n")
        f.write(str(barang))
        f.write("\n")
        f.write(str(ttbk_col))
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write(str(ttd))
    do_print(doc_id,selected_printer)
