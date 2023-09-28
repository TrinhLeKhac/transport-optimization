
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *

def convert_datetime_type1(s):
    try:
        result = datetime.strptime(s, "%Y-%d-%m %H:%M:%S")
    except:
        result = None
    return result

def convert_datetime_type2(s):
    try:
        result = datetime.strptime(s, "%Y-%d-%m %H:%M:%S")
    except:
        try:
            result = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except:
            result = None
    return result
    
def xu_ly_giao_dich():
    
    # Đọc thông tin giao dịch nvc best
    print('Xử lý giao dịch BEST...')
    best_df = pd.read_excel(ROOT_PATH + '/raw_data/TỶ LỆ GIAO TRẢ NVC 14.07.2023.xlsx', sheet_name='BEST', converters={'Số Điện Thoại':str})

    # Xử lý data
    best_df.loc[best_df['Có Hàng Đổi Trả'] == '✅', 'Có Hàng Đổi Trả'] = True
    best_df['Có Hàng Đổi Trả'] = best_df['Có Hàng Đổi Trả'].fillna(False)
    best_df['Tạo Lúc'] = pd.to_datetime(best_df['Tạo Lúc'], errors='coerce')
    best_df['Lần Cuối Giao'] = pd.to_datetime(best_df['Lần Cuối Giao'], errors='coerce')
    best_df['Giao lúc'] = pd.to_datetime(best_df['Giao lúc'], errors='coerce')
    best_df.drop('TT', inplace=True, axis=1)
    best_df['Lần Cuối Giao'] = best_df['Lần Cuối Giao'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    best_df['Giao lúc'] = best_df['Giao lúc'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    best_df['Tạo Lúc'] = best_df['Tạo Lúc'].apply(lambda x: str(x)).apply(convert_datetime_type2)
    
    # Đọc thông tin giao dịch nvc ninja van
    print('Xử lý giao dịch NINJA VAN...')
    njv_df = pd.read_excel(ROOT_PATH + '/raw_data/TỶ LỆ GIAO TRẢ NVC 14.07.2023.xlsx', sheet_name='NJV', converters={'Số Điện Thoại':str})

    # Xử lý data
    njv_df.loc[njv_df['Có Hàng Đổi Trả'] == '✅', 'Có Hàng Đổi Trả'] = True
    njv_df['Có Hàng Đổi Trả'] = njv_df['Có Hàng Đổi Trả'].fillna(False)
    njv_df['Tạo Lúc'] = pd.to_datetime(njv_df['Tạo Lúc'], errors='coerce')
    njv_df['Lần Cuối Giao'] = pd.to_datetime(njv_df['Lần Cuối Giao'], errors='coerce')
    njv_df['Giao lúc'] = pd.to_datetime(njv_df['Giao lúc'], errors='coerce')
    njv_df.drop('TT', inplace=True, axis=1)
    njv_df['Giao lúc'] = njv_df['Giao lúc'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    
    # Đọc thông tin giao dịch nvc ghn
    print('Xử lý giao dịch GHN...')
    ghn_df = pd.read_excel(ROOT_PATH + '/raw_data/TỶ LỆ GIAO TRẢ NVC 14.07.2023.xlsx', sheet_name='GHN', converters={'Số Điện Thoại':str})

    # Xử lý data
    ghn_df.loc[ghn_df['Có Hàng Đổi Trả'] == '✅', 'Có Hàng Đổi Trả'] = True
    ghn_df['Có Hàng Đổi Trả'] = ghn_df['Có Hàng Đổi Trả'].fillna(False)
    ghn_df['Tạo Lúc'] = pd.to_datetime(ghn_df['Tạo Lúc'], errors='coerce')
    ghn_df['Lần Cuối Giao'] = pd.to_datetime(ghn_df['Lần Cuối Giao'], errors='coerce')
    ghn_df['Giao lúc'] = pd.to_datetime(ghn_df['Giao lúc'], errors='coerce')
    ghn_df.drop('TT', inplace=True, axis=1)
    ghn_df['Giao lúc'] = ghn_df['Giao lúc'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    
    # Đọc thông tin giao dịch nvc viettel post
    print('Xử lý giao dịch VIETTEL POST...')
    vtp_df = pd.read_excel(ROOT_PATH + '/raw_data/TỶ LỆ GIAO TRẢ NVC 14.07.2023.xlsx', sheet_name='VTP', converters={'Số Điện Thoại':str})

    # Xử lý data
    vtp_df.loc[vtp_df['Có Hàng Đổi Trả'] == '✅', 'Có Hàng Đổi Trả'] = True
    vtp_df['Có Hàng Đổi Trả'] = vtp_df['Có Hàng Đổi Trả'].fillna(False)
    vtp_df['Tạo Lúc'] = pd.to_datetime(vtp_df['Tạo Lúc'], errors='coerce')
    vtp_df['Lần Cuối Giao'] = pd.to_datetime(vtp_df['Lần Cuối Giao'], errors='coerce')
    vtp_df['Giao lúc'] = pd.to_datetime(vtp_df['Giao lúc'], errors='coerce')
    vtp_df.drop('TT', inplace=True, axis=1)
    vtp_df['Giao lúc'] = vtp_df['Giao lúc'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    
    # Đọc thông tin giao dịch nhà vận chuyển shopee express
    print('Xử lý giao dịch SHOPEE EXPRESS...')
    spx_df = pd.read_excel(ROOT_PATH + '/raw_data/TỶ LỆ GIAO TRẢ NVC 14.07.2023.xlsx', sheet_name='SPX', converters={'Số Điện Thoại':str})
    
    # Xử lý data
    spx_df.loc[spx_df['Có Hàng Đổi Trả'] == '✅', 'Có Hàng Đổi Trả'] = True
    spx_df['Có Hàng Đổi Trả'] = spx_df['Có Hàng Đổi Trả'].fillna(False)
    spx_df['Tạo Lúc'] = pd.to_datetime(spx_df['Tạo Lúc'], errors='coerce')
    spx_df['Lần Cuối Giao'] = pd.to_datetime(spx_df['Lần Cuối Giao'], errors='coerce')
    spx_df['Giao lúc'] = pd.to_datetime(spx_df['Giao lúc'], errors='coerce')
    spx_df.drop('TT', inplace=True, axis=1)
    spx_df['Giao lúc'] = spx_df['Giao lúc'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    
    # Đọc thông tin giao dịch nhà vận chuyển ghtk
    print('Xử lý giao dịch GHTK...')
    ghtk_df = pd.read_excel(ROOT_PATH + '/raw_data/TỶ LỆ GIAO TRẢ NVC 14.07.2023.xlsx', sheet_name='GHTK', converters={'Số Điện Thoại':str})

    # Xử lý data
    ghtk_df.loc[ghtk_df['Có Hàng Đổi Trả'] == '✅', 'Có Hàng Đổi Trả'] = True
    ghtk_df['Có Hàng Đổi Trả'] = ghtk_df['Có Hàng Đổi Trả'].fillna(False)
    ghtk_df['Tạo Lúc'] = pd.to_datetime(ghtk_df['Tạo Lúc'], errors='coerce')
    ghtk_df['Lần Cuối Giao'] = pd.to_datetime(ghtk_df['Lần Cuối Giao'], errors='coerce')
    ghtk_df['Giao lúc'] = pd.to_datetime(ghtk_df['Giao lúc'], errors='coerce')
    ghtk_df.drop(['TT', 'Source.Name'], inplace=True, axis=1)
    ghtk_df[['Tạo Lúc', 'Lần Cuối Giao', 'Giao lúc']]
    ghtk_df['Giao lúc'] = ghtk_df['Giao lúc'].apply(lambda x: str(x)).apply(convert_datetime_type1)
    
    # Tổng hợp thông tin giao dịch toàn bộ nhà vận chuyển
    print('Tổng hợp giao dịch...')
    total_df = pd.concat([best_df, njv_df, ghn_df, vtp_df, spx_df, ghtk_df], ignore_index=True)
    total_df['Mã Vận Đơn'] = total_df['Mã Vận Đơn'].astype(str)
    total_df['Mã Lý Do'] = total_df['Mã Lý Do'].astype(str)
    total_df['Mã Đơn Khách Hàng'] = total_df['Mã Đơn Khách Hàng'].astype(str)
    total_df['Tên Người Nhận'] = total_df['Tên Người Nhận'].astype(str)
    total_df['Địa Chỉ Người Nhận'] = total_df['Địa Chỉ Người Nhận'].astype(str)
    total_df.columns=[
        'tao_luc', 'tinh_thanh_lay_hang', 'kho_lay_hang', 'khach_hang', 'ma_don_hang', 'ma_don_ngan',
        'trang_thai', 'nha_van_chuyen', 'ma_van_don', 'trang_thai_van_don', 'tinh_thanh_giao_hang',
        'quan_huyen_giao_hang', 'phuong_xa_giao_hang', 'ly_do', 'ma_ly_do', 'so_lan_giao', 'lan_giao_cuoi',
        'nguoi_giao_hang', 'ma_chuyen_ngoai', 'cap_nhat_luc', 'giao_luc', 'ma_don_khach_hang', 'co_hang_doi_tra',
        'hinh_thuc_gui_hang', 'so_lan_giao_lai', 'ten_nguoi_nhan', 'so_dien_thoai', 'dia_chi_nguoi_nhan'
    ]

    # Lưu thông tin
    print('Lưu thông tin...')
    total_df.to_parquet(ROOT_PATH + '/processed_data/giao_dich_tong.parquet', index=False)
    print('>>> Done')
    
def xu_ly_giao_dich_co_khoi_luong():

    # Đọc thông tin đơn có khối lượng
    print('Xử lý giao dịch có khối lượng...')
    khoi_luong_df = pd.read_excel(ROOT_PATH + '/raw_data/Tổng hợp đơn có khối lượng.xlsx', sheet_name='Combined')

    # Chọn cột cần thiết và đổi tên
    khoi_luong_df = khoi_luong_df.iloc[:, 1:37]
    khoi_luong_df.columns = [
        'ten_shop', 'ma_doi_soat', 'ngay_doi_soat', 'ma_don_khach_hang', 
        'ma_don_supership', 'trang_thai', 'thoi_gian_tao', 'khoi_luong', 
        'thu_ho', 'tri_gia', 'tra_truoc', 'phi_van_chuyen', 'phi_bao_hiem',
        'phi_chuyen_hoan', 'khuyen_mai', 'goi_cuoc', 'tra_phi', 'nguoi_nhan', 
        'dia_chi', 'phuong_xa', 'quan_huyen', 'tinh_thanh', 'ghi_chu', 
        'kho_hang', 'san_pham', 'loai', 'tinh_thanh_gui', 'ma_quan_huyen', 
        'kho_lay_hang', 'kho_giao_hang', 'phi_van_chuyen_goc', 'chuyen_ngoai_tuy_chinh', 
        'phi_tra_hang_doi', 'phi_doi_dia_chi', 'so_lan_gui_tin_zalo', 'hinh_thuc_gui_hang',
    ]

    # Xử lý thông tin
    khoi_luong_df['ma_don_khach_hang'] = khoi_luong_df['ma_don_khach_hang'].astype(str)
    khoi_luong_df['nguoi_nhan'] = khoi_luong_df['nguoi_nhan'].astype(str)
    khoi_luong_df['dia_chi'] = khoi_luong_df['dia_chi'].astype(str)
    khoi_luong_df['san_pham'] = khoi_luong_df['san_pham'].astype(str)

    # Lưu thông tin
    print('Lưu thông tin...')
    khoi_luong_df.to_parquet(ROOT_PATH + '/processed_data/giao_dich_co_khoi_luong.parquet', index=False)
    print('>>> Done')
    
def tong_hop_thong_tin_giao_dich():

    # Đọc thông tin giao dịch và giao dịch có khối lượng đã xử lý
    print('Đọc thông tin giao dịch và giao dịch có khối lượng...')
    giao_dich_tong = pd.read_parquet(ROOT_PATH + '/processed_data/giao_dich_tong.parquet')
    giao_dich_khoi_luong = pd.read_parquet(ROOT_PATH + '/processed_data/giao_dich_co_khoi_luong.parquet')

    # chọn đơn hàng hợp lệ
    print('Lọc đơn hàng hợp lệ...')
    don_hang = (
        set(giao_dich_tong['ma_don_hang'].tolist())
        .intersection(
            set(giao_dich_khoi_luong['ma_don_supership'].tolist()))
    )

    # lọc lấy giao dịch hợp lệ
    giao_dich_tong_filter = giao_dich_tong[giao_dich_tong['ma_don_hang'].isin(don_hang)]
    giao_dich_khoi_luong_filter = giao_dich_khoi_luong[giao_dich_khoi_luong['ma_don_supership'].isin(don_hang)]
    
    giao_dich_valid = giao_dich_tong_filter[[
        'tao_luc',
        'ma_don_hang', 
        'khach_hang', 
        'nha_van_chuyen', 
        'trang_thai_van_don',
        'tinh_thanh_giao_hang',
        'quan_huyen_giao_hang',
        'ly_do',
        'so_lan_giao',
        'lan_giao_cuoi',
        'ma_chuyen_ngoai',
        'giao_luc',
        'co_hang_doi_tra',
        'hinh_thuc_gui_hang',
        'so_lan_giao_lai'
    ]].merge(
        giao_dich_khoi_luong_filter[[
            'ma_don_supership',
            'thoi_gian_tao',
            'khoi_luong',
            'thu_ho',
            'tri_gia',
            'tra_truoc',
            'phi_van_chuyen',
            'phi_van_chuyen_goc',
            'phi_doi_dia_chi',
            'phi_bao_hiem',
            'phi_chuyen_hoan',
            'khuyen_mai',
            'goi_cuoc',
            'kho_hang',
            'loai',
            'kho_lay_hang',
            'kho_giao_hang',
            'so_lan_gui_tin_zalo',
        ]].rename(columns={'ma_don_supership': 'ma_don_hang'}), on='ma_don_hang', how='inner'
    )

    # Tách địa chỉ từ kho hàng
    giao_dich_valid['tinh_thanh_lay_hang'] = giao_dich_valid['kho_hang'].str.split(', ').str[-1]
    giao_dich_valid['quan_huyen_lay_hang'] = giao_dich_valid['kho_hang'].str.split(', ').str[-2]

    # Chuẩn hóa thông tin quận/huyện, tỉnh/thành
    print('Chuẩn hóa thông tin tỉnh/thành, quận/huyện lấy hàng...')
    giao_dich_valid = normalize_province_district(giao_dich_valid, tinh_thanh='tinh_thanh_lay_hang', quan_huyen='quan_huyen_lay_hang')
    
    print('Chuẩn hóa thông tin tỉnh/thành, quận/huyện giao hàng...')
    giao_dich_valid = normalize_province_district(giao_dich_valid, tinh_thanh='tinh_thanh_giao_hang', quan_huyen='quan_huyen_giao_hang')

    # Lưu thông tin giao dịch
    print('Lưu thông tin...')
    giao_dich_valid.to_parquet(ROOT_PATH + '/processed_data/giao_dich_combine_valid.parquet', index=False)