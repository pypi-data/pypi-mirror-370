# General-Validator

## 概述

General-Validator 是一款极简通用数据批量校验器，专为接口测试中的数据校验场景设计。通过极简的校验语法、灵活的阈值机制和强大的联合条件功能，轻松应对各种复杂的数据校验场景。🚀

## 核心特性

- **极简调用**: 一个函数搞定所有场景，如 `check(data, "field > 0")`
- **默认非空**: 无需记忆，符合最常见使用场景，如 `check(data, "field1", "field2")`  
- **直观语法**: `"field > 0"` 比复杂配置更好理解
- **智能解析**: 自动推断数据类型和校验逻辑
- **通配符支持**: `"*.field"` 实现批量校验，支持深度嵌套数据
- **零学习成本**: 接近自然语言的表达式
- **🆕 失败阈值机制**: 支持严格模式、数量阈值、比率阈值，灵活控制校验策略
- **🆕 联合条件校验**: 支持 `&&`（AND）和 `||`（OR）逻辑操作符
- **🆕 多种条件语义**: 严格条件、逐项条件、列表专用专项条件三种校验模式

## 主要函数

### 1. check() - 核心校验函数

最主要的校验函数，支持多种简洁的调用方式和失败阈值控制。

#### 基本语法
```python
check(data, *validations, failure_threshold=None)
```

#### 参数说明
- `data`: 要校验的数据
- `validations`: 校验规则（支持字符串和字典格式）
- `failure_threshold`: 🆕 失败阈值
  - `None`: 严格模式，一个失败全部失败（默认）
  - `int`: 每个规则最多允许N个失败
  - `float`: 每个规则最多允许N%失败率

#### 返回值说明
- `True`: 所有校验都通过或未超过阈值
- `False`: 存在校验失败且超过阈值
- 抛出异常: 当参数错误或数据结构异常时

### 2. check_not_empty() - 专门非空校验

```python
check_not_empty(data, *field_paths, failure_threshold=None)
```

### 3. check_when() - 严格条件校验

所有匹配项都满足条件时才执行then校验。

```python
check_when(data, condition, *then, failure_threshold=None)
```

### 4. check_when_each() - 🆕 逐项条件校验

对指定路径下的每个数据项分别进行条件+then检查。

```python
check_when_each(data, condition, *then, failure_threshold=None)
```

### 5. check_list_when() - 🆕 列表专用条件校验

check_when_each的简化版，专门用于列表数据。

```python
check_list_when(data_list, condition, *then, failure_threshold=None)
```

### 6. check_list() - 列表批量校验

```python
check_list(data_list, *field_names, failure_threshold=None, **validators)
```

### 7. check_nested() - 嵌套列表校验

```python
check_nested(data, list_path, nested_field, *field_validations, failure_threshold=None)
```

### 8. checker() - 链式调用

```python
checker(data).not_empty("field1").equals("field2", value).validate(failure_threshold=None)
```

**支持的链式调用方法：**

#### 基础校验
- `not_empty(*paths)` - 批量非空校验
- `equals(path, value)` - 等于校验
- `not_equals(path, value)` - 不等于校验

#### 数值校验
- `greater_than(path, value)` - 大于校验
- `greater_equal(path, value)` - 大于等于校验
- `less_than(path, value)` - 小于校验
- `less_equal(path, value)` - 小于等于校验
- `between(path, min_value, max_value, inclusive=True)` - 范围校验
- `is_positive(path)` - 正数校验
- `is_negative(path)` - 负数校验
- `is_non_negative(path)` - 非负数校验

#### 字符串校验
- `starts_with(path, prefix)` - 以指定字符串开头
- `ends_with(path, suffix)` - 以指定字符串结尾
- `contains(path, substring)` - 包含指定字符串
- `contained_by(path, container)` - 被指定字符串包含
- `matches_regex(path, pattern)` - 正则表达式匹配
- `is_email(path)` - 邮箱格式校验
- `is_phone(path)` - 手机号格式校验
- `is_url(path)` - URL格式校验

