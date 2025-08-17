import unittest
from file_state_manager.file_state_manager_base import FileStateManager
from file_state_manager.cloneable_file import CloneableFile
from file_state_manager.util_object_hash import UtilObjectHash


# -----------------------------
# ExampleClass 定義
# -----------------------------
class ExampleClassChild(CloneableFile):
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    @classmethod
    def from_dict(cls, src: dict):
        return cls(src["message"])

    def clone(self):
        return ExampleClassChild.from_dict(self.to_dict())

    def to_dict(self):
        return {"message": self.message}

    def __eq__(self, other):
        return isinstance(other, ExampleClassChild) and self.message == other.message

    def __hash__(self):
        return hash(self.message)


class ExampleClass(CloneableFile):
    def __init__(self, count: int, child: ExampleClassChild):
        super().__init__()
        self.count = count
        self.child = child

    @classmethod
    def from_dict(cls, src: dict):
        return cls(src["count"], ExampleClassChild.from_dict(src["child"]))

    def clone(self):
        return ExampleClass.from_dict(self.to_dict())

    def to_dict(self):
        return {"count": self.count, "child": self.child.to_dict()}

    def __eq__(self, other):
        return isinstance(other, ExampleClass) and self.count == other.count and self.child == other.child

    def __hash__(self):
        return hash((self.count, self.child))


# -----------------------------
# unittest
# -----------------------------
class TestFileStateManager(unittest.TestCase):
    def test_undo_redo(self):
        save_file = ExampleClass(0, ExampleClassChild("First State"))
        fsm = FileStateManager(save_file, stack_size=None)
        self.assertFalse(fsm.can_undo())

        save_file.child.message = "Second State"
        fsm.push(save_file)
        self.assertTrue(fsm.can_undo())
        self.assertFalse(fsm.can_redo())
        self.assertIsNone(fsm.redo())
        self.assertEqual(fsm.undo().child.message, "First State")
        self.assertTrue(fsm.can_redo())
        self.assertEqual(fsm.redo().child.message, "Second State")

        fsm.undo()
        save_file.child.message = "Third State"
        fsm.push(save_file)
        self.assertTrue(fsm.can_undo())
        self.assertEqual(fsm.undo().child.message, "First State")
        self.assertTrue(fsm.can_redo())
        self.assertEqual(fsm.redo().child.message, "Third State")
        fsm.undo()
        self.assertFalse(fsm.can_undo())
        self.assertIsNone(fsm.undo())

    def test_stack_size(self):
        save_file = ExampleClass(0, ExampleClassChild("First State"))
        fsm = FileStateManager(save_file, stack_size=2)
        save_file.child.message = "Second State"
        fsm.push(save_file)
        self.assertTrue(fsm.can_undo())
        self.assertEqual(fsm.undo().child.message, "First State")
        self.assertTrue(fsm.can_redo())
        self.assertEqual(fsm.redo().child.message, "Second State")
        save_file.child.message = "Third State"
        fsm.push(save_file)
        self.assertTrue(fsm.can_undo())
        self.assertEqual(fsm.undo().child.message, "Second State")
        self.assertTrue(fsm.can_redo())
        self.assertEqual(fsm.redo().child.message, "Third State")
        self.assertTrue(fsm.can_undo())
        self.assertEqual(fsm.undo().child.message, "Second State")
        self.assertFalse(fsm.can_undo())

    def test_history_restore(self):
        save_file = ExampleClass(0, ExampleClassChild("First State"))
        fsm = FileStateManager(save_file, stack_size=30)
        save_file.child.message = "Second State"
        fsm.push(save_file)

        # Save and restore history
        history = [i.to_dict() for i in fsm.get_stack()]
        restored_history = [ExampleClass.from_dict(i) for i in history]
        restored_fsm = FileStateManager(restored_history.pop(0), stack_size=30)
        for i in restored_history:
            restored_fsm.push(i)

        restored_now_state = restored_fsm.now()
        self.assertEqual(restored_now_state.child.message, "Second State")
        self.assertTrue(restored_fsm.can_undo())
        if restored_fsm.can_undo():
            self.assertEqual(restored_fsm.undo().child.message, "First State")

    def test_enable_diff_check(self):
        # non-enabled test
        save_file1 = ExampleClass(0, ExampleClassChild("First State"))
        save_file1_clone = save_file1.clone()
        self.assertEqual(hash(save_file1), hash(save_file1_clone))
        self.assertEqual(save_file1, save_file1_clone)

        fsm1 = FileStateManager(save_file1, stack_size=30)
        save_file1.child.message = "Second State"
        self.assertNotEqual(hash(save_file1), hash(save_file1_clone))
        self.assertNotEqual(save_file1, save_file1_clone)
        fsm1.push(save_file1)
        pre_index1 = fsm1.now_index()
        fsm1.push(save_file1)
        self.assertNotEqual(pre_index1, fsm1.now_index())
        save_file1.child.message = "Third State"
        fsm1.push(save_file1)
        self.assertNotEqual(pre_index1, fsm1.now_index())

        # enabled test
        save_file2 = ExampleClass(0, ExampleClassChild("First State"))
        fsm2 = FileStateManager(save_file2, stack_size=30, enable_diff_check=True)
        save_file2.child.message = "Second State"
        fsm2.push(save_file2)
        pre_index2 = fsm2.now_index()
        fsm2.push(save_file2)
        self.assertEqual(pre_index2, fsm2.now_index())
        save_file2.child.message = "Third State"
        fsm2.push(save_file2)
        self.assertNotEqual(pre_index2, fsm2.now_index())

        self.assertEqual(fsm2.undo().child.message, "Second State")
        self.assertEqual(fsm2.redo().child.message, "Third State")

    def test_skip_next_push(self):
        save_file1 = ExampleClass(0, ExampleClassChild("First State"))
        fsm1 = FileStateManager(save_file1, stack_size=30)
        self.assertEqual(fsm1.now_index(), 0)
        save_file1.child.message = "Second State"
        fsm1.push(save_file1)
        self.assertEqual(fsm1.now_index(), 1)
        save_file1.child.message = "Third State"
        fsm1.skip_next_push()
        fsm1.push(save_file1)
        self.assertEqual(fsm1.now_index(), 1)
        fsm1.push(save_file1)
        self.assertEqual(fsm1.now_index(), 2)


