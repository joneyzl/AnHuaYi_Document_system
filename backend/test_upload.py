import requests
import os

# 模拟上传测试
def test_upload():
    # 确保测试文件存在
    test_file_path = 'test_upload.txt'
    with open(test_file_path, 'w') as f:
        f.write('这是一个测试文件内容')
    
    # 上传请求URL
    url = 'http://192.168.1.95:5000/api/documents/'
    
    # 准备表单数据
    files = {'file': open(test_file_path, 'rb')}
    data = {
        'title': '测试文档',
        'description': '这是一个测试文档',
        'category_id': '1',
        'is_private': 'false'
    }
    
    # 添加JWT Token (假设使用默认的测试token)
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczMzQ1NTgzMCwianRpIjoiYWE5NTY4YzctMmI5Ni00NDk4LTg1MTktMzMxNDY2MmUyYzUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MSwidXNlcm5hbWUiOiJhZG1pbiJ9LCJuYmYiOjE3MzM0NTU4MzAsImV4cCI6MTczMzU0MjIzMH0.your-test-signature'
    }
    
    print('开始上传测试...')
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        print(f'响应状态码: {response.status_code}')
        print(f'响应内容: {response.json()}')
    except Exception as e:
        print(f'请求错误: {str(e)}')
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == '__main__':
    test_upload()