#### 类型校验
- `is_type(path, expected_type)` - 通用类型校验
- `is_string(path)` - 字符串类型校验
- `is_number(path)` - 数字类型校验（int或float）
- `is_integer(path)` - 整数类型校验
- `is_float(path)` - 浮点数类型校验
- `is_boolean(path)` - 布尔类型校验
- `is_list(path)` - 列表类型校验
- `is_dict(path)` - 字典类型校验
- `is_none(path)` - None类型校验

#### 集合校验
- `in_values(path, values)` - 值在指定集合中
- `not_in_values(path, values)` - 值不在指定集合中

#### 长度校验
- `length_equals(path, length)` - 长度等于指定值
- `length_greater_than(path, length)` - 长度大于指定值
- `length_less_than(path, length)` - 长度小于指定值
- `length_greater_equal(path, length)` - 长度大于等于指定值
- `length_less_equal(path, length)` - 长度小于等于指定值
- `length_between(path, min_length, max_length)` - 长度在指定范围内

#### 批量校验
- `all_fields_not_empty(*paths)` - 批量非空校验
- `all_fields_positive(*paths)` - 批量正数校验
- `all_fields_type(field_type, *paths)` - 批量类型校验

#### 条件校验
- `when(condition, *then)` - 严格条件校验：所有匹配项都满足条件时才执行then校验
- `when_each(condition, *then)` - 🆕 逐项条件校验：对每个数据项分别进行条件+then检查
- `list_when(condition, *then)` - 🆕 列表专用条件校验：when_each的简化版

## 🆕 失败阈值机制

General-Validator 新增了灵活的失败阈值控制机制，支持三种模式：

### 1. 严格模式（默认）
```python
# 任何校验失败都返回False，保证完全向后兼容
check(data, "field1", "field2 > 0", "field3")
```

### 2. 数量阈值
```python
# 允许最多2个校验失败
check(data, "field1", "field2", "field3", "field4", failure_threshold=2)

# 10个商品，允许最多1个不符合要求
check_list(products, "name", "price > 0", failure_threshold=1)
```

### 3. 比率阈值
```python
# 允许30%的校验失败
check(data, "field1", "field2", "field3", failure_threshold=0.3)

# 允许20%的活跃用户分数不达标
check_list_when(users, "status == 'active'", "score > 70", failure_threshold=0.2)
```

### 应用场景

#### 接口测试场景
```python
# 商品列表接口 - 允许少量数据异常
products = response["data"]["products"]
check_list(products, 
           "id", "name", "price",           # 基础字段非空
           "id > 0", "price >= 0",          # 数值校验
           failure_threshold=2)             # 允许2个商品有问题

# 用户权限接口 - 允许5%的权限配置异常
check(response, 
      "users.*.permissions.read",
      "users.*.permissions.write", 
      "users.*.permissions.admin",
      failure_threshold=0.05)              # 允许5%失败率
```

#### 数据质量监控
```python
# 批量数据导入 - 允许10%的数据格式问题
imported_data = get_imported_records()
checker(imported_data)\
    .not_empty("*.name", "*.email")\
    .is_email("*.email")\
    .greater_than("*.age", 0)\
    .validate(failure_threshold=0.1)        # 允许10%失败率
```

## 🆕 联合条件校验

支持 `&&`（AND）和 `||`（OR）逻辑操作符，可以构建复杂的条件表达式。

### 基本用法

#### AND条件（&&）
```python
# 活跃的VIP用户必须有积分记录
check_list_when(users, 
                "status == 'active' && level == 'vip'", 
                "score > 0", "last_login")

# 高级商品（电子产品且价格>100）必须有保修信息
check_when_each(data, 
                "products.*.category == 'electronics' && products.*.price > 100",
                "products.*.warranty", "products.*.support_phone")
```

#### OR条件（||）
```python
# VIP用户或管理员必须有特殊权限
check_list_when(users,
                "level == 'vip' || level == 'admin'",
                "special_permissions")

# 促销商品或新品必须有营销信息
check_when_each(data,
                "products.*.is_promotion == true || products.*.is_new == true",
                "products.*.marketing_info")
```

