from datetime import datetime

def konversi_tanggal(tanggal_str):
    bulan_dict = {
        "01": "Januari", "02": "Februari", "03": "Maret", "04": "April",
        "05": "Mei", "06": "Juni", "07": "Juli", "08": "Agustus",
        "09": "September", "10": "Oktober", "11": "November", "12": "Desember"
    }
    
    # Parsing string tanggal menjadi objek datetime
    tanggal = datetime.strptime(tanggal_str, "%Y-%m-%d")
    
    # Mengambil bagian hari, bulan, dan tahun
    hari = tanggal.strftime("%d")
    bulan = bulan_dict[tanggal.strftime("%m")]
    tahun = tanggal.strftime("%Y")
    
    # Menggabungkan hasil
    return f"{hari} {bulan} {tahun}"