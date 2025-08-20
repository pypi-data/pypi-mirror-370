# -*- coding: utf-8 -*-

import sqlite3
import sys
import time
import logging
import re
import argparse
from tabulate import tabulate

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.sql import SqlLexer
from prompt_toolkit.styles.pygments import style_from_pygments_dict
from pygments.token import Token
from pygments.styles import get_style_by_name

# --- 以下所有函数与 V0.9 相同 ---
def setup_logging():
    logger = logging.getLogger()
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler('workbench.log', mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def print_error_report(sql, error):
    print(f"\n{'='*20} [ SQL执行错误 ] {'='*20}")
    print(f"| 错误类型: {type(error).__name__}\n| 错误信息: {error}")
    print(f"| 您尝试执行的SQL语句是:\n| > {sql}\n{'='*58}\n")
    ai_helper_prompt = f"""
我正在使用SQLite3，尝试执行以下SQL语句时遇到了问题：
**SQL语句:**\n```sql\n{sql}\n```\n**收到的错误信息是:**\n```\n{error}\n```
请帮我分析可能的原因，并提供修改建议。"""
    print("📋 [AI助手模板] 您可以复制以下内容向AI提问：")
    print(f"{'-' * 60}\n{ai_helper_prompt.strip()}\n{'-' * 60}\n")

def execute_sql(cursor, sql_statement):
    logging.info(f"执行SQL: {sql_statement}")
    start_time = time.time()
    try:
        # V1.0 升级：使用 executescript 来支持未来可能的多语句
        # 对于单条语句，它的行为和 execute 一样，但更健壮
        cursor.executescript(sql_statement)
        # 注意：executescript 不返回结果，我们需要用另一条查询获取
        # 但为了保持简单，我们假设学习场景下一次只执行一条查询
        # 如果需要显示结果，我们还需要进一步处理
        # 暂时简化：对于可能返回结果的语句，我们还是用 execute
        # 这是一个权衡，我们先用一个简单的逻辑
        is_select_or_pragma = sql_statement.strip().upper().startswith(('SELECT', 'PRAGMA'))
        
        if is_select_or_pragma and ';' in sql_statement:
            # 对于单条查询，只执行分号前的部分
            single_statement = sql_statement.split(';')[0] + ';'
            cursor.execute(single_statement)
            rows = cursor.fetchall()
            if rows:
                headers = [desc[0] for desc in cursor.description]
                print(tabulate(rows, headers=headers, tablefmt="grid"))
                print(f"\n查询到 {len(rows)} 行。")
            else: # 例如 PRAGMA foreign_keys = ON;
                 print("命令执行成功。")
        else: # 对于 INSERT, UPDATE, CREATE 等
            print("命令执行成功。")

    except sqlite3.Error as e:
        print_error_report(sql_statement, e)
        logging.error(f"SQL执行失败: {e} | SQL: {sql_statement}")
    finally:
        duration = time.time() - start_time
        print(f"(操作耗时: {duration:.4f} 秒)")

def handle_dot_command(command, conn):
    # ... 此函数与 V0.9 完全相同 ...
    logging.info(f"执行元命令: {command}")
    parts = command.lower().split()
    cmd = parts[0]
    start_time = time.time()
    if cmd in [".exit", ".quit"]: return "exit"
    elif cmd == ".tables":
        print("数据库中的所有表:")
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        # 这里元命令自己就是完整的，直接调用execute
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            headers = [desc[0] for desc in cursor.description]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            print(f"\n查询到 {len(rows)} 行。")
        duration = time.time() - start_time
        print(f"(操作耗时: {duration:.4f} 秒)")
    elif cmd == ".help":
        print("欢迎使用帮助！当前支持的元命令:\n  .tables          显示所有表名。\n  .help            显示此帮助信息。\n  .exit, .quit     退出本程序。")
        duration = time.time() - start_time
        print(f"(操作耗时: {duration:.4f} 秒)")
    else:
        print(f"无法识别的元命令: '{command}'。输入 .help 查看帮助。")
        duration = time.time() - start_time
        print(f"(操作耗时: {duration:.4f} 秒)")
    return True

# SmartCompleter 类与 V0.9 完全相同
class SmartCompleter(Completer):
    def __init__(self, conn):
        self.conn = conn
        self.keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'CREATE', 'TABLE',
            'UPDATE', 'SET', 'DELETE', 'GROUP', 'BY', 'ORDER', 'ASC', 'DESC', 'AND',
            'OR', 'NOT', 'NULL', 'PRIMARY', 'KEY', 'INTEGER', 'TEXT', 'REAL', 'BLOB',
            'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'AS', 'DISTINCT',
            'PRAGMA', 'foreign_keys', 'table_info', 'index_list', 'user_version',
            'UNIQUE', 'CONSTRAINT', 'FOREIGN', 'REFERENCES', 'ALTER', 'ADD', 'COLUMN',
            '.tables', '.help', '.exit', '.quit'
        ]
        self.table_cache = None
        self.column_cache = {}

    def _get_tables(self):
        if self.table_cache is None:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
                self.table_cache = [row[0] for row in cursor.fetchall()]
            except sqlite3.Error: self.table_cache = []
        return self.table_cache

    def _get_columns(self, table_name):
        if table_name not in self.column_cache:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name});")
                self.column_cache[table_name] = [row[1] for row in cursor.fetchall()]
            except sqlite3.Error: self.column_cache[table_name] = []
        return self.column_cache[table_name]

    def _extract_table_context(self, text):
        match = re.search(r'\b(?:from|join|update)\s+([a-zA-Z0-9_]+)', text, re.IGNORECASE)
        if match: return match.group(1)
        return None

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        word = document.get_word_before_cursor(WORD=True)
        words = text.lower().split()

        pragma_match = re.search(r'table_info\(\s*([^)]*)$', text, re.IGNORECASE)
        if pragma_match:
            partial_table = pragma_match.group(1)
            for table in self._get_tables():
                if table.lower().startswith(partial_table.lower()):
                    yield Completion(table, start_position=-len(partial_table))
            return

        column_triggers = ['where', 'by', 'and', 'or', 'on', 'set']
        if words and words[-1] in column_triggers or (len(words) > 1 and words[-2] in column_triggers):
            table_name = self._extract_table_context(text)
            if table_name:
                for col in self._get_columns(table_name):
                    if col.lower().startswith(word.lower()):
                        yield Completion(col, start_position=-len(word))
                return

        table_triggers = ['from', 'update', 'join', 'into']
        if words and (words[-1] in table_triggers or (len(words) > 1 and words[-2] in table_triggers)):
            for table in self._get_tables():
                if table.lower().startswith(word.lower()):
                    yield Completion(table, start_position=-len(word))
            return
            
        for keyword in self.keywords:
            if keyword.lower().startswith(word.lower()):
                yield Completion(keyword, start_position=-len(word))


