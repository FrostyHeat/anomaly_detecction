from mods.shared_imports import *
#Создание переменных и чтение каждого датасета по каждой предметной области
# (it, астрофизика, механика и тд(функция не требуется

def create_tsdf_variables(folder_path):
    filenames = os.listdir(folder_path)
    for file_name in filenames:
        file_path = os.path.join(folder_path, file_name)
        new_file_name = os.path.splitext(file_name)[0]
        try:
            file_extension = file_path.split('.')[-1]

            if file_extension == 'csv':
                df = pd.read_csv(file_path)
            elif file_extension == 'xlsx':
                df = pd.read_excel(file_path)
            elif file_extension == 'json':
                df = pd.read_json(file_path)
            elif file_extension == 'html':
                df = pd.read_html(file_path)[0]
            df = pd.DataFrame(df)
            new_df_name = os.path.splitext(file_name)[0] + "_df"
            mystr = "Created variable " + str(new_file_name) + " with df "
            print("-" * len(mystr))
            print("Created variable " + str(new_file_name) + " with df ")
            print('-' * len(new_file_name))
            print(new_file_name)
            print('-' * len(new_file_name))
            display(df.head())
            display(df.info())
            globals()[new_df_name] = df
        except Exception as e:
            print(f"Ошибка чтения файла :  {str(e)}")

#смена типов столбцов "start" и "submit" чтобы с ними можно было работать как с  значениями времени
def df_processing(df):
    df["Start"] = pd.to_datetime(df["Start"])
    df['Submit'] = pd.to_datetime(df['Submit'])
    try:
        df = df.drop(columns = "Unnamed: 0")
    except KeyError:
        return df
    return df

# Добавление столбца с месяцем неделей и часом
def fe_time(df):
    # Добавление столбца с месяцем неделей и часом
    df['Month'] = df['Submit'].dt.month
    df['Week'] = df['Submit'].dt.isocalendar().week
    df['Hour'] = df['Submit'].dt.hour
    # Добавление столбца с временем дня (день или ночь)
    df['Time'] = df['Submit'].dt.strftime('%p')
    return df

def fe_id(df):
    df['diff_id'] = df.groupby('UID')['GID'].transform(lambda x: int((x.nunique() == len(x)) and (len(x) > 1)))
    df = df.sort_index()
    return df

#Обрабатываем значения соответствующие времени
def convert_to_timedelta(value):
    try:
        # Попытка преобразовать значение в формате '%d-%H:%M:%S'
        days, time = value.split('-')
        hours, minutes, seconds = map(int, time.split(':'))
        return pd.to_timedelta(f'{days} days {hours}:{minutes}:{seconds}')
    except ValueError:
        # Попытка преобразовать значение в формате '%H:%M:%S'
        hours, minutes, seconds = map(int, value.split(':'))
        return pd.to_timedelta(f'{hours}:{minutes}:{seconds}')

#Обрабатываем значения соответствующие времени
def fe_time_2(df):
    df['Elapsed'] = df['Elapsed'].apply(convert_to_timedelta)
    df['Start'] = pd.to_datetime(df['Start'])
    df['End'] = df['Start'] + df['Elapsed']
    df['Execution_time'] = df['Elapsed'].dt.total_seconds()
    return df

#ищем операции запущенные не сразу
def add_neg(df):
    col = []
    for i in range(0, len(df["UID"])-1):
        if df["Start"][i] < df["Start"][i+1]:
            col.append("pos")
        if df["Start"][i] == df["Start"][i+1]:
            col.append("eq")
        if df["Start"][i] > df["Start"][i+1]:
            col.append("neg")
    df["Diff_start"] = pd.Series(col)
    return df

#Объединяем значения Cancelled by в одно
def fe(df):
    fe_time(df)
    fe_time_2(df)
    df = df.iloc[:-1,1:]
    add_neg(df)
    df.loc[df["State"].str.startswith('CANCELLED by') , "State"] = "CANCELLED"
    return df
# ищем несовпадение между юзер айди и груп айди
def count_nq(df):
    count = []
    global ids
    ids = []
    print("Число UID которым соответствует несколько GID:  -   ")
    for uv in df["UID"].unique():
        if len(df["GID"][df["UID"] == uv].unique()) > 1:
            count.append(len(df["GID"][df["UID"] == uv].unique()))
            ids.extend(df[df["UID"] == uv].index.tolist())
    print(pd.Series(count).value_counts())
    print(len(ids))
    return count, ids

