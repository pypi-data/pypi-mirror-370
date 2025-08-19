# -*- coding:utf-8 -*-
from .logger import log_debug, log_info, log_warning, log_error, log_critical


class RuleStats:
    """单个校验规则的统计信息"""
    
    def __init__(self, rule_name):
        self.rule_name = rule_name
        self.total_count = 0      # 总校验次数
        self.failed_count = 0     # 失败次数
        self.failed_details = []  # 失败详情
    
    def add_result(self, success, detail=None):
        """添加校验结果"""
        self.total_count += 1
        if not success:
            self.failed_count += 1
            if detail:
                self.failed_details.append(detail)
    
    def get_failure_rate(self):
        """获取失败率"""
        return self.failed_count / self.total_count if self.total_count > 0 else 0.0
    
    def exceeds_threshold(self, threshold):
        """检查是否超过阈值"""
        if threshold is None:
            return self.failed_count > 0  # 严格模式
        elif isinstance(threshold, int):
            return self.failed_count > threshold  # 数量阈值
        elif isinstance(threshold, float):
            return self.get_failure_rate() > threshold  # 比率阈值
        else:
            raise ValueError(f"不支持的阈值类型: {type(threshold)}")


class ValidationContext:
    """校验上下文 - 管理所有规则的统计信息和执行控制"""
    
    def __init__(self, failure_threshold=None):
        self.failure_threshold = failure_threshold
        self.rule_stats = {}  # {rule_name: RuleStats}
        self.is_strict_mode = (failure_threshold is None)
        self.should_abort = False  # 严格模式快速失败标志
        self.current_rule_name = None  # 当前正在执行的规则名
        
        # 用于兼容原有日志格式的计数器
        self.passed_count = 0
        self.failed_count = 0
        self.total_validations = 0
    
    def get_or_create_rule_stats(self, rule_name):
        """获取或创建规则统计对象"""
        if rule_name not in self.rule_stats:
            self.rule_stats[rule_name] = RuleStats(rule_name)
        return self.rule_stats[rule_name]
    
    def set_current_rule(self, rule_name):
        """设置当前执行的规则名，用于日志输出"""
        self.current_rule_name = rule_name
    
    def record_field_result(self, success, field_path, validator, expect_value, check_value, detail=None):
        """记录单个字段的校验结果"""
        if self.current_rule_name:
            stats = self.get_or_create_rule_stats(self.current_rule_name)
            stats.add_result(success, detail)
            
            # 严格模式下遇到失败立即设置中断标志
            if self.is_strict_mode and not success:
                self.should_abort = True
    
    def record_rule_result(self, success):
        """记录整个规则的执行结果（用于兼容原有日志）"""
        # 更新全局计数器（用于严格模式的规则级别统计）
        if success:
            self.passed_count += 1
        else:
            self.failed_count += 1
            # 严格模式下规则失败时也要设置中断标志
            if self.is_strict_mode:
                self.should_abort = True
        
        self.total_validations += 1
    
    def check_all_thresholds(self):
        """检查是否有规则超过阈值"""
        if self.is_strict_mode:
            return self.failed_count == 0
        
        for rule_name, stats in self.rule_stats.items():
            if stats.exceeds_threshold(self.failure_threshold):
                log_warning(f"规则 '{rule_name}' 超过阈值: 失败{stats.failed_count}次，失败率{stats.get_failure_rate():.2%}")
                return False
        return True
    
    def get_validation_summary(self):
        """获取校验结果摘要"""
        if self.is_strict_mode:
            success_rate = f"{self.passed_count}/{self.total_validations}"
            rate_percent = (self.passed_count/self.total_validations*100) if self.total_validations > 0 else 0
            return success_rate, rate_percent
        else:
            total_rules = len(self.rule_stats)
            exceeded_rules = [stats for stats in self.rule_stats.values()
                            if stats.exceeds_threshold(self.failure_threshold)]
            return total_rules, len(exceeded_rules)


"""
通用工具函数
"""
def get_nested_value(obj, path):
    """根据点分隔的路径获取嵌套值"""
    if not path:
        return obj

    parts = path.split('.')
    current = obj

    for part in parts:
        if not isinstance(current, dict):
            raise TypeError(f"路径 '{path}' 中的 '{part}' 需要字典类型，当前类型: {type(current)}")
        if part not in current:
            raise KeyError(f"路径 '{path}' 中的字段 '{part}' 不存在")
        current = current[part]

    return current

def is_empty_value(value):
    """判断值是否为空"""
    if value is None:
        return True, "值为 None"
    if isinstance(value, str):
        if value.strip() == '':
            return True, "值为空字符串"
        if value.strip().lower() == 'null':
            return True, "值为字符串 'null'"
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True, f"值为空{type(value).__name__}"
    return False, None


"""
极简通用数据校验 - 默认非空校验，调用简洁
"""

