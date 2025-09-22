import oracledb
from typing import Generator, Any
import os
import tempfile
import base64
import oracledb
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class OracleDbPluginTool(Tool):
    def __init__(self, runtime=None, session=None):
        super().__init__(runtime, session)
        # 获取当前语言环境，默认为英文
        self.language = self.get_language()
        # 临时目录，用于存储钱包文件
        self.temp_dir = None
    
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
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # 或者也可以使用 Iterator[ToolInvokeMessage]，如果不需要指定 send 和 return 类型
        # def _invoke(self, tool_parameters: dict[str, Any]) -> Iterator[ToolInvokeMessage]:
        conn = None
        try:
            # 获取连接参数
            connection_type = tool_parameters.get('connection_type', 'standard')  # 默认使用标准连接
            sql_query = tool_parameters.get('query')
            
            # 验证查询参数
            if not sql_query:
                messages = {
                    'en_US': 'Missing required parameter: query',
                    'zh_Hans': '缺少必要参数：query'
                }
                yield self.create_json_message({
                    "status": "error",
                    "message": self.get_message(messages)
                })
                return
            
            # 根据连接类型处理不同的连接参数
            if connection_type == 'standard':
                # 标准连接方式（用户名密码）
                host = tool_parameters.get('host')
                port = tool_parameters.get('port')
                user = tool_parameters.get('user')
                password = tool_parameters.get('password')
                service_name = tool_parameters.get('service_name')
                
                # 验证必要参数
                if not all([host, port, user, password, service_name]):
                    messages = {
                        'en_US': 'Missing required parameters for standard connection: host, port, user, password, service_name are all required',
                        'zh_Hans': '缺少标准连接的必要参数：host、port、user、password、service_name都是必需的'
                    }
                    yield self.create_json_message({
                        "status": "error",
                        "message": self.get_message(messages)
                    })
                    return
                
                # 构建连接字符串
                dsn = f'{host}:{port}/{service_name}'
                
                # 连接数据库
            conn = oracledb.connect(
                user=user,
                password=password,
                dsn=dsn
            )
        elif connection_type == 'wallet':
                # ADB钱包连接方式
                wallet_b64 = tool_parameters.get('wallet_base64')
                wallet_password = tool_parameters.get('wallet_password')
                user = tool_parameters.get('wallet_user')
                password = tool_parameters.get('wallet_password')
                tns_name = tool_parameters.get('tns_name')
                
                # 验证必要参数
                if not all([wallet_b64, wallet_password, user, tns_name]):
                    messages = {
                        'en_US': 'Missing required parameters for wallet connection: wallet_base64, wallet_password, wallet_user, tns_name are all required',
                        'zh_Hans': '缺少钱包连接的必要参数：wallet_base64、wallet_password、wallet_user、tns_name都是必需的'
                    }
                    yield self.create_json_message({
                        "status": "error",
                        "message": self.get_message(messages)
                    })
                    return
                
                # 处理钱包文件
                try:
                    # 创建临时目录
                    self.temp_dir = tempfile.mkdtemp()
                    
                    # 解码并保存钱包文件
                    wallet_data = base64.b64decode(wallet_b64)
                    wallet_zip_path = os.path.join(self.temp_dir, 'wallet.zip')
                    with open(wallet_zip_path, 'wb') as f:
                        f.write(wallet_data)
                    
                    # 连接数据库
                    conn = oracledb.connect(
                        user=user,
                        password=password,
                        dsn=tns_name,
                        config_dir=self.temp_dir,
                        wallet_location=self.temp_dir,
                        wallet_password=wallet_password
                    )
                except Exception as e:
                    messages = {
                        'en_US': f'Failed to process wallet file: {str(e)}',
                        'zh_Hans': f'处理钱包文件失败：{str(e)}'
                    }
                    yield self.create_json_message({
                        "status": "error",
                        "message": self.get_message(messages)
                    })
                    return
            else:
                messages = {
                    'en_US': f'Invalid connection_type: {connection_type}. Must be "standard" or "wallet".',
                    'zh_Hans': f'无效的connection_type：{connection_type}。必须是"standard"或"wallet"。'
                }
                yield self.create_json_message({
                    "status": "error",
                    "message": self.get_message(messages)
                })
                return
            

            
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
                        # 处理LOB类型
                        if isinstance(value, oracledb.LOB):
                            try:
                                # 尝试将LOB转换为字符串
                                row_dict[key] = value.read()
                            except:
                                # 如果读取失败，设置为None或错误信息
                                row_dict[key] = None
                        # 转换datetime对象为字符串
                        elif hasattr(value, 'strftime'):
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
            
            # 清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    # 删除临时目录中的所有文件
                    for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                        for file in files:
                            os.remove(os.path.join(root, file))
                        for dir in dirs:
                            os.rmdir(os.path.join(root, dir))
                    os.rmdir(self.temp_dir)
                except:
                    pass
