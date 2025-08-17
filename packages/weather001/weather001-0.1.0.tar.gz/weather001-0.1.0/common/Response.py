class ReturnCode:
    """返回码常量类"""
    SUCCESS = 0  # 成功
    FAIL = 1  # 一般失败
    PARAM_ERROR = 1001  # 参数错误
    NOT_FOUND = 1002  # 资源未找到
    UNAUTHORIZED = 1003  # 未授权
    FORBIDDEN = 1004  # 禁止访问
    SERVER_ERROR = 1005  # 服务器内部错误
    TIMEOUT = 1006  # 超时


class Response:
    """统一响应结果类"""

    def __init__(self, code=ReturnCode.SUCCESS, message="", data=None):
        self.code = code
        self.message = message
        self.data = data if data is not None else {}

    def to_dict(self):
        """将对象转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }

    def to_json(self):
        """将对象转换为JSON字符串"""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, dict_data):
        """从字典创建Response对象"""
        return cls(
            code=dict_data.get("code", ReturnCode.SUCCESS),
            message=dict_data.get("message", ""),
            data=dict_data.get("data")
        )

    @property
    def is_success(self):
        """判断是否成功"""
        return self.code == ReturnCode.SUCCESS

    def __str__(self):
        return f"Response(code={self.code}, message='{self.message}', data={self.data})"

    def __repr__(self):
        return self.__str__()


# 便捷方法：创建成功响应
def success(data=None, message="success"):
    return Response(code=ReturnCode.SUCCESS, message=message, data=data)


# 便捷方法：创建失败响应
def fail(message="fail", code=ReturnCode.FAIL, data=None):
    return Response(code=code, message=message, data=data)


# # 使用示例
# # 成功响应
# success_response = success(data={"id": 1, "name": "test"})
# print(success_response.to_dict())
# # 输出: {'code': 0, 'message': 'success', 'data': {'id': 1, 'name': 'test'}}
#
# # 失败响应
# fail_response = fail(message="参数错误", code=ReturnCode.PARAM_ERROR)
# print(fail_response.to_dict())
# # 输出: {'code': 1001, 'message': '参数错误', 'data': {}}
#
# # 检查是否成功
# print(success_response.is_success)  # 输出: True
# print(fail_response.is_success)  # 输出: False
#
# # 使用常量
# error_response = Response(code=ReturnCode.NOT_FOUND, message="资源未找到")
# print(error_response.to_dict())
# # 输出: {'code': 1002, 'message': '资源未找到', 'data': {}}
