import requests
import json
from beautifultable import BeautifulTable
from do_print_utils import do_print
from get_base_url import get_base_url
from konversi_tanggal_utils import konversi_tanggal
from datetime import datetime

def print_gaji(doc_id, selected_printer, company_code):
    # Menggunakan get_base_url untuk mendapatkan domain yang sesuai
    base_url = get_base_url(company_code)

    # Menggunakan company_code untuk membangun URL
    response = requests.get(f"{base_url}/print/gaji/{doc_id}")
    json_obj = json.loads(response.content)
    print(json_obj)

    total = int(json_obj['data']['GAJI_TOTAL_POKOK'])+int(json_obj['data']['GAJI_TOTAL_PREMI'])
    sj = BeautifulTable()
    sj.columns.width = 40
    sj.columns.header = ["                                                         ", ""]
    sj.rows.append(["Gaji Pokok", format(int(json_obj['data']['GAJI_POKOK']), ',d')])

    if json_obj['data']['GAJI_JABATAN'] == "0":
        print('tidak ada')
    else:
        sj.rows.append(["Tunjangan Jabatan", format(int(json_obj['data']['GAJI_JABATAN']),',d')])

    sj.rows.append(["Tunjangan Komunikasi", format(int(json_obj['data']['GAJI_KOMUNIKASI']),',d')])
    sj.rows.append(["Uang Makan", format(int(json_obj['data']['GAJI_UANG_MAKAN_RUPIAH']),',d')])
    sj.rows.append(["Transportasi", format(int(json_obj['data']['GAJI_TRANSPORTASI']),',d')])

    if format(int(json_obj['data']['GAJI_BONUS'])) == "0":
        print('tidak ada')
    else:
        sj.rows.append([(json_obj['data']['GAJI_BONUS_LABEL']), format(int(json_obj['data']['GAJI_BONUS']),',d')])
    
    if format(int(json_obj['data']['GAJI_BONUS_2'])) == "0":
        print('tidak ada')
    else:
        sj.rows.append([(json_obj['data']['GAJI_BONUS_LABEL_2']), format(int(json_obj['data']['GAJI_BONUS_2']),',d')])

    if format(int(json_obj['data']['GAJI_PREMI_PENGANTARAN_RUPIAH'])) == "0":
        print('tidak ada')
    else :
        sj.rows.append(["Premi Pengantaran", format(int(json_obj['data']['GAJI_PREMI_PENGANTARAN_RUPIAH']),',d')])

    if format(int(json_obj['data']['GAJI_PREMI_PRODUKSI_RUPIAH'])) == "0":
        print('tidak ada')
    else :
        sj.rows.append(["Premi Produksi", format(int(json_obj['data']['GAJI_PREMI_PRODUKSI_RUPIAH']),',d')])
    
    if (
        json_obj['data']['GAJI_PREMI_GAS_RUPIAH'] == "0"
        and json_obj['data']['GAJI_PREMI_LIQUID_RUPIAH'] == "0"
        and json_obj['data']['GAJI_PREMI_SPAREPART_RUPIAH'] == "0"
        and json_obj['data']['GAJI_PREMI_TRANSPORTER_RUPIAH'] == "0"
    ):
        print('tidak ada')
    else:
        # Menghitung total premi lainnya
        total_premi = (
            int(json_obj['data']['GAJI_PREMI_GAS_RUPIAH']) +
            int(json_obj['data']['GAJI_PREMI_LIQUID_RUPIAH']) +
            int(json_obj['data']['GAJI_PREMI_SPAREPART_RUPIAH']) +
            int(json_obj['data']['GAJI_PREMI_TRANSPORTER_RUPIAH'])
        )
        
        # Menambahkan baris ke sj.rows
        sj.rows.append(["Premi Penjualan", format(total_premi, ',d')])

    sj.rows.append(["Total (+)", format(total, ',d')])
    sj.rows.append(["", ""])
    sj.rows.append(["Potongan (-)", format(int(json_obj['data']['GAJI_POTONGAN']),',d')])
    sj.rows.append(["Hutang (-)", format(int(json_obj['data']['GAJI_HUTANG']),',d')])
    sj.rows.append(["BPJS (-)", format(int(json_obj['data']['GAJI_BPJS']),',d')])
    sj.rows.append(["Total (+)", format(int(json_obj['data']['GAJI_TOTAL']),',d')])
    sj.set_style(BeautifulTable.STYLE_NONE)
    sj.columns.alignment = BeautifulTable.ALIGN_LEFT, BeautifulTable.ALIGN_RIGHT

    tanggal_hari_ini = datetime.today().strftime('%Y-%m-%d')

# Menyusun header
    

    ttd = BeautifulTable()
    ttd.columns.width = 25
    ttd.columns.header = ["Diterima Oleh", "", f"{konversi_tanggal(tanggal_hari_ini)}"]
    ttd.rows.append(["\n", "\n", "\n"])
    ttd.rows.append(["                       ", "                     ", "                       "])
    ttd.rows.append([f"{json_obj['data']['karyawan']['MASTER_KARYAWAN_NAMA']}", "",f"{json_obj['user']['USER_NAMA']}"])
    ttd.set_style(BeautifulTable.STYLE_NONE)
    ttd.columns.alignment = BeautifulTable.ALIGN_CENTER

    judul = BeautifulTable()
    judul.columns.width = 80
    judul.columns.header = [f"SLIP GAJI {json_obj['data']['karyawan']['MASTER_KARYAWAN_NAMA']} | Bulan : {json_obj['data']['GAJI_BULAN']} ; Tahun : {json_obj['data']['GAJI_TAHUN']}"]
    judul.rows.append([f"                                                                "])
    judul.set_style(BeautifulTable.STYLE_NONE)
    judul.columns.alignment = BeautifulTable.ALIGN_CENTER

    # with open(f'{id}.txt', 'w', encoding='utf-8') as f:
    with open(f'{doc_id}.txt', 'w') as f:
        f.write(f"{json_obj['perusahaan']['PERUSAHAAN_NAMA']}")
        f.write("\n")
        f.write(f"{json_obj['perusahaan']['PERUSAHAAN_ALAMAT']}")
        f.write("\n")
        f.write("\n")
        f.write(str(judul))
        f.write("\n")
        f.write(str(sj))
        f.write("\n")
        f.write("\n")
        f.write(str(ttd))
    do_print(doc_id,selected_printer)
