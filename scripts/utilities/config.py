from pathlib import Path
ROOT_PATH = str(Path(__file__).parent.parent.parent)

TRONG_SO = {
    'Ngưng giao nhận': {
        'Tiêu chí': 20,
        'Phân loại': {
            'Bình thường': 0,
            'Quá tải': -10,
        },
    },
    'Đánh giá ZNS': {
        'Tiêu chí': 6,
        'Phân loại': {
            'Loại': -10,
            '1 sao & Đánh giá xấu': -10,
            'Nhiều hơn 1 lần đánh giá 1 sao': -8,
            'Đánh giá 5 sao trên 95% đơn': 9,
            'Không phát sinh đánh giá 1, 2, 3 sao': 8,
            'Bình thường': 4,
            'Không có thông tin': 0,
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
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 85%': 1,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 75%': -2,
            'Tổng đơn hàng từ 5 đơn trở lên và có tỷ lệ giao hàng thành công trên 50%': -5,
            'Tổng đơn hàng từ 10 đơn trở lên và có tỷ lệ hoàn từ 25% trở lên': -10,
            'Tổng đơn hàng từ 4 đơn trở lên và có tỷ lệ hoàn từ 50% trở lên': -10,
            'TOP 10 KHU VỰC có số lượng đơn hàng từ 3 đơn trở lên và có tỷ lệ hoàn hơn 20%': -8,
            'Không có thông tin': 0,
            'Trường hợp khác': 4,
        },
    },
    'Chất lượng nội bộ': {
        'Tiêu chí': 3,
        'Phân loại': {
            'Ninja Van': {
                'Ti lệ trên 98% và tổng số đơn giao hàng trên 100 đơn': 10,
                'Ti lệ trên 98% và tổng số đơn giao hàng dưới 100 đơn': 8,
                'Ti lệ trên 94% và tổng số đơn giao hàng trên 100 đơn': 6,
                'Ti lệ trên 94% và tổng số đơn giao hàng dưới 100 đơn': 3,
                'Ti lệ trên 91% và tổng số đơn giao hàng dưới 100 đơn': -1,
                'Ti lệ trên 91% và tổng số đơn giao hàng trên 100 đơn': -2,
                'Ti lệ dưới 91% và tổng số đơn giao hàng dưới 100 đơn': -3,
                'Ti lệ dưới 91% và tổng số đơn giao hàng trên 100 đơn': -6,
                'Không có thông tin': 0,
            },
        }
    },
    'Thời gian giao hàng': {
        'Tiêu chí': 2,
        'Phân loại': {
            'Cách Miền': {
                # 96h
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 20 đơn': 10,
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 10 đơn': 9,
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 5 đơn': 8,
                'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 6,
                # 120h
                'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 120h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 120h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # trễ
                'Trung bình dưới 144h và tổng số đơn giao hàng lớn hơn 3 đơn': -2,
                'Trung bình dưới 144h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -1,
                'Trung bình dưới 168h và tổng số đơn giao hàng lớn hơn 3 đơn': -6,
                'Trung bình dưới 168h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -4,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 168h': -10,
                'Không có thông tin': 0,
            },
            'Liên Miền Đặc Biệt': {
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
                'Không có thông tin': 0,
            },
            'Liên Miền Tp.HCM - HN': {
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
                'Không có thông tin': 0,
            },
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
                'Không có thông tin': 0,
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
                'Không có thông tin': 0,
            },
            'Nội Miền Tp.HCM - HN': {
                # 24h
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 20 đơn': 10,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 10 đơn': 9,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 5 đơn': 8,
                'Trung bình dưới 24h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 6,
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # trễ
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 3 đơn': -2,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -1,
                'Trung bình dưới 96h và tổng số đơn giao hàng lớn hơn 3 đơn': -6,
                'Trung bình dưới 96h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -4,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 96h': -10,
                'Không có thông tin': 0,
            },
            'Nội Thành Tỉnh': {
                # 24h
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 24h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 4,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 3,
                # trễ
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 3 đơn': -4,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -2,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 72h': -10,
                'Không có thông tin': 0,
            },
            'Nội Thành Tp.HCM - HN': {
                # 24h
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 24h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 4,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 3,
                # trễ
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 3 đơn': -4,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -2,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 72h': -10,
                'Không có thông tin': 0,
            },
            'Ngoại Thành Tỉnh': {
                # 24h
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 24h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 4,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 3,
                # trễ
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 3 đơn': -4,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -2,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 72h': -10,
                'Không có thông tin': 0,
            },
            'Ngoại Thành Tp.HCM - HN': {
                # 24h
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 30 đơn': 10,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 20 đơn': 9,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 10 đơn': 8,
                'Trung bình dưới 24h và tổng số đơn giao hàng lớn hơn 5 đơn': 6,
                'Trung bình dưới 24h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 4,
                # 48h
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 30 đơn': 9,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 20 đơn': 8,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 10 đơn': 6,
                'Trung bình dưới 48h và tổng số đơn giao hàng lớn hơn 5 đơn': 4,
                'Trung bình dưới 48h và tổng số đơn giao hàng bé hơn hoặc bằng 5 đơn': 3,
                # trễ
                'Trung bình dưới 72h và tổng số đơn giao hàng lớn hơn 3 đơn': -4,
                'Trung bình dưới 72h và tổng số đơn giao hàng bé hơn hoặc bằng 3 đơn': -2,
                'Trung bình thời gian giao hàng lớn hơn hoặc bằng 72h': -10,
                'Không có thông tin': 0,
            },
        }
    },
    'Có kho giao nhận': {
        'Tiêu chí': 4,
        'Phân loại': {
            'Có từ 3 bưu cục cùng cấp quận/huyện trở lên': 10,
            'Có 2 bưu cục cùng cấp quận/huyện trở lên': 9,
            'Có bưu cục cùng cấp quận/huyện': 8,
            'Trong tỉnh có trên 80% bưu cục/tổng quận huyện của tỉnh': 6,
            'Trong tỉnh có trên 50% bưu cục/tổng quận huyện của tỉnh': 4,
            'Trong tỉnh có trên 30% bưu cục/tổng quận huyện của tỉnh': 2,
            'Trong tỉnh có bé hơn hoặc bằng 30% bưu cục/tổng quận huyện của tỉnh': 1,
            'Không có thông tin': 0,
            'Không có bưu cục trong tỉnh': -50
        }
    },
}

