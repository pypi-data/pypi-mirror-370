import requests
import json
from beautifultable import BeautifulTable
from do_print_utils import do_print
from get_base_url import get_base_url
from konversi_tanggal_utils import konversi_tanggal

def print_faktur_rekening(doc_id, selected_printer, company_code):
    # Get base URL using the company code
    base_url = get_base_url(company_code)

    # Make the request to get faktur data
    response = requests.get(f"{base_url}/print/faktur/{doc_id}")
    json_obj = json.loads(response.content)
    print(json_obj)

    # Ensure that 'data' and nested keys exist in JSON
    data = json_obj.get('data', {})
    perusahaan = json_obj.get('perusahaan', {})
    user = json_obj.get('user', {})

    # Access related fields
    relasi_name = json_obj['data'].get('relasi', {}).get('MASTER_RELASI_NAMA', '') if json_obj['data'].get('relasi') else ''
    supplier_name = json_obj['data'].get('supplier', {}).get('MASTER_SUPPLIER_NAMA', '') if json_obj['data'].get('supplier') else ''
    driver_name = json_obj['data'].get('driver', {}).get('MASTER_KARYAWAN_NAMA', '') if json_obj['data'].get('driver') else f'{relasi_name} {supplier_name}'

    # Header table
    header = BeautifulTable()
    header.columns.width = 40
    header.columns.header = [
        f"{perusahaan.get('PERUSAHAAN_NAMA', '')}\n{perusahaan.get('PERUSAHAAN_ALAMAT', '')}\n{perusahaan.get('PERUSAHAAN_TELP', '')}",
        f"Nomor: {data.get('FAKTUR_NOMOR', '')}\nTanggal: {konversi_tanggal(data.get('FAKTUR_TANGGAL', ''))}\nKepada: {relasi_name}{supplier_name}"
    ]
    header.rows.append(["", ""])
    header.set_style(BeautifulTable.STYLE_NONE)
    header.columns.alignment = BeautifulTable.ALIGN_LEFT

    # Surat Jalan Table (with format matching the requested output)
    sj_table = BeautifulTable()
    sj_table.columns.width = 40
    sj_table.columns.header = ["              Surat Jalan             ", "             Tanggal            "]
    sj_table.columns.alignment = BeautifulTable.ALIGN_CENTER

    for sj in json_obj.get('suratJalanData', []):
        sj_number_date = f"{sj.get('SURAT_JALAN_NOMOR', '')}"
        sj_table.rows.append([sj_number_date, konversi_tanggal(sj.get('SURAT_JALAN_TANGGAL', ''))])

    # Barang Data Table (Formatted as requested)
    barang_table = BeautifulTable()
    barang_table.columns.width = 20
    barang_table.columns.header =["     Nama Barang     ", "     Harga     ","     QTY     ","     Total     "]
    barang_table.columns.alignment = BeautifulTable.ALIGN_CENTER

    for sj in json_obj.get('suratJalanData', []):
        for barang in sj.get('suratjalanbarang', []):
            barang_surat_jalan = barang.get('barangSuratJalan', {})
            barang_table.rows.append([
                barang_surat_jalan.get('MASTER_BARANG_NAMA', ''),  # Mengambil MASTER_BARANG_NAMA
                format(float(barang.get('SURAT_JALAN_BARANG_HARGA', 0)), ',.2f'),
                barang.get('SURAT_JALAN_BARANG_QUANTITY', ''),
                format(float(barang.get('SURAT_JALAN_BARANG_HARGA_TOTAL', 0)), ',.2f')
            ])

    # Signature table
    ttd = BeautifulTable()
    ttd.columns.width = 25
    ttd.columns.header = ["", "", "Dibuat Oleh"]
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["                         ", "                         ", "                         "])
    ttd.rows.append([
        "",
        "",
        user.get('USER_NAMA', '')
    ])
    ttd.set_style(BeautifulTable.STYLE_NONE)
    ttd.columns.alignment = BeautifulTable.ALIGN_CENTER

    # Claim notice table
    klaim = BeautifulTable()
    klaim.columns.width = 80
    klaim.columns.header = [f"{perusahaan.get('PERUSAHAAN_BANK', '')}"]
    klaim.rows.append([" " * 80])
    klaim.set_style(BeautifulTable.STYLE_NONE)
    klaim.columns.alignment = BeautifulTable.ALIGN_CENTER

    # Title table
    judul = BeautifulTable()
    judul.columns.width = 80
    judul.columns.header = ["INVOICE"]
    judul.rows.append([" " * 80])
    judul.set_style(BeautifulTable.STYLE_NONE)
    judul.columns.alignment = BeautifulTable.ALIGN_CENTER

    # DataTransaksi Table
    transaksi = BeautifulTable()
    transaksi.columns.width = 80
    transaksi.rows.append(["","","Total (Rp)", format(float(json_obj['dataTransaksi']['FAKTUR_TRANSAKSI_TOTAL']), ',.2f')])
    transaksi.rows.append(["", "", "Pajak (Rp)", format(float(json_obj['dataTransaksi']['FAKTUR_TRANSAKSI_PAJAK_RUPIAH']), ',.2f')])
    transaksi.rows.append(["", "", "Grand (Rp)", format(float(json_obj['dataTransaksi']['FAKTUR_TRANSAKSI_GRAND_TOTAL']), ',.2f')])
    transaksi.rows.append(["                     ","               ","             ","                "])
    transaksi.set_style(BeautifulTable.STYLE_COMPACT)
    transaksi.columns.alignment = BeautifulTable.ALIGN_RIGHT

    # Write to file
    with open(f'{doc_id}.txt', 'w') as f:
        f.write(str(header))
        f.write("\n")
        f.write(str(judul))
        f.write("\n")
        f.write(str(sj_table))
        f.write("\n")
        f.write(str(barang_table))  # Write the barang data table
        f.write("\n")
        f.write(str(transaksi))  # Write the dataTransaksi table
        f.write("\n")
        f.write("\n")
        f.write(str(ttd))
        f.write("\n")
        f.write("\n")
        f.write(str(klaim))

    # Print the document
    do_print(doc_id, selected_printer)
