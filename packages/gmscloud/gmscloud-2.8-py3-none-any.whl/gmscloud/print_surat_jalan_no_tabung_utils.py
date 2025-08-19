import requests
import json
from beautifultable import BeautifulTable
from do_print_utils import do_print
from get_base_url import get_base_url
from konversi_tanggal_utils import konversi_tanggal

def print_surat_jalan_no_tabung(doc_id, selected_printer, company_code):
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
        f"Tanggal: {konversi_tanggal(json_obj['data']['SURAT_JALAN_TANGGAL'])}\n"
        f"Kepada: {relasi_name}{supplier_name}"
    ]
    
    header.rows.append(["", ""])
    header.set_style(BeautifulTable.STYLE_NONE)
    header.columns.alignment = BeautifulTable.ALIGN_LEFT

    table = BeautifulTable()
    table.columns.width = 20
    table.columns.header =["     Nama Barang     ", "  #  ","    Harga    ","    QTY    ","    Total    "]
    grandtotal = 0
    for result in json_obj['barang']:
        total = float(result.get('SURAT_JALAN_BARANG_HARGA', 0)) * float(result.get('SURAT_JALAN_BARANG_QUANTITY', 0))
        grandtotal += total
        table.rows.append([
            result.get('barangSuratJalan', {}).get('MASTER_BARANG_NAMA', 'N/A'), 
            result.get('SURAT_JALAN_BARANG_KEPEMILIKAN', 0), 
            format(result.get('SURAT_JALAN_BARANG_HARGA', 0), ',d'), 
            result.get('SURAT_JALAN_BARANG_QUANTITY', 0), 
            format(total, ',.2f')
        ])
    table.columns.alignment = BeautifulTable.ALIGN_RIGHT

    barang = BeautifulTable()
    barang.columns.width = 40
    barang.columns.header = ["            Nama Barang           ", "   Kepemilikan  ","        QTY       "]
    for result in json_obj['barang']:
        barang.rows.append([result['barangSuratJalan']['MASTER_BARANG_NAMA'], result['SURAT_JALAN_BARANG_KEPEMILIKAN'],result['SURAT_JALAN_BARANG_QUANTITY']])
    barang.columns.alignment = BeautifulTable.ALIGN_CENTER

    # ttbk_col = BeautifulTable()
    # ttbk_col.columns.width = 40
    # ttbk_col.columns.header = ["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ",
    #                            "   "]
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.rows.append(["   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   ", "   "])
    # ttbk_col.columns.alignment = BeautifulTable.ALIGN_CENTER

    ttbk_col = BeautifulTable()
    ttbk_col.columns.width = 10  # Sesuaikan lebar kolom
    ttbk_col.columns.header = ["    ", "    ", "    ", "    ", "    ", "    ", "    ", "    ", "    ", "    ", "    "]

    # Jumlah baris yang diinginkan (13 baris)
    num_rows = 13
    for _ in range(num_rows):
        ttbk_col.rows.append(["   "] * 11)  # 13 kolom dengan data kosong

    # Data suratjalanbarangnomor dari JSON
    suratjalanbarangnomor = json_obj['data']['suratjalanbarangnomor']

    # Looping untuk mengisi setiap sel dengan data
    for i, nomor in enumerate(suratjalanbarangnomor):
        # Hitung baris dan kolom yang sesuai
        row = i % num_rows  # Baris (0-12)
        col = i // num_rows  # Kolom (0, 1, 2, ...)
        
        # Jika kolom melebihi 13, hentikan pengisian (batas kolom)
        if col >= 13:
            break
        
        # Isi sel dengan nomor barang
        ttbk_col.rows[row][col] = nomor['SURAT_JALAN_BARANG_NOMOR']

    # Atur alignment tabel ke tengah
    ttbk_col.columns.alignment = BeautifulTable.ALIGN_CENTER


    keterangan = BeautifulTable()
    keterangan.rows.append([json_obj['data']['SURAT_JALAN_KETERANGAN']])
    keterangan.set_style(BeautifulTable.STYLE_NONE)

    ttd = BeautifulTable()
    ttd.columns.width = 25
    ttd.columns.header = ["Diterima Oleh", "Dibawa Oleh", "Dibuat Oleh"]
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["                         ", "                         ", "                         "])
    ttd.rows.append([
        f"{relasi_name} {supplier_name}".strip(),
        driver_name,
        json_obj['user']['USER_NAMA']
        ])
    ttd.set_style(BeautifulTable.STYLE_NONE)
    ttd.columns.alignment = BeautifulTable.ALIGN_CENTER

    klaim = BeautifulTable()
    klaim.columns.width = 80
    klaim.columns.header = ["Klaim hanya dapat dilayani dalam waktu 1x24 Jam sejak barang diterima."]
    klaim.rows.append(["                                                                                "])
    klaim.set_style(BeautifulTable.STYLE_NONE)
    klaim.columns.alignment = BeautifulTable.ALIGN_CENTER

    judul = BeautifulTable()
    judul.columns.width = 80
    judul.columns.header = ["SURAT JALAN"]
    judul.rows.append(["                                                                      "])
    judul.set_style(BeautifulTable.STYLE_NONE)
    judul.columns.alignment = BeautifulTable.ALIGN_CENTER

    # with open(f'{id}.txt', 'w', encoding='utf-8') as f:
    with open(f'{doc_id}.txt', 'w', encoding='cp1252', errors='replace') as f:
        f.write(str(header))
        f.write("\n")
        f.write(str(judul))
        f.write("\n")
        f.write(str(barang))
        f.write("\n")
        f.write(str(keterangan))
        f.write("\n")
        f.write(str(ttbk_col))
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write(str(ttd))
        f.write("\n")
        f.write("\n")
        f.write(str(klaim))
    do_print(doc_id,selected_printer)
