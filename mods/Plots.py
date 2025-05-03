from .shared_imports import *
# Graph with count of unique values in each  column from list

def show_dtypes(df):
    # Создаем DataFrame с типами данных
    data_types = df.dtypes.to_frame().rename(columns={0: 'Data Type'})

    # Применяем стили к таблице
    styled_table = data_types.style.set_properties(**{
        'border': '1px solid black',  # Границы для ячеек
        'text-align': 'left',  # Выравнивание текста
        'padding': '5px',  # Отступы внутри ячеек
    }).set_table_styles([{
        'selector': 'th',  # Стили для заголовков
        'props': [('background-color', '#4CAF50'), ('color', 'white')]
    }]).map(lambda x: 'background-color: lightblue', subset=['Data Type'])  # Цвет фона для столбца 'Data Type'

    # Отображаем таблицу
    display(styled_table)

def plt_unique(df, columns):
    unique_counts = [df[column].nunique() for column in columns]

    plt.bar(columns, unique_counts)
    plt.xlabel('Columns')
    plt.ylabel('Number of Unique Values')
    plt.title('Number of Unique Values for Each Column')
    plt.xticks(rotation=45)
    plt.show()

# Graph with value counts for one certain column
def plot_area_value_counts(col: pd.Series):
    # Получаем значения и их частоту
    col = col.value_counts()

    # Создаем горизонтальную столбчатую диаграмму
    plt.figure(figsize=(10, 6))  # Размер графика
    ax = col.plot(kind='barh', color='skyblue')  # Горизонтальная диаграмма

    # Добавляем заголовок и подписи
    plt.title("Распределение по " + str(col.name), fontsize=16, pad=20)
    plt.xlabel("Количество", fontsize=12)
    plt.ylabel(str(col.name), fontsize=12)
    ax.set_xticklabels([])  # Убираем числовые метки на оси X
    ax.set_xticks([])  # Убираем деления на оси X

    # Добавляем числа на столбцы
    for i, value in enumerate(col):
        ax.text(value, i, str(value), va='center', ha='left', fontsize=12)

    # Отображаем график
    plt.tight_layout()  # Улучшаем расположение элементов
    plt.show()

def plot_jobs_value_counts(col: pd.Series):
    # Ограничиваем количество данных (например, топ-20 значений)
    value_counts = col.value_counts().nlargest(20)

    # Создаем интерактивный график
    fig = px.bar(
        value_counts,
        orientation='h',
       # labels={'index': col.name, 'value': 'Количество'},
        text=value_counts.values  # Добавляем числа на столбцы
    )
    fig.update_traces(textposition='outside')  # Позиция текста
    fig.update_layout(
        title_x=0.5,
        xaxis_showticklabels=False,  # Убираем метки на оси X
        yaxis_title=col.name,
        xaxis_title="Количество вхождений конкретного имени процесса в датасет",
        showlegend=False
    )
    fig.show()

def boxplot(df):
    """
    Строит горизонтальный boxplot для столбца 'Execution_time' без выбросов.
    """
    # Создание горизонтального boxplot без выбросов
    box = plt.boxplot(df['Execution_time'], showfliers=False, vert=False, patch_artist=True)

    # Изменение цвета boxplot
    for patch in box['boxes']:
        patch.set_facecolor('lightblue')

    # Настройка осей и заголовка
    plt.xlabel('Execution_time')
    plt.ylabel('Значения')
    plt.title('Горизонтальный boxplot для Execution_time без выбросов')

    # Отображение графика
    plt.show()

def plot_top_timelimits(column: pd.Series, top_n: int = 30):
    """
    Строит график топ-N самых популярных меток времени.

    Параметры:
        column (pd.Series): Столбец данных с метками времени.
        top_n (int): Количество самых популярных меток времени для отображения (по умолчанию 30).
    """
    # Получаем топ-N значений
    top_timelimits = column.value_counts().nlargest(top_n)

    # Создаем DataFrame для Plotly
    top_df = pd.DataFrame({
        'Timelimit': top_timelimits.index,
        'Count': top_timelimits.values
    })

    # Динамически вычисляем высоту графика
    # Высота зависит от количества строк (top_n) и высоты каждой строки (например, 30 пикселей на строку)
    bar_height_per_row = 30  # Высота одной строки в пикселях
    graph_height = bar_height_per_row * top_n

    # Строим график
    fig = px.bar(
        top_df,
        x='Count',
        y='Timelimit',
        orientation='h',  # Горизонтальная диаграмма
        title=f'Топ-{top_n} популярных меток времени',
        labels={'Count': 'Количество', 'Timelimit': 'Метка времени'},
        text='Count',  # Добавляем числа на столбцы
        height=graph_height  # Динамическая высота графика
    )

    # Настраиваем отображение текста
    fig.update_traces(textposition='outside')

    # Настраиваем макет
    fig.update_layout(
        xaxis_title="Количество",
        yaxis_title="Метка времени",
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'},  # Сортировка по возрастанию
        margin=dict(l=50, r=50, t=50, b=50)  # Отступы для красивого отображения
    )

    # Показываем график
    fig.show()

