# 测试文档

本目录包含了 specphp-scanner 项目的单元测试。

## 测试结构

- `test_ref_resolution.py` - 测试 OpenAPI `$ref` 引用解析功能
- `test_scanner.py` - 测试请求体生成和扫描功能

## 运行测试

### 使用测试运行器

从项目根目录运行：

```bash
python run_tests.py
```

### 使用 Python unittest

运行所有测试：

```bash
python -m unittest discover tests
```

运行特定测试文件：

```bash
python -m unittest tests.test_ref_resolution
python -m unittest tests.test_scanner
```

运行特定测试方法：

```bash
python -m unittest tests.test_ref_resolution.TestRefResolution.test_simple_ref_resolution
```

## 测试覆盖

### test_ref_resolution.py

测试 `$ref` 引用解析功能：

- ✅ 简单 `$ref` 引用解析
- ✅ 嵌套 `$ref` 引用解析
- ✅ 数组中的 `$ref` 引用解析
- ✅ 复杂递归结构的 `$ref` 解析
- ✅ 无效 `$ref` 路径处理
- ✅ 外部 URL 引用处理（跳过不解析）
- ✅ JSON 和 YAML 文件加载
- ✅ 不支持的文件格式处理
- ✅ 文件不存在处理

### test_scanner.py

测试请求体生成功能：

- ✅ 对象类型 schema 的请求体生成
- ✅ 数组类型 schema 的请求体生成
- ✅ 基本类型（string, integer, number, boolean）的值生成
- ✅ 枚举值处理
- ✅ 格式化字符串（email, uuid, datetime 等）处理
- ✅ 约束条件处理（minLength, maxLength, minimum, maximum 等）
- ✅ 必需字段和可选字段处理
- ✅ 递归对象结构处理
- ✅ 空 schema 和 None schema 处理
- ✅ 不支持的 schema 类型处理

## 功能特性

### ✅ 已实现的功能

1. **本地 `$ref` 解析**：
   - 支持 `#/components/schemas/SchemaName` 格式的本地引用
   - 递归解析嵌套的 `$ref` 引用
   - 使用 `jsonschema.RefResolver` 库进行解析

2. **请求体生成**：
   - 基于解析后的 schema 生成符合规范的请求体
   - 支持所有基本 JSON Schema 类型
   - 处理约束条件和格式要求
   - 智能处理必需字段和可选字段

3. **文件格式支持**：
   - JSON 格式的 OpenAPI spec 文件
   - YAML 格式的 OpenAPI spec 文件

### ❌ 不支持的功能

1. **外部引用**：
   - 不支持 `https://` 或其他外部 URL 引用
   - 外部引用会被跳过并保留原始 `$ref`

2. **高级 Schema 特性**：
   - 不支持 `allOf`, `oneOf`, `anyOf` 组合
   - 不支持条件 schema (`if`/`then`/`else`)

## 运行环境

- Python 3.12+
- 依赖库：`jsonschema`, `pyyaml`, `unittest`

## 贡献

添加新测试时，请遵循以下规范：

1. 测试方法名以 `test_` 开头
2. 每个测试方法包含清晰的文档字符串
3. 使用 `setUp()` 方法准备测试数据
4. 使用适当的断言方法验证结果
5. 为边界条件和错误情况编写测试