#### 混合条件（优先级：&& > ||）
```python
# (活跃VIP用户) 或 (管理员且分数>80) 必须有高级功能
check_list_when(users,
                "status == 'active' && level == 'vip' || level == 'admin' && score > 80",
                "advanced_features")
```

### 高级特性

#### 短路求值优化
```python
# AND：遇到False立即返回，不继续检查后续条件
# OR：遇到True立即返回，不继续检查后续条件
check_list_when(users, 
                "status == 'inactive' && score > 100",  # 大部分用户status != 'inactive'，快速跳过
                "premium_features")
```

#### 引号内容保护
```python
# 正确处理引号内包含操作符的情况
check_list_when(logs, 
                "level == 'ERROR' && message *= 'connection && timeout'",
                "error_details")
```

## 条件校验的三种语义

### 1. check_when() - 严格条件校验

**语义**：所有匹配项都满足条件时才执行then校验

```python
# 当所有商品状态都为active时，才校验价格
check_when(data, "products.*.status == 'active'", "products.*.price > 0")

# 结合联合条件：当所有用户都是活跃VIP时，才校验高级权限
check_when(data, "users.*.status == 'active' && users.*.level == 'vip'", 
           "users.*.premium_features")
```

### 2. check_when_each() - 逐项条件校验

**语义**：对每个数据项分别进行条件+then检查

```python
# 对每个用户分别判断：如果是活跃用户，则校验积分
check_when_each(data, "users.*.status == 'active'", "users.*.score > 0")

# 对每个商品分别判断：如果是电子产品且价格>100，则校验保修
check_when_each(data, 
                "products.*.category == 'electronics' && products.*.price > 100",
                "products.*.warranty_info")
```

### 3. check_list_when() - 列表专用条件校验

**语义**：check_when_each的简化版，直接传入列表

```python
# 直接传入用户列表
users = data["users"]
check_list_when(users, "status == 'active'", "score > 0", "last_login")

# 结合阈值：允许20%的活跃用户积分不足
check_list_when(users, 
                "status == 'active' && level == 'vip'", 
                "score > 100",
                failure_threshold=0.2)
```

## 支持的校验器

### 比较操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `==` | 等于 | `"status_code == 200"` |
| `!=` | 不等于 | `"status != 'error'"` |
| `>` | 大于 | `"price > 0"` |
| `>=` | 大于等于 | `"count >= 1"` |
| `<` | 小于 | `"age < 100"` |
| `<=` | 小于等于 | `"score <= 100"` |

### 字符串操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `^=` | 以...开头 | `"name ^= 'test'"` |
| `$=` | 以...结尾 | `"email $= '@qq.com'"` |
| `~=` | 正则匹配 | `"phone ~= '^1[3-9]\\d{9}$'"` |

### 列表、元组、字典、字符串等操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `*=` | 包含 | `"description *= '商品'"` |
| `=*` | 被包含 | `"'a' =* 'abc'"` |
| `#=` | 长度等于 | `"name #= 5"` |
| `#!=` | 长度不等于 | `"list #!= 0"` |
| `#>` | 长度大于 | `"content #> 10"` |
| `#>=` | 长度大于等于 | `"tags #>= 1"` |
| `#<` | 长度小于 | `"title #< 50"` |
| `#<=` | 长度小于等于 | `"items #<= 100"` |

### 🆕 逻辑操作符
| 操作符 | 说明 | 优先级 | 示例 |
|--------|------|--------|------|
| `&&` | 逻辑与(AND) | 高 | `"status == 'active' && level == 'vip'"` |
| `\|\|` | 逻辑或(OR) | 低 | `"type == 'premium' \|\| level == 'admin'"` |

### 类型操作符
| 操作符 | 说明 | 示例 |
|--------|------|------|
| `@=` | 类型匹配 | `"age @= 'int'"` |