def check(data, *validations, failure_threshold=None):
    """
    极简数据校验函数 - 默认非空校验
    
    :param data: 要校验的数据
    :param validations: 校验规则，支持多种简洁格式
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认，保持完全兼容性）
        - int: 每个规则最多允许N个失败 (如 failure_threshold=3)
        - float: 每个规则最多允许N%失败率 (如 failure_threshold=0.1 表示10%)
    :return: True表示所有校验通过，False表示存在校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例用法：
    # 默认非空校验 - 最简形式
    check(response, "data.product.id", "data.product.name")
    
    # 带校验器的形式
    check(response, "data.product.id > 0", "data.product.price >= 10.5")
    
    # 混合校验
    check(response, 
          "data.product.id",           # 默认非空
          "data.product.price > 0",    # 大于0
          "status_code == 200")        # 等于200
    
    # 列表批量校验 - 通配符
    check(response, "data.productList.*.id", "data.productList.*.name")
    
    # 嵌套列表校验
    check(response, "data.productList.*.purchasePlan.*.id > 0")
    """
    # 打印任务信息和数据概览
    log_info(f"开始执行数据校验 - 共{len(validations)}个校验规则")
    log_debug(f"待校验数据类型: {type(data).__name__}")
    log_debug(f"校验规则列表: {list(validations)}")
    log_debug(f"失败阈值: {'默认严格模式' if failure_threshold is None else failure_threshold}")
    
    # 创建校验上下文
    context = ValidationContext(failure_threshold)
    
    # 执行所有校验规则
    for i, validation in enumerate(validations):
        try:
            log_debug(f"[{i+1}/{len(validations)}] 开始校验: {validation}")
            
            # 设置当前规则名（用于统计）
            rule_name = f"rule_{i+1}: {validation}"
            context.set_current_rule(rule_name)
            
            result = _parse_and_validate(data, validation, context)
            
            # 记录规则级别的结果（用于正确的统计显示）
            if context.is_strict_mode:
                # 在严格模式下，规则的成功与否由_parse_and_validate的返回值决定
                context.record_rule_result(result)
                
                if not result:
                    log_warning(f"[{i+1}/{len(validations)}] 校验失败: {validation} ✗")
                    break
                else:
                    log_debug(f"[{i+1}/{len(validations)}] 校验通过: {validation} ✓")
            else:
                # 阈值模式下：在执行后立即检查该规则是否超过阈值
                if rule_name in context.rule_stats:
                    rule_stats = context.rule_stats[rule_name]
                    rule_exceeds_threshold = rule_stats.exceeds_threshold(context.failure_threshold)

                    # 记录规则结果：不超过阈值为成功
                    context.record_rule_result(not rule_exceeds_threshold)

                    if rule_exceeds_threshold:
                        log_warning(f"[{i+1}/{len(validations)}] 校验失败: {validation} ✗")
                    else:
                        log_debug(f"[{i+1}/{len(validations)}] 校验通过: {validation} ✓")
                else:
                    # 如果rule_stats不存在，说明可能没有字段级别的失败，默认为成功
                    context.record_rule_result(True)
                    log_debug(f"[{i+1}/{len(validations)}] 校验通过: {validation} ✓")
                
        except (KeyError, IndexError, TypeError, ValueError) as e:
            error_msg = f"数据结构异常: {validation} - {str(e)}"
            log_error(f"[{i+1}/{len(validations)}] ❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"校验出现异常: {validation} - '{str(e)}'"
            log_error(f"[{i+1}/{len(validations)}] ❌ {error_msg}")
            raise Exception(error_msg)
    
    # 计算最终结果
    if context.is_strict_mode:
        # 严格模式：任何失败都返回False
        final_result = not context.should_abort
        success_rate = f"{context.passed_count}/{len(validations)}"
        log_info(f"数据校验完成: {success_rate} 通过 (成功率: {context.passed_count/len(validations)*100:.1f}%)")
        
        if context.failed_count > 0:
            log_debug(f"失败统计: 共{context.failed_count}个校验失败")
    else:
        # 阈值模式：检查是否有规则超过阈值
        exceeded_rules = [stats for stats in context.rule_stats.values() 
                         if stats.exceeds_threshold(failure_threshold)]
        final_result = len(exceeded_rules) == 0
        
        # 输出详细统计
        _log_validation_summary(context)
    
    return final_result



def _log_validation_summary(context):
    """输出校验结果摘要"""
    total_rules = len(context.rule_stats)
    exceeded_rules = [stats for stats in context.rule_stats.values() 
                     if stats.exceeds_threshold(context.failure_threshold)]
    
    if isinstance(context.failure_threshold, int):
        threshold_desc = f"数量阈值{context.failure_threshold}"
    elif isinstance(context.failure_threshold, float):
        threshold_desc = f"比率阈值{context.failure_threshold:.1%}"
    else:
        threshold_desc = "严格模式"
    
    log_info(f"数据校验完成: 总规则{total_rules}个，超过阈值{len(exceeded_rules)}个 | 阈值设置: {threshold_desc}")
    
    if exceeded_rules:
        for stats in exceeded_rules:
            log_warning(f"规则超阈值详情: {stats.rule_name} - 失败{stats.failed_count}/{stats.total_count} (失败率{stats.get_failure_rate():.1%})")


def _parse_and_validate(data, rule, context):
    """解析校验规则并执行校验"""
    if isinstance(rule, str):
        return _parse_string_rule(data, rule, context)
    elif isinstance(rule, dict):
        return _parse_dict_rule(data, rule, context)
    else:
        raise ValueError(f"不支持的校验规则格式: {type(rule)}")


def _parse_logical_condition(data, rule, context):
    """解析包含逻辑操作符的联合条件表达式
    
    支持的逻辑操作符：
    - && (AND): 逻辑与，优先级高
    - || (OR): 逻辑或，优先级低
    
    操作符优先级: && > ||
    支持短路求值优化
    
    示例:
    - "status == 'active' && level == 'vip'"
    - "type == 'premium' || level == 'admin'"  
    - "status == 'active' && level == 'vip' || type == 'admin'"
    """
    log_debug(f"解析联合条件: {rule}")
    
    # 第一步: 按 || 分割 (优先级最低)
    or_parts = _split_logical_expression(rule, '||')
    
    if len(or_parts) > 1:
        # 有OR条件，任何一个为True即可 (短路求值)
        for or_part in or_parts:
            or_part = or_part.strip()
            try:
                if _evaluate_and_condition(data, or_part, context):
                    log_debug(f"OR条件命中: {or_part}")
                    return True
            except Exception as e:
                # 如果某个OR分支失败，继续尝试下一个
                log_debug(f"OR条件失败: {or_part} - {str(e)}")
                continue
        # 所有OR条件都失败
        log_debug("所有OR条件都失败")
        return False
    else:
        # 没有OR，只有AND或单一条件
        return _evaluate_and_condition(data, rule, context)


def _evaluate_and_condition(data, rule, context):
    """评估AND条件表达式"""
    # 按 && 分割
    and_parts = _split_logical_expression(rule, '&&')
    
    if len(and_parts) > 1:
        # 有AND条件，所有都必须为True (短路求值)
        for and_part in and_parts:
            and_part = and_part.strip()
            if not _parse_single_condition(data, and_part, context):
                log_debug(f"AND条件失败: {and_part}")
                return False
        log_debug("所有AND条件都通过")
        return True
    else:
        # 单一条件
        return _parse_single_condition(data, rule, context)


def _split_logical_expression(expression, operator):
    """安全分割逻辑表达式，正确处理引号内容"""
    parts = []
    current_part = ""
    in_quotes = False
    quote_char = None
    i = 0
    
    while i < len(expression):
        char = expression[i]
        
        # 处理引号
        if char in ('"', "'") and (i == 0 or expression[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        
        # 检查操作符
        if not in_quotes and i <= len(expression) - len(operator):
            if expression[i:i+len(operator)] == operator:
                # 找到操作符
                parts.append(current_part)
                current_part = ""
                i += len(operator)
                continue
        
        current_part += char
        i += 1
    
    # 添加最后一部分
    parts.append(current_part)
    return parts


def _parse_single_condition(data, rule, context):
    """解析单一条件（原_parse_string_rule的核心逻辑）"""
    # 支持的操作符映射 (注意：按长度排序，避免匹配冲突)
    operators = [
        ("#<=", "length_le"), ("#>=", "length_ge"), ("#!=", "length_ne"), ("#=", "length_eq"), ("#<", "length_lt"), ("#>", "length_gt"), ("!=", "ne"),
        ("==", "eq"), ("<=", "le"), (">=", "ge"), ("<", "lt"), (">", "gt"),
        ("~=", "regex"), ("^=", "startswith"), ("$=", "endswith"), ("*=", "contains"), ("=*", "contained_by"),
        ("@=", "type_match")
    ]
    
    # 尝试匹配操作符
    for op, validator in operators:
        if op in rule:
            parts = rule.split(op, 1)
            if len(parts) == 2:
                field_path = parts[0].strip()
                expect_value = parts[1].strip()
                
                # 解析期望值
                expect_value = _parse_expect_value(expect_value)
                
                # 执行校验
                return _validate_field_path(data, field_path, validator, expect_value, context)
    
    # 没有操作符，默认为非空校验
    field_path = rule.strip()
    return _validate_field_path(data, field_path, "not_empty", True, context)


def _parse_string_rule(data, rule, context):
    """解析字符串格式的校验规则"""
    # 检查是否包含逻辑操作符
    if '&&' in rule or '||' in rule:
        return _parse_logical_condition(data, rule, context)
    
    # 单一条件，使用原有逻辑
    return _parse_single_condition(data, rule, context)


def _parse_dict_rule(data, rule, context):
    """解析字典格式的校验规则"""
    field_path = rule.get('field')
    validator = rule.get('validator', 'not_empty')
    expect_value = rule.get('expect')
    
    if not field_path:
        raise ValueError("字典格式校验规则必须包含'field'键")
    
    return _validate_field_path(data, field_path, validator, expect_value, context)


def _parse_expect_value(value_str):
    """解析期望值字符串为合适的类型"""
    value_str = value_str.strip()
    
    # 去掉引号
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # 数字
    if value_str.isdigit():
        return int(value_str)
    
    # 浮点数
    try:
        if '.' in value_str:
            return float(value_str)
    except ValueError:
        pass
    
    # 布尔值
    if value_str.lower() in ['true', 'false']:
        return value_str.lower() == 'true'
    
    # null
    if value_str.lower() in ['null', 'none']:
        return None
    
    # 默认返回字符串
    return value_str


def _validate_field_path(data, field_path, validator, expect_value, context):
    """校验字段路径 - 统一严格模式和阈值模式
    
    :param context: ValidationContext对象，None表示当前是执行条件校验condition条件规则检查，不记录结果到统计中
    :return: True表示校验通过或需要继续执行，False表示严格模式下需要立即停止
    """
    # 特殊处理：条件校验(校验规则为字典格式场景，直接调用对应函数)
    if validator.startswith("conditional"):
        condition = expect_value['condition']
        then_rules = expect_value['then'] if isinstance(expect_value['then'], list) else [expect_value['then']]
        if validator == "conditional_check":
            return check_when(data, condition, *then_rules, failure_threshold=context.failure_threshold)
        elif validator == "conditional_list_check":
            return check_list_when(data, condition, *then_rules, failure_threshold=context.failure_threshold)
        elif validator == "conditional_each_check":
            return check_when_each(data, condition, *then_rules, failure_threshold=context.failure_threshold)

    values = _get_values_by_path(data, field_path)
    log_debug(f"字段路径 '{field_path}' 匹配到 {len(values)} 个值")
    if len(values) == 0:
        raise ValueError(f"字段路径 '{field_path}' 匹配到 0 个值，请检查字段路径是否正确")
    
    for value, path in values:
        result = _execute_validator(validator, value, expect_value, path)
        detail = f"校验字段 '{path}': {type(value).__name__} = {repr(value)} | 校验器: {validator} | 期望值: {repr(expect_value)}"
        
        if context is not None:
            # context不为 None，说明当前是执行普通校验规则，记录结果到统计中
            context.record_field_result(result, path, validator, expect_value, value, detail)
            if result:
                log_debug(f"{detail} | 检验结果: ✓")
            else:
                log_warning(f"{detail} | 检验结果: ✗")
                # 严格模式下立即返回失败
                if context.is_strict_mode:
                    return False
        else:
            # context为 None，说明当前是执行条件校验condition条件规则检查，不记录结果到统计中
            if result:
                log_debug(f"{detail} | 检验结果: ✓")
            else:
                log_warning(f"{detail} | 检验结果: ✗")
                return False

    return True



def _get_values_by_path(obj, path):
    """根据路径获取值，支持通配符*"""
    if not path:
        return [(obj, "")]
    
    parts = path.split('.')
    current_objects = [(obj, "")]
    
    for part in parts:
        next_objects = []
        for current_obj, current_path in current_objects:
            new_path = f"{current_path}.{part}" if current_path else part
            
            if part == '*':
                if isinstance(current_obj, list):
                    for i, item in enumerate(current_obj):
                        next_objects.append((item, f"{current_path}[{i}]" if current_path else f"[{i}]"))
                elif isinstance(current_obj, dict):
                    for key, value in current_obj.items():
                        next_objects.append((value, f"{current_path}.{key}" if current_path else key))
                else:
                    raise TypeError(f"通配符'*'只能用于列表或字典，路径: {current_path}, 类型: {type(current_obj)}")
            else:
                if isinstance(current_obj, dict):
                    if part not in current_obj:
                        raise KeyError(f"字段不存在: {new_path}")
                    next_objects.append((current_obj[part], new_path))
                elif isinstance(current_obj, list):
                    if not part.isdigit():
                        raise ValueError(f"列表索引必须是数字: {part}")
                    index = int(part)
                    if index < 0 or index >= len(current_obj):
                        raise IndexError(f"索引超出范围: {new_path}")
                    next_objects.append((current_obj[index], f"{current_path}[{index}]" if current_path else f"[{index}]"))
                else:
                    raise TypeError(f"无法在{type(current_obj)}上访问字段: {part}")
        current_objects = next_objects
    
    return current_objects


def _check_type_match(check_value, expect_value):
    """检查值的类型是否匹配期望类型
    
    :param check_value: 要检查的值
    :param expect_value: 期望的类型，可以是类型对象或类型名称字符串
    :return: True表示类型匹配，False表示类型不匹配
    """
    def get_type(name):
        """根据名称获取类型对象"""
        if isinstance(name, type):
            return name
        elif isinstance(name, str):
            # 支持常见的类型名称
            type_mapping = {
                'int': int,
                'float': float,
                'str': str,
                'string': str,
                'bool': bool,
                'boolean': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'nonetype': type(None),
                'none': type(None),
                'null': type(None)
            }
            
            # 先检查自定义映射
            if name.lower() in type_mapping:
                return type_mapping[name.lower()]
            
            # 尝试从内置类型获取
            try:
                return eval(name)
            except:
                raise ValueError(f"不支持的类型名称: {name}")
        else:
            raise ValueError(f"期望值必须是类型对象或类型名称字符串，当前类型: {type(expect_value)}")
    
    try:
        expected_type = get_type(expect_value)
        return isinstance(check_value, expected_type)
    except Exception as e:
        raise TypeError(f"类型匹配检查失败: {str(e)}")


def _safe_numeric_compare(check_value, expect_value):
    """安全的数值比较，支持字符串数字自动转换
    
    :param check_value: 要检查的值
    :param expect_value: 期望值
    :return: (转换后的check_value, 转换后的expect_value)
    :raises: ValueError: 当值无法转换为数字时
    """
    def to_number(value):
        """将值转换为数字"""
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            # 去除首尾空格
            value = value.strip()
            # 尝试转换为整数
            try:
                return int(value)
            except ValueError:
                pass
            # 尝试转换为浮点数
            try:
                return float(value)
            except ValueError:
                pass
        # 无法转换，返回原值
        return value
    
    # 转换两个值
    converted_check = to_number(check_value)
    converted_expect = to_number(expect_value)
    
    # 如果任一值无法转换为数字，回退到原始比较
    if (not isinstance(converted_check, (int, float)) or not isinstance(converted_expect, (int, float))):
        return check_value, expect_value
    
    return converted_check, converted_expect


def _execute_validator(validator, check_value, expect_value, field_path):
    """执行具体的校验
    
    :return: True表示校验通过，False表示校验失败
    :raises: ValueError: 当校验器不支持时
    :raises: TypeError: 当数据类型不匹配时
    """
    try:
        if validator == "not_empty":
            is_empty, _ = is_empty_value(check_value)
            return not is_empty
        
        elif validator == "eq":
            return check_value == expect_value
        
        elif validator == "ne":
            return check_value != expect_value
        
        elif validator == "gt":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val > expect_val
        
        elif validator == "ge":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val >= expect_val
        
        elif validator == "lt":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val < expect_val
        
        elif validator == "le":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val <= expect_val
        
        elif validator == "contains":
            return expect_value in check_value
        
        elif validator == "contained_by":
            return check_value in expect_value
        
        elif validator == "startswith":
            return str(check_value).startswith(str(expect_value))
        
        elif validator == "endswith":
            return str(check_value).endswith(str(expect_value))
        
        elif validator == "regex":
            import re
            try:
                return bool(re.match(str(expect_value), str(check_value)))
            except re.error:
                return False
        
        elif validator == "type_match":
            return _check_type_match(check_value, expect_value)
        
        elif validator == "custom_number_check":
            return isinstance(check_value, (int, float))
        
        elif validator == "in_values":
            return check_value in expect_value
        
        elif validator == "not_in_values":
            return check_value not in expect_value
        
        elif validator == "length_eq":
            return len(check_value) == expect_value
        
        elif validator == "length_ne":
            return len(check_value) != expect_value
        
        elif validator == "length_gt":
            return len(check_value) > expect_value
        
        elif validator == "length_ge":
            return len(check_value) >= expect_value

        elif validator == "length_lt":
            return len(check_value) < expect_value
        
        elif validator == "length_le":
            return len(check_value) <= expect_value

        elif validator == "length_between":
            min_len, max_len = expect_value
            return min_len <= len(check_value) <= max_len
        
        else:
            raise ValueError(f"不支持的校验器: {validator}")
    
    except Exception as e:
        log_error(f"执行校验时出现异常：校验字段 '{field_path}': {type(check_value).__name__} = {repr(check_value)} | 校验器: {validator} | 期望值: {repr(expect_value)} | 异常信息: {str(e)}")
        raise


def _parse_path_expression(expression):
    """
    解析路径表达式，返回路径前缀和相对表达式
    
    支持联合条件和单一条件的路径解析，基于列表通配符.*的位置进行分割

    例如：
    "users.*.status == 'active'" -> ("users.*", "status == 'active'")
    "users.*.status == 'active' && users.*.level == 'vip'" -> ("users.*", "status == 'active' && level == 'vip'")
    "data.regions.*.cities.*.status == 'active'" -> ("data.regions.*.cities.*", "status == 'active'")
    
    :param expression: 路径表达式字符串，必须包含列表通配符.*以定位列表数据项集合
    :return: (路径前缀, 相对表达式)
    :raises: ValueError: 当表达式格式不正确时
    """
    if not expression or not isinstance(expression, str):
        raise ValueError(f"表达式必须是非空字符串，当前值: {expression}")
    
    expression = expression.strip()
    
    # 验证必须包含列表通配符.*以定位列表数据项集合
    if '.*' not in expression:
        raise ValueError(f"路径表达式必须包含列表通配符.*以定位列表数据项集合: {expression}")
    
    # 检查是否为联合条件
    if '&&' in expression or '||' in expression:
        return _parse_compound_path_expression(expression)
    else:
        return _parse_single_path_expression(expression)


def _parse_single_path_expression(expression):
    """解析单一条件的路径表达式"""
    # 找到最后一个列表通配符.*的位置
    last_wildcard_pos = expression.rfind('.*')
    
    # 向前查找到最近的点号，确定路径前缀的结束位置
    prefix_end = last_wildcard_pos + 2  # 包含.*号
    
    # 向后查找到最近的点号，确定相对表达式的开始位置
    remaining_part = expression[prefix_end:]
    if remaining_part.startswith('.'):
        relative_start = prefix_end + 1  # 跳过点号
    else:
        raise ValueError(f"路径表达式中列表通配符.*后必须有具体字段: {expression}")
    
    # 分割路径前缀和相对表达式
    path_prefix = expression[:prefix_end]
    relative_expression = expression[relative_start:]
    
    # 验证相对表达式不为空
    if not relative_expression:
        raise ValueError(f"路径表达式中列表通配符.*后必须有具体字段: {expression}")
    
    return path_prefix, relative_expression


def _parse_compound_path_expression(expression):
    """解析联合条件的路径表达式"""
    # 首先找到所有的路径前缀
    path_prefixes = set()
    
    # 分解联合条件为单个条件
    conditions = _extract_individual_conditions(expression)
    
    for condition in conditions:
        condition = condition.strip()
        if '.*' not in condition:
            continue
            
        # 找到最后一个列表通配符.*的位置
        last_wildcard_pos = condition.rfind('.*')
        prefix_end = last_wildcard_pos + 2  # 包含.*号
        
        # 确定路径前缀
        path_prefix = condition[:prefix_end]
        path_prefixes.add(path_prefix)
    
    # 验证所有条件使用相同的路径前缀
    if len(path_prefixes) != 1:
        raise ValueError(f"联合条件中所有子条件必须使用相同的路径前缀: {list(path_prefixes)}")
    
    common_prefix = list(path_prefixes)[0]
    
    # 构建相对表达式：将所有条件的路径前缀替换为空
    relative_expression = _build_relative_expression(expression, common_prefix)
    
    return common_prefix, relative_expression


def _extract_individual_conditions(expression):
    """从联合条件表达式中提取单个条件"""
    # 首先按 || 分割
    or_parts = _split_logical_expression(expression, '||')
    
    conditions = []
    for or_part in or_parts:
        # 再按 && 分割每个 OR 部分
        and_parts = _split_logical_expression(or_part, '&&')
        conditions.extend(and_parts)
    
    return [cond.strip() for cond in conditions if cond.strip()]


def _build_relative_expression(expression, path_prefix):
    """构建相对表达式，去掉路径前缀"""
    # 替换所有路径前缀为空
    prefix_pattern = path_prefix + '.'
    relative_expr = expression.replace(prefix_pattern, '')
    
    # 清理多余的空格
    relative_expr = ' '.join(relative_expr.split())
    
    return relative_expr


def _perform_item_wise_conditional_check(data_list, condition, then_rules, failure_threshold):
    """
    执行逐项条件校验的核心逻辑
    
    对列表中的每个数据项分别进行条件+then检查的通用实现
    
    :param data_list: 要校验的数据项列表
    :param condition: 条件表达式（已解析好的相对表达式）
    :param then_rules: then规则列表（已解析好的相对表达式）
    :param failure_threshold: 失败阈值
    :return: 校验结果布尔值
    :raises: Exception: 当条件校验异常或数据结构异常时
    """
    # 统计满足条件的数据项
    satisfied_items = []
    
    # 第一轮：筛选满足条件的数据项
    for i, item in enumerate(data_list):
        try:
            condition_result = _parse_and_validate(item, condition, context=None)
            if condition_result:
                satisfied_items.append(item)
                log_debug(f"数据项[{i}]满足条件: {condition}")
            else:
                log_debug(f"数据项[{i}]不满足条件: {condition}, 跳过")
        except Exception as e:
            error_msg = f"数据项[{i}]条件校验异常: {condition} - {str(e)}"
            log_error(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    if not satisfied_items:
        log_warning(f"没有数据项满足条件: {condition}, 跳过then校验")
        return True
    
    log_debug(f"共{len(satisfied_items)}/{len(data_list)}个数据项满足条件，开始then校验")
    
    # 第二轮：对满足条件的数据项执行then校验
    # 需要将then规则转换为适合字典列表的格式（添加*.前缀）
    list_then_rules = [f"*.{rule}" for rule in then_rules]
    return check(satisfied_items, *list_then_rules, failure_threshold=failure_threshold)


def check_not_empty(data, *field_paths, failure_threshold=None):
    """专门的非空校验 - 最常用场景"""
    return check(data, *field_paths, failure_threshold=failure_threshold)


def check_when(data, condition, *then, failure_threshold=None):
    """
    严格条件校验 - 所有匹配项都满足条件时才执行then校验（第一种语义）

    语义说明：
    1. 对所有数据项进行条件校验
    2. 如果所有数据项都满足条件，就执行then规则校验
    3. 如果任一数据项不满足条件，就跳过整个then校验
    4. 每个then规则有独立的统计维度
    
    :param data: 要校验的数据
    :param condition: 条件表达式，支持所有校验器语法
    :param then: then表达式，支持所有校验器语法，可传入多个校验规则
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :return: True表示校验通过或条件不成立，False表示校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    # 单个then校验 - 当status为active时，price必须大于0
    check_when(data, "status == 'active'", "price > 0")
    
    # 多个then校验 - 当type为premium时，features字段不能为空且price必须大于100
    check_when(data, "type == 'premium'", "features", "price > 100")
    
    # 批量校验 - 当status为active时，多个字段都必须校验通过
    check_when(data, "status == 'active'",
               "price > 0",
               "name",
               "description",
               "category != 'test'")
    
    # 支持通配符 - 当所有产品状态为active时，价格都必须大于0且名称不能为空
    check_when(data, "products.*.status == 'active'",
               "products.*.price > 0",
               "products.*.name")
    
    # 混合条件校验 - 当用户为VIP时，多个权限字段都必须校验
    check_when(data, "user.level == 'vip'",
               "user.permissions.download == true",
               "user.permissions.upload == true",
               "user.quota > 1000")

    注意：
    1. 当条件满足时，所有then校验都必须通过才算成功
    2. 当条件不满足时，跳过所有then校验（返回True）
    """
    
    # 参数验证
    if not then:
        raise ValueError("至少需要提供一个then校验规则")
    
    log_info(f"开始严格条件校验 - 数据长度: {len(data)}, then规则数: {len(then)}")
    log_debug(f"校验规则: check_when({condition}) then({', '.join(str(rule) for rule in then)})")
    log_debug(f"失败阈值: {'默认严格模式' if failure_threshold is None else failure_threshold}")
    
    try:
        # 检查条件是否满足（条件检查不计入统计）
        condition_result = _parse_and_validate(data, condition, context=None)

        if not condition_result:
            # 条件不成立，跳过then校验
            log_warning(f"条件不成立: check_when({condition}), 跳过then校验")
            return True

        # 条件成立，直接调用check()函数校验then规则。这样每个then规则自然成为独立的统计维度
        log_debug(f"条件成立: check_when({condition}), 执行then校验")
        return check(data, *then, failure_threshold=failure_threshold)
        
    except (KeyError, IndexError, TypeError, ValueError) as e:
        error_msg = f"严格条件校验数据结构异常: check_when({condition}) - {str(e)}"
        log_error(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"严格条件校验出现异常: check_when({condition}) - '{str(e)}'"
        log_error(f"❌ {error_msg}")
        raise Exception(error_msg)


def check_when_each(data, condition, *then, failure_threshold=None):
    """
    逐项条件校验 - 对指定路径下的每个数据项分别进行条件+then检查（第二种语义）
    
    语义说明：
    1. 通过路径表达式定位要检查的数据项列表
    2. 对每个数据项分别进行条件检查
    3. 对满足条件的数据项执行then规则校验，不满足则跳过
    4. 每个then规则按照满足条件的数据项独立统计失败率

    与check_list_when的区别：
    - check_list_when：专门用于列表数据，需要预先提取列表，如 users = data["users"]
    - check_when_each：支持任意数据类型，直接使用路径表达式，如 "users.*.status == 'active'"
    
    :param data: 要校验的数据（任意类型）
    :param condition: 条件表达式，使用路径表达式，如 "users.*.status == 'active'"
    :param then: then规则，使用路径表达式，如 "users.*.score > 70"，可传入多个校验规则
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :return: True表示校验通过或条件都不成立，False表示校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例用法：
    # 基础用法 - 直接使用路径表达式，无需预提取列表
    check_when_each(data, "users.*.status == 'active'", "users.*.score > 70")
    
    # 多个then规则 - 活跃VIP用户必须有名字且分数大于80
    check_when_each(data, "users.*.status == 'active'", "users.*.name", "users.*.score > 80")
    
    # 深度嵌套场景 - 支持复杂路径表达式
    check_when_each(response, "data.regions.*.cities.*.status == 'active'", "data.regions.*.cities.*.population > 0")
    
    # 阈值模式 - 允许30%的活跃用户分数不达标
    check_when_each(data, "users.*.status == 'active'", "users.*.score > 70", failure_threshold=0.3)
    
    # 与当前check_list_when的等价用法对比：
    # 当前方式（需要预提取）：
    # users = data["users"]
    # check_list_when(users, "status == 'active'", "score > 70")
    # 
    # 新方式（直接路径表达式）：
    # check_when_each(data, "users.*.status == 'active'", "users.*.score > 70")
    
    适用场景：
    - 任意数据结构，不限于列表
    - 需要通过复杂路径表达式定位数据项
    - 希望统计满足条件的数据项中then规则的失败率
    - 避免手动提取数据子集

    注意事项：
    1. 条件表达式中必须包含列表通配符.*以定位进行校验的数据项集合列表
    2. 条件表达式中列表通配符.*后必须有具体字段，如"users.*.status == 'active'"
    3. 条件表达式使用联合条件时，列表通配符.*定位进行校验的数据项集合列表必须一致，否则无法确定校验对象
       - 正确示例："users.*.status == 'active' && users.*.level == 'vip'" -> 校验对象为users列表中的每个数据项
       - 错误示例："orders.*.status == 'active' && orders.*.items.*.price > 40" -> 无法确定校验对象为orders列表还是items列表
    """
    
    # 参数验证
    if not then:
        raise ValueError("至少需要提供一个then校验规则")
    
    log_info(f"开始逐项条件校验 - 数据长度: {len(data)}, then规则数: {len(then)}")
    log_debug(f"校验规则: check_when_each({condition}) then({', '.join(str(rule) for rule in then)})")
    log_debug(f"失败阈值: {'默认严格模式' if failure_threshold is None else failure_threshold}")
    
    try:
        # 解析条件表达式，提取路径前缀和相对条件
        condition_path_prefix, relative_condition = _parse_path_expression(condition)
        log_debug(f"条件表达式解析: 路径前缀='{condition_path_prefix}', 相对条件='{relative_condition}'")
        
        # 验证所有条件和then规则都使用相同的路径前缀（各个then规则可以嵌套深度不一样，但路径前缀必须和condition路径前缀一致，以确保针对的列表对象一致）
        relative_then_rules = []
        for i, rule in enumerate(then):
            if not rule.startswith(condition_path_prefix + '.'):
                raise ValueError(f"条件和then规则的路径前缀必须相同: 条件路径前缀='{condition_path_prefix}' vs then[{i+1}]='{rule}'")

            # 相对规则等于rule规则删掉所有condition_path_prefix路径前缀(支持单规则和联合规则)
            relative_rule = rule.replace(condition_path_prefix + '.', '') if rule.startswith(condition_path_prefix + '.') else rule
            log_debug(f"then规则[{i+1}]解析: 路径前缀='{condition_path_prefix}', 相对规则='{relative_rule}'")

            relative_then_rules.append(relative_rule)
        
        # 获取要遍历的数据项列表
        log_debug(f"使用路径前缀获取数据项: {condition_path_prefix}")
        data_items = _get_values_by_path(data, condition_path_prefix)
        data_list = [item_value for item_value, _ in data_items]
        
        if not data_list:
            log_warning(f"路径 '{condition_path_prefix}' 没有匹配到任何数据项, 跳过校验")
            return True
        
        log_debug(f"路径 '{condition_path_prefix}' 匹配到 {len(data_list)} 个数据项")
        
        
        # 调用核心函数执行逐项条件校验
        return _perform_item_wise_conditional_check(data_list, relative_condition, relative_then_rules, failure_threshold)
        
    except (KeyError, IndexError, TypeError, ValueError) as e:
        error_msg = f"逐项条件校验数据结构异常: check_when_each({condition}) - {str(e)}"
        log_error(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"逐项条件校验出现异常: check_when_each({condition}) - '{str(e)}'"
        log_error(f"❌ {error_msg}")
        raise Exception(error_msg)


def check_list_when(data_list, condition, *then, failure_threshold=None):
    """
    条件校验第二种语义：逐项条件校验 - check_when_each函数的简化版，专门用于列表数据

    语义说明：
    1. 针对数据项列表，对每个数据项分别进行条件检查
    2. 对满足条件的数据项执行then规则校验，不满足则跳过
    3. 每个then规则按照满足条件的数据项独立统计失败率
    4. 每个then规则的失败率 = (满足条件但then失败的数据项数) / (满足条件的数据项总数)

    :param data_list: 要校验的数据列表
    :param condition: 条件表达式，支持所有校验器语法
    :param then: then表达式，支持所有校验器语法，可传入多个校验规则
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :return: True表示校验通过或条件都不成立，False表示校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常

    示例用法：
    # 基础用法 - 对用户列表，活跃用户的分数必须大于70
    users = [
        {"name": "张三", "status": "active", "score": 85},
        {"name": "李四", "status": "active", "score": 65},  # 条件满足但then失败
        {"name": "王五", "status": "inactive", "score": 70}  # 条件不满足，跳过
    ]
    check_list_when(users, "status == 'active'", "score > 70")

    # 多个then规则 - 活跃用户必须有名字且分数大于80
    check_list_when(users, "status == 'active'", "name", "score > 80")

    # 阈值模式 - 允许30%的活跃用户分数不达标
    check_list_when(users, "status == 'active'", "score > 70", failure_threshold=0.3)

    与check_when的区别：
    - check_when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
    - check_list_when：每个数据项单独进行条件+then检查（逐项检查）

    适用场景：
    - list of dict 列表数据结构
    - 需要对列表中符合条件的数据项进行个别校验
    - 希望统计满足条件的数据项中then规则的失败率
    """

    # 参数验证
    if not isinstance(data_list, list):
        raise TypeError(f"data_list必须是列表，当前类型: {type(data_list)}")

    if not then:
        raise ValueError("至少需要提供一个then校验规则")

    log_info(f"开始列表逐项条件校验 - 列表长度: {len(data_list)}, then规则数: {len(then)}")
    log_debug(f"校验规则: check_list_when({condition}) then({', '.join(str(rule) for rule in then)})")
    log_debug(f"失败阈值: {'默认严格模式' if failure_threshold is None else failure_threshold}")

    try:
        # 调用核心函数执行逐项条件校验
        return _perform_item_wise_conditional_check(data_list, condition, then, failure_threshold)

    except (KeyError, IndexError, TypeError, ValueError) as e:
        error_msg = f"列表逐项条件校验数据结构异常: check_list_when({condition}) - {str(e)}"
        log_error(f"❌ {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"列表逐项条件校验出现异常: check_list_when({condition}) - '{str(e)}'"
        log_error(f"❌ {error_msg}")
        raise Exception(error_msg)


def check_list(data_list, *field_names, failure_threshold=None, **validators):
    """
    列表数据批量校验 - 简化版
    
    :param data_list: 数据列表
    :param field_names: 字段名（默认非空校验，同时支持符号表达式校验和字典格式参数校验）
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :param validators: 带校验器的字段 field_name="validator expression"}
    :return: True表示所有校验通过，False表示存在校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    # 默认非空校验
    check_list(productList, "id", "name", "price")
    
    # 带校验器
    check_list(productList, "name", id="> 0", price=">= 0")
    或
    check_list(productList, "name", "id > 0", "price >= 0")
    
    # 混合使用
    check_list(productList, "name", "description", id="> 0", status="== 'active'")
    或
    check_list(productList, "name", "description", "id > 0", "status == 'active'")
    """
    
    total_fields = len(field_names) + len(validators)
    log_info(f"列表数据批量校验 - 列表长度: {len(data_list) if isinstance(data_list, list) else '未知'}, 字段数: {total_fields}")
    log_debug(f"非空校验字段: {list(field_names)}")
    log_debug(f"带校验器字段: {dict(validators)}")
    
    if not isinstance(data_list, list):
        raise TypeError(f"data_list必须是列表，当前类型: {type(data_list)}")
    
    # 构建校验规则
    rules = []
    
    # 默认非空校验的字段
    for field in field_names:
        rules.append(f"*.{field}")
    
    # 带校验器的字段
    for field, validator_expr in validators.items():
        rules.append(f"*.{field} {validator_expr}")
    
    # 执行校验
    return check(data_list, *rules, failure_threshold=failure_threshold)


def check_nested(data, list_path, nested_field, *field_validations, failure_threshold=None):
    """
    嵌套列表数据批量校验 - 简化版
    
    :param data: 要校验的数据
    :param list_path: 主列表路径
    :param nested_field: 嵌套字段名
    :param field_validations: 字段校验规则
    :param failure_threshold: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率
    :return: True表示所有校验通过，False表示存在校验失败
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    # 默认非空校验
    check_nested(response, "data.productList", "purchasePlan", "id", "name")
    
    # 带校验器
    check_nested(response, "data.productList", "purchasePlan", "id > 0", "amount >= 100")
    """
    
    log_info(f"嵌套列表数据批量校验 - 路径: {list_path}.*.{nested_field}, 字段数: {len(field_validations)}")
    log_debug(f"主列表路径: {list_path}")
    log_debug(f"嵌套字段名: {nested_field}")
    log_debug(f"字段校验规则: {list(field_validations)}")
    
    main_list_value = get_nested_value(data, list_path)
    if isinstance(main_list_value, list) and len(main_list_value) > 0:
        nested_field_value = main_list_value[0][nested_field]
    else:
        raise ValueError(f"主列表路径 {list_path} 的值不是列表或为空列表")

    # 构建校验规则
    rules = []
    for validation in field_validations:
        if isinstance(nested_field_value, list):
            # 嵌套字段值为列表
            rules.append(f"{list_path}.*.{nested_field}.*.{validation}")
        elif isinstance(nested_field_value, dict):
            # 嵌套字段值为字典
            rules.append(f"{list_path}.*.{nested_field}.{validation}")
        else:
            raise ValueError(f"嵌套字段 {nested_field} 的值不是列表或字典")

    return check(data, *rules, failure_threshold=failure_threshold)


class DataChecker:
    """链式调用的数据校验器"""
    
    def __init__(self, data):
        self.data = data
        self.rules = []
    
    def field(self, path, validator=None, expect=None):
        """添加字段校验"""
        if validator is None:
            # 默认非空
            self.rules.append(path)
        elif expect is None:
            # 字符串表达式
            self.rules.append(f"{path} {validator}")
        else:
            # 分离的校验器和期望值
            self.rules.append(f"{path} {validator} {expect}")
        return self
    
    def not_empty(self, *paths):
        """批量非空校验"""
        self.rules.extend(paths)
        return self
    
    # 等值比较校验
    def equals(self, path, value):
        """等于校验"""
        self.rules.append(f"{path} == {repr(value)}")
        return self
    
    def not_equals(self, path, value):
        """不等于校验"""
        self.rules.append(f"{path} != {repr(value)}")
        return self
    
    # 数值比较校验
    def greater_than(self, path, value):
        """大于校验"""
        self.rules.append(f"{path} > {value}")
        return self
    
    def greater_equal(self, path, value):
        """大于等于校验"""
        self.rules.append(f"{path} >= {value}")
        return self
    
    def less_than(self, path, value):
        """小于校验"""
        self.rules.append(f"{path} < {value}")
        return self
    
    def less_equal(self, path, value):
        """小于等于校验"""
        self.rules.append(f"{path} <= {value}")
        return self
    
    # 数值范围校验
    def between(self, path, min_value, max_value, inclusive=True):
        """数值区间校验"""
        if inclusive:
            self.rules.append(f"{path} >= {min_value}")
            self.rules.append(f"{path} <= {max_value}")
        else:
            self.rules.append(f"{path} > {min_value}")
            self.rules.append(f"{path} < {max_value}")
        return self
    
    # 字符串校验
    def starts_with(self, path, prefix):
        """以指定字符串开头"""
        self.rules.append(f"{path} ^= {repr(prefix)}")
        return self
    
    def ends_with(self, path, suffix):
        """以指定字符串结尾"""
        self.rules.append(f"{path} $= {repr(suffix)}")
        return self
    
    def contains(self, path, substring):
        """包含指定字符串"""
        self.rules.append(f"{path} *= {repr(substring)}")
        return self
    
    def contained_by(self, path, container):
        """被指定字符串包含"""
        self.rules.append(f"{path} =* {repr(container)}")
        return self
    
    def matches_regex(self, path, pattern):
        """正则表达式匹配"""
        self.rules.append(f"{path} ~= {repr(pattern)}")
        return self
    
    # 类型校验
    def is_type(self, path, expected_type):
        """类型校验"""
        if isinstance(expected_type, type):
            type_name = expected_type.__name__
        else:
            type_name = str(expected_type)
        self.rules.append(f"{path} @= {repr(type_name)}")
        return self
    
    def is_string(self, path):
        """字符串类型校验"""
        return self.is_type(path, 'str')
    
    def is_number(self, path):
        """数字类型校验（int或float）"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'custom_number_check',
            'expect': None
        })
        return self
    
    def is_integer(self, path):
        """整数类型校验"""
        return self.is_type(path, 'int')
    
    def is_float(self, path):
        """浮点数类型校验"""
        return self.is_type(path, 'float')
    
    def is_boolean(self, path):
        """布尔类型校验"""
        return self.is_type(path, 'bool')
    
    def is_list(self, path):
        """列表类型校验"""
        return self.is_type(path, 'list')
    
    def is_dict(self, path):
        """字典类型校验"""
        return self.is_type(path, 'dict')
    
    def is_none(self, path):
        """None类型校验"""
        return self.is_type(path, 'none')
    
    # 集合校验
    def in_values(self, path, values):
        """值在指定集合中"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'in_values',
            'expect': values
        })
        return self
    
    def not_in_values(self, path, values):
        """值不在指定集合中"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'not_in_values',
            'expect': values
        })
        return self
    
    # 长度校验
    def length_equals(self, path, length):
        """长度等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_eq',
            'expect': length
        })
        return self
    
    def length_not_equals(self, path, length):
        """长度不等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_ne',
            'expect': length
        })
        return self
    
    def length_greater_than(self, path, length):
        """长度大于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_gt',
            'expect': length
        })
        return self
    
    def length_less_than(self, path, length):
        """长度小于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_lt',
            'expect': length
        })
        return self

    def length_greater_equal(self, path, length):
        """长度大于等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_ge',
            'expect': length
        })
        return self
    
    def length_less_equal(self, path, length):
        """长度小于等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_le',
            'expect': length
        })
        return self

    def length_between(self, path, min_length, max_length, inclusive=True):
        """长度在指定范围内"""
        if inclusive:
            self.rules.append({
                'field': path,
                'validator': 'length_ge',
                'expect': min_length
            })
            self.rules.append({
                'field': path,
                'validator': 'length_le',
                'expect': max_length
            })
        else:
            self.rules.append({
                'field': path,
                'validator': 'length_gt',
                'expect': min_length
            })
            self.rules.append({
                'field': path,
                'validator': 'length_lt',
                'expect': max_length
            })
        return self
    
    # 特殊校验
    def is_email(self, path):
        """邮箱格式校验"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': email_pattern
        })
        return self
    
    def is_phone(self, path):
        """手机号格式校验（中国大陆）"""
        phone_pattern = r'^1[3-9]\d{9}$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': phone_pattern
        })
        return self
    
    def is_url(self, path):
        """URL格式校验"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': url_pattern
        })
        return self
    
    def is_positive(self, path):
        """正数校验"""
        return self.greater_than(path, 0)
    
    def is_negative(self, path):
        """负数校验"""
        return self.less_than(path, 0)
    
    def is_non_negative(self, path):
        """非负数校验"""
        return self.greater_equal(path, 0)
    
    # 批量操作
    def all_fields_not_empty(self, *paths):
        """批量非空校验（别名）"""
        return self.not_empty(*paths)
    
    def all_fields_positive(self, *paths):
        """批量正数校验"""
        for path in paths:
            self.is_positive(path)
        return self
    
    def all_fields_type(self, field_type, *paths):
        """批量类型校验"""
        for path in paths:
            self.is_type(path, field_type)
        return self

    # 条件校验
    def when(self, condition, *then):
        """
        严格条件校验 - 所有匹配项都满足条件时才执行then校验（第一种语义）

        语义说明：
        1. 对所有数据项进行条件校验
        2. 如果所有数据项都满足条件，就执行then规则校验
        3. 如果任一数据项不满足条件，就跳过整个then校验
        4. 每个then规则有独立的统计维度

        与when_each和list_when方法的区别：
        - when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
        - when_each：每个数据项单独进行条件+then检查（逐项条件检查）
        - list_when：when_each的简化版，专门用于列表数据

        :param condition: 条件表达式，支持所有校验器语法
        :param then: then表达式，支持所有校验器语法，可传入多个校验规则
        :return: self（支持链式调用）
        
        示例：
        # 单个then校验 - 当status为active时，price必须大于0
        .when("status == 'active'", "price > 0")
        
        # 多个then校验 - 当type为premium时，features字段不能为空且price必须大于100
        .when("type == 'premium'", "features", "price > 100")
        
        # 批量校验 - 当status为active时，多个字段都必须校验通过
        .when("status == 'active'", 
              "price > 0", 
              "name", 
              "description",
              "category != 'test'")
        
        # 支持通配符 - 当所有产品状态为active时，价格都必须大于0且名称不能为空
        .when("products.*.status == 'active'", 
              "products.*.price > 0", 
              "products.*.name")
        
        # 链式调用示例
        checker(data).when("user.level == 'vip'", 
                          "user.permissions.download == true",
                          "user.permissions.upload == true", 
                          "user.quota > 1000") \
                     .when("user.status == 'active'", 
                          "user.last_login", 
                          "user.email") \
                     .validate()
        
        注意：
        1. 当条件满足时，所有then校验都必须通过才算成功
        2. 当条件不满足时，跳过所有then校验（返回True）
        3. 支持链式调用，可以添加多个条件校验
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建条件校验规则（校验器标识为conditional_check）
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self
    

    def when_each(self, condition, *then):
        """
        逐项条件校验：对指定路径下的每个数据项分别进行条件+then检查（第二种语义）
        
        语义说明：
        1. 通过路径表达式定位要检查的数据项列表
        2. 对每个数据项分别进行条件检查
        3. 对满足条件的数据项执行then规则校验，不满足则跳过
        4. 每个then规则按照满足条件的数据项独立统计失败率
        
        与when和list_when方法的区别：
        - when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
        - when_each：每个数据项单独进行条件+then检查（逐项条件检查）
        - list_when：when_each的简化版，专门用于列表数据
        
        适用场景：
        - 任意数据结构，不限于列表
        - 需要通过复杂路径表达式定位数据项
        - 希望统计满足条件的数据项中then规则的失败率
        - 避免手动提取数据子集

        :param condition: 条件表达式，使用路径表达式，如 "users.*.status == 'active'"
        :param then: then规则，使用路径表达式，如 "users.*.score > 70"，可传入多个校验规则
        :return: self（支持链式调用）
        
        示例：
        # 基础用法 - 直接使用路径表达式
        checker(data).when_each("users.*.status == 'active'", "users.*.score > 70").validate()
        
        # 多个then规则 - 活跃用户必须有名字且分数大于80
        checker(data).when_each("users.*.status == 'active'",
                               "users.*.name", "users.*.score > 80").validate()

        # 深度嵌套场景
        checker(response).when_each("data.regions.*.cities.*.status == 'active'",
                                   "data.regions.*.cities.*.population > 0").validate()

        # 链式调用示例
        checker(data).when_each("users.*.status == 'active'", "users.*.score > 70") \
                     .when_each("orders.*.status == 'paid'", "orders.*.amount > 0") \
                     .validate()

        # 与传统用法的对比：
        # 传统方式（需要预提取）：
        users = data["users"]
        checker(users).list_when("status == 'active'", "score > 70").validate()

        # 新方式（直接路径表达式）：
        checker(data).when_each("users.*.status == 'active'", "users.*.score > 70").validate()

        注意：
        1. 条件和then规则必须使用相同的路径前缀
        2. 路径表达式必须包含通配符*来定位要遍历的数据项
        3. 支持失败阈值设置
        4. 支持链式调用
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建路径条件校验规则（校验器标识为conditional_each_check）
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_each_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self
    
    def list_when(self, condition, *then):
        """
        逐项条件校验：when_each的简化版，专门用于列表数据
        
        :param condition: 条件表达式，支持所有校验器语法
        :param then: then表达式，支持所有校验器语法，可传入多个校验规则
        :return: self（支持链式调用）
        
        与when和when_each方法的区别：
        - when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
        - when_each：每个数据项单独进行条件+then检查（逐项条件检查）
        - list_when：when_each的简化版，专门用于列表数据
        
        适用场景：
        - 当前数据是列表格式
        - 需要对列表中符合条件的数据项进行个别校验
        - 希望统计满足条件的数据项中then规则的失败率
        
        示例：
        # 对用户列表，活跃用户的分数必须大于70
        checker(users).list_when("status == 'active'", "score > 70").validate()
        
        # 多个then规则 - 活跃用户必须有名字且分数大于80
        checker(users).list_when("status == 'active'", "name", "score > 80").validate()
        
        注意：
        1. 当前数据必须是列表格式，否则校验时会抛出异常
        2. 每个数据项单独进行条件+then检查
        3. 支持失败阈值设置
        4. 支持链式调用
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建条件校验规则（校验器标识为conditional_list_check）
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_list_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self

    def validate(self, failure_threshold=None):
        """执行校验
        
        :param failure_threshold: 失败阈值
            - None: 严格模式，一个失败全部失败（默认）
            - int: 每个规则最多允许N个失败
            - float: 每个规则最多允许N%失败率
        :return: True表示所有校验通过，False表示存在校验失败
        :raises: Exception: 当参数错误或数据结构异常时抛出异常
        """
        return check(self.data, *self.rules, failure_threshold=failure_threshold)


def checker(data):
    """创建数据校验器"""
    return DataChecker(data)