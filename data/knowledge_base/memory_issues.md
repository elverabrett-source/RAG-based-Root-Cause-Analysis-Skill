# 内存与资源泄露排查手册

## 1. Java OutOfMemoryError (OOM)

### 现象
JVM 抛出 `java.lang.OutOfMemoryError: Java heap space`.

### 可能原因
1. **内存泄漏**：存在长时间存活的对象未被 GC 回收。
2. **堆大小设置过小**：物理内存充足，但 `-Xmx` 参数设置不合理。

### 排查工具
- 使用 `jmap -dump:format=b,file=heap.hprof <pid>` 获取堆转储。
- 使用 **Eclipse MAT** 分析大对象占据情况。

---

## 2. Python 内存占用异常

### 现象
Python 进程占用的 RSS (Resident Set Size) 持续上升且不回落。

### 根因分析
- 全局变量缓存了大量数据。
- 循环引用导致 `gc.collect()` 无法回收。

### 优化建议
- 使用 `objgraph` 查找循环引用。
- 尽量使用生成器 (Generator) 代替一次性列表加载数据。
