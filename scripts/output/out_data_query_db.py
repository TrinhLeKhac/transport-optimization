import optparse
import sys
from pathlib import Path

ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

from scripts.utilities.helper import *
from scripts.utilities.config import *


def out_data_order_type(carriers=ACTIVE_CARRIER, include_supership=True, show_logs=True):

    if show_logs:
        print('1. Mapping 713 * 713 tỉnh thành, quận huyện gửi/nhận...')
    if include_supership:
        carriers = carriers + ['SuperShip']
    carrier_id_df = pd.DataFrame(data={'carrier_id': [MAPPING_CARRIER_ID[v] for v in carriers]})

    sender_df = PROVINCE_MAPPING_DISTRICT_DF[['province_code', 'district_code']]
    sender_df.columns = ['sender_province_code', 'sender_district_code']

    receiver_df = PROVINCE_MAPPING_DISTRICT_DF[['province_code', 'district_code']]
    receiver_df.columns = ['receiver_province_code', 'receiver_district_code']

    input_df = carrier_id_df.merge(sender_df, how='cross').merge(receiver_df, how='cross')

    if show_logs:
        print('2. Mapping data...')
    order_type_df = create_type_of_delivery(input_df)

    if show_logs:
        print('3. Transform data...')
    order_type_df = order_type_df.rename(columns={'order_type_id': 'new_type', 'sys_order_type_id': 'route_type'})
    order_type_df = order_type_df.reset_index().rename(columns={"index": "id"})
    order_type_df['new_type'] = order_type_df['new_type'].astype(str)
    order_type_df['route_type'] = order_type_df['route_type'].astype(str)
    order_type_df = order_type_df[[
        'id', 'carrier_id', 'sender_province_code', 'sender_district_code',
        'receiver_province_code', 'receiver_district_code',
        'new_type', 'route_type'
    ]]

    if show_logs:
        print('4. Saving data...')
    order_type_df.to_parquet(ROOT_PATH + "/output/data_order_type.parquet", index=False)


def out_data_service_fee():
    print('Xử lý data service_fee...')
    cuoc_phi_df = pd.read_parquet(ROOT_PATH + '/processed_data/cuoc_phi.parquet')
    cuoc_phi_df['order_type_id'] = cuoc_phi_df['order_type'].map(MAPPING_ORDER_TYPE_ID)

    cuoc_phi_df = cuoc_phi_df[['carrier_id', 'lt_or_eq', 'order_type', 'order_type_id', 'service_fee']].rename(
        columns={'lt_or_eq': 'weight', 'order_type_id': 'new_type', 'service_fee': 'price'})
    cuoc_phi_df['new_type'] = cuoc_phi_df['new_type'].astype(str)

    # Add fee lấy tận nơi, gửi bưu cục
    service_fee_df1 = cuoc_phi_df.copy()
    service_fee_df1['pickup'] = '0'

    service_fee_df2 = cuoc_phi_df.copy()
    service_fee_df2['pickup'] = '1'

    service_fee_df = pd.concat([service_fee_df1, service_fee_df2], ignore_index=True)
    service_fee_df.loc[(service_fee_df['pickup'] == '1') & (service_fee_df['carrier_id'] == 7), 'price'] = \
        service_fee_df['price'] + 1500
    service_fee_df.loc[(service_fee_df['pickup'] == '1') & (service_fee_df['carrier_id'] == 2), 'price'] = \
        service_fee_df['price'] + 1000

    service_fee_df = service_fee_df[['carrier_id', 'order_type', 'new_type', 'pickup', 'weight', 'price']]
    service_fee_df.to_parquet(ROOT_PATH + '/output/service_fee.parquet', index=False)
    print('-' * 100)


if __name__ == '__main__':
    parser = optparse.OptionParser(description="Running mode")
    parser.add_option(
        '-m', '--mode',
        action="store", dest="mode",
        help="mode string", default=True
    )
    options, args = parser.parse_args()
    # print(options.mode)

    include_supership = True

    if options.mode == 'init':
        if include_supership:
            print('Out data query_db and assigning SuperShip carrier...')
        else:
            print('Out data query_db...')
        try:
            out_data_order_type(include_supership=include_supership)
            out_data_service_fee()
        except Exception as e:
            error = type(e).__name__ + " – " + str(e)
            telegram_bot_send_error_message(error)
    elif options.mode == 'daily':
        pass
