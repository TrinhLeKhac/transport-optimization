import sys
from pathlib import Path
ROOT_PATH = str(Path(__file__)).split("/supership/final/scripts/")[0] + "/supership/final"

TRONG_SO = {
    'Ngưng giao nhận': {
        'Tiêu chí': 10,
        'Phân loại': {
            'Bình thường': 1,
            'Quá tải': -10,
        },
    },
    'Đánh giá ZNS': {
        'Tiêu chí': 3,
        'Phân loại': {
            'Loại': -10,
            '1 sao & Nhân viên không nhiệt tình': -8,
            'Nhiều hơn 1 lần đánh giá 1 sao': -6,
            'Đánh giá 5 sao trên 95% đơn': 10,
            'Không phát sinh đánh giá 1, 2, 3 sao': 6,
            'Bình thường': 5,
            'Không có thông tin': 5,
        },
    },
    'Tỉ lệ giao hàng': {
        'Tiêu chí': 10,
        'Phân loại': {
            'Tổng đơn hàng từ 30 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%': 10,
            'Tổng đơn hàng từ 20 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%': 9,
            'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%': 8,
            'Tổng đơn hàng từ 30 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%': 8,
            'Tổng đơn hàng từ 20 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%': 7,
            'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%': 6,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 95%': 5,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 90%': 4,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 85%': 3,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 75%': 2,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 50%': 1,
            'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ hoàn từ 25% trở lên': -10,
            'Tổng đơn hàng từ 4 đơn trở lên và có tỷ lệ hoàn từ 50% trở lên': -10,
            'TOP 10 KHU VỰC có số lượng đơn hàng từ 3 đơn trở lên và có tỷ lệ hoàn hơn 20%': -6,
            'Không có thông tin': 5,
            'Trường hợp khác': 5,
        },
    },
    'Chất lượng nội bộ': {
        'Tiêu chí': 2,
        'Phân loại': {
            'ninja_van': {
                'Ti lệ trên 95% và tổng số đơn giao hàng trên 100 đơn': 10,
                'Ti lệ trên 95% và tổng số đơn giao hàng dưới 100 đơn': 9,
                'Ti lệ trên 90% và tổng số đơn giao hàng trên 100 đơn': 8,
                'Ti lệ trên 90% và tổng số đơn giao hàng dưới 100 đơn': 7,
                'Ti lệ dưới 90% và tổng số đơn giao hàng dưới 100 đơn': -2,
                'Ti lệ dưới 90% và tổng số đơn giao hàng trên 100 đơn': -6,
                'Không có thông tin': 5,
            },
           'best': {
                'Tỉ lệ trên 98%': 10,
                'Tỉ lệ trên 95%': 9,
                'Tỉ lệ trên 90%': 8,
                'Tỉ lệ trên 80%': 5,
                'Không có thông tin': 5,
                'Tỉ lệ bé hơn hoặc bằng 80%': -6,
           }
        }
    },
    'Thời gian giao hàng': {
        'Tiêu chí': 10,
        'Phân loại': {
            'Cận Miền': {
                # 72h
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn': 10,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn': 9,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn': 8,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 6,
                # 96h
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # trễ
                'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 3 đơn': -2,
                'Trung bình dưới 120h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -1,
                'Trung bình dưới 144h và tổng số đơn giao hàng lớn hơn 3 đơn': -6,
                'Trung bình dưới 144h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -4,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 144h': -10,
                'Không có thông tin': 5,
            },
            'Nội Miền': {
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 10,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 6,
                # 72h
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # trễ
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 3 đơn': -2,
                'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -1,
                'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 3 đơn': -6,
                'Trung bình dưới 120h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -4,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 120h': -10, 
                'Không có thông tin': 5,
            },
            'Nội Thành Tỉnh': {
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # 72h
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 30 đơn': 9,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn': 8,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn': 6,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn': 4,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 3,
                # trễ
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 3 đơn': -4,
                'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -2,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 96h': -10, 
                'Không có thông tin': 5,
            },
            'Ngoại Thành Tỉnh': {
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # 72h
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 30 đơn': 9,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 20 đơn': 8,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 10 đơn': 6,
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 5 đơn': 4,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 3,
                # trễ
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 3 đơn': -4,
                'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -2,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 96h': -10, 
                'Không có thông tin': 5,
            },
        }
    },
    'Có kho giao nhận': {
        'Tiêu chí': 3,
        'Phân loại': {
            'Có từ 3 bưu cục cùng cấp quận/huyện trở lên': 10,
            'Có 2 bưu cục cùng cấp quận/huyện trở lên': 9,
            'Có bưu cục cùng cấp quận/huyện': 8,
            'Trong tỉnh có trên 80% bưu cục/tổng quận huyện của tỉnh': 6,
            'Trong tỉnh có trên 50% bưu cục/tổng quận huyện của tỉnh': 4,
            'Trong tỉnh có trên 30% bưu cục/tổng quận huyện của tỉnh': 2,
            'Trong tỉnh có bé hơn hoặc bằng 30% bưu cục/tổng quận huyện của tỉnh': 1,
            'Không có thông tin': 5,
            'Không có bưu cục trong tỉnh': -10
        }
    },
}

TIEU_CHI_MAPPING_ID = {
    'Ngưng giao nhận': 1, 
    'Đánh giá ZNS': 2, 
    'Tỉ lệ hoàn hàng': 3, 
    'Chất lượng nội bộ': 4,
    'Thời gian giao hàng': 5,
    'Có kho giao nhận': 6,  
}

MAPPING_ID_NVC = {
    'ninja_van': 7,
    'ghn': 2,
    'best': 6,
    'shopee_express': 10,
    'ghtk':  1,
    'viettel_post': 4,
    'tikinow': 12, 
}

LOAI_VAN_CHUYEN_DICT = {
    'Nội Miền': 'Nội Miền',
    'Nội Miền Đặc Biệt': 'Nội Miền',
    'Liên Miền': 'Cận Miền',
    'Liên Miền Đặc Biệt': 'Cận Miền',
    'Liên Vùng': 'Cận Miền',
    'Nội Tỉnh': 'Ngoại Thành Tỉnh',
    'Nội Thành': 'Nội Thành Tỉnh',
}

LIST_NVC = ['ninja_van', 'ghn', 'best', 'shopee_express', 'ghtk', 'viettel_post', 'tikinow']
STATUS_NVC = [nvc + '_stt' for nvc in LIST_NVC]
SCORE_NVC = [nvc + '_score' for nvc in LIST_NVC]
SELECTED_COLS = [
    'tinh_thanh', 'quan_huyen', 'tieu_chi', 'trong_so', 
    'ninja_van_stt', 'ninja_van_score',
    'ghn_stt', 'ghn_score', 
    'best_stt', 'best_score',
    'shopee_express_stt', 'shopee_express_score', 
    'ghtk_stt', 'ghtk_score', 
    'viettel_post_stt', 'viettel_post_score', 
    'tikinow_stt', 'tikinow_score',
]