**支持的类型名称：**
- `int`/`integer`：整数类型
- `float`：浮点数类型  
- `str`/`string`：字符串类型
- `bool`/`boolean`：布尔类型
- `list`：列表类型
- `dict`：字典类型
- `tuple`：元组类型
- `set`：集合类型
- `none`/`null`：None类型

### 默认校验器
- 无操作符时默认为非空校验
- 支持嵌套路径和通配符

## 使用示例

### 基础用法

```python
# 示例数据
response = {
    "status_code": 200,
    "message": "success",
    "data": {
        "product": {
            "id": 7,
            "name": "商品A",
            "price": 99.99,
            "description": "这是一个测试商品"
        },
        "productList": [
            {
                "id": 1,
                "name": "商品1",
                "price": 10.5,
                "status": "active",
                "purchasePlan": [
                    {"id": 101, "name": "计划1", "amount": 100},
                    {"id": 102, "name": "计划2", "amount": 200}
                ]
            },
            {
                "id": 2,
                "name": "商品2", 
                "price": 20.0,
                "status": "active",
                "purchasePlan": [
                    {"id": 201, "name": "计划3", "amount": 300}
                ]
            }
        ]
    }
}

# 1. 最简单的非空校验
check(response, "data.product.id", "data.product.name")

# 2. 带校验器的简洁语法  
check(response, 
      "status_code == 200",
      "data.product.id > 0", 
      "data.product.price >= 10")

# 3. 混合校验
check(response, 
      "data.product.id",           # 默认非空
      "data.product.price > 0",    # 大于0
      "status_code == 200",        # 等于200
      "message ^= 'suc'")          # 以'suc'开头

# 4. 通配符批量校验
check(response, 
      "data.productList.*.id",           # 所有商品ID非空
      "data.productList.*.name",         # 所有商品名称非空
      "data.productList.*.id > 0",       # 所有商品ID大于0
      "data.productList.*.price >= 0")   # 所有商品价格大于等于0

# 5. 嵌套列表校验
check(response, 
      "data.productList.*.purchasePlan.*.id > 0",
      "data.productList.*.purchasePlan.*.name",
      "data.productList.*.purchasePlan.*.amount >= 100")
```

### 🆕 失败阈值示例

```python
# 1. 严格模式（默认） - 任何失败都返回False
result = check(response, "data.productList.*.id > 0", "data.productList.*.name")

# 2. 数量阈值 - 允许最多1个商品有问题
result = check(response, 
               "data.productList.*.id > 0",
               "data.productList.*.name", 
               "data.productList.*.price > 0",
               failure_threshold=1)

# 3. 比率阈值 - 允许20%的商品有问题  
result = check(response,
               "data.productList.*.id > 0",
               "data.productList.*.name",
               "data.productList.*.price > 0", 
               failure_threshold=0.2)

# 4. 链式调用阈值
result = checker(response)\
    .not_empty("data.productList.*.name")\
    .greater_than("data.productList.*.id", 0)\
    .greater_than("data.productList.*.price", 0)\
    .validate(failure_threshold=2)
```

### 🆕 联合条件校验示例

```python
# 1. AND条件 - 活跃商品且价格>10
check_when_each(response, 
                "data.productList.*.status == 'active' && data.productList.*.price > 10",
                "data.productList.*.name")

# 2. OR条件 - 高价商品或活跃商品必须有描述
check_when_each(response,
                "data.productList.*.price > 50 || data.productList.*.status == 'active'",
                "data.productList.*.description")

# 3. 混合条件 - (活跃且价格>10) 或 (价格>100)
check_when_each(response,
                "data.productList.*.status == 'active' && data.productList.*.price > 10 || data.productList.*.price > 100",
                "data.productList.*.premium_features")

# 4. 列表专用联合条件
products = response["data"]["productList"]
check_list_when(products,
                "status == 'active' && price > 15",
                "name", "purchasePlan")
```

### 专用函数用法

