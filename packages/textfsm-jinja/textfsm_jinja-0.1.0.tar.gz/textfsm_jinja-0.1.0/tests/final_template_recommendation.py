from textfsm_jinja import TextFSMParser
import json

# 推荐的合并模板
recommended_template = """Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value nexthop_port (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop_address}(?: tag ${tag})? -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_port} -> Record"""

# 更加简化的方案（如果不需要区分nexthop类型）
simplified_template = """Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop}(?: tag ${tag})? -> Record"""

# 测试数据
test_data = """ip route-static 1.1.1.1 32 2.2.2.2
ip route-static 1.1.1.1 32 2.2.2.2 tag 300
ip route-static 1.1.1.1 32 null0"""

print("=== 推荐的合并模板 ===")
try:
    parser1 = TextFSMParser(recommended_template)
    result1 = parser1.parse(test_data)
    print(json.dumps(result1, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"推荐模板出错: {e}")

print("\n=== 简化模板 ===")
try:
    parser2 = TextFSMParser(simplified_template)
    result2 = parser2.parse(test_data)
    print(json.dumps(result2, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"简化模板出错: {e}")

print("\n=== 原始多规则模板（对比） ===")
original_template = """Value ip_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value mask (\\d+)
Value nexthop_address (\\d+\\.\\d+\\.\\d+\\.\\d+)
Value nexthop_port (\\S+)
Value tag (\\d+)

Start
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} tag ${tag} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_address} -> Record
  ^ip route-static ${ip_address} ${mask} ${nexthop_port} -> Record"""

try:
    parser3 = TextFSMParser(original_template)
    result3 = parser3.parse(test_data)
    print(json.dumps(result3, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"原始模板出错: {e}")