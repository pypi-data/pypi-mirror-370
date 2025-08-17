from typing import Any, Dict, List, Set


class UtilObjectHash:
    """
    (en) This is a utility for object hash calculations.
    This makes it easy to calculate hashes, for example
    if you want to enable enableDiffCheck flag in FileStateManager.

    (ja) これはオブジェクトハッシュ計算用のユーティリティです。
    利用することで、FileStateManagerのenableDiffCheckフラグを有効化したい場合などに、
    ハッシュ計算を簡単に行えます。
    """

    @staticmethod
    def calc_map(m: Dict[Any, Any]) -> int:
        """
        (en) Calculate hash code for map. Supports nesting of Maps, Lists, and Sets.
        (ja) Mapのハッシュコードを計算します。Map, List, Setのネストに対応しています。
        """
        r = 17
        for key, value in m.items():
            if isinstance(value, dict):
                r = 37 * r + hash(key)
                r = 37 * r + UtilObjectHash.calc_map(value)
            elif isinstance(value, list):
                r = 37 * r + hash(key)
                r = 37 * r + UtilObjectHash.calc_list(value)
            elif isinstance(value, set):
                r = 37 * r + hash(key)
                r = 37 * r + UtilObjectHash.calc_set(value)
            else:
                r = 37 * r + hash(key)
                r = 37 * r + (hash(value) if value is not None else 0)
        return r

    @staticmethod
    def calc_list(lst: List[Any]) -> int:
        """
        (en) Calculate hash code for list. Supports nesting of Maps, Lists, and Sets.
        (ja) Listのハッシュコードを計算します。Map, List, Setのネストに対応しています。
        """
        r = 17
        for i, v in enumerate(lst):
            if isinstance(v, dict):
                r = 37 * r + (UtilObjectHash.calc_map(v) ^ i)
            elif isinstance(v, list):
                r = 37 * r + (UtilObjectHash.calc_list(v) ^ i)
            elif isinstance(v, set):
                r = 37 * r + (UtilObjectHash.calc_set(v) ^ i)
            else:
                r = 37 * r + ((hash(v) if v is not None else 0) ^ i)
        return r

    @staticmethod
    def calc_set(s: Set[Any]) -> int:
        """
        (en) Calculate hash code for set. Supports nesting of Maps, Lists, and Sets.
        (ja) Setのハッシュコードを計算します。Map, List, Setのネストに対応しています。
        """
        r = 17
        for v in s:
            if isinstance(v, dict):
                r = 37 * r + UtilObjectHash.calc_map(v)
            elif isinstance(v, list):
                r = 37 * r + UtilObjectHash.calc_list(v)
            elif isinstance(v, set):
                r = 37 * r + UtilObjectHash.calc_set(v)
            else:
                r = 37 * r + (hash(v) if v is not None else 0)
        return r