# --- V1.0 核心改动：全新的 REPL 逻辑 ---
def run_repl(conn):
    base_style_name = 'monokai'
    style_dict = get_style_by_name(base_style_name).styles
    style_dict[Token.Literal.String] = '#e6db74'
    final_style = style_from_pygments_dict(style_dict)
    
    session = PromptSession(
        history=FileHistory('.workbench_history'),
        auto_suggest=AutoSuggestFromHistory(),
        style=final_style,
    )
    
    completer = SmartCompleter(conn)

    print(f"欢迎使用Python版SQLite3工作台 V1.0 (稳定版)。")
    print(f"当前配色: {base_style_name} (自定义)。")
    # V1.0 新增提示
    print("提示: SQL语句必须以分号 (;) 结尾才能执行，支持多行输入。")
    print("输入 .help 获取帮助。")

    # V1.0 核心逻辑：语句缓冲区
    sql_buffer = ""

    while True:
        try:
            # 根据缓冲区是否为空，决定主/次提示符
            prompt_str = "sqlite> " if not sql_buffer else "   ...> "
            
            line = session.prompt(
                prompt_str, 
                lexer=PygmentsLexer(SqlLexer), 
                completer=completer
            )
            
            # 如果缓冲区为空，且输入的是元命令，则直接处理
            if not sql_buffer and line.strip().startswith('.'):
                 if handle_dot_command(line.strip(), conn) == "exit":
                     break
                 continue

            # 将新输入的一行加入缓冲区
            if sql_buffer:
                sql_buffer += "\n" + line
            else:
                sql_buffer = line

            # 检查缓冲区内容是否以分号结尾 (忽略末尾空白)
            if sql_buffer.strip().endswith(';'):
                command_to_run = sql_buffer
                logging.info(f"执行缓冲区SQL: {command_to_run}")
                
                execute_sql(conn.cursor(), command_to_run)
                conn.commit()
                
                # 执行完毕，清空缓冲区
                sql_buffer = ""
            
        except KeyboardInterrupt: # Ctrl+C 可以清空当前正在输入的语句
            if sql_buffer:
                print("\n当前输入已取消。")
                sql_buffer = ""
            else:
                # 如果缓冲区是空的，Ctrl+C 没意义，直接换行
                print()
                continue
        except EOFError:
            print("\n再见！")
            break

def main():
    setup_logging()
    
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(
        description="一个支持自动补全和语法高亮的SQLite3命令行终端。",
        epilog="如果没有提供数据库文件路径，程序会提示您输入。"
    )
    parser.add_argument(
        "db_path",
        nargs='?',  # '?' 表示这个参数是可选的
        default=None,
        help="要连接的SQLite3数据库文件的路径。"
    )
    args = parser.parse_args()

    db_path = args.db_path
    
    # 如果未通过命令行提供路径，则提示用户输入
    if db_path is None:
        try:
            db_path = str(input('请输入 sqlite3 数据库路径 (例如 my_database.db): '))
        except (KeyboardInterrupt, EOFError):
            print("\n操作取消。")
            sys.exit(0)

    conn = None
    try:
        conn = sqlite3.connect(db_path)
        logging.info(f"成功连接到数据库: {db_path}")
        print(f"已成功连接到数据库: {db_path}")
        run_repl(conn)
    except sqlite3.Error as e:
        logging.critical(f"数据库连接失败: {e}")
        print(f"数据库连接失败: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            logging.info("数据库连接已关闭。")
            print("数据库连接已关闭。")

if __name__ == "__main__":
    main() 