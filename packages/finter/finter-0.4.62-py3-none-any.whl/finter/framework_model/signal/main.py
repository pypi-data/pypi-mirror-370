import bisect
from abc import abstractmethod
from datetime import datetime
from typing import cast

import numpy as np
import pandas as pd
from tqdm import tqdm

from finter.backtest import Simulator
from finter.backtest.config.config import AVAILABLE_MARKETS
from finter.data.manager.adaptor import DataAdapter
from finter.data.manager.type import DataType
from finter.framework_model.alpha import BaseAlpha


class BaseSignal(BaseAlpha):
    def __init__(self):
        super().__init__()

        self._initialized = False

        self.last_date: int = int(datetime.now().strftime("%Y%m%d"))

        self.universe: str
        self.data_list: list
        self.first_date: int
        self.lookback_window: int

        self.adapter: DataAdapter
        self.simulator: Simulator

        self.signal: pd.DataFrame
        self.position: pd.DataFrame

        self.setup()

    @abstractmethod
    def config(self):
        """
        설정 메서드 - 사용자가 구현
        Args:
            universe: 유니버스 ("kr_stock", "us_stock" 등)
            start: 시작일
            end: 종료일
            data_list: 기본 데이터 리스트 (["close", "volume"] 등)

        self.universe = universe
        self.first_date = first_date
        self.data_list = data_list
        """
        pass

    def setup(self):
        self.config()

        params = {
            "universe": self.universe,
            "data_list": self.data_list,
            "first_date": self.first_date,
            "lookback_window": self.lookback_window,
        }
        if missing := [k for k, v in params.items() if not v]:
            raise ValueError(
                f"setup() must be called first or provide the following parameters: {', '.join(missing)}"
            )

        self.adapter = DataAdapter(self.universe, self.first_date, self.last_date)
        self.adapter.add(self.data_list)

        # self.adapter.add_data("window", 1, "static")

        self.simulator = Simulator(
            cast(AVAILABLE_MARKETS, self.universe),
            start=self.first_date,
            end=self.last_date,
        )

        # 데이터 캐싱 및 초기화 완료
        self._cache_data()
        self.adapter.info()
        self._initialized = True

    @abstractmethod
    def step(self, t: datetime) -> np.ndarray:  # (N)
        pass

    def _cache_data(self):
        if DataType.STOCK in self.adapter.dm.data:
            self.stock_data = self.adapter.stock
        if DataType.MACRO in self.adapter.dm.data:
            self.macro_data = self.adapter.macro
        if DataType.ENTITY in self.adapter.dm.data:
            self.entity_data = self.adapter.entity
        if DataType.STATIC in self.adapter.dm.data:
            self.static_data = self.adapter.static

    def _normalize_signal(self):
        print("normalizing signal")

        # 각 행의 절대값 합 계산
        abs_sum = self.signal.abs().sum(axis=1)

        # 1보다 큰 날만 찾기
        over_exposed = abs_sum > 1.0

        if over_exposed.any():
            print(f"Normalizing {over_exposed.sum()} days with exposure > 1.0")

            # 벡터화된 연산으로 처리
            # over_exposed인 행들만 선택
            over_exposed_signals = self.signal[over_exposed]

            # long/short 분리 (over_exposed 행들만)
            long_mask = over_exposed_signals > 0
            short_mask = over_exposed_signals < 0

            # 각 행의 long/short 합계 계산
            long_sum = (over_exposed_signals * long_mask).sum(axis=1)
            short_sum = (over_exposed_signals * short_mask).abs().sum(axis=1)
            total_sum = long_sum + short_sum

            # total_sum이 0이 아닌 경우만 정규화
            valid_mask = total_sum > 0

            # 스케일 팩터 계산 (벡터화)
            scale_factors = pd.Series(0.0, index=over_exposed_signals.index)
            scale_factors[valid_mask] = 1.0 / total_sum[valid_mask]

            # 정규화 적용 (브로드캐스팅 사용)
            normalized_signals = over_exposed_signals.multiply(scale_factors, axis=0)

            # 원본 시그널 업데이트
            self.signal = pd.concat(
                [self.signal[~over_exposed], normalized_signals]
            ).sort_index()

        # 검증
        final_abs_sum = self.signal.abs().sum(axis=1)
        print(f"Max exposure: {final_abs_sum.max():.4f}")
        print(
            f"Days with exposure <= 1.0: {(final_abs_sum <= 1.0001).sum()} / {len(final_abs_sum)}"
        )
        print("-" * 50)

    def get(self, start: int, end: int):
        start_date = pd.Timestamp(datetime.strptime(str(start), "%Y%m%d"))
        end_date = pd.Timestamp(datetime.strptime(str(end), "%Y%m%d"))

        # start, end 날짜의 인덱스 찾기
        start_pos = bisect.bisect_left(self.stock_data.T, start_date)
        end_pos = bisect.bisect_right(self.stock_data.T, end_date)

        # 검증: start_pos - lookback_window가 음수인 경우
        if start_pos < self.lookback_window:
            first_available_date = self.stock_data.T[self.lookback_window]
            raise ValueError(
                f"Start date {start} requires lookback from index {start_pos - self.lookback_window}, "
                f"but data starts at index 0. "
                f"Please use start date >= {first_available_date.strftime('%Y%m%d')} "
                f"(requires {self.lookback_window} days of lookback)"
            )

        # start~end 기간만큼의 신호 배열 초기화
        signal_list = []
        date_index = []

        # start부터 end까지만 계산
        for idx in tqdm(
            range(start_pos, min(end_pos, len(self.stock_data.T))),
            desc=f"Calculating signals from {start} to {end}",
        ):
            t = self.stock_data.T[idx]
            signal_t = self.step(t)
            if signal_t.ndim != 1:
                raise ValueError(
                    f"step() must be 1D array, but got {signal_t.ndim}D array. shape: {signal_t.shape}"
                )
            signal_list.append(signal_t)
            date_index.append(t)

        # start~end 기간만의 DataFrame 생성
        self.signal = pd.DataFrame(
            signal_list,
            index=date_index,
            columns=list(self.stock_data.N),
        )

        if self.signal.abs().sum(axis=1).any() > 1.0:
            print("some signal is over exposure")
        if self.signal.abs().sum(axis=1).any() < 1.0:
            print("some signal is under exposure")

        self._normalize_signal()

        assert (self.signal.abs().sum(axis=1) <= 1.01).all(), (
            "signal sum must be less than 1.0"
        )

        self.position = (
            (self.signal * 1e8)
            .shift()
            .replace(0, np.nan)
            .dropna(how="all", axis=1)[str(start) : str(end)]
        )

        return self.position

    def backtest(self, start: int, end: int):
        position = self.get(start, end)
        simulator = self.simulator.run(position)

        print(simulator.statistics)
        return simulator
