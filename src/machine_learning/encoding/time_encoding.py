from enum import Enum
import pandas as pd
from pandas import DataFrame
from datetime import datetime, timezone
import dateparser
import holidays
from numpy import *

# Enumerazione per i tipi di dati temporali
class TimeType(Enum):
    DATE = 'date'
    DURATION = 'duration'
    NONE = 'none'

# Enumerazione per i tipi di encoding temporale
class TimeEncodingType(Enum):
    DATE = 'date'
    DURATION = 'duration'
    DATE_AND_DURATION = 'date_and_duration'
    NONE = 'none'

# Funzione principale per l'encoding temporale
def time_encoding(df: DataFrame, encoding_type) -> DataFrame:
    last_time = [None] * len(df)
    df_output = DataFrame()

    for column_name in df.keys():
        current_time = df[column_name]
        column_type = is_time_or_duration(current_time)

        # Se la colonna contiene date e l'encoding_type è NONE
        if column_type == TimeType.DATE.value and encoding_type == TimeEncodingType.NONE.value:
            df_output[column_name] = convert_datetime_in_UTC(current_time)

        # Se la colonna contiene date e l'encoding_type è DATE o DATE_AND_DURATION
        if column_type == TimeType.DATE.value and encoding_type in [TimeEncodingType.DATE.value, TimeEncodingType.DATE_AND_DURATION.value]:
            result_df = parse_date(current_time, column_name)
            df_output = pd.concat([df_output, result_df], axis=1)

        # Se la colonna non contiene dati temporali o l'encoding_type è DURATION
        if column_type == TimeType.NONE.value or encoding_type == TimeEncodingType.DURATION.value:
            df_output[column_name] = current_time

        # Se la colonna contiene durate e l'encoding_type è DURATION o DATE_AND_DURATION
        if column_type == TimeType.DURATION.value and encoding_type in [TimeEncodingType.DURATION.value, TimeEncodingType.DATE_AND_DURATION.value]:
            if not all(val is None for val in last_time) and not all(val is None for val in current_time):
                result_df = parse_duration(current_time, column_name, last_time)
                df_output = pd.concat([df_output, result_df], axis=1)
            last_time = [
                old_time if new_time is None else new_time
                for new_time, old_time in zip(current_time, last_time)
            ]

    return df_output

# Funzione per convertire le date in timestamp UTC
def convert_datetime_in_UTC(column: list):
    return [
        value.replace(tzinfo=timezone.utc).timestamp()
        if isinstance(value, datetime)
        else dateparser.parse(value).replace(tzinfo=timezone.utc).timestamp()
        for value in column
    ]

# Funzione per determinare se una colonna contiene dati temporali o durate
def is_time_or_duration(column: list):
    column_type = TimeType.NONE.value

    if is_duration(column):
        column_type = TimeType.DURATION.value
    elif is_date(column):
        column_type = TimeType.DATE.value

    return column_type

# Funzione per verificare se tutti gli elementi di una colonna possono essere interpretati come date
def is_date(column: list) -> bool:
    for value in column:
        if isinstance(value, str):
            if value != "" and value != 'None':
                try:
                    float(value)
                    return False
                except ValueError:
                    try:
                        parse(value)
                    except ValueError:
                        return False
        elif isinstance(value, datetime) or value is None:
            pass
        else:
            return False

    return True

# Funzione per verificare se tutti gli elementi di una colonna possono essere interpretati come durate
def is_duration(column: list) -> bool:
    for value in column:
        if isinstance(value, str):
            if value != "" and value != 'None':
                try:
                    float(value)
                    return False
                except ValueError:
                    groups = format_string_duration_parse(value)
                    if not all([
                        (len(group) == 2 and group[0].isnumeric() and group[1] in duration_allowed_word)
                        for group in groups
                    ]):
                        return False
        elif value is None:
            pass
        else:
            return False

    return True

# Lista di parole chiave consentite per le durate
duration_allowed_word = ['d', 'days', 'h', 'hours', 'm', 'minutes', 's', 'seconds']

# Funzione per analizzare una stringa di durata e restituire gruppi di numeri e parole chiave
def format_string_duration_parse(string: str) -> list:
    string = string.replace(" ", "")
    chars = [string[0]]
    for char in string[1:]:
        if not chars[-1].isnumeric() and char.isnumeric():
            chars += ['|']
            chars += [char]
        elif chars[-1].isnumeric() and not char.isnumeric():
            chars += ['_']
            chars += [char]
        else:
            chars += [char]
    formatted_string = [tuple(group.split('_')) for group in "".join(chars).split('|')]
    return formatted_string