```python
# 1. 专门的非空校验
check_not_empty(response, "data.product.id", "data.product.name", "message")

# 2. 列表批量校验（支持阈值）
check_list(response["data"]["productList"], 
           "id", "name",                    # 默认非空
           "price > 0", "id > 0",           # 带校验器
           failure_threshold=1)             # 允许1个商品有问题

# 3. 嵌套列表校验（支持阈值）
check_nested(response, "data.productList", "purchasePlan",
             "id > 0", "name", "amount >= 50",
             failure_threshold=0.1)          # 允许10%失败率

# 4. 链式调用
checker(response)\
    .not_empty("data.product.id", "data.product.name")\
    .equals("status_code", 200)\
    .greater_than("data.product.id", 0)\
    .validate()
```

### 条件校验用法

```python
# 1. 严格条件校验 - 当所有商品都是活跃状态时，校验价格
check_when(response, "data.productList.*.status == 'active'", 
           "data.productList.*.price > 0")

# 2. 逐项条件校验 - 对每个商品分别判断
check_when_each(response, "data.productList.*.status == 'active'", 
                "data.productList.*.price > 0", "data.productList.*.name")

# 3. 列表专用条件校验
products = response["data"]["productList"]
check_list_when(products, "status == 'active'", 
                "price > 0", "name", 
                failure_threshold=0.3)       # 允许30%失败率

# 4. 联合条件校验
check_list_when(products, 
                "status == 'active' && price > 10", 
                "name", "purchasePlan",
                failure_threshold=1)         # 允许1个失败

# 5. 链式条件校验
checker(response)\
    .when("data.productList.*.status == 'active'", "data.productList.*.price > 0")\
    .when_each("data.productList.*.status == 'active'", "data.productList.*.name")\
    .validate()
```

### 字典格式校验

```python
# 字典格式（兼容旧版本）
check(response, {
    "field": "data.product.id",
    "validator": "gt",
    "expect": 0
})

# 混合使用字符串和字典格式
check(response,
      "status_code == 200",              # 字符串格式
      {
          "field": "data.product.id", 
          "validator": "gt", 
          "expect": 0
      },                                 # 字典格式
      "data.product.name")               # 默认非空
```

## 实际应用场景

### 接口测试验证

```python
def test_product_api():
    """商品接口测试 - 使用失败阈值应对数据质量问题"""
    response = requests.get("/api/products")
    data = response.json()
    
    # 基础响应校验 - 严格模式
    check(data, 
          "status_code == 200",
          "message == 'success'",
          "data.total >= 0")
    
    # 商品列表校验 - 允许5%的商品数据异常  
    products = data["data"]["products"]
    check_list(products,
               "id", "name", "price",           # 基础字段
               "id > 0", "price >= 0",          # 数值校验  
               "name #>= 2",                    # 长度校验
               failure_threshold=0.05)          # 5%容错率
    
    # 活跃商品专项校验 - 允许2个商品异常
    check_list_when(products,
                    "status == 'active' && is_visible == true",
                    "image_url", "description",
                    "price > 0", "stock > 0",
                    failure_threshold=2)

def test_user_permissions():
    """用户权限接口测试 - 联合条件校验"""
    response = requests.get("/api/users/permissions")
    data = response.json()
    
    # VIP用户或管理员必须有高级权限
    check_when_each(data,
                    "users.*.level == 'vip' || users.*.level == 'admin'",
                    "users.*.advanced_permissions",
                    "users.*.quota > 1000")
    
    # 活跃付费用户必须有完整权限配置
    check_when_each(data,
                    "users.*.status == 'active' && users.*.is_paid == true",
                    "users.*.permissions.read == true",
                    "users.*.permissions.write == true",
                    "users.*.permissions.delete")
```

### 数据质量监控

