import oracledb
from typing import Generator, Any

import oracledb
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class OracleDbPluginTool(Tool):
    def __init__(self, runtime=None, session=None):
        super().__init__(runtime, session)
        # 获取当前语言环境，默认为英文
        self.language = self.get_language()
    
    def get_language(self):
        # 从运行环境中获取语言设置，默认返回'en_US'
        try:
            # 实际应用中可能需要从不同位置获取语言设置
            # 这里仅作为示例
            return 'en_US'
        except:
            return 'en_US'
    
    def get_message(self, messages_dict):
        # 根据当前语言返回对应消息，如果没有对应语言的消息，返回英文消息
        return messages_dict.get(self.language, messages_dict.get('en_US', ''))
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        conn = None
        try:
            # 获取连接参数
            host = tool_parameters.get('host')
            port = tool_parameters.get('port')
            user = tool_parameters.get('user')
            password = tool_parameters.get('password')
            service_name = tool_parameters.get('service_name')
            sql_query = tool_parameters.get('query')
            
            # 验证必要参数
            if not all([host, port, user, password, service_name, sql_query]):
                messages = {
                    'en_US': 'Missing required parameters: host, port, user, password, service_name, query are all required',
                    'zh_Hans': '缺少必要参数：host、port、user、password、service_name、query都是必需的'
                }
                yield self.create_json_message({
                    "status": "error",
                    "message": self.get_message(messages)
                })
                return
            
            # python-oracledb默认使用Thin Mode，无需额外配置
            
            # 构建连接字符串
            dsn = f'{host}:{port}/{service_name}'
            
            # 连接数据库
            conn = oracledb.connect(
                user=user,
                password=password,
                dsn=dsn
            )
            
            # 创建游标
            with conn.cursor() as cursor:
                # 执行查询
                cursor.execute(sql_query)
                
                # 获取列名
                columns = [col[0] for col in cursor.description]
                
                # 获取查询结果
                results = []
                for row in cursor.fetchall():
                    # 将每行数据转换为字典
                    row_dict = {columns[i]: value for i, value in enumerate(row)}
                    # 处理可能的特殊类型
                    for key, value in row_dict.items():
                        # 转换datetime对象为字符串
                        if hasattr(value, 'strftime'):
                            row_dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
                    results.append(row_dict)
                
                # 返回结果
                messages = {
                    'en_US': f'Query executed successfully, returned {len(results)} rows.',
                    'zh_Hans': f'查询执行成功，返回了{len(results)}行数据。'
                }
                yield self.create_json_message({
                    "status": "success",
                    "data": results,
                    "columns": columns,
                    "message": self.get_message(messages)
                })
        except Exception as e:
            # 处理异常并返回错误信息
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })
        finally:
            # 确保连接关闭
            if conn:
                try:
                    conn.close()
                except:
                    pass