# Funzione per verificare se una data è una festività in vari paesi
def is_special_occasion(date):
    countries = ['AR', 'AU', 'AT', 'BY', 'BE', 'BR', 'BG', 'CA', 'CL', 'CO', 'HR', 'CZ', 'DK', 'EG', 'EE', 'FI', 'FR',
               'DE', 'GR', 'HU', 'IS', 'IN', 'IE', 'IL', 'IT', 'JM', 'JP', 'LT', 'MX', 'MA', 'NL', 'NZ', 'PL', 'PT',
               'RO', 'RU', 'SA', 'RS', 'SK', 'SI', 'ZA', 'ES', 'SE', 'CH', 'TR', 'UA', 'AE', 'GB', 'US']
    for country in countries:
        holiday = holidays.CountryHoliday(country)
        if date.strftime("%m-%d-%Y") in holiday:
            return True
    return False

# Funzione per codificare una data in attributi separati
def encode_date(value):
    if isinstance(value, datetime):
        date = value
    else:
        date = dateparser.parse(value)  # Restituisce un oggetto datetime
    return [date.isoweekday(), date.day, date.month, date.year, date.hour, date.minute, date.second,
            is_special_occasion(date)]

# Funzione per convertire una colonna di date in attributi separati
def parse_date(column: list, column_name: str) -> (DataFrame, list):
    columns = [(column_name+'_date_week_day'), (column_name+'_date_day'), (column_name+'_date_month'),
               (column_name+'_date_year'), (column_name+'_date_hours'), (column_name+'_date_minutes'),
               (column_name+'_date_seconds'), (column_name+'_date_special_occasion')]

    encoded_dates = [
        [None for _ in columns]
        if (value is None or value == '' or value == 'None')
        else encode_date(value)
        for value in column
    ]

    results_df = DataFrame(data=encoded_dates, columns=columns)
    results_df = results_df.where(pd.notnull(results_df), None)

    return results_df

# Funzione per codificare una durata in giorni, ore, minuti e secondi
def encode_duration(value):
    return [value.days, value.seconds // 3600, (value.seconds // 60) % 60, value.seconds % 60]

# Funzione per calcolare la differenza tra due date e restituire una durata
def encode_dates_for_duration(date: datetime, last_date: datetime):
    if date is None or last_date is None:
        return None
    else:
        total_seconds = int((date - last_date).total_seconds())

        if total_seconds > 0:
            days = total_seconds // 86400
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds // 60) % 60
            seconds = total_seconds % 60
            return datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        else:
            return None

# Funzione per convertire una colonna di durate in giorni, ore, minuti e secondi
def parse_duration(current_time: list, column_name: str, last_time: list) -> DataFrame:
    columns = [(column_name+'_elapsed_days'), (column_name+'_elapsed_hours'), (column_name+'_elapsed_minutes'),
               (column_name+'_elapsed_seconds')]

    encoded_durations = [
        encode_duration(
            encode_dates_for_duration(new_date, old_date)
        )
        for new_date, old_date in zip(current_time, last_time)
    ]

    results_df = DataFrame(data=encoded_durations, columns=columns)
    results_df = results_df.where(pd.notnull(results_df), None)

    return results_df

if __name__ == '__main__':
    # Esempi di dati di test per le funzioni di parsing e encoding
    time_test = [
        '1990-12-1',
        '',
        None,
        'None',
        '01/19/1990',
        '01/19/90',
        'Jan 1990',
        'January1990',
        '2005/3',
        'Monday at 12:01am',
        'January 1, 2047 at 8:21:00AM',
    ]

    duration_test = [
        '2d9h32m46s',
        '2d 9h',
        '',
        None,
        'None',
        '2days9hours37minutes46seconds',
        '2days 9hours 37minutes 46seconds',
    ]

    print("Tipo di dati rilevato per i dati temporali: ", is_time_or_duration(time_test))
    print("Tipo di dati rilevato per le durate: ", is_time_or_duration(duration_test))

    parsed_dates = parse_date(time_test, 't1')
    print("Date parse: ", parsed_dates.head())

    parsed_durations = parse_duration(duration_test, 't2', [None] * len(duration_test))
    print("Durate parse: ", parsed_durations.head())
