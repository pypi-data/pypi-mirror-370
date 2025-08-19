import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests

from netiob.settings import *
from netiob.utils.preprocessors import *

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

max_workers = MAX_WORKERS or min(8, int((os.cpu_count() or 1) * 0.75))
logger.info(f"Max available workers are {max_workers}/{int((os.cpu_count() or 1))}")


def check_net_iob_server_is_live():
    try:
        url = OREF0_API_SERVER_URL
        response = requests.get(url)
        return response.status_code == 200
    except Exception as ex:
        logger.error(f"NetIOB API is not available {ex.__str__()}")
        raise


def get_net_iob(pumphistory, profile, clock, autosens=None, pumphistory24=None):
    try:
        url = f'{OREF0_API_SERVER_URL}/iob'
        data = {
            "history": pumphistory,
            "profile": profile,
            "clock": clock,
            "autosens": autosens,
            "history24": pumphistory24
        }
        response = requests.post(url, json=data)
        return response.json()
    except Exception as ex:
        logger.error(f"NetIOB API is not available {ex.__str__()}")
        raise


def calculate_net_iob(insulin_df: pd.DataFrame):
    if not check_net_iob_server_is_live():
        logger.error(f"NetIOB API is not available")
        raise Exception(f"NetIOB API is not available")

    logger.info('[calculate_net_iob] NetIOB API is available, calculating...')

    insulin_df.fillna(0, inplace=True)
    insulin_df = insulin_df.round(2)

    basal_ins_subtypes = ['basal', 'basal_chunk']
    bolus_ins_subtypes = ['normal', 'extended']

    insulin_data = insulin_df
    basal_records = insulin_data[insulin_data['FACAT'] == 'BASAL']
    basal_rate_profile, profile = avg_basal_rate(basal_records)

    interval = timedelta(minutes=5)
    start_time = insulin_data['FADTC'].astype(str).min()
    end_time = insulin_data['FADTC'].astype(str).max()
    time_range = pd.date_range(start=start_time, end=end_time, freq=interval)

    main_basal_insulin_records = basal_records[basal_records['FATEST'] == 'BASAL INSULIN']
    basal_with_duration = compute_basal_duration(main_basal_insulin_records)[['FADTC', 'FASTRESN', 'DURATION']]

    def process_time(time):
        time_zoned_iso = datetime_to_zoned_iso(time, '+00:00')
        last_xhr_records = get_last_x_hr(insulin_data, time, 24)
        pumphistory_data = []

        for _, row in last_xhr_records.iterrows():
            timestamp = datetime_to_zoned_iso(pd.to_datetime(row['FADTC']), '+00:00')

            if row['FATEST'] == 'BASAL INSULIN' and row['INSSTYPE'] in basal_ins_subtypes:
                duration = basal_with_duration.loc[basal_with_duration['FADTC'] == row['FADTC'], 'DURATION']
                duration = duration.iloc[0] if not duration.empty else 0
                duration = 0 if np.isnan(duration) else duration

                pumphistory_data.append(
                    {"timestamp": timestamp, "_type": "TempBasalDuration", "duration (min)": duration})
                pumphistory_data.append(
                    {"timestamp": timestamp, "_type": "TempBasal", "temp": "absolute", "rate": row['FASTRESN']})

            elif row['FATEST'] == 'BOLUS INSULIN' and row['INSSTYPE'] in bolus_ins_subtypes:
                pumphistory_data.append({"timestamp": timestamp, "_type": "Bolus", "amount": row['INSNMBOL'],
                                         "programmed": row['INSNMBOL'], "unabsorbed": 0, "duration": 0})
                if row['INSSTYPE'] == 'extended':
                    # Append the normal bolus amount first
                    pumphistory_data.append({"timestamp": timestamp, "_type": "Bolus", "amount": row['INSNMBOL'],
                                             "programmed": row['INSNMBOL'], "unabsorbed": 0, "duration": 0
                                             })
                    # Then the extended bolus value
                    pumphistory_data.append({"timestamp": timestamp, "_type": "Bolus", "amount": row['INSEXBOL'],
                                             "programmed": row['INSEXBOL'], "unabsorbed": 0, "duration": 0})

        if not pumphistory_data:
            return None

        try:
            output = get_net_iob(pumphistory=pumphistory_data, profile=profile, clock=time_zoned_iso)
            return output
        except ConnectionError as ex:
            logger.error(ex.__str__(), exc_info=True)
        except Exception as ex:
            logger.error(ex.__str__(), exc_info=True)
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_time, time_range))

    results = [r for r in results if r is not None]

    return results
