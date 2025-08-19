import json
import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecutorInfo:
    id: str
    pid: int
    port: int
    status: str
    start_time: float
    end_time: float | None = None
    error_message: str | None = None


class ExecutorInfoLogger:
    def __init__(self, log_dir: Path):
        self.logs_dir = log_dir / "executor"
        self.info_file_name = "info.json"

    def create_executor_logs_dir(self, executor_id: str) -> Path:
        executor_dir = self.logs_dir / executor_id
        executor_dir.mkdir(parents=True, exist_ok=True)

        return executor_dir

    def write_executor_info(self, executor_info: ExecutorInfo):
        executor_dir = self.create_executor_logs_dir(executor_info.id)
        info_file = executor_dir / self.info_file_name

        data = {
            "id": executor_info.id,
            "pid": executor_info.pid,
            "port": executor_info.port,
            "status": executor_info.status,
            "start_time": executor_info.start_time,
            "end_time": executor_info.end_time,
            "error_message": executor_info.error_message,
        }

        with info_file.open("w") as f:
            json.dump(data, f, indent=2)
            f.flush()

    def read_executor_info(self, executor_id: str) -> ExecutorInfo | None:
        try:
            executor_dir = self.logs_dir / executor_id
            info_file = executor_dir / self.info_file_name

            if not info_file.exists():
                return None

            with open(info_file) as f:
                data = json.load(f)

            if not data:
                return None

            return ExecutorInfo(
                id=data["id"],
                pid=data["pid"],
                port=data["port"],
                status=data["status"],
                start_time=data["start_time"],
                end_time=data.get("end_time"),
                error_message=data.get("error_message"),
            )

        except Exception as e:
            print(f"Failed to read executor info: {e}")
            return None

    def update_executor_info(
        self,
        executor_id: str,
        status: str,
        error_message: str | None = None,
        end_time: float | None = None,
    ) -> None:
        info_file = self.logs_dir / executor_id / self.info_file_name

        if not info_file.exists():
            return

        # Read current info
        with open(info_file) as f:
            current_info = json.load(f)

        if not current_info:
            return

        # Update fields
        current_info["status"] = status
        if error_message:
            current_info["error_message"] = error_message
        if end_time:
            current_info["end_time"] = end_time

        # Write
        with open(info_file, "w") as f:
            json.dump(current_info, f)

    def cleanup_logs(self) -> None:
        if not self.logs_dir.exists():
            return

        for dir in self.logs_dir.iterdir():
            if dir.is_dir():
                shutil.rmtree(dir)