MAPPING_TIEU_CHI_ID = {
    'Ngưng giao nhận': 1, 
    'Đánh giá ZNS': 2, 
    'Tỉ lệ giao hàng': 3,
    'Chất lượng nội bộ': 4,
    'Thời gian giao hàng': 5,
    'Có kho giao nhận': 6,  
}

MAPPING_ORDER_TYPE_ID = {
    'Nội Thành Tỉnh': 1,
    'Ngoại Thành Tỉnh': 2,
    'Nội Thành Tp.HCM - HN': 3,
    'Ngoại Thành Tp.HCM - HN': 4,
    'Nội Miền': 5,
    'Cận Miền': 6,
    'Cách Miền': 7,
    'Nội Miền Tp.HCM - HN': 8,
    'Liên Miền Tp.HCM - HN': 9,
    'Liên Miền Đặc Biệt': 10,
}

MAPPING_ORDER_TYPE_ID_ROUTE_TYPE = {
    1: 5,
    2: 5,
    3: 1,
    4: 1,
    5: 6,
    6: 7,
    7: 7,
    8: 3,
    9: 4,
    10: 2
}

OVERLOADING_SCORE_DICT = {
    'Ngưng giao nhận': [-10],
    'Đánh giá ZNS': [-8, -10],
    'Tỉ lệ giao hàng': [-10],
    'Chất lượng nội bộ': [-6],
    'Thời gian giao hàng': [-10],
    'Có kho giao nhận': [-50]
}

ACTIVE_CARRIER = [
    # 'GHTK',
    'GHN',
    'Viettel Post',
    'BEST Express',
    'Ninja Van',
    'SPX Express'
]
MAPPING_CARRIER_ID = {
    'GHTK': 1,
    'GHN': 2,
    'J&T Express': 3,
    'Viettel Post': 4,
    'VNPost':  5,
    'BEST Express': 6,
    'Ninja Van': 7,
    'Snappy Express': 8,
    'ZTO Express': 9,
    'SPX Express': 10,
    'NETCO Post': 11,
    'TikiNOW Smart Logistics': 12,
    'SuperShip': 13,
}

