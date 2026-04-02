# 网络故障排查手册

## 1. 504 Gateway Timeout (网关超时)

### 现象
浏览器返回 `504 Gateway Timeout`, 并在 Nginx 日志中查出 `upstream timed out`.

### 可能原因
1. **后端处理缓慢**：应用代码中有耗时较长的阻塞操作。
2. **连接超时设置过低**：Nginx 的 `proxy_read_timeout` 低于后端的处理时间。

---

## 2. DNS 解析失败 (DNS Resolution)

### 现象
系统报错 `UnknownHostException` 或 `curl: (6) Could not resolve host`.

### 可能原因
1. **CoreDNS 异常**：Kubernetes 集群内部 CoreDNS 负载过高。
2. **缓存问题**：过期的 DNS 记录仍在应用缓存中。

### 解决方案
- 尝试重启 Pod 刷新 DNS 记录。
- 增加集群内部 DNS 副本数以缓解负载压力。
