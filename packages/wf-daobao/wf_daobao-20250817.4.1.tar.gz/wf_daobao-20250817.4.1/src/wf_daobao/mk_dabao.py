# -*- encoding:utf-8 -*-
import os
import shutil
import datetime
import sys
import pyperclip
# if __package__:  
from wf_daobao import json_peizhilei
from wf_daobao import log_rizhi
# else:
# import json_peizhilei
# import log_rizhi
log = log_rizhi.uru_log('uru_log')
#生成安装包 pipreqs .
#pip install -r requirements.txt
#pip install pyinstaller==5.8.0

class DaoBao:
    def __init__(self,lj="."):
        self.lj=lj
        #主文件绝对路径
        self.运行文件绝对路径  = os.path.realpath(sys.argv[0])
        self.根目录 = os.path.dirname(self.运行文件绝对路径)
        self.创建打包附件文件夹(lj=self.lj) 
        #时间
        
    def 判断是否根目录(self,lj="."):
        if os.path.isdir(lj):            
            根目录=lj
        else:
            根目录=self.根目录
        log.info("根目录{}".format(根目录))      
        return 根目录
    def 创建附件目录(self,lj=""):
        self.打包附件路径 = os.path.join(lj,"________打包附件")
        if os.path.isdir(self.打包附件路径)==False:
            os.mkdir(self.打包附件路径)
        self.配置路径=os.path.join(self.打包附件路径, "________打包附件.json")        
        self.peizhi=json_peizhilei.Peizhi(lj=self.配置路径)
        return self.打包附件路径
    def 创建打包附件文件夹(self,lj=""):
        self.根目录s=self.判断是否根目录(lj=lj)
        self.创建附件目录s=self.创建附件目录(lj=self.根目录s)        
        self.peizhi字典=self.peizhi.读取配置(mrz=[])

        self.待打包位置位置=self.peizhi字典.get("待打包位置位置")
        self.主文件名=self.peizhi字典.get("主文件名")
        self.待打包附件位置名称=self.peizhi字典.get("待打包附件位置名称")
        self.待打包附件json配置名称=self.peizhi字典.get("待打包附件json配置名称")

        self.虚拟环境位置=self.peizhi字典.get("虚拟环境位置")
        self.虚拟环境文件夹名称=self.peizhi字典.get("虚拟环境文件夹名称")        
        self.py模版字典=self.peizhi字典.get("py模版字典")
        self.配置列表=self.peizhi字典.get("配置列表")
        self.入口文件绝对路径=os.path.join(self.待打包位置位置,self.主文件名) .replace("\\","/")
        self.日期格式化=str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
      
        




    def tjmk(self,mm):
        """1生成：绝对路径和模块名"""
        #模块绝对名路径
        zhs0=os.path.join(self.待打包位置位置,mm).replace("\\","/")
        # zhs0=os.path.abspath(mm)
        #模块名
        wjm=os.path.basename(zhs0)
        zhs1=wjm.split(".")[0]
        zhs2="-p {0} --hidden-import {1} ".format(zhs0,zhs1)
        return zhs2
    def get_folder_name(self,path):
        """取文件夹名"""
        # 使用 os.path.basename 获取路径的最后一个部分
        # 如果路径以斜杠结尾，则先使用 os.path.dirname 去掉最后的斜杠（如果需要）
        # 不过 os.path.basename 本身对这种情况也是安全的
        folder_name = os.path.basename(os.path.normpath(path))
        return folder_name
    def scml(self,模块文件字典,入口文件绝对路径,配置文件列表):    
        """2.添加模块"""
        #主文件绝对路径
        strs=入口文件绝对路径
        #模块名{}    
        if 模块文件字典!=False: 
            for i in 模块文件字典:
                strs+=" {}".format(self.tjmk(模块文件字典.get(i)))
        #--add-data="data:data"
        if 配置文件列表!=False:
            for j in 配置文件列表:
                peizhi=os.path.join(self.待打包位置位置,j).replace("\\","/") 
                # peizhi=os.path.abspath(j)
                if os.path.isfile(peizhi):
                    j="."
                else:
                    j=self.get_folder_name(j)
                strs+=' --add-data="{};{}"'.format(os.path.abspath(peizhi).replace("\\","/"),j)
        return strs

   
    def 生成打包命令(self,wjm="9.--------打包代码--------.txt",shu="4"):
        """3.文件名，时间，模块文件名，主文件名"""
                # ,self.py模版字典,self.配置列表,self.日期格式化,dblj=self.创建附件目录s,wjm="9.--------打包代码--------.txt") 
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        tt=open(xnlj,"w")
        tt.write("-------打包时间：{}-------\npip install pyinstaller==5.13.0\n".format(self.日期格式化))
        入口文件绝对路径=os.path.join(self.待打包位置位置,self.主文件名).replace("\\","/")
        tt.write("-----------------------\n1.单文件，无黑框\n")
        单文件无黑框=r"pyinstaller -F -w {}".format(self.scml(self.py模版字典,入口文件绝对路径,self.配置列表))
        tt.write(单文件无黑框)

        tt.write("\n\n2.单文件，有黑框\n")
        单文件有黑框=r"pyinstaller -F {}".format(self.scml(self.py模版字典,入口文件绝对路径,self.配置列表))
        tt.write(单文件有黑框)

        tt.write("\n\n3.多文件，无黑框\n")
        多文件无黑框=r"pyinstaller -w {}".format(self.scml(self.py模版字典,入口文件绝对路径,self.配置列表))
        tt.write(多文件无黑框)

        tt.write("\n\n4.多文件，有黑框\n")
        多文件带有黑框=r"pyinstaller {}".format(self.scml(self.py模版字典,入口文件绝对路径,self.配置列表))
        tt.write(多文件带有黑框)

        tt.close()
        
        jg=""
        if shu=="1":
            jg=单文件无黑框
        elif shu=="2":
            jg=单文件有黑框
        elif shu=="3":
            jg=多文件无黑框
        elif shu=="4":
            jg=多文件带有黑框
        log.info(wjm,"完成")
        return jg
        




    # def yinhangpeizhifuzhi(self,yuanwenjian,mubiaowenjian):
    #     """复制：源文件，目标文件"""
    #     ywj1=os.path.abspath(yuanwenjian)
    #     mbwj1=mubiaowenjian
    #     shutil.copy(ywj1,mbwj1)
    #     log.info("-------\n源路径：{}\n复制到目录路径：{}-------".format(ywj1,mbwj1))


    def 创建虚拟环境(self,wjm="2.创建虚拟环境.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr="""
    cd /d {1}
    python -m venv {0}
    cd {1}/{0}
    echo cmd /k "{1}/{0}/Scripts/activate.bat" > new_script.bat
    cmd /k "{1}/{0}/Scripts/activate.bat"
    """.format(self.虚拟环境文件夹名称,self.虚拟环境位置)
        # 附件位置=os.path.join(self.待打包位置位置,self.待打包附件位置名称)
        xnlj=os.path.join(self.待打包位置位置+"/"+self.待打包附件位置名称,wjm)
        if os.path.isfile(xnlj)==False:
            xnlj=os.path.join(self.lj,self.待打包附件位置名称,wjm)

        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")
    def 启动虚拟环境(self,wjm="3.启动虚拟环境.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr='cmd /k "cd /d {1}/{0} && {1}/{0}/Scripts/activate.bat"'.format(self.虚拟环境文件夹名称,self.虚拟环境位置)
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")
    def 打开文件夹(self,wjm="4.打开文件夹.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        xnstr='start {1}/{0}'.format(self.虚拟环境文件夹名称,self.虚拟环境位置)
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")

    def 导出包(self,wjm="7.2安装后导出模块名.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        #f_path2:附件文件夹，xnhj：虚拟环境路径
        附件位置=os.path.join(self.待打包位置位置,self.待打包附件位置名称)
        xnstr='cmd /k "cd /d {0} && {2}/{1}/Scripts/activate.bat && pip freeze > requirements.txt"'.format(附件位置,self.虚拟环境文件夹名称,self.虚拟环境位置)
        xnlj=os.path.join(附件位置,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")
        # self.导出包(self.虚拟环境文件夹名称,self.创建附件目录s,wjm="7.2安装后导出模块名.bat")
    def 虚拟环境执行py(self,wjm="11.虚拟环境执行py.bat"):       
        """虚拟环境执行py:return 返回附件目录路径"""
        # 附件位置=os.path.join(self.待打包位置位置,self.待打包附件位置名称)
        strs2='cmd /k "cd /d {} && call {}/{}/Scripts/activate.bat &&  python {}"'.format(self.待打包位置位置,self.虚拟环境位置,self.虚拟环境文件夹名称,self.主文件名)
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        with open(xnlj,"w",encoding="gbk") as xwj:
            xwj.write(strs2)   
        log.info(wjm,"完成")  
        return xnlj


       
    
    def 批量安装包(self,wjm="8.批量安装包.bat"):
        """导出包:xnhj：虚拟环境路径,dblj:附件文件夹,wjm:文件名"""
        附件位置=os.path.join(self.待打包位置位置,self.待打包附件位置名称)
        xnstr='cmd /k "cd /d {0} && {2}/{1}/Scripts/activate.bat && pip install -r requirements.txt"'.format(附件位置,self.虚拟环境文件夹名称,self.虚拟环境位置)
        xnlj=os.path.join(附件位置,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")

    #递归导出包名
    def diguibianli(self,lj):
        for root, dirs, files in os.walk(lj):
            for file in files:
                wj=os.path.join(root,file)
                if wj.endswith(".py") :               
                    if os.path.isfile(wj):
                        log.info(wj)
    #log.info(os.listdir(lj))
    #导出包名
    # def bianli(self,lj,dblj,wjm="2.导出包名.txt"):
    # #主文件绝对路径
    #     运行文件绝对路径  = os.path.realpath(sys.argv[0])
    #     log.info("运行文件绝对路径:",运行文件绝对路径)
    #     运行文件上一级路径 = os.path.dirname(运行文件绝对路径)
    #     strs1=""
    #     strs2="pip install pyinstaller==5.8.0\n"
    #     for i in os.listdir(lj):
    #         ljs = os.path.join(运行文件上一级路径,i)
    #         if ljs.endswith(".py") and ljs.endswith("00_打包附件.py")==False:               
    #             if os.path.isfile(ljs) :
    #                 with open(ljs,"r",encoding="utf-8") as wj:
    #                     s=0
    #                     for j in wj:
    #                         s+=1
    #                         if j.find("import") != -1 and j[0].find("#") ==-1:   
    #                             if strs1.find(j.strip()) ==-1:
    #                                 strs1+=j  
    #                                 strs2+=j.replace("import", "pip install") 
    #     xnlj=os.path.join(dblj,wjm)           
    #     with open(xnlj,"w",encoding="utf-8") as xwj:
    #         xwj.write(strs2)                        
    #     return strs2
    def bianli2(self,wjm="7.1安装前导出模块名pipreqs.bat"):
        # file_path  = os.path.realpath(sys.argv[0])
        # f_path1 = os.path.dirname(file_path)
        strs2='cmd /k "cd /d {} &&  pipreqs .'.format(self.待打包位置位置)
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        with open(xnlj,"w",encoding="gbk") as xwj:
            xwj.write(strs2)   
        log.info(wjm,"完成")                   
        return strs2
    def 打包工具安装(self,wjm="6.安装打包工具_pyinstaller_5.8.bat"):
        xnstr='cmd /k "cd /d {1}/{0} && {1}/{0}/Scripts/activate.bat && pip install pyinstaller==5.8.0"'.format(self.虚拟环境文件夹名称,self.虚拟环境位置)
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")
    def pandas安装(self,wjm="5.安装pandas_openpyxl_xlrd.bat"):
        xnstr='cmd /k "cd /d {1}/{0} && {1}/{0}/Scripts/activate.bat && pip install pandas==2.2.3 && pip install openpyxl==3.1.2 && pip install xlrd==2.0.1"'.format(self.虚拟环境文件夹名称,self.虚拟环境位置)
        xnlj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        with open(xnlj,mode="w",encoding="gbk") as pp:
            pp.write(xnstr)
        log.info(wjm,"完成")
    def 加密模块(self,wjm="10.加密模块.bat"):       
        lj=os.path.join(self.待打包位置位置,self.待打包附件位置名称,wjm)
        wz="""
@echo off
chcp 65001 > nul
REM 切换到上级目录
cd /d ..
echo 当前目录已切换至：%cd%
REM 遍历并加密所有.py文件
for %%f in (*.py) do (
    echo 正在加密文件：%%f
    pyarmor g "%%f"
)
echo 所有.py文件加密完成
pause
"""
        with open(lj,"w",encoding="utf-8") as pp:
            pp.write(wz)
        
    def 生成打包附件(self):
        self.创建打包附件文件夹(lj=r"{}".format(self.lj))        
        #复制config.xls
        #self.yinhangpeizhifuzhi("config.xls",r"D:\xn\yin_hang\dist\config.xls")
        #self.yinhangpeizhifuzhi("config.xls",r"D:\xn\yin_hang_win7.38\dist\config.xls")
        #生成pyinstaller        
        self.创建虚拟环境(wjm="2.创建虚拟环境.bat")
        self.启动虚拟环境(wjm="3.启动虚拟环境.bat")
        self.打开文件夹(wjm="4.打开文件夹.bat")        
        self.pandas安装(wjm="5.安装pandas_openpyxl_xlrd.bat")
        self.打包工具安装(wjm="6.安装打包工具_pyinstaller_5.8.bat")
        self.bianli2(wjm="7.1安装前导出模块名pipreqs.bat")
        self.导出包(wjm="7.2安装后导出模块名.bat")
        self.批量安装包(wjm="8.批量安装包.bat")
        # self.bianli(运行文件上一级路径,打包附件路径,wjm="2.1.导出包名.txt")
        self.生成打包命令(wjm="9.--------打包代码--------.txt",shu="4")        
        self.加密模块(wjm="10.加密模块.bat")
        self.虚拟环境执行py(wjm="11.虚拟环境执行py.bat")
        log.info("完成！")
    def 修改json文件(self,待打包位置位置="",主文件名="",虚拟环境路径="",虚拟环境文件夹名称="",生成py模版字典={},生成配置列表=[],打包附件位置名称="________打包附件",打包附件json配置名称="________打包附件.json"):  
        打包文件内容={
            "待打包位置位置":待打包位置位置,
            "主文件名":主文件名,
            "待打包附件位置名称":打包附件位置名称,
            "待打包附件json配置名称":打包附件json配置名称,
            "虚拟环境位置":虚拟环境路径,
            "虚拟环境文件夹名称":虚拟环境文件夹名称,           
            "py模版字典":生成py模版字典,
            "配置列表":生成配置列表
        } 
        self.peizhi.修改配置(打包文件内容)        
        return 打包文件内容
       
def xuanze(jg="",daobao=None,字典=None): 
    mc=字典.get(jg,"输入错误")
    if jg=="1":
        daobao.生成打包附件()
        log.info("生成打包附件，完成！") 
    elif jg=="7.3":
        shutil.copy(os.path.join(daobao.lj, "requirements.txt"), os.path.join(daobao.待打包位置位置,daobao.待打包附件位置名称, "requirements.txt"))
        log.info("requirements.txt复制到附件文件夹，完成！") 
    elif jg=="9.1":
        pyperclip.copy(daobao.生成打包命令(wjm="9.--------打包代码--------.txt",shu="1"))   
        log.info("单文件无黑框，打包代码，复制完成！") 
    elif jg=="9.2":
        pyperclip.copy(daobao.生成打包命令(wjm="9.--------打包代码--------.txt",shu="2"))   
        log.info("单文件有黑框，打包代码，复制完成！") 
    elif jg=="9.3":
        pyperclip.copy(daobao.生成打包命令(wjm="9.--------打包代码--------.txt",shu="3"))   
        log.info("多文件无黑框，打包代码，复制完成！") 
    elif jg=="9.4":
        pyperclip.copy(daobao.生成打包命令(wjm="9.--------打包代码--------.txt",shu="4"))   
        log.info("多文件有黑框，打包代码，复制完成！") 
    elif jg=="10":
        batlj=os.path.join(daobao.待打包位置位置,daobao.待打包附件位置名称)
        os.chdir(batlj)
        log.info("加密位置",os.getcwd())
        batljs=os.path.join(batlj,mc)
        if os.path.isfile(batljs):
            os.startfile(batljs)
        log.info("代码，加密完成！") 
    elif jg=="0":
        exit()
    else:        
        if mc != "输入错误":
            batlj=os.path.join(daobao.待打包位置位置+"/"+daobao.待打包附件位置名称,mc)
            log.info(batlj)
            if os.path.isfile(batlj):
                os.startfile(batlj)
def main(lj="",s=""):     
    zfc="""=================================
    请输入:【首次请选1】
    【1.生成打包附件】
    【2.创建虚拟环境.bat】
    【3.启动虚拟环境.bat】
    【4.打开文件夹.bat】
    【5.安装pandas_openpyxl_xlrd.bat】
    【6.安装打包工具_pyinstaller_5.8.bat】
    【7.1安装前导出模块名pipreqs.bat】
    【7.2安装后导出模块名.bat】
    【7.3把requirements.txt复制到打包附件文件夹中】
    【8.批量安装包.bat】
    【9.1复制代码：单文件无黑框】   
    【9.2复制代码：单文件有黑框】 
    【9.3复制代码：多文件无黑框】 
    【9.4复制代码：多文件带有黑框】  
    【10.加密模块.bat】 
    【11.虚拟环境执行py.bat】
    【0.退出】\n>>"""
    字典 = {
        "1": "生成打包附件",
        "2": "2.创建虚拟环境.bat",
        "3": "3.启动虚拟环境.bat",
        "4": "4.打开文件夹.bat",
        "5": "5.安装pandas_openpyxl_xlrd.bat",
        "6": "6.安装打包工具_pyinstaller_5.8.bat",
        "7.1": "7.1安装前导出模块名pipreqs.bat",
        "7.2": "7.2安装后导出模块名.bat",
        "7.3": "7.3把requirements.txt复制到打包附件文件夹中",
        "8": "8.批量安装包.bat",
        "9.1": "9.复制代码：单文件无黑框",
        "9.2": "9.复制代码：单文件有黑框",
        "9.3": "9.复制代码：多文件无黑框",
        "9.4": "9.复制代码：多文件有黑框",
        "10": "10.加密模块.bat",
        "11": "11.虚拟环境执行py.bat",
        "0": "退出"

    }
    if lj=="":
        路径=input("请录入路径:>>") 
        if 路径=="":
            运行文件绝对路径  = os.path.realpath(sys.argv[0])
            根目录 = os.path.dirname(运行文件绝对路径).replace("\\","/")
            路径=根目录
            daobao=DaoBao(路径)
    else:
        路径=lj
        if os.path.isdir(路径):
            daobao=DaoBao(r"{}".format(路径.replace("\\","/")))
        else:
            log.info("路径错误")
            exit()
    log.info(r"待打包位置位置:{}".format(路径.replace("\\","/")))
    
    if s=="":
        while True:
            jg=input(zfc)
            xuanze(jg,daobao,字典) 
    else:
        jg=s
        xuanze(jg,daobao,字典) 
    
        

                

        
if "__main__"==__name__: 
    main()  
    
    
   
