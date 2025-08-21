import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, List, Union
import numpy as np


def add_horizontal_line(ax: plt.Axes, y_value: float) -> plt.Axes:
    ax.axhline(y=y_value, linestyle='--', alpha=0.5, color='black', linewidth=0.5)
    return ax


def add_vertical_line(ax: plt.Axes, x_value: float) -> plt.Axes:
    ax.axvline(x=x_value, linestyle='--', alpha=0.5, color='black', linewidth=0.5)
    return ax


def set_plot_title(ax: plt.Axes, title: str) -> plt.Axes:
    ax.set_title(title)
    return ax


def set_axis_labels(ax: plt.Axes, x_label: str, y_label: str) -> plt.Axes:
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    return ax


def add_legend(ax: plt.Axes, option_legend_location: str = 'inner') -> plt.Axes:
    if option_legend_location == 'outer':
        ax.legend(
            bbox_to_anchor=(0.5, -0.1),
            loc='upper center',
            ncol=10,
            frameon=False,
            columnspacing=2.0
        )
    else:
        ax.legend()
    return ax


def add_grid(ax: plt.Axes) -> plt.Axes:
    ax.grid(True, alpha=0.3)
    return ax


def add_last_values(
    ax: plt.Axes, 
    timeseries: pd.DataFrame, 
    columns: List[str], 
    decimal_places: int = 2,
    option_main: bool = False,
    option_name: Optional[Union[bool, List[str]]] = None,
    option_num_to_show: Union[int, bool] = True,  # 새로운 파라미터 추가
) -> plt.Axes:
    
    # option_num_to_show에 따라 표시할 컬럼 결정
    if isinstance(option_num_to_show, bool):
        if option_num_to_show:  # True: 전부 표시
            columns_to_display = columns
        else:  # False: 전부 표시하지 않음
            columns_to_display = []
    elif isinstance(option_num_to_show, int):
        if option_num_to_show >= 1:
            # 0이면 1개, 1이면 2개, ... n이면 n+1개 표시
            num_to_display = option_num_to_show
            columns_to_display = columns[:num_to_display]
        else:
            columns_to_display = []
    else:
        columns_to_display = columns
    
    for i, col in enumerate(columns_to_display):
        if col in timeseries.columns:
            last_index = timeseries.index[-1]
            last_value = timeseries[col].iloc[-1]
            
            # Determine text to display
            if option_name is not None:
                if isinstance(option_name, bool) and option_name:
                    display_text = col
                elif isinstance(option_name, list) and col in option_name:
                    display_text = col
                else:
                    display_text = f"{last_value:.{decimal_places}f}"
            else:
                display_text = f"{last_value:.{decimal_places}f}"
            
            # Determine font weight
            is_main_column = option_main and i == 0
            font_weight = 'bold' if is_main_column else 'normal'
            
            ax.annotate(
                display_text,
                xy=(last_index, last_value),
                xytext=(5, 0),
                textcoords='offset points',
                color='black',
                fontsize=9,
                ha='left',
                va='center',
                weight=font_weight
            )
    
    return ax


def add_reference_lines(ax: plt.Axes, timeseries: pd.DataFrame, index_ref: str, numeric_cols: List[str]) -> plt.Axes:
    """
    지정된 인덱스(날짜)의 값들을 기준으로 수평선을 그립니다.
    
    Parameters:
    -----------
    ax : plt.Axes
        matplotlib axes 객체
    timeseries : pd.DataFrame
        시계열 데이터프레임
    index_ref : str
        기준 날짜 (예: '2025-01-01')
    numeric_cols : List[str]
        숫자형 컬럼 리스트
    """
    try:
        # 인덱스가 datetime이면 문자열을 datetime으로 변환
        if isinstance(timeseries.index, pd.DatetimeIndex):
            ref_date = pd.to_datetime(index_ref)
        else:
            ref_date = index_ref
        
        # 해당 인덱스가 데이터에 존재하는지 확인
        if ref_date in timeseries.index:
            ref_row = timeseries.loc[ref_date]
            
            # 각 숫자형 컬럼의 값에 대해 수평선 그리기
            for col in numeric_cols:
                if col in ref_row.index and pd.notna(ref_row[col]):
                    y_value = ref_row[col]
                    ax.axhline(
                        y=y_value, 
                        linestyle='-',      # 실선
                        color='black', 
                        linewidth=1.0,      # 조금 더 굵게
                        alpha=0.7,          # 적당한 투명도
                        zorder=1            # 라인 그래프보다 뒤에 그리기
                    )
        else:
            print(f"Warning: 인덱스 '{index_ref}'가 데이터에 존재하지 않습니다.")
            # 가장 가까운 날짜 찾기
            if isinstance(timeseries.index, pd.DatetimeIndex):
                closest_idx = timeseries.index[timeseries.index.get_indexer([ref_date], method='nearest')[0]]
                print(f"가장 가까운 날짜: {closest_idx}")
    
    except Exception as e:
        print(f"Error: 기준선 그리기 실패 - {e}")
    
    return ax