THOI_GIAN_GIAO_HANG_DEFAULT = {
    'Nội Thành Tỉnh': '1.75 - 2.25 ngày',
    'Ngoại Thành Tỉnh': '1.75 - 2.25 ngày',
    'Nội Thành Tp.HCM - HN': '1.75 - 2.25 ngày',
    'Ngoại Thành Tp.HCM - HN': '1.75 - 2.25 ngày',
    'Nội Miền Tp.HCM - HN': '0.75 - 1.25 ngày',
    'Nội Miền': '1.75 - 2.25 ngày',
    'Cận Miền': '2.75 - 3.25 ngày',
    'Liên Miền Tp.HCM - HN': '2.75 - 3.25 ngày',
    'Liên Miền Đặc Biệt': '2.75 - 3.25 ngày',
    'Cách Miền': '3.75 - 4.25 ngày',
}

MAPPING_ID_CARRIER = {}
for carrier, id in MAPPING_CARRIER_ID.items():
    MAPPING_ID_CARRIER[id] = carrier

CUSTOMER_BEST_CARRIER_DEFAULT = 'BEST Express'
PARTNER_BEST_CARRIER_DEFAULT = 'BEST Express'

CHUA_GIAO_STATUS = [
    'Xuất hàng khỏi trung tâm khai thác (trung tâm chia chọn)',
    'Trọng lượng bưu kiện',
    'Giao hàng không thành công',
    'Đến nơi sắp xếp hàng',
    'Đang trung chuyển',
    'Nhận hàng vào trung tâm khai thác (trung tâm chia chọn)',
    'Đang chờ lên lịch lại',
    'Nhận hàng vào bưu cục phát hàng',
    'In Transit | Đang vận chuyển',
    'Nhập kho',
    'Đóng bảng kê đi',
    'Nhận bảng kê đến',
    'Lần đầu tiên giao hàng thất bại',
    'Tồn - Khách hàng nghỉ, không có nhà',
    'Nhận từ bưu tá - Bưu cục gốc',
    'Chờ xác nhận giao lại',
    'Xuất hàng đến trung tâm khai thác (trung tâm chia chọn)',
    'Lấy hàng thành công',
    'Tồn - Khách hàng đến bưu cục nhận',
    'Phát tiếp',
    'Trên các phương tiện cho giao hàng (RTS)',
    'Sửa phiếu gửi',
    'On Hold | Chờ giao lại',
    'Chuyển tiếp bưu cục khác',
    'Đang tương tác với người nhận',
    'Đến Khu Phân Loại Hàng',
]
DANG_GIAO_STATUS = [
    'Xuất hàng để đi giao',
    'Giao bưu tá đi phát',
    'Trên xe để giao hàng',
    'Đang giao hàng',
]
HOAN_HANG_STATUS = [
    'Trả hàng thành công',
    'Trả lại cho người gửi',
    'Returned | Trả hàng thành công',
    'Trả lại cho người gửi được kích hoạt',
    'xuất hàng khỏi trung tâm khai thác (trung tâm chia chọn) để trả về',
    'Hoàn hàng thành công',
    'Returning | Đang trả hàng',
    'Thành công - Chuyển trả người gửi',
    'Tồn - Thông báo chuyển hoàn bưu cục gốc',
    'Nhận hàng vào trung tâm khai thác (trung tâm chia chọn) để trả về',
    'Chuyển hoàn',
    'Xuất hàng khỏi bưu cục phát để trả về',
    'Đang trung chuyển hàng hoàn',
    'Chuyển hoàn bưu cục gốc',
    'Nhận hàng vào bưu cục trả hàng',
    'Đang hoàn hàng',
    'Bưu cục phát duyệt hoàn',
    'Xác nhận chuyển hoàn',
]
THANH_CONG_STATUS = [
    'Giao hàng thành công',
    'Đã hoàn thành',
    'Thành công - Phát thành công',
    'Delivered | Giao hàng thành công',
]
THAT_LAC_STATUS = [
    'Thất lạc',
    'Hàng thất lạc',
]
KHONG_XET_STATUS = [
    'Hủy đơn',
    'Đã hủy',
    'Đơn huỷ',
    'Chờ lấy hàng',
]