class TestUtilObjectHash(unittest.TestCase):
    def test_util_object_hash(self):
        m1 = {"a": "a"}
        m2 = {"a": "a"}
        m3 = {"a": "b"}
        m4 = {"b": "a"}
        m5 = {"a": "a", "b": "b"}

        self.assertEqual(UtilObjectHash.calc_map(m1), UtilObjectHash.calc_map(m2))
        self.assertNotEqual(UtilObjectHash.calc_map(m1), UtilObjectHash.calc_map(m3))
        self.assertNotEqual(UtilObjectHash.calc_map(m1), UtilObjectHash.calc_map(m4))
        self.assertNotEqual(UtilObjectHash.calc_map(m1), UtilObjectHash.calc_map(m5))

        m6 = {"a": {"a": 1}}
        m7 = {"a": {"a": 1}}
        m8 = {"a": {"a": 2}}
        m9 = {"b": {"a": 1}}
        m10 = {"a": {"a": 1}, "b": {"a": 1}}
        self.assertEqual(UtilObjectHash.calc_map(m6), UtilObjectHash.calc_map(m7))
        self.assertNotEqual(UtilObjectHash.calc_map(m6), UtilObjectHash.calc_map(m8))
        self.assertNotEqual(UtilObjectHash.calc_map(m6), UtilObjectHash.calc_map(m9))
        self.assertNotEqual(UtilObjectHash.calc_map(m6), UtilObjectHash.calc_map(m10))

        l1 = ["a"]
        l2 = ["a"]
        l3 = ["b"]
        l4 = ["a", "b"]
        self.assertEqual(UtilObjectHash.calc_list(l1), UtilObjectHash.calc_list(l2))
        self.assertNotEqual(UtilObjectHash.calc_list(l1), UtilObjectHash.calc_list(l3))
        self.assertNotEqual(UtilObjectHash.calc_list(l1), UtilObjectHash.calc_list(l4))

        l6 = [[1]]
        l7 = [[1]]
        l8 = [[2]]
        l9 = [[1], [1]]
        self.assertEqual(UtilObjectHash.calc_list(l6), UtilObjectHash.calc_list(l7))
        self.assertNotEqual(UtilObjectHash.calc_list(l6), UtilObjectHash.calc_list(l8))
        self.assertNotEqual(UtilObjectHash.calc_list(l6), UtilObjectHash.calc_list(l9))

        s1 = {"a"}
        s2 = {"a"}
        s3 = {"b"}
        s4 = {"a", "b"}
        self.assertEqual(UtilObjectHash.calc_set(s1), UtilObjectHash.calc_set(s2))
        self.assertNotEqual(UtilObjectHash.calc_set(s1), UtilObjectHash.calc_set(s3))
        self.assertNotEqual(UtilObjectHash.calc_set(s1), UtilObjectHash.calc_set(s4))

        s6 = {frozenset({1})}
        s7 = {frozenset({1})}
        s8 = {frozenset({2})}
        s9 = {frozenset({1}), frozenset({2})}
        self.assertEqual(UtilObjectHash.calc_set(s6), UtilObjectHash.calc_set(s7))
        self.assertNotEqual(UtilObjectHash.calc_set(s6), UtilObjectHash.calc_set(s8))
        self.assertNotEqual(UtilObjectHash.calc_set(s6), UtilObjectHash.calc_set(s9))


if __name__ == "__main__":
    unittest.main()
