"""marketsymbol の定数定義.

このモジュールはシンボルのバリデーションに使用される定数を定義する。
値は ISO 10383 (MIC コード) や内部ビジネスルールに基づく。
"""

from typing import Final

# ISO 10383 MIC コード長
MIC_LENGTH: Final[int] = 4

# コードの最小/最大長 (資産クラスにより異なる: Equity=1-10, Future=2-6, Option=2-10)
# バリデーション時は資産クラスごとの制約を適用すること
MIN_CODE_LENGTH: Final[int] = 1
MAX_CODE_LENGTH: Final[int] = 10

# 限月の長さ (YYYYMMDD 形式)
EXPIRY_LENGTH: Final[int] = 8

# 権利行使価格の最小値
MIN_STRIKE: Final[int] = 1

# シンボル文字列の最大長 (DoS 対策)
MAX_SYMBOL_LENGTH: Final[int] = 100