#создание датасета из аномалий
def anomalies_df(dfe):
    dfe["Marker"] = "0"
    dfe.loc[dfe["Partition"] == "nv", "Marker"] = "Partition_nv"
    dfe.loc[dfe["State"] == "OUT_OF_MEMORY", "Marker"] = "State_memory"
    dfe.loc[dfe["State"] == "NODE_FAIL", "Marker"] = "State_node_fail"
    dfe.loc[dfe["State"] == "TIMEOUT", "Marker"] = "State_timeout"
    dfe.loc[dfe["State"] == "FAILED", "Marker"] = "State_failed"
    dfe.loc[dfe["State"] == "nv", "Marker"] = "State_nv"
    dfe.loc[dfe["Diff_start"] == "neg", "Marker"] = "Diff_start_neg"
    dfe.loc[count_nq(dfe)[1], "Marker"] = "nq"

    # Я не думаю, что Execution time - важный признак так что пока что попробуем обойтись без него
    # outliers_a = dfe[dfe["Execution_time"].isin(outlier_values)]

    return dfe.loc[dfe["Marker"] != "0"].reset_index()

def separation(df, num_pieces ):
    dfs = np.array_split(df, num_pieces)
    return dfs

def swap_columns(dataset, new_order):
    return dataset.reindex(columns=new_order)

def sort_columns(dataset, cols):
    variation_ranges = []
    dataset = dataset[cols]
    for column in dataset.columns:
        unique_values = dataset[column].nunique()
        variation_ranges.append({'Признак': column, 'Число уникальных значений': unique_values})

    # Сортировка вариационных рядов по убыванию числа уникальных значений
    variation_ranges_sorted = sorted(variation_ranges, key=lambda x: x['Число уникальных значений'], reverse=True)

    # Создание массива из названий столбцов в порядке убывания их значений
    column_names_sorted = [item['Признак'] for item in variation_ranges_sorted]
    return column_names_sorted

def swapping_columns(dfssa):
    dfc = pd.DataFrame()
    for df in dfssa:
        sorted_columns = sort_columns(df, df.columns)
        swapped_dataset = swap_columns(df, sorted_columns)
        swapped_dataset_str = swapped_dataset.astype(str)
        dfc = pd.concat([dfc, swapped_dataset_str])
        dfc = dfc.reindex(columns=sorted_columns)
    return dfc

def toy_df_f(df):
    toydf1 = df.loc[10000:10005, ["Submit", "Start"]]
    toydf2 = df.loc[10500:10503, ["Submit", "Start"]]
    toydf = pd.concat([toydf1, toydf2])
    toydf = toydf.reset_index()
    toydf.loc[9, 'Submit'] = toydf.loc[8, 'Submit']
    toydf.loc[9, 'Start'] = toydf.loc[8, 'Start']
    toydf.loc[5:6, 'Submit'] = toydf.loc[7, 'Submit']
    toydf.loc[5:6, 'Start'] = toydf.loc[4, 'Start']
    return toydf


def create_toy_df(df):

    toy_df_submit = toy_df_f(df)
    toy_df_id_dict = {
        'UID': [1, 1, 3, 4, 1, 10, 1, 4, 9, 10],
        'GID': [10, 10, 20, 20, 10, 30, 10, 200, 50, 30]
    }
    toy_df_id = pd.DataFrame(toy_df_id_dict)
    toy_df = pd.concat([fe_time(toy_df_submit), fe_id(toy_df_id)], axis=1)
    toy_df["Elapsed"] = df["Elapsed"].iloc[0:10]
    toy_df["Elapsed"][3] = df["Elapsed"][1005]
    toy_df["Elapsed"][1] = df["Elapsed"][1005]
    toy_df = fe_time_2(toy_df)
    features = ['Area',
           "JobName",
           'Partition',
           'ReqNodes',
           'ReqCPUS',
           'Timelimit',
           'Priority',
           'State',
           'ExitCode']
    df = pd.concat([toy_df, df[features].iloc[:10, :]], axis = 1)
    df = df.iloc[:,1:]
    return df


def df_dates_making(df: pd.DataFrame, time_step: str, start_of_interval: str = None,
                    end_of_interval: str = None) -> pd.DataFrame:
    """
    Обрабатывает временной ряд, фильтруя по интервалу и агрегируя с заданным шагом.

    Параметры:
        step: Шаг для ресемплинга ('1min', '5min', '1H', "1D")
        df: DataFrame с данными временного ряда
        start_of_interval: Начало интервала (по умолчанию df['Start'].min())
        end_of_interval: Конец интервала (по умолчанию df['Start'].max())

    Возвращает:
        DataFrame с агрегированными данными
    """
    if start_of_interval is None:
        start_of_interval = df['Start'].min()
    else:
        start_of_interval = pd.to_datetime(start_of_interval)
    if end_of_interval is None:
        end_of_interval = df['Start'].max()
    else:
        end_of_interval = pd.to_datetime(end_of_interval)
    # Фильтруем по интервалу
    # df_filtered = df.loc[(df['Start'] >= pd.to_datetime(start_of_interval)) & (df['Start'] <= pd.to_datetime(end_of_interval))].copy()
    # Устанавливаем временные интервалы
    dates = pd.date_range(start=start_of_interval, end=pd.to_datetime(end_of_interval), freq=time_step)
    dates = pd.to_datetime(dates)
    # число активных задач

    return dates


