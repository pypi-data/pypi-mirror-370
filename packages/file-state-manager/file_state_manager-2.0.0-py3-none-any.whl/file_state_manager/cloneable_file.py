from abc import ABC, abstractmethod
from typing import Any, Dict

class CloneableFile(ABC):
    """
    (en) An abstract class that has deep copy and serialization capabilities
    and is managed by the FileStateManager.

    (ja) ディープコピーとシリアライズの機能を持ち、FileStateManagerで管理される抽象クラス。
    """

    def __init__(self):
        """Normal constructor."""
        pass

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> 'CloneableFile':
        """
        (en) Restore this object from the dictionary.
        (ja) このオブジェクトを辞書から復元します。

        Args:
            src (Dict[str, Any]): A dictionary made with to_dict of this class.

        Returns:
            CloneableFile: 復元されたオブジェクト
        """
        raise NotImplementedError("from_dict must be implemented in subclasses")

    @abstractmethod
    def clone(self) -> 'CloneableFile':
        """
        (en) Returns a deep copy of this object.
        (ja) このオブジェクトのディープコピーを返します。
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        (en) Convert the object to a dictionary.
        The returned dictionary can only contain primitive types, null, lists
        or maps with only primitive elements.
        If you want to include other classes,
        the target class should inherit from this class and chain calls to_dict.

        (ja) このオブジェクトを辞書に変換します。
        戻り値の辞書にはプリミティブ型かプリミティブ型要素のみのリスト
        またはマップ等、そしてNoneのみを含められます。
        それ以外のクラスを含めたい場合、対象のクラスもこのクラスを継承し、
        to_dictを連鎖的に呼び出すようにしてください。
        """
        pass
