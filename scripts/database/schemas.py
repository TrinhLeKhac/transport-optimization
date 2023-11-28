from sqlalchemy.types import NUMERIC, SMALLINT, INTEGER, VARCHAR, Boolean, TEXT, TIMESTAMP

TABLE_SCHEMA = {
    # 1. Table from API
    'zns': {
        "receiver_province": VARCHAR(length=30),
        "receiver_district": VARCHAR(length=30),
        "carrier_id": SMALLINT,
        "message_count": INTEGER,
        "star": INTEGER,
        "feedbacks": "TEXT []",
        "note": VARCHAR(length=100),
        "submitted_at": VARCHAR(length=20),
        "date": VARCHAR(length=10),
    },
    'order': {
        "order_code": VARCHAR(length=30),
        "created_at": VARCHAR(length=20),
        "sent_at": VARCHAR(length=20),
        "order_status": VARCHAR(length=30),
        "carrier_id": SMALLINT,
        "carrier_status": VARCHAR(length=30),
        "sender_province": VARCHAR(length=30),
        "sender_district":VARCHAR(length=30),
        "receiver_province": VARCHAR(length=30),
        "receiver_district": VARCHAR(length=30),
        "delivery_count": INTEGER,
        "pickup": VARCHAR(length=1),
        "barter": VARCHAR(length=1),
        "carrier_delivered_at": VARCHAR(length=20),
        "picked_at": VARCHAR(length=20),
        "last_delivering_at": VARCHAR(length=20),
        "carrier_updated_at": VARCHAR(length=20),
        "date": VARCHAR(length=10),
    },
    # 2. Table ingest from processing Excel data
    'buu_cuc_best': {
        'receiver_province': VARCHAR(length=30),
        'receiver_district': VARCHAR(length=30),
        'n_post_offices': SMALLINT,
        "import_time": TIMESTAMP,
    },
    'buu_cuc_ghn': {
        'receiver_province': VARCHAR(length=30),
        'receiver_district': VARCHAR(length=30),
        'n_post_offices': SMALLINT,
        "import_time": TIMESTAMP,
    },
    'buu_cuc_ghtk': {
        'receiver_province': VARCHAR(length=30),
        'receiver_district': VARCHAR(length=30),
        'n_post_offices': SMALLINT,
        "import_time": TIMESTAMP,
    },
    'buu_cuc_ninja_van': {
        'receiver_province': VARCHAR(length=30),
        'receiver_district': VARCHAR(length=30),
        'n_post_offices': SMALLINT,
        "import_time": TIMESTAMP,
    },
    'chat_luong_noi_bo_njv': {
        'receiver_province': VARCHAR(length=30),
        'receiver_district': VARCHAR(length=30),
        "njv_post_office": VARCHAR(length=100),
        "delivery_success_rate": NUMERIC(3, 2),
        "is_more_than_100": Boolean,
        "import_time": TIMESTAMP,
    },
    'ngung_giao_nhan': {
        "receiver_province": VARCHAR(length=30),
        "receiver_district": VARCHAR(length=30),
        "carrier": VARCHAR(length=20),
        "status": VARCHAR(length=30),
        "import_time": TIMESTAMP,
    },
    'phan_vung_nvc': {
        "carrier": VARCHAR(length=20),
        "receiver_province": VARCHAR(length=30),
        "receiver_district": VARCHAR(length=30),
        "outer_region": VARCHAR(length=30),
        "inner_region": VARCHAR(length=30),
        "import_time": TIMESTAMP,
    },
    'order_type': {
        'id': INTEGER,
        'carrier_id': SMALLINT,
        'sender_province_code': VARCHAR(length=2),
        'sender_district_code': VARCHAR(length=3),
        'receiver_province_code': VARCHAR(length=2),
        'receiver_district_code': VARCHAR(length=3),
        'new_type': VARCHAR(length=1),
        'route_type': VARCHAR(length=1),
    },
    'service_fee': {
        'carrier_id': SMALLINT,
        'new_type': VARCHAR(length=1),
        'pickup': VARCHAR(length=1),
        'weight': INTEGER,
        'service_fee': INTEGER,
    },
    'data_api': {
        'id': INTEGER,
        'receiver_province_code': VARCHAR(length=2),
        'receiver_district_code': VARCHAR(length=3),
        'carrier_id': SMALLINT,
        'new_type': VARCHAR(length=1),
        'status': SMALLINT,
        'description': VARCHAR(length=200),
        'time_data': NUMERIC(5, 2),
        'time_display': VARCHAR(length=30),
        'speed_ranking': SMALLINT,
        'score_ranking': SMALLINT,
        'for_shop': SMALLINT,
        "total_order": SMALLINT,
        'rate_ranking': SMALLINT,
        'rate': NUMERIC(5, 2),
        "score": NUMERIC(3, 2),
        "star": NUMERIC(2, 1),
        "import_date": VARCHAR(length=10),
    },
    'data_api_full': {
        'id': INTEGER,
        'receiver_province_code': VARCHAR(length=2),
        "receiver_province": VARCHAR(length=30),
        'receiver_district_code': VARCHAR(length=3),
        "receiver_district": VARCHAR(length=30),
        'carrier_id': SMALLINT,
        "carrier": VARCHAR(length=20),
        'new_type': SMALLINT,
        "order_type": VARCHAR(length=30),
        'status': SMALLINT,
        'description': VARCHAR(length=200),
        'time_data': NUMERIC(5, 2),
        'time_display': VARCHAR(length=30),
        'speed_ranking': SMALLINT,
        'score_ranking': SMALLINT,
        'for_shop': SMALLINT,
        'shop_best_carrier': VARCHAR(length=20),
        "total_order": SMALLINT,
        'rate_ranking': SMALLINT,
        'rate': NUMERIC(5, 2),
        "score": NUMERIC(3, 2),
        "star": NUMERIC(2, 1),
        "import_date": VARCHAR(length=10),
    },
    'data_check_output': {
        'id': INTEGER,
        'order_code': VARCHAR(length=30),
        'sender_province_code': VARCHAR(length=2),
        "sender_province": VARCHAR(length=30),
        'sender_district_code': VARCHAR(length=3),
        "sender_district": VARCHAR(length=30),
        'receiver_province_code': VARCHAR(length=2),
        "receiver_province": VARCHAR(length=30),
        'receiver_district_code': VARCHAR(length=3),
        "receiver_district": VARCHAR(length=30),
        'carrier_id': SMALLINT,
        "carrier": VARCHAR(length=20),
        'new_type': SMALLINT,
        "order_type": VARCHAR(length=30),
        'route_type': SMALLINT,
        "weight": INTEGER,
        'price': INTEGER,
        'pickup_type': VARCHAR(length=30),
        'status': SMALLINT,
        'description': VARCHAR(length=200),
        'time_data': NUMERIC(5, 2),
        'time_display': VARCHAR(length=30),
        'rate_ranking': SMALLINT,
        'rate': NUMERIC(5, 2),
        'for_shop': SMALLINT,
        'shop_best_carrier': VARCHAR(length=20),
        'for_partner': SMALLINT,
        'partner_best_carrier': VARCHAR(length=20),
        'price_ranking': SMALLINT,
        'speed_ranking': SMALLINT,
        'score_ranking': SMALLINT,
        "score": NUMERIC(3, 2),
        "star": NUMERIC(2, 1),
        "import_date": VARCHAR(length=10),
    },
}
