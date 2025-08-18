import json
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
import windnd

# if __package__:  

from wf_daobao import ui_treeview
from wf_daobao import mk_dabao
# else:

# import ui_treeview
# import mk_dabao
# import log_rizhi
# log = log_rizhi.uru_log('uru_log')
class DataProcessor:
    def __init__(self, master):
        self.master = master
        self.执行路径=os.path.realpath(sys.argv[0])
        #self.执行路径 = os.path.abspath(__file__)        
        #本路径的文件夹名
        self.根目录 = os.path.dirname(self.执行路径)        
        self.UI界面()
        self.读取json配置文件()
        self.配置文件写入UI()
        
    def UI界面(self):        
        self.主py文件 = ttk.LabelFrame(self.master, text="入口文件名", labelanchor="n")
        self.主py文件.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
        self.主py文件表格= ui_treeview.App(self.主py文件,["py主文件名"],[],jbkj=False,fy="不分页",pdshu=False)        
        #拖拽文件
        windnd.hook_dropfiles(self.主py文件, func=self.主py文件表格导入) # 拖拽文件

        self.主py模块文件 = ttk.LabelFrame(self.master, text="py模块文件名", labelanchor="n")
        self.主py模块文件.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
        self.主py模块文件表格= ui_treeview.App(self.主py模块文件,["py模块文件名"],[],jbkj=False,fy="不分页",pdshu=False)
        
        #拖拽文件
        windnd.hook_dropfiles(self.主py模块文件, func=self.主py模块表格导入) # 拖拽文件

        self.主py配置文件 = ttk.LabelFrame(self.master, text="配置文件名", labelanchor="n")
        self.主py配置文件.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
        self.主py配置文件表格= ui_treeview.App(self.主py配置文件,["py配置文件名"],[],jbkj=False,fy="不分页",pdshu=False)
        
        #拖拽文件
        windnd.hook_dropfiles(self.主py配置文件, func=self.主py配置表格导入) # 拖拽文件

        self.按钮容器 = ttk.Frame(self.master)
        self.按钮容器.pack(side=tk.LEFT, fill=tk.BOTH)
        self.按钮容器0= ttk.Frame(self.按钮容器)
        self.按钮容器0.pack(side=tk.TOP,fill=tk.BOTH)
        ttk.Label(self.按钮容器0, text="待打包的位置：").pack(side=tk.LEFT)
        self.待打包位置变量=tk.StringVar()
        self.待打包输入框0=ttk.Entry(self.按钮容器0,textvariable=self.待打包位置变量)
        self.待打包输入框0.pack(side=tk.LEFT, fill=tk.X)
        
        ttk.Button(self.按钮容器0, text="导入", command=lambda:self.path_ui(pd="3")).pack(side=tk.LEFT)
        #拖拽文件
        windnd.hook_dropfiles(self.按钮容器0, func=self.path_ui) 
        ttk.Button(self.按钮容器0, text="读取", command=lambda:self.读取json配置文件()).pack(side=tk.LEFT)
        ttk.Button(self.按钮容器0, text="清空", command=lambda:self.清空所有()).pack(side=tk.LEFT)
        ttk.Button(self.按钮容器0, text="打开当前文件夹", command=lambda:os.startfile(self.判断是否根目录())).pack(side=tk.LEFT)


        
        self.按钮容器1= ttk.Frame(self.按钮容器)
        self.按钮容器1.pack(side=tk.TOP,fill=tk.BOTH)
        ttk.Label(self.按钮容器1, text="虚拟环境位置：").pack(side=tk.LEFT)
        self.虚拟环境变量=tk.StringVar()
        self.输入框0=ttk.Entry(self.按钮容器1,textvariable=self.虚拟环境变量)
        self.输入框0.pack(side=tk.LEFT, fill=tk.X)
        
        ttk.Label(self.按钮容器1, text="虚拟环境文件夹名称：").pack(side=tk.LEFT)
        self.文件夹名称=tk.StringVar()
        self.输入框=ttk.Entry(self.按钮容器1,textvariable=self.文件夹名称)
        self.输入框.pack(side=tk.LEFT, fill=tk.X)
        ttk.Button(self.按钮容器1, text="打开json配置文件", command=lambda:self.打开json附件()).pack(side=tk.LEFT, fill=tk.X)
            
        
        self.按钮3 = ttk.Button(self.按钮容器, text="生成并保存【json配置文件】", command=lambda:self.修改后json())
        self.按钮3.pack(side=tk.TOP, fill=tk.X)
        # 统计信息框
        self.输入文件框 = scrolledtext.ScrolledText( self.按钮容器,wrap=tk.WORD,width=80,height=16)
        self.输入文件框.pack(side=tk.TOP, fill=tk.X)
        # self.按钮容器2= ttk.Frame(self.按钮容器)
        self.按钮容器2 = ttk.LabelFrame(self.按钮容器, text="功能按钮", labelanchor="n")
        self.按钮容器2.pack(side=tk.TOP,fill=tk.BOTH)
        # ttk.Button(self.按钮容器2, text="清空", command=lambda:self.插入字符串("")).grid(row=0,column=0)
       
        ttk.Button(self.按钮容器2, text="1.生成打包附件", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"1")).grid(row=0,column=2,sticky=tk.W,columnspan=1)
        ttk.Button(self.按钮容器2, text="2.创建虚拟环境", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"2")).grid(row=0,column=3,sticky=tk.W,columnspan=1)
        ttk.Button(self.按钮容器2, text="3.启动虚拟环境", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"3")).grid(row=0,column=4,sticky=tk.W,columnspan=1)
        ttk.Button(self.按钮容器2, text="4.打开虚拟环境文件夹", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"4")).grid(row=0,column=5,sticky=tk.W,columnspan=1)
        ttk.Button(self.按钮容器2, text="5.安装pandas_openpyxl_xlrd", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"5")).grid(row=1,column=1,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="6.安装打包工具_pyinstaller_5.8", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"6")).grid(row=2,column=1,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="7.1安装前导出模块名pipreqs", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"7.1")).grid(row=3,column=1,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="7.2安装后导出模块名", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"7.2")).grid(row=4,column=1,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="7.3把requirements.txt复制到打包附件文件夹中", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"7.3")).grid(row=5,column=1,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="8.批量安装包", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"8")).grid(row=6,column=1,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="9.1复制代码：单文件无黑框", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"9.1")).grid(row=1,column=5,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="9.2复制代码：单文件有黑框", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"9.2")).grid(row=2,column=5,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="9.3复制代码：多文件无黑框", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"9.3")).grid(row=3,column=5,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="9.4复制代码：多文件有黑框", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"9.4")).grid(row=4,column=5,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="10.加密模块.bat", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"10")).grid(row=5,column=5,sticky=tk.W,columnspan=3)
        ttk.Button(self.按钮容器2, text="11.虚拟环境执行py.bat", command=lambda:mk_dabao.main(self.待打包位置变量.get(),"11")).grid(row=6,column=5,sticky=tk.W,columnspan=3)
    
 
    

    def 清空所有(self):
        # self.待打包位置变量.set("")
        # self.虚拟环境变量.set("")
        # self.文件夹名称.set("")
        # self.主文件名=""
        self.主py文件表格.bghs_删除(dx=False)
        self.主py模块文件表格.bghs_删除(dx=False)
        self.主py配置文件表格.bghs_删除(dx=False)

    def 判断是否根目录(self):
        if os.path.isdir(self.待打包位置变量.get()):            
            根目录=self.待打包位置变量.get()
        else:
            根目录=self.根目录
        return 根目录
    def 打开json附件(self,fjwjj="________打包附件",fjjson="________打包附件.json"):
        os.startfile(os.path.join(self.判断是否根目录(),fjwjj,fjjson))
        
    def 读取json配置文件(self):
        self.导包模块=mk_dabao.DaoBao(self.判断是否根目录())    
        self.导包模块.创建打包附件文件夹(self.判断是否根目录())
        self.配置文件写入UI()
        
    def 配置文件写入UI(self): 
        self.待打包位置变量.set(self.导包模块.待打包位置位置)      
        self.主py文件表格.bghs_插入(lbnr=[self.导包模块.主文件名],zj=False)
        self.文件夹名称.set(self.导包模块.虚拟环境文件夹名称)
        self.虚拟环境变量.set("{}".format(self.导包模块.虚拟环境位置))
        if self.导包模块.py模版字典:
            p1=[v for k,v in self.导包模块.py模版字典.items()]
            self.主py模块文件表格.bghs_插入(lbnr=p1,zj=False)
        if self.导包模块.配置列表:
            p1=[v for v in self.导包模块.配置列表]
            self.主py配置文件表格.bghs_插入(lbnr=p1,zj=False)
  
     
    def path_ui(self,files=None,pd="1"): 
        """1.2打开文件路径或拖拽"""
        # log.info(pd)
        if pd=="1":
            p1='\n'.join((item.decode('gbk') for item in files))#获得选择好的文件
            if os.path.isfile(p1):
                self.待打包位置变量.set(p1)
            else:
                self.待打包位置变量.set(p1)
        elif pd=="2":
            p1=tk.filedialog.askopenfilename()#获得选择好的文件
            self.待打包位置变量.set(p1)
        elif pd=="3":
            p1=tk.filedialog.askdirectory()#获得选择好的文件夹
            self.待打包位置变量.set(p1)
    
        
    def 插入字符串(self, texts):
        self.输入文件框.delete(1.0, tk.END)
        self.输入文件框.insert(tk.END, str(texts))
    # 生成py模版字典
    def 生成py模版字典(self):
        # 调用主py模块文件表格的bghs_查询方法，获取查询结果
        zunzd=self.主py模块文件表格.bghs_查询()
        # 创建一个空字典
        zhidian={}
        # 遍历查询结果
        for k,v in enumerate(zunzd):
            # 将查询结果中的py模块文件名添加到字典中，键为索引，值为py模块文件名
            zhidian[str(k)]=v['py模块文件名']
        # 打印字典
        # log.info(zhidian)
        # 返回字典
        return zhidian
    def 生成配置列表(self):
        zunzd=self.主py配置文件表格.bghs_查询()
        liebiao=[]
        for k,v in enumerate(zunzd):
            liebiao.append(v['py配置文件名'])
        # log.info(liebiao)
        return liebiao
    def 修改后json(self):
        self.导包模块.创建打包附件文件夹(self.判断是否根目录())
        待打包位置位置=self.待打包位置变量.get().replace("\\", "/")
        zunzd=self.主py文件表格.bghs_查询()
        if zunzd:
            主文件名=zunzd[0]['py主文件名']
        else:
            主文件名="main.py"
        虚拟环境路径=self.虚拟环境变量.get().replace("\\", "/")
        虚拟环境文件夹名称=self.文件夹名称.get()
        生成py模版字典=self.生成py模版字典()
        生成配置列表=self.生成配置列表()
        修改json=self.导包模块.修改json文件(待打包位置位置=待打包位置位置,主文件名=主文件名,虚拟环境路径=虚拟环境路径,虚拟环境文件夹名称=虚拟环境文件夹名称,生成py模版字典=生成py模版字典,生成配置列表=生成配置列表)
        修改jsons=json.dumps(修改json, ensure_ascii=False, indent=4)
        self.插入字符串(修改jsons)    
        return 修改jsons
    def 主py文件表格导入(self,files=None,pdwj="1"): 
        """1.2打开文件路径或拖拽"""
        # log.info(pdwj)
        if pdwj=="1":
            p1=[os.path.basename(item.decode('gbk')) for item in files]#获得选择好的文件            
            self.主py文件表格.bghs_插入(lbnr=p1,zj=True)
        elif pdwj=="2":
            p1=tk.filedialog.askopenfilename()#获得选择好的文件            
        # log.info(p1)
    
    def 主py模块表格导入(self,files=None,pdwj="1"): 
        """1.2打开文件路径或拖拽"""
        # log.info(pdwj)
        if pdwj=="1":
            p1=[os.path.basename(item.decode('gbk')) for item in files]#获得选择好的文件            
            self.主py模块文件表格.bghs_插入(lbnr=p1,zj=True)
        elif pdwj=="2":
            p1=tk.filedialog.askopenfilename()#获得选择好的文件            
        # log.info(p1)
    def 主py配置表格导入(self,files=None,pdwj="1"): 
        """1.2打开文件路径或拖拽"""
        # log.info(pdwj)
        if pdwj=="1":
            p1=[os.path.basename(item.decode('gbk')) for item in files]#获得选择好的文件            
            self.主py配置文件表格.bghs_插入(lbnr=p1,zj=True)
        elif pdwj=="2":
            p1=tk.filedialog.askopenfilename()#获得选择好的文件            
        # log.info(p1)
    def main(self):
        root = tk.Tk()
        app = DataProcessor(root)
        root.title("生成打包文件")
        root.geometry("1300x600")
        root.mainloop()
        return app
       
def main():
    root = tk.Tk()
    app = DataProcessor(root)
    root.title("生成打包文件")
    root.geometry("1300x600")
    root.mainloop()
    return app
       

if __name__ == "__main__":
    main()