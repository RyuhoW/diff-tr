from dataclasses import dataclass
from typing import List, Dict, Any
from data_models import ExecutionTrace


@dataclass
class Diff:
    """差分を表す汎用クラス"""

    type: str
    path: List[str]
    old_value: Any = None
    new_value: Any = None


class TraceComparator:
    """二つのExecutionTraceオブジェクトを比較する"""

    def __init__(self, trace1: ExecutionTrace, trace2: ExecutionTrace):
        self.trace1 = trace1
        self.trace2 = trace2
        self.diffs: List = []

    def compare(self) -> List:
        """比較を実行し、差分のリストを返す"""
        self._compare_phases()
        return self.diffs

    def _compare_phases(self):
        """実行フェーズを比較する"""
        phases1 = {p.name: p for p in self.trace1.phases}
        phases2 = {p.name: p for p in self.trace2.phases}

        for name, phase1 in phases1.items():
            if name not in phases2:
                self.diffs.append(Diff(type="removed", path=["phase", name]))
            else:
                self._compare_operations(phase1, phases2[name])

        for name in phases2:
            if name not in phases1:
                self.diffs.append(Diff(type="added", path=["phase", name]))

    def _compare_operations(self, phase1, phase2):
        """特定フェーズ内のリソース操作を比較する"""
        ops1 = phase1.operations
        ops2 = phase2.operations

    def _compare_events(self, events1, events2):
        """イベントシーケンスを比較する"""

    def _diff_payloads(self, payload1: Dict, payload2: Dict, path: List[str]) -> List:
        """ペイロード（辞書）を再帰的に比較する"""
        return []
