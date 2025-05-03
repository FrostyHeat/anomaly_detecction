# Стандартные библиотеки
import datetime as dt
from datetime import datetime, timedelta
import glob
import os
import time
import warnings
from dateutil.parser import parse
from importlib import reload
from IPython.display import display

# Сторонние пакеты
from colorama import Fore, Style
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from scipy import stats
from scipy.signal import find_peaks
import seaborn as sns
from sklearn.metrics import (classification_report, ConfusionMatrixDisplay,
                            f1_score, precision_recall_curve, precision_score,
                precision_score, recall_score, f1_score, classification_report)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import OneHotEncoder, QuantileTransformer, StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import tablib
import torch

# Merlion
from merlion.evaluate.forecast import ForecastMetric
from merlion.models.factory import ModelFactory
from merlion.models.forecast.arima import Arima, ArimaConfig
from merlion.utils import TimeSeries

# Локальные модули
import mods.Data_processing_functions as dpf
import mods.shared_imports as si