def calculate_active_processors(df, time_points):
    """
    Рассчитывает количество запрошенных процессоров в каждый момент времени

    Параметры:
        df: DataFrame с задачами
        time_points: Временные точки для анализа

    Возвращает:
        Series с количеством активных процессоров
    """
    cpus = pd.Series(0, index=time_points, name='active_processors')
    nodes = pd.Series(0, index=time_points, name='active_nodes')
    names = pd.Series("", index=time_points, name='JobNames')
    for idx, ts in enumerate(time_points):
        # Находим задачи, активные в этот момент
        active_jobs = df[(df['Start'] <= ts) & (df['End'] >= ts)]

        # Суммируем запрошенные процессоры
        cpus.iloc[idx] = active_jobs['ReqCPUS'].sum()
        nodes.iloc[idx] = active_jobs['ReqNodes'].sum()
        job_names = active_jobs['JobName'].unique()
        names.iloc[idx] = ",".join(job_names) if len(job_names) > 0 else "Нет задач"
    return pd.concat([cpus, nodes, names], axis=1)

def data_X_Y(df, cols:list):
    #упорядочиваем значения по времени загрузки в систему
    df = df.sort_values(by="Submit").reset_index()
    #время с последней операции
    df['time_since_last'] = df['Submit'].diff().dt.total_seconds().fillna(0)
    X_selected = df[cols]
    y = df["State"]
    X_selected = pd.get_dummies(X_selected, columns=['Area', 'Partition', "Month", "Week", "Hour"],sparse=True, drop_first=True, dtype=int)
    X_selected.drop("Submit", axis=1, inplace=True)
    return X_selected, y

def OHE(df, columns=None):
    if columns is None:
        columns = df.select_dtypes(include=['object', 'category']).columns
    columns = columns.append("Priority")
    # Создаем OHE-признаки
    dummies = pd.get_dummies(df[columns], drop_first=True, dtype=int)

    # Удаляем исходные колонки, которые были преобразованы
    df = df.drop(columns=columns)

    # Объединяем исходный датафрейм (без исходных колонок) с новыми OHE-колонками
    df = pd.concat([df, dummies], axis=1)
    return df



# Разделение на train/test с учетом временного порядка
def train_test_ts_split(X, train_size_percent, y):
    split_id = int(train_size_percent * len(df))
    X_train, X_test = X[:split_id], X[split_id:]
    y_train, y_test = y[:splwit_id], y[split_id:]
    return X_train, X_test, y_train, y_test


def normalize_Quantile_features(df, cols):
    # примечание для себя - можно попробовать Standart_scaler, Robust_scaler - не работает
    # Настройка трансформера (можно задать output_distribution='uniform'/'normal')
    scaler = QuantileTransformer(output_distribution='normal', random_state=42)

    # Применяем к выбранным столбцам
    df[cols] = scaler.fit_transform(
        df[cols]
    )

    df[cols] = scaler.fit_transform(df[cols])
    return df

def normalize_std_features(df, cols):
    #примечание для себя - можно попробовать Standart_scaler, Robust_scaler - не работает
    # Настройка трансформера (можно задать output_distribution='uniform'/'normal')
    scaler = StandardScaler()
    # Применяем к выбранным столбцам
    scaler.fit(df[cols])
    df[cols] = scaler.transform(df[cols])
    return df

def normalize_log_features(df, cols):
    #примечание для себя - можно попробовать Standart_scaler, Robust_scaler - не работает
    scaler = LogScaler(base='10', C=1)
    # Применяем к выбранным столбцам
    scaler.fit(df[cols])
    df[cols] = scaler.transform(df[cols])
    return df

