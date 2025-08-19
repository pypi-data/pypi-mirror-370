import requests
import json
from beautifultable import BeautifulTable
from do_print_utils import do_print
from get_base_url import get_base_url
from konversi_tanggal_utils import konversi_tanggal

def print_ttd(doc_id, selected_printer, company_code):
    # Menggunakan get_base_url untuk mendapatkan domain yang sesuai
    base_url = get_base_url(company_code)

    # Menggunakan company_code untuk membangun URL
    response = requests.get(f"{base_url}/print/ttd/{doc_id}")
    json_obj = json.loads(response.content)
    print(json_obj)

    relasi_name = json_obj['data'].get('relasi', {}).get('MASTER_RELASI_NAMA', '') if json_obj['data'].get('relasi') else ''

    header = BeautifulTable()
    header.columns.width = 40
    header.columns.header = [
        f"{json_obj['perusahaan']['PERUSAHAAN_NAMA']}\n"
        f"{json_obj['perusahaan']['PERUSAHAAN_ALAMAT']}\n"
        f"{json_obj['perusahaan']['PERUSAHAAN_TELP']}",
    ]
    
    header.rows.append([""])
    header.set_style(BeautifulTable.STYLE_NONE)
    header.columns.alignment = BeautifulTable.ALIGN_LEFT

    table = BeautifulTable()
    barang = BeautifulTable()
    barang.columns.width = 40
    barang.columns.header = [" No ", "       Dokumen       ", "       Keterangan      ", "      Nilai      "]

    total_nilai = 0

    for result in json_obj['dataDetail']:
        nilai = float(result['TTD_NILAI'])  # Ambil nilai sebagai integer
        total_nilai += nilai  # Tambahkan nilai ke total
        barang.rows.append([
            result['TTD_NO'],
            result['TTD_DOKUMEN'],
            result['TTD_DOKUMEN_KETERANGAN'],
            format(nilai, ',.2f') if nilai != 0 else ""  # Tulis kosong jika nilai == 0
        ])

    barang.rows.append(["", "", "Total", format(total_nilai, ',.2f')])
    barang.columns.alignment = BeautifulTable.ALIGN_CENTER
  

    subtable2 = BeautifulTable()
    subtable2.rows.append(["                                          "])
    subtable2.rows.append([f"{json_obj['data']['TTD_KETERANGAN']}"])

    # table.rows.append([f"Nama : {relasi_name} "])
    # table.rows.append([""])
    # table.set_style(BeautifulTable.STYLE_NONE)
    # table.columns.alignment = BeautifulTable.ALIGN_LEFT

    ttd = BeautifulTable()
    ttd.columns.width = 25
    ttd.columns.header = ["Diserahkan Oleh", "", "Diterima Oleh"]
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["                         ", "                         ", "                         "])
    ttd.rows.append([
        json_obj['user']['USER_NAMA'],
        "",
         f"{relasi_name}".strip()
        ])
    ttd.set_style(BeautifulTable.STYLE_NONE)
    ttd.columns.alignment = BeautifulTable.ALIGN_CENTER

    judul = BeautifulTable()
    judul.columns.width = 80
    judul.columns.header = [f"TANDA TERIMA DOKUMEN"]
    judul.rows.append([f"{json_obj['data']['TTD_NOMOR']}"])
    judul.rows.append([f"{konversi_tanggal(json_obj['data']['TTD_TANGGAL'])}"])
    judul.rows.append(["                                                                             "])
    judul.set_style(BeautifulTable.STYLE_NONE)
    judul.columns.alignment = BeautifulTable.ALIGN_CENTER
    with open(f'{doc_id}.txt', 'w') as f:
        f.write(str(header))
        f.write("\n")
        f.write(str(judul))
        f.write("\n")
        f.write("Kepada Yth,")
        f.write("\n")
        f.write(f"   {relasi_name}")
        f.write("\n")
        f.write(f"   UP. {json_obj['data']['TTD_UP']}")
        f.write("\n")
        f.write("\n")
        f.write(f"Telah diterima dari {json_obj['perusahaan']['PERUSAHAAN_NAMA']} Dokumen sebagai berikut :")
        f.write(str(table))
        f.write("\n")
        f.write(str(barang))
        f.write("\n")
        f.write(f"{json_obj['data']['TTD_KETERANGAN']}")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write(str(ttd))
    do_print(doc_id,selected_printer)
