# 数据库故障排查手册

## 1. 数据库连接失败 (Connection Refused/Failed)

### 现象
系统日志出现 `Failed to connect to postgresql://db:5432` 或 `SqlException: Connection refused`.

### 可能原因
1. **网络隔离**：防火墙规则变更，导致应用服务器无法访问数据库端口。
2. **连接池耗尽**：应用层未正确释放连接，导致 `max_connections` 达到上限。
3. **身份验证失败**：密码过期或配置文件中的 API Key 被错误修改。

### 根因分析步骤
- 使用 `telnet db_host 5432` 测试端口连通性。
- 执行 `SELECT count(*) FROM pg_stat_activity` 查看活跃连接数。
- 检查 `pg_hba.conf` 的访问控制列表。

### 解决方案
- **临时修复**：重启应用服务释放连接。
- **长期修复**：优化连接池配置，设置合理的 `idle_timeout`。

---

## 2. 数据库响应变慢 (Slow Query)

### 现象
日志捕获到大量执行时间超过 5s 的 SQL 语句。

### 根因分析
- 大多数情况下是由于缺少索引或发生了全表扫描。
- 数据库正在执行重型维护任务（如 VACUUM）。

### 解决方案
- 执行 `EXPLAIN ANALYZE` 检查查询计划。
- 对热点字段添加 `B-tree` 索引。
