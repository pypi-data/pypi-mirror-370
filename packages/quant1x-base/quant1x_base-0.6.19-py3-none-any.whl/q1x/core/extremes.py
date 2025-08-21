#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Project : q1x-base
@Package : 
@File    : extremes.py
@Author  : wangfeng
@Date    : 2025/8/19 16:28
@Desc    : 
"""

import math
from typing import List, Tuple, Optional, Dict, Any, Callable, Union

WAVE_FLOAT_EPS = 1e-9

class ExtremeType:
    PEAK = 0  # 波峰（局部最大值）
    TROUGH = 1  # 波谷（局部最小值）

    @staticmethod
    def to_string(e: int) -> str:
        if e == ExtremeType.PEAK:
            return "ExtremePeak"
        elif e == ExtremeType.TROUGH:
            return "ExtremeTrough"
        else:
            return "Unknown"

class SegmentSide:
    LEFT = 0
    RIGHT = 1

class SearchMode:
    FIND_INFLECTION = 0  # 从左到右：找拐点
    PRESERVE_TREND = 1  # 从右到左：保终局

    @staticmethod
    def to_string(m: int) -> str:
        if m == SearchMode.FIND_INFLECTION:
            return "FindInflection"
        elif m == SearchMode.PRESERVE_TREND:
            return "PreserveTrend"
        else:
            return "Unknown"

class PeaksResult:
    def __init__(self):
        self.peaks: List[int] = []  # 主趋势波峰（含所有主峰）
        self.breakouts: List[int] = []  # 异常突破点

    def __str__(self) -> str:
        return f"Peaks: {self.peaks}, Breakouts: {self.breakouts}"

    def has_breakouts(self) -> bool:
        return len(self.breakouts) > 0

    def count(self) -> int:
        return len(self.peaks)

    def first_peak(self) -> int:
        if not self.peaks:
            return -1
        return self.peaks[0]

    def last_peak(self) -> int:
        if not self.peaks:
            return -1
        return self.peaks[-1]

    def values(self, data: List[float]) -> List[float]:
        vals = []
        for i in self.peaks:
            if 0 <= i < len(data):
                vals.append(data[i])
        return vals

    def is_empty(self) -> bool:
        return len(self.peaks) == 0

class SideModes:
    def __init__(self, left: int = SearchMode.FIND_INFLECTION, right: int = SearchMode.FIND_INFLECTION):
        self.left = left  # 第一个主峰/主谷左侧使用的模式
        self.right = right  # 最后一个主峰/主谷右侧使用的模式

    def __str__(self) -> str:
        return f"Left: {SearchMode.to_string(self.left)}, Right: {SearchMode.to_string(self.right)}"

def check_and_append(data: List[float], curr_idx: int, valid: List[int], breakouts: List[int], should_increase: bool) -> None:
    if not valid:
        valid.append(curr_idx)
        return

    last_val = data[valid[-1]]
    curr_val = data[curr_idx]

    if should_increase:
        if curr_val >= last_val:
            valid.append(curr_idx)
        else:
            breakouts.append(curr_idx)
    else:
        if curr_val <= last_val:
            valid.append(curr_idx)
        else:
            breakouts.append(curr_idx)

class Config:
    def __init__(self, eps: float = WAVE_FLOAT_EPS):
        self.eps = eps

def with_epsilon(eps: float) -> Callable[[Config], None]:
    def config_func(c: Config) -> None:
        c.eps = eps
    return config_func

def find_extremes_with_breakouts(
        data: List[float],
        extremes: Optional[List[int]],
        start: int,
        end: int,
        modes: SideModes,
        direction: int,
        **kwargs
) -> PeaksResult:
    result = PeaksResult()

    # Apply options
    cfg = Config()
    if 'eps' in kwargs:
        cfg.eps = kwargs['eps']

    # Protection
    if not data or start < 0 or end > len(data) or start >= end or len(data) < 3:
        return result

    # Fallback: if extremes is empty, find local extremes automatically
    if extremes is None or not extremes:
        temp_extremes = find_local_extremes_in(data, start, end, direction)
        if not temp_extremes:
            extremes = None  # Clear, skip review
        else:
            extremes = temp_extremes

    # Step 1: Find global extreme value in [start, end)
    if direction == ExtremeType.PEAK:
        main_val = max(data[start:end])
    else:
        main_val = min(data[start:end])

    # Step 2: Collect all points equal to main_val → major extremes (value-driven)
    major_extremes = [i for i in range(start, end) if math.isclose(data[i], main_val, abs_tol=cfg.eps)]

    if not major_extremes:
        return result

    major_extremes.sort()
    first_major = major_extremes[0]
    last_major = major_extremes[-1]

    # Step 3: Segment processing
    results = []
    breakouts = []

    # Only review if extremes exist
    if extremes and extremes:
        # 1. Process left free segment
        process_extreme_segment_with_eps(
            data, start, first_major,
            extremes, modes.left,
            results, breakouts,
            main_val, direction, SegmentSide.LEFT,
            cfg.eps
        )

        # 2. Process right free segment
        process_extreme_segment_with_eps(
            data, last_major + 1, end,
            extremes, modes.right,
            results, breakouts,
            main_val, direction, SegmentSide.RIGHT,
            cfg.eps
        )

    # 3. Add all points in major area
    results.extend(major_extremes)

    # 4. Sort output
    results.sort()
    breakouts.sort()

    result.peaks = results
    result.breakouts = breakouts
    return result

def process_extreme_segment_with_eps(
        data: List[float],
        seg_start: int,
        seg_end: int,
        extremes: List[int],
        mode: int,
        results: List[int],
        breakouts: List[int],
        main_val: float,
        direction: int,
        side: int,
        eps: float
) -> None:
    if seg_start < 0 or seg_end > len(data) or seg_start >= seg_end:
        return

    seg_extremes = [idx for idx in extremes if seg_start <= idx < seg_end and not math.isclose(data[idx], main_val, abs_tol=eps)]

    if not seg_extremes:
        return

    valid = []
    increasing = False  # True: non-decreasing; False: non-increasing
    reverse_order = False

    if mode == SearchMode.FIND_INFLECTION and side == SegmentSide.LEFT and direction == ExtremeType.PEAK:
        reverse_order = True
        increasing = False
    elif mode == SearchMode.FIND_INFLECTION and side == SegmentSide.RIGHT and direction == ExtremeType.PEAK:
        reverse_order = False
        increasing = False
    elif mode == SearchMode.PRESERVE_TREND and side == SegmentSide.LEFT and direction == ExtremeType.PEAK:
        reverse_order = False
        increasing = True
    elif mode == SearchMode.PRESERVE_TREND and side == SegmentSide.RIGHT and direction == ExtremeType.PEAK:
        reverse_order = True
        increasing = True
    elif mode == SearchMode.FIND_INFLECTION and side == SegmentSide.LEFT and direction == ExtremeType.TROUGH:
        reverse_order = True
        increasing = True
    elif mode == SearchMode.FIND_INFLECTION and side == SegmentSide.RIGHT and direction == ExtremeType.TROUGH:
        reverse_order = False
        increasing = True
    elif mode == SearchMode.PRESERVE_TREND and side == SegmentSide.LEFT and direction == ExtremeType.TROUGH:
        reverse_order = False
        increasing = False
    elif mode == SearchMode.PRESERVE_TREND and side == SegmentSide.RIGHT and direction == ExtremeType.TROUGH:
        reverse_order = True
        increasing = False

    indices = seg_extremes
    if reverse_order:
        for i in reversed(range(len(seg_extremes))):
            check_and_append(data, seg_extremes[i], valid, breakouts, increasing)
    else:
        for idx in indices:
            check_and_append(data, idx, valid, breakouts, increasing)

    if reverse_order:
        valid.reverse()

    results.extend(valid)

def find_local_extremes_in(data: List[float], start: int, end: int, direction: int) -> List[int]:
    extremes = []

    # Left endpoint
    if start + 1 < end:
        if (direction == ExtremeType.PEAK and data[start] > data[start + 1]) or \
                (direction == ExtremeType.TROUGH and data[start] < data[start + 1]):
            extremes.append(start)

    # Internal points
    for i in range(start + 1, end - 1):
        is_peak = data[i - 1] < data[i] and data[i] > data[i + 1]
        is_trough = data[i - 1] > data[i] and data[i] < data[i + 1]

        if (direction == ExtremeType.PEAK and is_peak) or (direction == ExtremeType.TROUGH and is_trough):
            extremes.append(i)

    return extremes

def extract_alternating_peaks_valleys(peaks: List[int], valleys: List[int]) -> Tuple[List[int], List[int]]:
    if not peaks or not valleys:
        return [], []

    result = []
    i, j = 0, 0

    # Determine starting type: which has smaller first index
    next_is_peak = peaks[i] < valleys[j] if peaks and valleys else False

    while i < len(peaks) and j < len(valleys):
        if next_is_peak:
            # Find next peaks[i] > result.last
            last = result[-1][0] if result else -1
            while i < len(peaks) and peaks[i] <= last:
                i += 1
            if i >= len(peaks) or (result and peaks[i] <= result[-1][0]):
                break
            result.append((peaks[i], True))
            i += 1
            next_is_peak = False  # Next must be valley
        else:
            last = result[-1][0] if result else -1
            while j < len(valleys) and valleys[j] <= last:
                j += 1
            if j >= len(valleys) or (result and valleys[j] <= result[-1][0]):
                break
            result.append((valleys[j], False))
            j += 1
            next_is_peak = True  # Next is peak

    # Split results
    selected_peaks = [item[0] for item in result if item[1]]
    selected_valleys = [item[0] for item in result if not item[1]]

    return selected_peaks, selected_valleys

DEFAULT_PEAK_MODES = SideModes(
    left=SearchMode.PRESERVE_TREND,  # 左侧既成事实，保留
    right=SearchMode.FIND_INFLECTION  # 右侧审查是否破坏趋势
)

DEFAULT_VALLEY_MODES = SideModes(
    left=SearchMode.PRESERVE_TREND,
    right=SearchMode.FIND_INFLECTION
)

def find_peaks(data: List[float], start: int, end: int, modes: SideModes = None, **kwargs) -> PeaksResult:
    if modes is None or (modes.left == 0 and modes.right == 0):
        modes = DEFAULT_PEAK_MODES

    return find_peaks_with_auto_modes(data, start, end, **kwargs)

def find_peaks_with_auto_modes(data: List[float], start: int, end: int, **kwargs) -> PeaksResult:
    extremes = find_local_extremes_in(data, start, end, ExtremeType.PEAK)
    if not extremes:
        modes = SideModes(
            left=SearchMode.FIND_INFLECTION,
            right=SearchMode.PRESERVE_TREND
        )
        return find_extremes_with_breakouts(data, None, start, end, modes, ExtremeType.PEAK, **kwargs)

    main_val = max(data[i] for i in extremes)

    cfg = Config()
    if 'eps' in kwargs:
        cfg.eps = kwargs['eps']

    major_extremes = [i for i in extremes if math.isclose(data[i], main_val, abs_tol=cfg.eps)]
    if not major_extremes:
        return PeaksResult()

    major_extremes.sort()
    last_major = major_extremes[-1]
    mid_point = start + int((end - start) * 0.6)

    if last_major >= mid_point:
        left_mode = SearchMode.PRESERVE_TREND
    else:
        left_mode = SearchMode.FIND_INFLECTION

    modes = SideModes(
        left=left_mode,
        right=SearchMode.PRESERVE_TREND
    )

    return find_extremes_with_breakouts(data, None, start, end, modes, ExtremeType.PEAK, **kwargs)

def find_valleys(data: List[float], start: int, end: int, modes: SideModes = None, **kwargs) -> PeaksResult:
    if modes is None or (modes.left == 0 and modes.right == 0):
        modes = DEFAULT_VALLEY_MODES
    return find_valleys_with_auto_modes(data, start, end, **kwargs)

def find_valleys_with_auto_modes(data: List[float], start: int, end: int, **kwargs) -> PeaksResult:
    extremes = find_local_extremes_in(data, start, end, ExtremeType.TROUGH)
    if not extremes:
        modes = SideModes(
            left=SearchMode.FIND_INFLECTION,
            right=SearchMode.PRESERVE_TREND
        )
        return find_extremes_with_breakouts(data, None, start, end, modes, ExtremeType.TROUGH, **kwargs)

    main_val = min(data[i] for i in extremes)

    cfg = Config()
    if 'eps' in kwargs:
        cfg.eps = kwargs['eps']

    major_extremes = [i for i in extremes if math.isclose(data[i], main_val, abs_tol=cfg.eps)]
    if not major_extremes:
        return PeaksResult()

    major_extremes.sort()
    last_major = major_extremes[-1]
    mid_point = start + int((end - start) * 0.6)

    if last_major >= mid_point:
        left_mode = SearchMode.PRESERVE_TREND
    else:
        left_mode = SearchMode.FIND_INFLECTION

    modes = SideModes(
        left=left_mode,
        right=SearchMode.PRESERVE_TREND
    )

    return find_extremes_with_breakouts(data, None, start, end, modes, ExtremeType.TROUGH, **kwargs)

class PriceSeries:
    def __init__(self):
        self.high: List[float] = []  # 最高价序列
        self.low: List[float] = []  # 最低价序列
        self.close: List[float] = []  # 收盘价（可选）
        self.timestamps: List[int] = []  # 时间戳（可选）

class SupportResistance:
    def __init__(self):
        self.resistance: PeaksResult = PeaksResult()  # 压力线（来自 high 的波峰）
        self.support: PeaksResult = PeaksResult()  # 支撑线（来自 low 的波谷）
        self.breakout = {
            'resistance_break': False,  # 压力线被突破
            'support_break': False,  # 支撑线被跌破
            'first_break_idx': 0  # 首次突破位置
        }

def find_support_resistance(ps: PriceSeries, start: int, end: int) -> SupportResistance:
    sr = SupportResistance()

    if end <= start:
        return sr

    modes = SideModes(
        left=SearchMode.PRESERVE_TREND,
        right=SearchMode.FIND_INFLECTION
    )

    # 1. Find extremes
    sr.resistance = find_extremes_with_breakouts(ps.high, None, start, end, modes, ExtremeType.PEAK)
    sr.support = find_extremes_with_breakouts(ps.low, None, start, end, modes, ExtremeType.TROUGH)

    # 2. Get "pre-breakout" main resistance (highest before last main peak)
    prev_resistance = -math.inf
    last_peak_idx = -1
    if sr.resistance.peaks:
        sr.resistance.peaks.sort()
        last_peak_idx = sr.resistance.peaks[-1]
        for idx in sr.resistance.peaks:
            if idx < last_peak_idx and ps.high[idx] > prev_resistance:
                prev_resistance = ps.high[idx]
        if prev_resistance == -math.inf:
            prev_resistance = 0  # Or set to minimum value

    # 3. Check for breakout: current High > previous main resistance
    for i in range(start, end):
        if i in sr.resistance.peaks and ps.high[i] > prev_resistance:
            sr.breakout['resistance_break'] = True
            if sr.breakout['first_break_idx'] == 0 or i < sr.breakout['first_break_idx']:
                sr.breakout['first_break_idx'] = i

    return sr

def contains(slice: List[int], val: int) -> bool:
    return val in slice

def get_max_peak_value(high: List[float], peaks: List[int]) -> float:
    if not peaks:
        return -math.inf
    last_peak = peaks[-1]
    return high[last_peak]

def get_min_valley_value(low: List[float], peaks: List[int]) -> float:
    if not peaks:
        return math.inf
    last_valley = peaks[-1]
    return low[last_valley]

def is_in_future(idx: int, peaks: List[int]) -> bool:
    if not peaks:
        return True
    last_peak = peaks[-1]
    return idx > last_peak

class TrendDirection:
    UNKNOWN = 0
    UPWARD = 1  # 上升趋势（如：波谷后回升）
    DOWNWARD = 2  # 下降趋势（如：波峰后回落）

    @staticmethod
    def to_string(t: int) -> str:
        if t == TrendDirection.UPWARD:
            return "Upward"
        elif t == TrendDirection.DOWNWARD:
            return "Downward"
        else:
            return "Unknown"

class TradeOpportunity:
    def __init__(self):
        self.type: int = ExtremeType.PEAK  # 机会类型：ExtremePeak（高点卖出/做空）或 ExtremeTrough（低点买入/做多）
        self.start_idx: int = 0  # 该机会分析的起始索引
        self.end_idx: int = 0  # 该机会分析的结束索引
        self.peaks: List[int] = []  # 合规的趋势点（主趋势+自由段合规点）
        self.breakouts: List[int] = []  # 异常突破点（破坏趋势的点）
        self.value: float = 0.0  # 主极值点的值（价格）
        self.direction: int = TrendDirection.UNKNOWN  # 趋势方向（可选）

    def __str__(self) -> str:
        typ = "Peak" if self.type == ExtremeType.PEAK else "Trough"
        return (f"TradeOpportunity{{Type: {typ}, Start: {self.start_idx}, End: {self.end_idx}, "
                f"Value: {self.value:.3f}, Direction: {TrendDirection.to_string(self.direction)}, "
                f"Peaks: {self.peaks}, Breakouts: {self.breakouts}}}")

def find_breakout_opportunities(ps: PriceSeries, start: int, end: int) -> List[TradeOpportunity]:
    sr = find_support_resistance(ps, start, end)
    opportunities = []

    if sr.breakout['first_break_idx'] != 0:
        sub_start = sr.breakout['first_break_idx']
        sub_end = end

        sub_modes = SideModes(
            left=SearchMode.PRESERVE_TREND,
            right=SearchMode.PRESERVE_TREND
        )

        # Break resistance → find new upward trend (find troughs in low)
        if sr.breakout['resistance_break']:
            sub_valley = find_extremes_with_breakouts(ps.low, None, sub_start, sub_end, sub_modes, ExtremeType.TROUGH)
            if sub_valley.peaks:
                last = sub_valley.peaks[-1]
                to = TradeOpportunity()
                to.type = ExtremeType.TROUGH
                to.start_idx = sub_start
                to.end_idx = sub_end
                to.peaks = sub_valley.peaks
                to.breakouts = sub_valley.breakouts
                to.value = ps.low[last]
                opportunities.append(to)

        # Break support → find new downward trend (find peaks in high)
        if sr.breakout['support_break']:
            sub_peak = find_extremes_with_breakouts(ps.high, None, sub_start, sub_end, sub_modes, ExtremeType.PEAK)
            if sub_peak.peaks:
                last = sub_peak.peaks[-1]
                to = TradeOpportunity()
                to.type = ExtremeType.PEAK
                to.start_idx = sub_start
                to.end_idx = sub_end
                to.peaks = sub_peak.peaks
                to.breakouts = sub_peak.breakouts
                to.value = ps.high[last]
                opportunities.append(to)

    return opportunities