class LogScaler():
    def __init__(self, base='natural', C=1):
        """
        :param base: 'natural' (ln), '10' (log10), '2' (log2)
        :param C: Константа, добавляемая к X (по умолчанию 1).
        """
        self.base = base
        self.C = C

    def fit(self, X, y=None):
        return self  # Ничего не вычисляем в fit

    def transform(self, X):
        X = X.copy() + self.C
        if self.base == 'natural':
            return np.log(X)
        elif self.base == '10':
            return np.log10(X)
        elif self.base == '2':
            return np.log2(X)
        else:
            raise ValueError("Неподдерживаемое основание логарифма")

    def inverse_transform(self, X):
        if self.base == 'natural':
            return np.exp(X) - self.C
        elif self.base == '10':
            return 10 ** X - self.C
        elif self.base == '2':
            return 2 ** X - self.C

"""
def get_current_chunk_stats(df, current_time, interval='10h'):


    # Базовые признаки
    num_operations = len(chunk_jobs)
    total_cpus = chunk_jobs['ReqCPUS'].sum()
    unique_uids = chunk_jobs['UID'].nunique()
    total_execution = chunk_jobs['Execution_time'].sum()
    mean_cpus = chunk_jobs['ReqCPUS'].mean()
    avg_execution = chunk_jobs['Execution_time'].mean()

    # Дополнительные статистические признаки
    median_cpus = chunk_jobs['ReqCPUS'].median()
    std_cpus = chunk_jobs['ReqCPUS'].std()
    min_cpus = chunk_jobs['ReqCPUS'].min()
    max_cpus = chunk_jobs['ReqCPUS'].max()

    median_execution = chunk_jobs['Execution_time'].median()
    std_execution = chunk_jobs['Execution_time'].std()
    min_execution = chunk_jobs['Execution_time'].min()
    max_execution = chunk_jobs['Execution_time'].max()

    # Процентили для анализа распределения
    cpu_percentiles = chunk_jobs['ReqCPUS'].quantile([0.25, 0.5, 0.75, 0.9])
    exec_percentiles = chunk_jobs['Execution_time'].quantile([0.25, 0.5, 0.75, 0.9])

    # Коэффициенты вариации
    cv_cpus = std_cpus / mean_cpus if mean_cpus != 0 else 0
    cv_execution = std_execution / avg_execution if avg_execution != 0 else 0

    # Плотность задач (задач на единицу времени)
    time_interval = (chunk_end - chunk_start).total_seconds()
    job_density = num_operations / time_interval if time_interval > 0 else 0

    # Отношения и производные метрики
    cpu_utilization = total_cpus / (num_operations * mean_cpus) if mean_cpus != 0 else 0
    execution_per_cpu = total_execution / total_cpus if total_cpus != 0 else 0

    # Признаки распределения
    skew_cpus = chunk_jobs['ReqCPUS'].skew()
    kurtosis_cpus = chunk_jobs['ReqCPUS'].kurtosis()
    skew_execution = chunk_jobs['Execution_time'].skew()
    kurtosis_execution = chunk_jobs['Execution_time'].kurtosis()

    # Бинарные признаки (пример)
    has_large_job = int(max_cpus > mean_cpus + 2 * std_cpus) if not np.isnan(std_cpus) else 0
    has_long_job = int(max_execution > avg_execution + 2 * std_execution) if not np.isnan(std_execution) else 0


    return {
        # Базовые признаки
        'interval_start': chunk_start,
        'interval_end': chunk_end,
        'total_cpus': total_cpus,
        'unique_jobs': unique_uids,
        'avg_execution': avg_execution,
        'total_execution': total_execution,
        'load_type': load_type,
        'active_jobs_count': num_operations,

        # Дополнительные статистики
        'mean_cpus': mean_cpus,
        'median_cpus': median_cpus,
        'std_cpus': std_cpus,
        'min_cpus': min_cpus,
        'max_cpus': max_cpus,
        'cpu_p25': cpu_percentiles[0.25],
        'cpu_p75': cpu_percentiles[0.75],
        'cpu_p90': cpu_percentiles[0.9],

        'median_execution': median_execution,
        'std_execution': std_execution,
        'min_execution': min_execution,
        'max_execution': max_execution,
        'exec_p25': exec_percentiles[0.25],
        'exec_p75': exec_percentiles[0.75],
        'exec_p90': exec_percentiles[0.9],

        # Коэффициенты
        'cv_cpus': cv_cpus,
        'cv_execution': cv_execution,
        'job_density': job_density,
        'cpu_utilization': cpu_utilization,
        'execution_per_cpu': execution_per_cpu,

        # Характеристики распределения
        'skew_cpus': skew_cpus,
        'kurtosis_cpus': kurtosis_cpus,
        'skew_execution': skew_execution,
        'kurtosis_execution': kurtosis_execution,

        # Бинарные признаки
        'has_large_job': has_large_job,
        'has_long_job': has_long_job
"""