def add_reference_area(ax: plt.Axes, timeseries: pd.DataFrame, index_ref: str) -> plt.Axes:
    """
    index_ref 이전 구간에 옅은 회색 음영을 추가합니다.
    
    Parameters:
    -----------
    ax : plt.Axes
        matplotlib axes 객체
    timeseries : pd.DataFrame
        시계열 데이터프레임
    index_ref : str
        기준 날짜 (예: '2025-01-01')
    """
    try:
        # 인덱스가 datetime이면 문자열을 datetime으로 변환
        if isinstance(timeseries.index, pd.DatetimeIndex):
            ref_date = pd.to_datetime(index_ref)
        else:
            ref_date = index_ref
        
        # 해당 인덱스가 데이터에 존재하는지 확인
        if ref_date in timeseries.index:
            # x축 범위 구하기
            x_min = timeseries.index[0]
            x_max = ref_date
            
            # y축 범위 구하기 (현재 축의 범위 사용)
            y_min, y_max = ax.get_ylim()
            
            # 기준 날짜 이전 구간에 음영 추가
            ax.axvspan(
                x_min, 
                x_max,
                alpha=0.15,          # 매우 옅은 투명도
                color='gray',        # 회색
                zorder=0             # 모든 그래프 요소보다 뒤에 그리기
            )
        else:
            print(f"Warning: 기준 음영을 위한 인덱스 '{index_ref}'가 데이터에 존재하지 않습니다.")
    
    except Exception as e:
        print(f"Error: 기준 음영 그리기 실패 - {e}")
    
    return ax


def get_main_column_style(color: str = 'orange', linewidth: float = 2.5, alpha: float = 1.0) -> dict:
    return {
        'color': color,
        'linewidth': linewidth,
        'alpha': alpha
    }

# GRAY_COLORS = ['#404040', '#606060', '#808080', '#A0A0A0', '#C0C0C0']


def generate_gray_colors(num_colors: int, start_value: int = 0x40, end_value: int = 0xC0) -> List[str]:
    if num_colors <= 0:
        return []    
    if num_colors == 1:
        return [f"#{start_value:02x}{start_value:02x}{start_value:02x}"]
    gray_values = np.linspace(start_value, end_value, num_colors, dtype=int)
    colors = [f"#{val:02x}{val:02x}{val:02x}" for val in gray_values]
    return colors


def get_sub_column_styles(num_cols: int, colors: List[str] = None, linewidth: float = 0.5, alpha: float = 0.7) -> List[dict]:
    colors = colors or generate_gray_colors(num_cols)

    styles = []
    
    for i in range(num_cols):
        color_idx = i % len(colors)
        styles.append({
            'color': colors[color_idx],
            'linewidth': linewidth,
            'alpha': alpha
        })
    
    return styles


def plot_main_sub_columns(ax: plt.Axes, timeseries: pd.DataFrame, numeric_cols: list) -> plt.Axes:

    main_col = numeric_cols[0]
    sub_cols = numeric_cols[1:]
    
    main_style = get_main_column_style()
    ax.plot(timeseries.index, timeseries[main_col], label=main_col, **main_style)
    
    if sub_cols:
        sub_styles = get_sub_column_styles(len(sub_cols))
        for i, col in enumerate(sub_cols):
            ax.plot(timeseries.index, timeseries[col], label=col, **sub_styles[i])
    
    return ax


def plot_regular_columns(ax: plt.Axes, timeseries: pd.DataFrame, numeric_cols: list) -> plt.Axes:

    for col in numeric_cols:
        ax.plot(timeseries.index, timeseries[col], label=col)
    return ax
