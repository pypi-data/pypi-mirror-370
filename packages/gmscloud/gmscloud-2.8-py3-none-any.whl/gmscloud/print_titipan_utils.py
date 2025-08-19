import requests
import json
from beautifultable import BeautifulTable
from do_print_utils import do_print
from get_base_url import get_base_url
from konversi_tanggal_utils import konversi_tanggal

def print_titipan(doc_id, selected_printer, company_code):
    # Menggunakan get_base_url untuk mendapatkan domain yang sesuai
    base_url = get_base_url(company_code)

    # Menggunakan company_code untuk membangun URL
    response = requests.get(f"{base_url}/print/titipan/{doc_id}")
    json_obj = json.loads(response.content)
    print(json_obj)

    relasi_name = json_obj['data'].get('relasiTitipan', {}).get('MASTER_RELASI_NAMA', '') if json_obj['data'].get('relasiTitipan') else ''
    supplier_name = json_obj['data'].get('supplierTitipan', {}).get('MASTER_SUPPLIER_NAMA', '') if json_obj['data'].get('supplierTitipan') else ''

    header = BeautifulTable()
    header.columns.width = 40
    header.columns.header = [
        f"{json_obj['perusahaan']['PERUSAHAAN_NAMA']}\n"
        f"{json_obj['perusahaan']['PERUSAHAAN_ALAMAT']}\n"
        f"{json_obj['perusahaan']['PERUSAHAAN_TELP']}",
        f"Nomor: {json_obj['data']['TITIPAN_NOMOR']}\n"
        f"Tanggal: {konversi_tanggal(json_obj['data']['TITIPAN_TANGGAL'])}\n"
        f"Kepada: {relasi_name}{supplier_name}"
    ]
    
    header.rows.append(["", ""])
    header.set_style(BeautifulTable.STYLE_NONE)
    header.columns.alignment = BeautifulTable.ALIGN_LEFT


    barang_ttbk = BeautifulTable()
    barang_ttbk.columns.width = 40
    barang_ttbk.columns.header = ["          Nama Barang          ", "      Masuk      ", "      Keluar      "]
    for result in json_obj['titipanBarang']:
        barang_ttbk.rows.append([result['barang']['MASTER_BARANG_NAMA'], result['JURNAL_TABUNG_KEMBALI'],result['JURNAL_TABUNG_KIRIM']])
    barang_ttbk.columns.alignment = BeautifulTable.ALIGN_CENTER

    ttd = BeautifulTable()
    ttd.columns.width = 25
    ttd.columns.header = ["Diketahui Oleh", "", "Dibuat Oleh"]
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["                         ", "                         ", "                         "])
    ttd.rows.append([
        f"{relasi_name} {supplier_name}".strip(),
        "",
        json_obj['user']['USER_NAMA']
          ])
    ttd.set_style(BeautifulTable.STYLE_NONE)
    ttd.columns.alignment = BeautifulTable.ALIGN_CENTER

    judul = BeautifulTable()
    judul.columns.width = 80
    judul.columns.header = ["TITIPAN"]
    judul.rows.append(["                                                                      "])
    judul.set_style(BeautifulTable.STYLE_NONE)
    judul.columns.alignment = BeautifulTable.ALIGN_CENTER


    # with open(f'{id}.txt', 'w', encoding='utf-8') as f:
    with open(f'{doc_id}.txt', 'w') as f:
        f.write(str(header))
        f.write("\n")
        f.write(str(judul))
        f.write("\n")
        f.write(str(barang_ttbk))
        f.write("\n")
        f.write("\n")
        f.write(str(ttd))
    do_print(doc_id,selected_printer)
