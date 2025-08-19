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
    def __init__(self, universe: str):
        super().__init__()

        self.adapter = DataAdapter(
            universe, 20150101, int(datetime.now().strftime("%Y%m%d"))
        )
        self.simulator = Simulator(
            cast(AVAILABLE_MARKETS, universe),
            start=20150101,
            end=int(
                datetime.now().strftime("%Y%m%d"),
            ),
        )

        self.signal: pd.DataFrame = pd.DataFrame()
        self.position: pd.DataFrame = pd.DataFrame()

    @abstractmethod
    def register_data(self):
        pass

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

            # long/short 분리
            long_signal = self.signal[self.signal > 0].fillna(0)
            short_signal = self.signal[self.signal < 0].fillna(0).abs()

            for idx in self.signal.index[over_exposed]:
                long_row = long_signal.loc[idx]
                short_row = short_signal.loc[idx]

                long_sum = long_row.sum()
                short_sum = short_row.sum()
                total_sum = long_sum + short_sum

                if total_sum > 0:
                    # 비율 유지하면서 전체 합을 1로 조정
                    scale_factor = 1.0 / total_sum

                    if long_sum > 0:
                        long_signal.loc[idx] = long_row * scale_factor
                    if short_sum > 0:
                        short_signal.loc[idx] = short_row * scale_factor

            # 최종 시그널 재구성 (over_exposed인 날만 업데이트)
            self.signal[over_exposed] = (long_signal - short_signal)[over_exposed]

        # 검증
        final_abs_sum = self.signal.abs().sum(axis=1)
        print(f"Max exposure: {final_abs_sum.max():.4f}")
        print(
            f"Days with exposure <= 1.0: {(final_abs_sum <= 1.0001).sum()} / {len(final_abs_sum)}"
        )
        print("-" * 50)

    def get(self, start: int, end: int):
        self.register_data()
        self._cache_data()
        self.adapter.info()

        signal_list = []

        for t in tqdm(self.stock_data.T):
            signal_t = self.step(t)
            signal_list.append(signal_t)

        self.signal = pd.DataFrame(
            signal_list,
            index=self.stock_data.T,
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