```python
def monitor_data_quality():
    """数据质量监控 - 批量校验"""
    imported_records = get_daily_import_data()
    
    # 基础数据完整性 - 允许1%异常
    checker(imported_records)\
        .not_empty("*.user_id", "*.email", "*.created_at")\
        .is_email("*.email")\
        .greater_than("*.user_id", 0)\
        .validate(failure_threshold=0.01)
    
    # 业务数据逻辑性 - 允许5%异常  
    check_list_when(imported_records,
                    "status == 'active' && account_type == 'premium'",
                    "subscription_end_date",
                    "payment_method",
                    "last_payment_date",
                    failure_threshold=0.05)

def validate_config_consistency():
    """配置一致性校验 - 严格模式"""
    configs = load_service_configs()
    
    # 所有微服务配置必须一致
    check_when(configs,
               "services.*.environment == 'production'",
               "services.*.database.host",
               "services.*.database.port == 3306",
               "services.*.cache.enabled == true")
```

### 业务规则验证

```python
def validate_order_business_rules():
    """订单业务规则校验"""
    orders = get_pending_orders()
    
    # 高价值订单必须完整信息 - 允许少量异常
    check_list_when(orders,
                    "total_amount > 1000 && payment_method == 'credit_card'",
                    "billing_address",
                    "phone_verified == true",
                    "id_verified == true",
                    failure_threshold=2)
    
    # 国际订单特殊要求
    check_list_when(orders,
                    "shipping_country != 'CN' && total_amount > 500",
                    "customs_declaration",
                    "shipping_insurance == true",
                    "tracking_number")

def validate_promotion_rules():
    """促销规则校验 - 复杂联合条件"""
    promotions = get_active_promotions()
    
    # 高级促销或节假日促销必须有审批
    check_list_when(promotions,
                    "discount_rate > 0.3 || is_holiday_promotion == true",
                    "approval_status == 'approved'",
                    "approver_id",
                    "approval_date")
    
    # 限时促销必须有明确时间范围
    check_list_when(promotions,
                    "type == 'flash_sale' && is_active == true",
                    "start_time", "end_time",
                    "max_participants > 0")
```

## 在测试用例中的使用

### YAML测试文件中使用

```yaml
# testcase.yml
name: 商品接口测试

request:
  url: /api/products
  method: GET

validate:
  # 基础响应校验
  - eq:
    - ${check(content, "status_code == 200", "content.data.products")}
    - True
  
  # 失败阈值校验 - 允许5%商品异常
  - eq:
    - ${check_list(content.data.products, "id", "name", "price > 0", failure_threshold=0.05)}
    - True
  
  # 联合条件校验 - 活跃高价商品必须有详情
  - eq:
    - ${check_list_when(content.data.products, "status == 'active' && price > 100", "description", "images")}
    - True
```

### Python测试文件中使用

```python
# test_products.py
import pytest
from general_validator import check, check_list, check_when_each, checker

class TestProducts:
    
    def test_product_detail(self, response):
        """商品详情接口测试"""
        # 基础校验 - 严格模式
        check(response, 
              "status_code == 200",
              "data.product.id > 0",
              "data.product.name",
              "data.product.price >= 0")
    
    def test_product_list_with_threshold(self, response):
        """商品列表接口测试 - 失败阈值模式"""
        products = response["data"]["products"]
        
        # 允许2个商品有问题
        check_list(products,
                   "id", "name", "price",           # 非空校验
                   "id > 0", "price >= 0",          # 数值校验
                   failure_threshold=2)
        
        # 允许10%的商品缺少可选字段
        check_list(products,
                   "description", "tags", "images",
                   failure_threshold=0.1)
    
    def test_conditional_validation(self, response):
        """条件校验测试 - 联合条件"""
        products = response["data"]["products"]
        
        # 活跃商品且价格>50的必须有详细信息
        check_list_when(products,
                        "status == 'active' && price > 50",
                        "description", "specification",
                        "warranty_info")
        
        # VIP商品或促销商品必须有营销信息
        check_list_when(products,
                        "is_vip == true || is_promotion == true",
                        "marketing_tags", "promotion_text")
    
    def test_comprehensive_validation(self, response):
        """综合校验测试 - 链式调用"""
        # 一次性校验多个层级的数据
        checker(response)\
            .equals("status_code", 200)\
            .not_empty("data.products")\
            .when("data.total_count > 0", "data.products.*.id")\
            .when_each("data.products.*.status == 'active'", 
                      "data.products.*.name", "data.products.*.price > 0")\
            .validate(failure_threshold=0.05)
```

