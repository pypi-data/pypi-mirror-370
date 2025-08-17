from typing import List, Optional
from .cloneable_file import CloneableFile


class FileStateManager:
    """
    (en) This is a manager class that allows you to Undo and Redo
    complex file changes.
    (ja) 複雑なファイルの変更をUndo,Redoできるようにするためのマネージャクラスです。
    """

    def __init__(self, f: CloneableFile, stack_size: Optional[int] = None, enable_diff_check: bool = False):
        """
        Args:
            f (CloneableFile): A managed file. Can be new or loaded.
            stack_size (Optional[int]): Maximum stack size. None for unlimited.
            enable_diff_check (bool): Whether to skip unchanged pushes (requires __eq__ and __hash__ in files)
        """
        self._ur_stack: List[CloneableFile] = []
        self._now_index: int = -1
        self.stack_size: Optional[int] = stack_size
        self.enable_diff_check: bool = enable_diff_check
        self._skip_next: bool = False

        self.push(f)

    def push(self, f: CloneableFile):
        """
        (en) Adds elements that have been changed.
        (ja) 変更が加えられた要素を追加します。
        """
        if self._skip_next:
            self._skip_next = False
            return

        if self.enable_diff_check and self._ur_stack:
            if self._ur_stack[self._now_index] == f:
                return

        cloned_data = f.clone()

        # スタック内に収まるように調整
        if self.stack_size is None:
            self._now_index += 1
        else:
            if self._now_index < self.stack_size - 1:
                self._now_index += 1
            else:
                self._ur_stack.pop(0)

        # 新しいデータを追加し、以降のデータがあれば削除
        if self._now_index < len(self._ur_stack):
            self._ur_stack[self._now_index] = cloned_data
            # 余分なデータを削除
            del self._ur_stack[self._now_index + 1:]
        else:
            self._ur_stack.append(cloned_data)

    def skip_next_push(self):
        """
        (en) Calling this will disable the next push.
        (ja) これを呼び出すと、次回のpushが無効化されます。
        """
        self._skip_next = True

    def can_undo(self) -> bool:
        """
        (en) Returns true only if Undo is possible.
        (ja) Undo可能な場合のみtrueを返します。
        """
        return len(self._ur_stack) >= 2 and self._now_index >= 1

    def can_redo(self) -> bool:
        """
        (en) Returns true only if Redo is possible.
        (ja) Redo可能な場合のみtrueを返します。
        """
        return self._now_index < len(self._ur_stack) - 1

    def undo(self) -> Optional[CloneableFile]:
        """
        (en) Returns the previously pushed data.
        (ja) １つ前にpushされたデータを返します。
        """
        if self.can_undo():
            self._now_index -= 1
            return self._ur_stack[self._now_index].clone()
        return None

    def redo(self) -> Optional[CloneableFile]:
        """
        (en) Returns the next pushed data.
        (ja) １つ後にpushされたデータを返します。
        """
        if self.can_redo():
            self._now_index += 1
            return self._ur_stack[self._now_index].clone()
        return None

    def now(self) -> Optional[CloneableFile]:
        """
        (en) Returns the now data.
        (ja) 現在のデータを返します。
        """
        if 0 <= self._now_index < len(self._ur_stack):
            return self._ur_stack[self._now_index].clone()
        return None

    def now_index(self) -> int:
        """
        (en) Returns the current index into the stack.
        (ja) 現在スタックのどこを参照しているのかという、インデックスを返します。
        """
        return self._now_index

    def get_stack(self) -> List[CloneableFile]:
        """
        (en) Returns a reference to the stack maintained by this class.
        (ja) このクラスで保持しているスタックの参照を返します。
        """
        return self._ur_stack
