from textfsm_jinja import TextFSMParser
import json

# 原始模板（多个规则）
original_template = """Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value nexthop_port (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} tag ${tag} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_port} -> Record"""

# 改进的合并模板
improved_template = """Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value nexthop_port (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop_address}(?: tag ${tag})? -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_port} -> Record"""

# 更进一步的尝试 - 使用更明确的分组
advanced_template = """Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop}(?: tag ${tag})? -> Record"""

# 测试数据
test_data = """ip route-static 1.1.1.1 32 2.2.2.2
ip route-static 1.1.1.1 32 2.2.2.2 tag 300
ip route-static 1.1.1.1 32 null0"""

print("=== 原始模板（多个规则） ===")
try:
    parser1 = TextFSMParser(original_template)
    result1 = parser1.parse(test_data)
    print(json.dumps(result1, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"原始模板出错: {e}")

print("\n=== 改进的合并模板 ===")
try:
    parser2 = TextFSMParser(improved_template)
    result2 = parser2.parse(test_data)
    print(json.dumps(result2, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"改进模板出错: {e}")

print("\n=== 高级模板（简化变量） ===")
try:
    parser3 = TextFSMParser(advanced_template)
    result3 = parser3.parse(test_data)
    print(json.dumps(result3, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"高级模板出错: {e}")