## 错误处理

### 常见错误类型

1. **字段不存在**: `KeyError: 字段不存在: data.invalid_field`
2. **类型错误**: `TypeError: 无法在str上访问字段: field`
3. **索引错误**: `IndexError: 索引超出范围: data.list.10`
4. **校验失败**: 返回 `False`，不抛出异常
5. **阈值类型错误**: `ValueError: 不支持的阈值类型`

### 错误处理策略

```python
# 1. 校验结果处理
result = check(response, "data.product.id > 0", "data.product.name")
if not result:
    print("校验失败，请检查数据")

# 2. 异常处理
try:
    result = check(response, "data.invalid_field")
except Exception as e:
    print(f"数据结构异常: {e}")

# 3. 阈值模式错误处理
try:
    result = check(response, 
                   "data.product.id > 0",
                   "data.product.name",
                   failure_threshold="invalid")  # 错误的阈值类型
except ValueError as e:
    print(f"阈值参数错误: {e}")

# 4. 组合使用
try:
    result = checker(response)\
        .not_empty("data.product.name")\
        .greater_than("data.product.id", 0)\
        .validate(failure_threshold=0.2)
    
    if result:
        print("所有校验通过")
    else:
        print("部分校验失败，但在阈值范围内")
        
except Exception as e:
    print(f"数据结构异常: {e}")
```

## 日志控制

不同日志级别的输出内容：

### DEBUG级别
显示每个字段的详细校验过程：
- 待校验数据类型和规则列表
- 每个字段的具体值、类型、校验器和期望值
- 校验成功/失败的详细原因
- 失败阈值统计信息

### INFO级别  
显示校验开始和完成的汇总信息：
- 校验任务开始信息（规则数量、阈值设置）
- 校验完成结果（成功率统计、阈值达标情况）

### WARNING级别
显示校验失败的字段：
- `"[2/5] ✗ 校验失败: data.product.id > 0"`
- 阈值模式下的规则超限警告
- 条件校验下条件检查无匹配数据时，标识为校验通过

### ERROR级别
显示数据结构异常等严重错误：
- `"❌ 数据结构异常: 字段不存在"`
- `"❌ 数据结构异常: 字段路径匹配到 0 个值，请检查字段路径是否正确"`

```python
from general_validator.logger import setup_logger

# 设置不同的日志级别
setup_logger("DEBUG")    # 开发调试时使用
setup_logger("INFO")     # 生产环境推荐
setup_logger("WARNING")  # 只关注失败信息
setup_logger("ERROR")    # 只关注异常错误
```

```shell
# 搭配接口测试工具APIMeter使用时，支持直接在命令行自定日志级别
apimeter api-test.yml --log-level debug
apimeter api-test.yml --log-level info
apimeter api-test.yml --log-level warning
apimeter api-test.yml --log-level error
```


## 性能优化建议

1. **批量校验**: 尽量在一次`check()`调用中完成多个校验
2. **通配符使用**: 使用`*.field`比循环调用更高效
3. **阈值模式**: 合理设置失败阈值，避免不必要的严格校验
4. **短路求值**: 联合条件中，将常见的失败条件放在前面
5. **日志控制**: 生产环境使用`INFO`级别，避免DEBUG的性能开销
6. **合理分组**: 将相关的校验规则分组，便于维护和阅读


## 最佳实践

1. **优先使用字符串格式**: 比字典格式更简洁直观
2. **善用默认非空**: 大部分场景无需显式指定校验器
3. **通配符批量处理**: 列表数据优先使用通配符
4. **合理设置阈值**: 根据业务场景选择合适的失败阈值
5. **联合条件优化**: 利用短路求值特性优化性能
6. **条件语义选择**: 根据业务逻辑选择合适的条件校验方式
7. **错误信息友好**: 使用有意义的字段路径名称
8. **分层校验**: 按数据层级组织校验规则


## 常见注意事项

