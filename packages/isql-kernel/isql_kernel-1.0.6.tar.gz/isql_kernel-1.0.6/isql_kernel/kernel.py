import io
from ipykernel.kernelbase import Kernel
from jupyter_client import KernelManager
from queue import Empty
import traceback
import sqlite3
import re
import pandas as pd
import sqlparse
from IPython.display import HTML
import textwrap


class ISQLRouterKernel(Kernel):
    implementation = "isql"
    implementation_version = "1.0"
    banner = "ISQL kernel: route to python3 when #kernel: python is used"
    language_info = {
        "name": "isql",
        "file_extension": ".isql",
        "mimetype": "text/x-isql",
        "codemirror_mode": "isql",
    }





    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initialized = False
        self.conn = None
        self.cursor = None
        self.variables = {}







    def initialize_if_needed(self):
        if not self.initialized:
            self.conn = sqlite3.connect(":memory:")
            self.cursor = self.conn.cursor()
            self.initialized = True






    def _launch_python_kernel(self):
        km = KernelManager(kernel_name="python3")
        km.start_kernel()
        kc = km.client()
        kc.start_channels()
        return {"manager": km, "client": kc}
    







    def _extract_kernel_choice(self, code: str) -> str:
        lines = code.lstrip().splitlines()
        if lines and lines[0].lower().startswith("#kernel:"):
            if lines[0].split(":", 1)[1].strip().lower().startswith("python"):
                return "python"
        return ""
    







    def _strip_first_line(self, code):
        lines = code.splitlines()
        return "\n".join(lines[2:]) if (lines and lines[0].lower().startswith("#kernel:")) else code
    








    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        kernel_choice = self._extract_kernel_choice(code)
        exec_code = self._strip_first_line(code)
        if kernel_choice == "python":
            try:
                if not hasattr(self, "_python"):
                    self._python = self._launch_python_kernel()
                kc = self._python["client"]
                msg_id = kc.execute(exec_code)
                while True:
                    try:
                        msg = kc.get_iopub_msg(timeout=10)
                    except Empty:
                        break
                    if msg["parent_header"].get("msg_id") != msg_id:
                        continue
                    if msg["msg_type"] in {
                        "stream", "display_data", "execute_result", "error", "clear_output"
                    }:
                        if msg["msg_type"] == "execute_result":
                            msg_type = "display_data"
                            content = {
                                "data": msg["content"]["data"],
                                "metadata": msg["content"].get("metadata", {}),
                            }
                        else:
                            msg_type = msg["msg_type"]
                            content = msg["content"]
                        self.session.send(
                            self.iopub_socket, msg_type, content, parent=self._parent_header
                        )
                    elif msg["msg_type"] == "status" and msg["content"].get("execution_state") == "idle":
                        break
                return {
                    'status': 'ok',
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {}
                }
            except Exception as e:
                tb = traceback.format_exc()
                self.send_response(self.iopub_socket, "stream", {
                    "name": "stderr",
                    "text": f"[Router‑Error] {e}\n{tb}"
                })
                return {"status": "error",
                        "execution_count": self.execution_count,
                        "ename": type(e).__name__,
                        "evalue": str(e),
                        "traceback": tb.splitlines()}
        else:
            self.initialize_if_needed()
            code = code.strip()
            statements = [stmt.strip() for stmt in sqlparse.split(code) if stmt.strip()]
            result_output = ""
            try:
                for stmt in statements:
                    match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(SELECT .+)', stmt, re.IGNORECASE | re.DOTALL)
                    try:
                        if match:
                            varname, select_query = match.groups()
                            self.cursor.execute(select_query)
                            columns = [desc[0] for desc in self.cursor.description]
                            rows = self.cursor.fetchall()
                            df = pd.DataFrame(rows, columns=columns)
                            self.variables[varname] = df
                            result_output += f"Stored result in variable '{varname}'\n"
                            self._python = self._launch_python_kernel()
                            python_kc = self._python["client"]
                            csv_buffer = io.StringIO()
                            df.to_csv(csv_buffer, index=False)
                            csv_content = csv_buffer.getvalue()
                            inject_code = textwrap.dedent(f"""
                                import pandas as pd
                                import io
                                {varname} = pd.read_csv(io.StringIO({csv_content!r}))
                            """)
                            msg_id = python_kc.execute(inject_code)
                            while True:
                                msg = python_kc.get_iopub_msg(timeout=5)
                                if msg['parent_header'].get('msg_id') != msg_id:
                                    continue
                                if msg['msg_type'] == 'status' and msg['content'].get('execution_state') == 'idle':
                                    break
                        else:
                            if stmt.upper().startswith("SELECT"):
                                self.cursor.execute(stmt)
                                columns = [desc[0] for desc in self.cursor.description]
                                rows = self.cursor.fetchall()
                                formatted = '\t'.join(columns) + '\n' + '\n'.join(['\t'.join(map(str, row)) for row in rows])
                                result_output += formatted + '\n'
                            else:
                                load_csv_match = re.match(r"LOAD\s+CSV\s+'(.+?)'\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;", stmt, re.IGNORECASE | re.DOTALL)
                                if load_csv_match:
                                    csv_path, table_name = load_csv_match.groups()
                                    try:
                                        df = pd.read_csv(csv_path)
                                        df.to_sql(table_name, self.conn, if_exists='replace', index=False)
                                        result_output += f"Loaded CSV '{csv_path}' into table '{table_name}'\n"
                                    except Exception as e:
                                        return {
                                            'status': 'error',
                                            'execution_count': self.execution_count,
                                            'ename': 'CSV‑Load‑Error',
                                            'evalue': str(e),
                                            'traceback': [str(e)],
                                        }
                                else:
                                    self.cursor.execute(stmt)
                                    self.conn.commit()
                                    result_output += f"Executed: \"{stmt[0:len(stmt)-1]}\"\n"
                    except Exception as e:
                        result_output += f"Error in executing: \"{stmt[0:len(stmt)-1]}\" ---> {str(e)}\n"
                if not silent:
                    s = HTML(f"<pre style='color:#AAAAAA;font-family:monospace;'>{result_output}</pre>")
                    self.send_response(self.iopub_socket,
                        'display_data',
                        {
                            'data': {
                                'text/html': str(s.data)
                            },
                            'metadata': {}
                        }
                    )
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
            except Exception as e:
                return {
                    'status': 'error',
                    'execution_count': self.execution_count,
                    'ename': 'ISQL‑Error',
                    'evalue': str(e),
                    'traceback': [str(e)],
                }





    def do_complete(self, code, cursor_pos):
        kernel_choice = self._extract_kernel_choice(code)
        if kernel_choice == "python":
            code_without_header = self._strip_first_line(code)
            lines = code.splitlines()
            adjustment = sum(len(line) + 1 for line in lines[:2]) if lines and lines[0].lower().startswith("#kernel:") else 0
            adjusted_cursor = max(cursor_pos - adjustment, 0)
            try:
                if not hasattr(self, "_python"):
                    self._python = self._launch_python_kernel()
                kc = self._python["client"]
            except Exception:
                return {
                    'status': 'ok',
                    'matches': [],
                    'cursor_start': cursor_pos,
                    'cursor_end': cursor_pos,
                    'metadata': {},
                }
            msg_id = kc.complete(code_without_header, adjusted_cursor)
            while True:
                try:
                    msg = kc.get_shell_msg(timeout=5)
                except Empty:
                    break
                if msg['parent_header'].get('msg_id') != msg_id:
                    continue
                if msg['msg_type'] == 'complete_reply':
                    content = msg['content']
                    content['cursor_start'] += adjustment
                    content['cursor_end'] += adjustment
                    return content
        return {
            'status': 'ok',
            'matches': [],
            'cursor_start': cursor_pos,
            'cursor_end': cursor_pos,
            'metadata': {},
        }
    




    def do_shutdown(self, restart):
        if hasattr(self, "_python"):
            try:
                self._python["client"].stop_channels()
                self._python["manager"].shutdown_kernel(now=True)
            except Exception:
                pass
        return super().do_shutdown(restart)
