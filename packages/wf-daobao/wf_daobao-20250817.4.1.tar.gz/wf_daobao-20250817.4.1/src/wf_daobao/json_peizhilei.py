import json
import os
import sys

class Peizhi():
    def __init__(self, lj='config.json'):
        # self.执行路径=os.path.realpath(sys.argv[0])
        # #self.执行路径 = os.path.abspath(__file__)        
        # #本路径的文件夹名
        # self.根目录 = os.path.dirname(self.执行路径)
        # self.lj=lj
        self.配置路径=lj#os.path.join(self.lj, "________打包附件.json")
        # print("配置路径:",self.配置路径)
        # 创建 ConfigParser 对象      
        if os.path.isfile(self.配置路径)==False:
            self.初始化配置()
    def 初始化配置(self):
        # 添加配置节和选项
        Database = {
        "待打包位置位置":".",
        "主文件名": "main.py",
        "待打包附件位置名称":"________打包附件",
        "待打包附件json配置名称":"________打包附件.json",
        "虚拟环境位置":"D:/xn",
        "虚拟环境文件夹名称": "demo",        
        "py模版字典": {},
        "配置列表": []
        }   
        # 写入文件
        with open(self.配置路径, 'w', encoding='utf-8') as f:
            json.dump(Database,f,ensure_ascii=False,indent=4,sort_keys=True)
        return Database
        
    def 读取配置(self,mrz=[]):
        try:
            if os.path.exists(self.配置路径):
                with open(self.配置路径, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data ==None:
                        data=mrz
            else:
                data=mrz
            return data
        except Exception as e:
            print(f"配置解析错误: {str(e)}")
            return None
            

    def 修改配置(self,data=[]):
        with open(self.配置路径, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data
        
if __name__ == '__main__':
    # 创建配置文件
    peizhi=Peizhi()
    # 读取配置文件
    print(peizhi.读取配置(mrz=[]))
    # 修改配置文件
    peizhi.修改配置(data={"s":"d"})