1. 校验规则有操作符、无参数值，默认为空字符串校验："status == && level == 'vip'"；
2. 条件校验场景中，包含condition条件规则和then校验规则，如果条件规则筛选不到数据，则相当于跳过then校验规则，默认标识为校验通过；
3. 校验规则匹配不到数据项，会抛出异常提醒：请检查字段路径是否正确；
4. 不仅仅在条件校验函数check_when、check_when_each、check_list_when中支持使用逻辑操作符进行联合条件校验，而且支持在核心校验函数check和check_when中使用逻辑操作符进行联合规则校验；
5. check_when_each函数条件表达式使用联合条件校验时，列表通配符.*定位进行校验的数据项集合列表必须一致，否则无法确定校验对象，例如：
```python
# 无法确定校验对象为orders列表还是items列表
"orders.*.status == 'active' && orders.*.items.*.price > 40"
```
6. 失败率阈值机制针对的不是整体校验规则的失败率，而是针对单个校验规则的失败率，因此任意一个校验规则的失败率超过阈值都将导致校验结果失败
```python
data = {
    "field1": "value1",
    "field2": "",       # 空
    "field3": "value3",
    "field4": None,     # 空
    "field5": "value5"
}

# 严格模式：False
check_not_empty(data, "field1", "field2", "field3")

# 比率阈值：False，因为失败率不是40%，而是两个规则有100%失败率，阈值是针对单个校验规则，而不是针对所有规则的整体情况
check_not_empty(data, "field1", "field2", "field3", "field4", "field5", failure_threshold=0.5)

# 数量阈值：True，因为两个规则都只有一个失败，所以阈值1也能通过
check_not_empty(data, "field1", "field2", "field3", "field4", "field5", failure_threshold=1)
```

7. 校验规则找不到对应字段，默认抛出异常。比如，空列表抛出异常
```python
empty_list = []

with pytest.raises(Exception):
    check_list(empty_list, "any_field")

with pytest.raises(Exception):
    check_list(empty_list, "field1", "field2", id="> 0")
```

## 常见问题

### Q: 如何校验字段值为null？
```python
check(response, "data.field == null")
```

### Q: 如何选择合适的失败阈值？
```python
# 严格业务逻辑：使用默认严格模式
check(data, "user.permissions", "user.status == 'active'")

# 数据质量监控：使用比率阈值
check(data, "records.*.email", failure_threshold=0.05)  # 允许5%异常

# 批量导入验证：使用数量阈值  
check(data, "items.*.name", failure_threshold=10)  # 允许10个异常
```

### Q: 联合条件的优先级如何理解？
```python
# && 优先级高于 ||，相当于：(A && B) || C
"status == 'active' && level == 'vip' || type == 'admin'"

# 如需改变优先级，将条件拆分到多个校验中
check_list_when(users, "status == 'active'", "permissions")  # 先校验活跃用户
check_list_when(users, "level == 'vip' || type == 'admin'", "advanced_features")  # 再校验高级用户
```

### Q: 三种条件校验语义怎么选择？
```python
# 1. check_when - 严格全部匹配，适用于全局条件
check_when(data, "all_products.*.status == 'active'", "all_products.*.price > 0")

# 2. check_when_each - 逐项检查，适用于个体条件  
check_when_each(data, "products.*.status == 'active'", "products.*.price > 0")

# 3. check_list_when - 列表专用，适用于已提取的列表
products = data["products"]  
check_list_when(products, "status == 'active'", "price > 0")
```

### Q: 如何处理复杂的嵌套数据？
```python
# 多层嵌套使用通配符
check(data, "regions.*.cities.*.districts.*.name")

# 复杂条件使用逐项校验
check_when_each(data, 
                "regions.*.cities.*.population > 1000000",
                "regions.*.cities.*.metro_lines", 
                "regions.*.cities.*.airports")
```

---

General-Validator 让数据校验变得简单而强大。通过极简的校验语法、灵活的阈值机制和强大的联合条件功能，轻松应对各种复杂的数据校验场景。🚀