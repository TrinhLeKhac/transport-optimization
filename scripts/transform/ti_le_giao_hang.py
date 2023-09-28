
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent)

from config import *
from helper import *
        
def transform_data_ti_le_giao_hang():

    # Đọc thông tin giao dịch valid
    giao_dich_valid = pd.read_parquet(ROOT_PATH + '/processed_data/giao_dich_combine_valid.parquet')

    # Transform data hoàn hàng
    hoan_hang = giao_dich_valid[giao_dich_valid['trang_thai_van_don'].isin([
        'Trả hàng thành công',
        'Trả lại cho người gửi',
        'Returned | Trả hàng thành công',
        'Hoàn hàng thành công',
        'Đã đối soát công nợ trả hàng',
        'Thành công - Chuyển trả người gửi'
    ])][['nha_van_chuyen', 'tinh_thanh_giao_hang', 'quan_huyen_giao_hang']]
    hoan_hang.columns = ['nha_van_chuyen', 'tinh_thanh', 'quan_huyen']
    hoan_hang['nha_van_chuyen'] = hoan_hang['nha_van_chuyen'].map({
        'BEST Express': 'best',
        'Ninja Van': 'ninja_van',
        'GHN': 'ghn',
        'Shopee Express': 'shopee_express',
        'Viettel Post': 'viettel_post',
        'GHTK': 'ghtk',
        'TikiNow':'tikinow', 
    })
    hoan_hang['cnt'] = 1
    hoan_hang = pd.pivot_table(
        data=hoan_hang, 
        index=['tinh_thanh', 'quan_huyen'], 
        columns=['nha_van_chuyen'], 
        values='cnt',
        aggfunc=np.sum,
        fill_value=0
    ).rename_axis(None, axis=1)#.reset_index()

    for c in ['ninja_van', 'ghn', 'best', 'shopee_express', 'ghtk', 'viettel_post', 'tikinow']:
        if c not in hoan_hang.columns.tolist():
            hoan_hang[c] = 0
    hoan_hang.columns = [c + '_hoan_hang' for c in hoan_hang.columns]

    # Check logic transform data hoàn hàng
    assert giao_dich_valid[giao_dich_valid['trang_thai_van_don'].isin([
        'Trả hàng thành công',
        'Trả lại cho người gửi',
        'Returned | Trả hàng thành công',
        'Hoàn hàng thành công',
        'Đã đối soát công nợ trả hàng',
        'Thành công - Chuyển trả người gửi'
    ])].shape[0] == hoan_hang.sum().sum(), 'Transform data không chính xác'

    # Transform data giao dịch tổng
    tong_don = giao_dich_valid[['nha_van_chuyen', 'tinh_thanh_giao_hang', 'quan_huyen_giao_hang']]
    tong_don.columns = ['nha_van_chuyen', 'tinh_thanh', 'quan_huyen']
    tong_don['nha_van_chuyen'] = tong_don['nha_van_chuyen'].map({
        'BEST Express': 'best',
        'Ninja Van': 'ninja_van',
        'GHN': 'ghn',
        'Shopee Express': 'shopee_express',
        'Viettel Post': 'viettel_post',
        'GHTK': 'ghtk',
        'TikiNow':'tikinow', 
    })
    tong_don['cnt'] = 1
    tong_don = pd.pivot_table(
        data=tong_don, 
        index=['tinh_thanh', 'quan_huyen'], 
        columns=['nha_van_chuyen'], 
        values='cnt',
        aggfunc=np.sum,
        fill_value=0
    ).rename_axis(None, axis=1)#.reset_index()
    for c in ['ninja_van', 'ghn', 'best', 'shopee_express', 'ghtk', 'viettel_post', 'tikinow']:
        if c not in tong_don.columns.tolist():
            tong_don[c] = 0
    tong_don.columns = [c + '_tong_don' for c in tong_don.columns]

    # Check logic transform data giao dịch tổng
    assert giao_dich_valid.shape[0] == tong_don.sum().sum(), 'Transform data không chính xác'
    
    # Tính toán tỉ lệ giao hàng
    ti_le_giao_hang = tong_don.join(hoan_hang).fillna(0).astype(int).reset_index()
    ti_le_giao_hang = ti_le_giao_hang[[
        'tinh_thanh', 'quan_huyen',
        'best_hoan_hang', 'best_tong_don', 
        'ghn_hoan_hang', 'ghn_tong_don', 
        'ninja_van_hoan_hang', 'ninja_van_tong_don', 
        'shopee_express_hoan_hang', 'shopee_express_tong_don', 
        'viettel_post_hoan_hang', 'viettel_post_tong_don',
        'ghtk_hoan_hang', 'ghtk_tong_don',
        'tikinow_hoan_hang', 'tikinow_tong_don'
    ]]
    
    for col in LIST_NVC:
        # tỉ lệ giao thành công
        ti_le_giao_hang[col] = 1 - ti_le_giao_hang[col + '_hoan_hang']/ti_le_giao_hang[col + '_tong_don'] 
        ti_le_giao_hang[col] = ti_le_giao_hang[col].fillna(-4) # không phát sinh đơn hàng
        
        # Tiêu chí loại 1
        condition1 = (
            (
                (ti_le_giao_hang[col + '_tong_don'] >= 10) & 
                (1 - ti_le_giao_hang[col] >= 0.25)
            )
        )
        # Tiêu chí loại 2
        condition2 = (
            (
                (ti_le_giao_hang[col + '_tong_don'] >= 4) & 
                (1 - ti_le_giao_hang[col] >= 0.5)
            )
        )
        ti_le_giao_hang.loc[condition1, col] = -1 # loại theo tiêu chí 1
        ti_le_giao_hang.loc[condition2, col] = -2 # loại theo tiêu chí 2
        
    # Tiêu chí loại top 10 khu vực có số đơn hàng >= 3 đơn + tỷ lệ hoàn > 20% 
    # (top 10 chọn theo tiêu chí tổng đơn + tỉ lệ giao hàng thành công)
    for col in LIST_NVC:
        sort_df = ti_le_giao_hang.sort_values([col + '_tong_don', col], ascending=[False, True])[[col + '_tong_don', col]]
        filter_df = sort_df.loc[
            ~sort_df[col].isin([-1, -2, -4]) &
            ((1 - sort_df[col]) > 0.2) &
            (sort_df[col + '_tong_don'] >= 3)
        ]
        if len(filter_df) > 0:
            # top 10 index có tỉ lệ giao hàng thành công(cột col) nhỏ nhất(khác -1) + số đơn hàng >= 3 đơn + tỷ lệ hoàn > 20% 
            top10_idx = filter_df.index.tolist()[:10] 
        
            # ngưỡng tỉ lệ giao hàng thành công cần loại
            value = filter_df.loc[top10_idx[-1], col]
            
            # loại bằng cách gắn cho value giá trị -1 nếu số đơn hàng >= 3 đơn + tỉ lệ hoàn > 20% 
            # và tỉ lệ giao hàng thành công <= ngưỡng
            ti_le_giao_hang.loc[
                ~ti_le_giao_hang[col].isin([-1, -2, -4]) &
                (ti_le_giao_hang[col] <= value) &
                ((1 - ti_le_giao_hang[col]) > 0.2) &
                (ti_le_giao_hang[col + '_tong_don'] >= 3), 
                col
            ] = -3 # Loại theo tiêu chí 3

    # Xử lý score và status
    for col in LIST_NVC:
        ti_le_giao_hang[col + '_stt'] = (
            ti_le_giao_hang[[col + '_tong_don', col]]
            .apply(lambda x: score_ti_le_giao_hang(x[col + '_tong_don'], x[col]), axis=1)
        )
        ti_le_giao_hang[col + '_score'] = ti_le_giao_hang[col + '_stt'].map(TRONG_SO['Tỉ lệ giao hàng']['Phân loại'])
    
    for col in LIST_NVC:
        ti_le_giao_hang[col + '_stt'] = (
            ti_le_giao_hang[[col + '_tong_don', col]]
            .rename(columns={col + '_tong_don': 'tong_don', col: 'ti_le_giao_thanh_cong'})
            .to_dict(orient='records') 
        )
        
    ti_le_giao_hang['tieu_chi'] = 'Tỉ lệ giao hàng'
    ti_le_giao_hang['trong_so'] = TRONG_SO['Tỉ lệ giao hàng']['Tiêu chí']
    ti_le_giao_hang = ti_le_giao_hang[SELECTED_COLS]

    # Check data tỉ lệ giao hàng
    assert ti_le_giao_hang.isna().sum().all() == 0, 'Transform data không chính xác'

    return ti_le_giao_hang
    # Lưu thông tin giao dịch
    # ti_le_giao_hang.to_parquet('../../output/ti_le_giao_hang.parquet', index=False)