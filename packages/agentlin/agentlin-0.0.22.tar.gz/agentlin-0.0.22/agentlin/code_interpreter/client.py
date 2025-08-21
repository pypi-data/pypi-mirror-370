from typing_extensions import Literal, Optional, Dict, Any, List
import json
import requests
import uuid

class JupyterClient:
    """Client for interacting with Jupyter kernels"""

    def __init__(
        self,
        jupyter_host: str = "localhost",
        jupyter_port: int = 8888,
        jupyter_token: str = "jupyter_server_token",
    ):
        self.jupyter_host = jupyter_host
        self.jupyter_port = jupyter_port
        self.jupyter_token = jupyter_token
        self.jupyter_base_url = f"http://{jupyter_host}:{jupyter_port}"
        self.session = requests.Session()

    def _get_jupyter_headers(self):
        return {"Authorization": f"token {self.jupyter_token}"}

    def list_kernels(self) -> List[Dict[str, Any]]:
        """Lists all running kernels."""
        url = f"{self.jupyter_base_url}/api/kernels"
        try:
            response = self.session.get(url, headers=self._get_jupyter_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to list kernels: {e}") from e

    def create_kernel(self, kernel_spec_name: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new kernel."""
        url = f"{self.jupyter_base_url}/api/kernels"
        payload = {}
        if kernel_spec_name:
            payload["name"] = kernel_spec_name
        try:
            response = self.session.post(url, headers=self._get_jupyter_headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to create kernel: {e}") from e

    def get_kernel_info(self, kernel_id: str) -> Dict[str, Any]:
        """Gets information about a specific kernel."""
        url = f"{self.jupyter_base_url}/api/kernels/{kernel_id}"
        try:
            response = self.session.get(url, headers=self._get_jupyter_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get kernel info for {kernel_id}: {e}") from e

    def delete_kernel(self, kernel_id: str):
        """Deletes a kernel."""
        url = f"{self.jupyter_base_url}/api/kernels/{kernel_id}"
        try:
            response = self.session.delete(url, headers=self._get_jupyter_headers())
            response.raise_for_status()
            # DELETE returns 204 No Content on success, so no return value
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to delete kernel {kernel_id}: {e}") from e

    def get_kernel_id(self) -> Optional[str]:
        """
        Gets an available kernel ID.
        If a kernel is running, it returns the first one.
        If not, it creates a new one.
        """
        kernels = self.list_kernels()
        if kernels:
            return kernels[0].get("id")

        kernel_info = self.create_kernel()
        return kernel_info.get("id")

    def restart_kernel(self, kernel_id: Optional[str] = None) -> Dict[str, Any]:
        if not kernel_id:
            kernels = self.list_kernels()
            if kernels:
                for kernel in kernels:
                    self.delete_kernel(kernel.get("id"))
        else:
            self.delete_kernel(kernel_id)
        return self.get_kernel_id()

    def close(self):
        """Closes the underlying requests session."""
        self.session.close()


class CodeInterpreterClient(JupyterClient):
    """Client for interacting with code interpreter service"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8889,
        jupyter_host: str = "localhost",
        jupyter_port: int = 8888,
        jupyter_token: str = "jupyter_server_token",
    ):
        super().__init__(jupyter_host, jupyter_port, jupyter_token)
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    def execute_code(
        self,
        code: str,
        mode: Literal["simple", "full", "debug"] = "full",
        kernel_id: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """
        Executes code using the code interpreter service.
        """
        if not kernel_id:
            kernel_id = self.get_kernel_id()
            if not kernel_id:
                raise RuntimeError("Could not get or create a Jupyter kernel.")

        url = f"{self.base_url}/api/v2/execute"
        payload = {
            "kernel_id": kernel_id,
            "code": code,
            "mode": mode,
            "timeout": timeout,
            "jupyter_host": self.jupyter_host,
            "jupyter_port": str(self.jupyter_port),
            "jupyter_token": self.jupyter_token,
            "jupyter_timeout": timeout,
            "session_id": session_id or str(uuid.uuid4()),
        }

        try:
            response = self.session.post(url, json=payload, timeout=timeout + 5)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            raise RuntimeError(f"Failed to connect to code interpreter service: {e}") from e


    def streaming_execute_code(
        self,
        code: str,
        mode: Literal["simple", "full", "debug"] = "full",
        kernel_id: Optional[str] = None,
        session_id: Optional[str] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """
        Executes code using the code interpreter service.
        """
        if not kernel_id:
            kernel_id = self.get_kernel_id()
            if not kernel_id:
                raise RuntimeError("Could not get or create a Jupyter kernel.")

        url = f"{self.base_url}/streaming_execute"
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }
        payload = {
            "kernel_id": kernel_id,
            "code": code,
            "mode": mode,
            "timeout": timeout,
            "jupyter_host": self.jupyter_host,
            "jupyter_port": str(self.jupyter_port),
            "jupyter_token": self.jupyter_token,
            "jupyter_timeout": timeout,
            "session_id": session_id or str(uuid.uuid4()),
        }

        try:
            from sseclient import SSEClient
            response = self.session.post(url, json=payload, timeout=timeout + 5, stream=True, headers=headers)
            client = SSEClient(response)

            # 迭代接收事件
            for event in client.events():
                print(f"事件类型: {event.event}")
                print(f"数据内容: {event.data}")
        except requests.exceptions.RequestException as e:
            # Handle connection errors, timeouts, etc.
            raise RuntimeError(f"Failed to connect to code interpreter service: {e}\nEnsure you have this installed: pip install sseclient-py") from e


def run_code(
    code: str,
    kernel_id: Optional[str] = None,
    mode: Literal["simple", "full", "debug"] = "full",
    host: str = "localhost",
    port: int = 8889,
    jupyter_host: str = "localhost",
    jupyter_port: int = 8888,
    jupyter_token: str = "jupyter_server_token",
    jupyter_timeout: int = 60,
):
    client = CodeInterpreterClient(
        host=host,
        port=port,
        jupyter_host=jupyter_host,
        jupyter_port=jupyter_port,
        jupyter_token=jupyter_token,
    )
    resp = client.execute_code(code=code, kernel_id=kernel_id, mode=mode, timeout=jupyter_timeout)
    print(json.dumps(resp, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Example usage:
    # Make sure the code_interpreter.py server is running.
    # You might need to start a jupyter server and get a kernel_id first.

    # 1. Start Jupyter server:
    # jupyter notebook --no-browser --port 8888 --NotebookApp.token='jupyter_server_token'

    # 2. This script will now create and manage the kernel.

    client = CodeInterpreterClient(
        port=8889,
        jupyter_port=8888,
        jupyter_token="jupyter_server_token",
    )

    kernel_id_to_delete = None
    try:
        print("Executing code (kernel will be auto-managed)...")

        # We don't need to provide kernel_id, the client will handle it.
        code_to_run = "print('Hello, from Code Interpreter Client!')\nimport numpy as np\nnp.arange(10)"
        result = client.execute_code(code=code_to_run)

        print("\nExecution Result:")
        import json

        print(json.dumps(result, indent=2))

        run_code("print('Hello, World!')")

        # Clean up any kernel that might have been created
        kernels = client.list_kernels()
        if kernels:
            kernel_id_to_delete = kernels[0].get("id")

    except (ValueError, RuntimeError, requests.exceptions.RequestException) as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if kernel_id_to_delete:
            print(f"\nDeleting kernel {kernel_id_to_delete}...")
            try:
                client.delete_kernel(kernel_id_to_delete)
                print(f"Successfully deleted kernel {kernel_id_to_delete}.")
            except (RuntimeError, requests.exceptions.RequestException) as e:
                print(f"Error deleting kernel: {e}")
        client.close()
        print("\nClient closed.")
