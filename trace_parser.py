# trace_parser.py
import re

# import json
from typing import IO, Dict, Optional
from data_models import ExecutionTrace, ExecutionPhase, ResourceOperation, ProviderCall


# 正規表現パターンの定義
# 例: 2023-10-27T10:30:00.123Z [provider.stdio]...
LOG_LINE_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)\s+"
    r"\[(?P<level>\w+)\]\s+(?P<source>[^:]+):\s+(?P<message>.*)$"
)

# gRPCコールのような複数行にまたがるイベントを追跡するための正規表現
GRPC_REQ_RE = re.compile(
    r"grpc: SERVER_US:\s+(?P<method>/\w+\.\w+/\w+)\s+body=(?P<json_body>.+)"
)
GRPC_RESP_RE = re.compile(
    r"grpc: CLIENT_US:\s+(?P<method>/\w+\.\w+/\w+)\s+body=(?P<json_body>.+)"
)

# リソース操作を特定するための正規表現
APPLY_START_RE = re.compile(r'Applied resource "(?P<address>[^"]+)"')


class TraceParser:
    """
    Terraformトレースログファイルを解析し、ExecutionTraceオブジェクトを構築する。
    ステートフルなパーサーとして、進行中の操作を追跡する。
    """

    def __init__(self, log_file: IO[str]):
        self.log_file = log_file
        self.trace = ExecutionTrace(phases=[])
        self._current_phase: Optional[ExecutionPhase] = None
        self._current_operations: Dict = {}
        # 進行中のgRPCコールなどを追跡するための状態変数
        self._pending_grpc_calls: Dict[str, ProviderCall] = {}

    def parse(self) -> ExecutionTrace:
        """ログファイルの解析を実行するメインメソッド"""
        for line in self.log_file:
            self._parse_line(line.strip())
        return self.trace

    def _parse_line(self, line: str):
        """ログの各行を解析し、状態を更新する"""
        match = LOG_LINE_RE.match(line)
        if not match:
            return

        data = match.groupdict()
        source = data["source"]
        message = data["message"]

        self._detect_phase_change(message)

        if source == "provider.stdio":
            self._handle_grpc_log(message)
        elif source.startswith("provider-"):
            self._handle_provider_log(message)
        elif source == "http.Tracer":
            self._handle_http_log(message)
        else:  # Terraform Coreなど
            self._handle_core_log(message)

    def _detect_phase_change(self, message: str):
        """ログメッセージから実行フェーズの変化を検出する"""
        if "starting plan" in message:
            self._current_phase = ExecutionPhase(name="plan", operations={})
            self.trace.phases.append(self._current_phase)
        elif "Terraform will perform the following actions:" in message:
            # Planが完了し、Applyが始まる前の確認フェーズ
            pass
        elif "Apply complete!" in message:
            self._current_phase = None

    def _handle_grpc_log(self, message: str):
        """gRPCプロトコルログを処理する"""
        # ここにgRPCリクエストとレスポンスをマッチングさせるロジックを実装
        # 例: リクエストを検出したら_pending_grpc_callsに追加し、
        #     レスポンスを検出したら対応するリクエストと結合してProviderCallオブジェクトを作成
        pass

    def _handle_provider_log(self, message: str):
        """プロバイダー固有のログを処理する"""
        # 将来的な拡張ポイント：プロバイダー固有デコーダーを呼び出す
        pass

    def _handle_http_log(self, message: str):
        """HTTPクライアントログを処理する"""
        # HTTPリクエストとレスポンスを解析し、ApiRequestオブジェクトを作成するロジック
        pass

    def _handle_core_log(self, message: str):
        """Terraform Coreのログを処理する"""
        apply_match = APPLY_START_RE.search(message)
        if apply_match and self._current_phase:
            address = apply_match.group("address")
            if address not in self._current_phase.operations:
                self._current_phase.operations[address] = ResourceOperation(
                    address=address, events=[]
                )
            # 現在の操作対象リソースを更新
            # ...