def search_outliers(df, col_name, lower_percentile = 0.20, upper_percentile = 99.80):

    lower_bound = np.percentile(df[col_name], lower_percentile)
    upper_bound = np.percentile(df[col_name], upper_percentile)

    # Фильтрация данных для получения выбросов
    outliers = df[(df[col_name] < lower_bound) | (df[col_name] > upper_bound)]

    # Вывод значений выбросов
    global outlier_values
    outlier_values = outliers[col_name].values
    print("Количество выбросов для заданных процентилей:" + str(len(outlier_values)))
    print("Минимальное значение: " + str(min(outlier_values)))
    print("Максимальное значение: " + str(max(outlier_values)))

def time_difference(df, col_name, timestamp1, timestamp2):
    time_difference = timestamp2 - timestamp1
    return time_difference

def plot_variation_curves1(dataset, cols):
    variation_ranges = []
    dataset = dataset[cols]
    for column in dataset.columns:
        unique_values = dataset[column].nunique()
        variation_ranges.append({'Признак': column, 'Число уникальных значений': unique_values})

    # Сортировка вариационных рядов по убыванию числа уникальных значений
    variation_ranges_sorted = sorted(variation_ranges, key=lambda x: x['Число уникальных значений'], reverse=True)
    # Вывод упорядоченных вариационных рядов
    for variation_range in variation_ranges_sorted:
        print(variation_range)

    # Рисование графика
    labels = [variation_range['Признак'] for variation_range in variation_ranges_sorted]
    values = [variation_range['Число уникальных значений'] for variation_range in variation_ranges_sorted]

    plt.bar(labels, values)
    plt.xlabel('Признак')
    plt.ylabel('Число уникальных значений')
    plt.title('Упорядоченный график вариационных рядов')
    plt.xticks(rotation=90)
    plt.show()
    print("количество признаков " + str(len(variation_ranges_sorted)))

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


#Временной ряд зависимости оличества загрузок задач в суперкомпьютер за определённый интервал от времени
def time_series_visualisation(df: pd.DataFrame, start_date, end_date):
    # Преобразуем даты в datetime формат
    print("Заданный интервал:", start_date, "-", end_date)
    df["Submit"] = pd.to_datetime(df["Submit"], format="%Y-%m-%dT%H:%M:%S", errors='coerce')

    # Сортируем по времени
    df = df.sort_values(by="Submit")

    # Фильтруем данные по заданному интервалу
    df_filtered = df[(df["Submit"] >= start_date) & (df["Submit"] <= end_date)]

    # Проверяем, есть ли данные после фильтрации
    if df_filtered.empty:
        print("Нет данных в заданном интервале.")
        return

    # Устанавливаем 'Submit' как индекс и убеждаемся, что это DatetimeIndex
    df_filtered = df_filtered.set_index("Submit")

    # Группируем по дням и считаем количество задач
    df_grouped = df_filtered.resample("D").size()

    # Проверяем, есть ли данные после группировки
    if df_grouped.empty:
        print("Нет данных после группировки.")
        return

    # Находим пики (локальные максимумы) с добавлением минимального расстояния
    peaks, _ = find_peaks(df_grouped, height=0, distance=10)  # Пики не ближе 10 дней друг от друга

    # Визуализация
    plt.figure(figsize=(12, 6))
    plt.plot(df_grouped.index, df_grouped, label="Number of tasks per day", color="blue")
    plt.scatter(df_grouped.index[peaks], df_grouped.iloc[peaks], color="red", label="Peaks", marker="o")
    plt.xlabel("Date")
    plt.ylabel("Number of tasks")
    plt.title("Time series of task starts")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)  # Поворот меток по оси X для лучшей читаемости

    # Устанавливаем диапазон для оси Y
    y_min = 0  # Минимальное значение оси Y
    y_max = df_grouped.max()  # Максимальное значение оси Y

    # Проверяем, что y_max не NaN или Inf
    if pd.isna(y_max) or np.isinf(y_max):
        y_max = 1  # Значение по умолчанию, если данные некорректны

    plt.ylim(y_min, y_max * 1.1)  # Устанавливаем диапазон оси Y с небольшим отступом

    # Улучшение отображения
    plt.tight_layout()  # Убирает перекрытия и улучшает расположение элементов
    plt.show()


def plot_distribution_comparison(df, column):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    # Гистограмма с KDE
    sns.histplot(df[column], kde=True, ax=ax1)
    ax1.set_title(f'Распределение {column}')

    # Q-Q plot
    stats.probplot(df[column], plot=ax2)
    ax2.set_title(f'Q-Q Plot {column}')

    # Боксплот
    sns.boxplot(x=df[column], ax=ax3)
    ax3.set_title(f'Боксплот {column}')

    plt.tight_layout()
    plt.show()



