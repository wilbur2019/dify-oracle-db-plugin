## oracle_db_plugin
# Oracle 数据库查询插件

**作者:** Wilbur
**版本:** 0.0.1
**类型:** 工具

### 描述

此插件允许您使用 Oracle 的 Thin 模式连接到 Oracle 数据库并执行 SQL 查询。它提供了一个简单的界面，可直接从 Dify 查询 Oracle 数据库。

### 功能特性

- 使用 Thin 模式连接到 Oracle 数据库（无需安装 Oracle 客户端）
- 执行 SQL 查询并以结构化格式检索结果
- 支持常见的 Oracle 数据类型
- 错误处理和详细的错误信息

### 参数说明

使用此插件时，您需要提供以下参数：

| 参数名 | 类型 | 是否必需 | 描述 |
|---------|------|----------|------|
| host | 字符串 | 是 | Oracle 数据库服务器的主机名或 IP 地址 |
| port | 整数 | 是 | Oracle 数据库服务器的端口号（默认是 1521） |
| user | 字符串 | 是 | 连接到 Oracle 数据库的用户名 |
| password | 字符串 | 是 | 连接到 Oracle 数据库的密码 |
| service_name | 字符串 | 是 | Oracle 数据库的服务名称 |
| query | 字符串 | 是 | 要在 Oracle 数据库上执行的 SQL 查询 |

### 使用示例

```sql
-- 从表中获取数据的示例查询
SELECT * FROM employees WHERE department = 'IT' LIMIT 10;
```

### 返回格式

插件以 JSON 格式返回结果，结构如下：

```json
{
  "status": "success",
  "data": [
    {"column1": "value1", "column2": "value2"}, 
    {"column1": "value3", "column2": "value4"}
  ],
  "columns": ["column1", "column2"],
  "message": "查询执行成功，返回 2 行数据。"
}
```

如果发生错误，响应将是：

```json
{
  "status": "error",
  "message": "错误描述"
}
```
### 依赖要求

- oracledb >= 2.0.0
- dify-plugin >= 0.2.0



