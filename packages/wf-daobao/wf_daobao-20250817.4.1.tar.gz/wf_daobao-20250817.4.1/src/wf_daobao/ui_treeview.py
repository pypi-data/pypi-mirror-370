# -*- encoding:utf-8 -*-

# import tkinter
import sys
from tkinter import ttk # 导入内部包
import tkinter as tk
from tkinter import filedialog
import datetime
import pandas as pd
import windnd  #拖拽
import os
import pyperclip
# import mk_DocToPdf
"""v2.0增加复制与粘贴，ttk按钮美化，分页插入-20250328"""
BBH="2.0"  
class App(tk.Frame):
    def __init__(self, parent, bg_bt=None,bg_nr=None,jbkj=False,fy=False,pdshu=True,*args, **kwargs):
        """parent父控件，bg_bt表格标题，bg_nr表格内容,jbkj控件隐藏，fy分页,pdshu判断是否是树"""
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.file_path  = os.path.realpath(sys.argv[0])
        #print(file_path)
        #路径转文件夹
        self.f_path2 = os.path.dirname(self.file_path )
        #标题，内容
        self.bg_bt=bg_bt or ["初始化"]
        self.bg_nr =bg_nr#[[]]  
        self.frame0 = ttk.LabelFrame(parent, text="控件1", labelanchor="n")
        self.frame0.pack(fill=tk.X,padx='5px')
        self.frame1 = ttk.LabelFrame(parent, text="控件2", labelanchor="n")
        self.frame1.pack(fill=tk.X,padx='5px') 
        #控件框架
        self.frame3 = ttk.LabelFrame(parent, text="按钮", labelanchor="n")
        self.frame3.pack(fill=tk.X,padx='5px')
        #控件框架
        self.frame2 = ttk.Frame(parent)#, text="表格列表", labelanchor="n"
        self.frame2.pack(fill=tk.BOTH,padx='5px',expand=True)
        #拖拽文件
        windnd.hook_dropfiles(self.frame0, func=self.path_uis)

        #表格控件
        #滚动条1------------- 
        self.scorllbary = ttk.Scrollbar(self.frame2)
        self.scorllbarx = ttk.Scrollbar(self.frame2, orient=tk.HORIZONTAL)
        self.scorllbary.pack(side=tk.RIGHT, fill=tk.Y)
        self.scorllbarx.pack(side=tk.BOTTOM, fill=tk.X)
        #滚动条2------------- 
        if pdshu==True:
            self.tree = ttk.Treeview(self.frame2,columns=self.bg_bt,show='tree headings',displaycolumns="#all",style='Treeview',yscrollcommand=self.scorllbary.set,xscrollcommand=self.scorllbarx.set)
            self.tree.heading("#0", text="标题",anchor="w")
            for i in range(len(self.bg_bt)):
                self.tree.heading(self.bg_bt[i],text=self.bg_bt[i])
                #stretch=False#不动自伸缩
                self.tree.column(self.bg_bt[i],width=160,anchor='center' ,stretch=True)#
            self.fill_tree(r"{}".format(self.f_path2)) 
        else: 
            self.tree = ttk.Treeview(self.frame2,columns=self.bg_bt,show='headings',style='Treeview',yscrollcommand=self.scorllbary.set,xscrollcommand=self.scorllbarx.set,height=20)    
            for i in range(len(self.bg_bt)):
                self.tree.column(self.bg_bt[i],width=160,anchor='center' ,stretch=False)
                self.tree.heading(self.bg_bt[i],text=self.bg_bt[i])
                #tree.heading('1',text='姓名')
            self.bg_bt2 = [x for x in self.bg_bt]  # 获取列名
            for col in self.bg_bt2:  # 每个列名都加上排序
                self.treeview_sort_column(self.tree, col, False)
        self.tree.pack(fill='both', expand=True)#(side=tk.LEFT, fill=tk.BOTH)
        
        #滚动条3------------- 
        self.scorllbarx.config(command=self.tree.xview)
        self.scorllbary.config(command=self.tree.yview)
        if jbkj:
            ttk.Button(self.frame3,text='导入文件',command=lambda :self.path_uis(pd="2")).pack(side=tk.LEFT, fill=tk.BOTH)
            ttk.Button(self.frame3,text='导入文件夹',command=lambda :self.path_uis(pd="3")).pack(side=tk.LEFT, fill=tk.BOTH)
            ttk.Button(self.frame3,text='查询',command=lambda :self.bghs_查询(dx=False)).pack(side=tk.LEFT, fill=tk.BOTH)
            ttk.Button(self.frame3,text='点选查询',command=lambda :self.bghs_查询(dx=True)).pack(side=tk.LEFT, fill=tk.BOTH)            
            ttk.Button(self.frame3,text='插入列表',command=lambda :self.bghs_插入(lbnr=[[1,2,3,4]],zj=True)).pack(side=tk.LEFT, fill=tk.BOTH)        
            ttk.Button(self.frame3,text='插入单元格',command=lambda :self.bghs_修改([["#1","55"]])).pack(side=tk.LEFT, fill=tk.BOTH)        
            ttk.Button(self.frame3,text='点选删除',command=lambda :self.bghs_删除(dx=True)).pack(side=tk.LEFT, fill=tk.BOTH)
            ttk.Button(self.frame3,text='清空',command=lambda :self.bghs_删除(dx=False)).pack(side=tk.LEFT, fill=tk.BOTH)
            ttk.Button(self.frame3,text='导出',  command=lambda :self.导出()).pack(side=tk.LEFT, fill=tk.BOTH)
                
       
        self.entry = tk.Entry(self.frame2,highlightthickness=1, bg='#F3F3F4', textvariable='')
        self.entry.bind("<FocusIn>", self.bd_焦点输入)
        self.entry.bind("<FocusOut>",self.bd_焦点离开)        
        self.entry.bind("<Return>",self.bd_回车)            
        self.tree.bind('<ButtonRelease-1>', self.bd_单击)#绑定单击离开事件===========
        self.tree.bind("<Double-1>",self.bd_双击)
        #Text内部支持复制，粘贴
        self.menubar = tk.Menu(parent, tearoff=False)
        #绑定右键复制粘贴功能
        self.tree.bind('<Button-3>', lambda x: self.rightKey(x))
        if fy=="不分页":
            self.bghs_插入(self.bg_nr)
        elif fy=="分页":
            self.data = self.bg_nr
            self.rows_per_page = 100
            self.current_page = 1
            self.total_pages = (len(self.data) + self.rows_per_page - 1) // self.rows_per_page  # 向上取整
            
            # 创建分页按钮
            self.prev_button1 = ttk.Button(self.frame3, text="首页", command=lambda:self.display_page(1,pd=True))
            self.prev_button1.pack(side=tk.LEFT)
            self.prev_button = ttk.Button(self.frame3, text="上一页", command=self.prev_page)
            self.prev_button.pack(side=tk.LEFT)
            # 显示当前页码和总页数
            self.page_label = ttk.Label(self.frame3, text=f"Page {self.current_page} of {self.total_pages}")
            self.page_label.pack(side=tk.LEFT)
            
            self.next_button = ttk.Button(self.frame3, text="下一页", command=self.next_page)
            self.next_button.pack(side=tk.LEFT)    
            self.next_button4 = ttk.Button(self.frame3, text="尾页", command=lambda:self.display_page(self.total_pages,pd=True))
            self.next_button4.pack(side=tk.LEFT)
            self.entry5 = ttk.Entry(self.frame3)
            self.entry5.pack(side=tk.LEFT)
            self.entry5.insert(0, "1")  # 输入条插入内容
            self.next_button5 = ttk.Button(self.frame3, text="跳转", command=lambda:self.display_page(int(self.entry5.get()),pd=True))
            self.next_button5.pack(side=tk.LEFT)
            self.display_page(self.current_page)
        
    def fill_tree(self,path, parent_node=''):  
        for item in os.listdir(path):
            item_full_path = r"{}".format(os.path.join(path, item)) 
            # print(item_full_path) 
            node = self.tree.insert(parent_node, 'end', text=item,values=(item_full_path,), open=False)     
            # 如果该项是目录，那么递归填充树  
            if os.path.isdir(item_full_path):  
                self.fill_tree(item_full_path, node)   
    def display_page(self, page,pd=False):
        """显示指定页的数据"""
        # 清空Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 计算当前页的数据范围
        start = (page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        for row in self.data[start:end]:
            self.tree.insert("", tk.END, values=row)
        if pd==True:
            self.current_page=page
        
        # 更新当前页码显示
        # self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")
        self.page_label.config(text=f"第{self.current_page}页，共{self.total_pages}页，合计{len(self.data)}条")   

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_page(self.current_page)

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_page(self.current_page)
    def rightKey(self,event):
        self.menubar.delete(0, 'end')
        self.menubar.add_command(label='复制',command=lambda:self.fuzhi())
        self.menubar.add_command(label='剪切',command=lambda:self.剪切())
        self.menubar.add_command(label='粘贴',command=lambda:self.zhantiai())
        self.menubar.add_command(label='粘贴文件名',command=lambda:self.zhantiai(wjm=True))
        self.menubar.add_command(label='导入文件',command=lambda :self.path_uis(pd="2"))
        self.menubar.add_command(label='导入文件夹',command=lambda :self.path_uis(pd="3"))
        self.menubar.add_command(label='查询',command=lambda :self.bghs_查询(dx=False))
        self.menubar.add_command(label='点选查询',command=lambda :self.bghs_查询(dx=True))            
        self.menubar.add_command(label='插入列表',command=lambda :self.bghs_插入(lbnr=[[1,2,3,4]],zj=True))        
        self.menubar.add_command(label='插入单元格',command=lambda :self.bghs_修改([["#1","55"]]))        
        self.menubar.add_command(label='点选删除',command=lambda :self.bghs_删除(dx=True))
        self.menubar.add_command(label='清空',command=lambda :self.bghs_删除(dx=False))
        self.menubar.add_command(label='导出',  command=lambda :self.导出())
        self.menubar.add_command(label='打开文件',command=lambda:self.dakai(pd="1"))
        self.menubar.add_command(label='打开文件位置',command=lambda:self.dakai(pd="2"))
        self.menubar.add_command(label='保存',command=lambda:self.dakai(pd="3",texts=app.smdq_1.get(1.0, "end").strip()))
        self.menubar.add_command(label='运行内容py',command=lambda:self.dakai(pd="4",texts=app.smdq_1.get(1.0, "end").strip()))
        self.menubar.post(event.x_root,event.y_root)    
    def 剪切(self):
        self.fuzhi()
        self.bghs_删除(dx=True)
    def fuzhi(self):
        xx=[self.tree.set(x) for x in self.tree.selection()] #[{}]
        zlh=""  
        for i in xx:
            zlh+="\t".join(list(i.values()))+"\n"
        print("复制列表共{}个内容:{}".format(len(xx),zlh)) 
        pyperclip.copy(zlh)        
        return zlh
    def zhantiai(self,wjm=False):
        """粘贴"""
        if wjm==False:
            ztb=pyperclip.paste().strip().split("\n")
            dlb=[i.strip().split("\t") for i in ztb]
            print("已转列表：共{}个,内容：{}".format(len(dlb),dlb))
            self.bghs_插入(lbnr=dlb,zj=True)
        else:
            ztb=pyperclip.paste().strip().split("\n")
            dlb=[os.path.basename(i).strip() for i in ztb]
            print("已转列表：共{}个,内容：{}".format(len(dlb),dlb))
            self.bghs_插入(lbnr=dlb,zj=True)
    def dakai(self,pd="",texts=""):  
        print(texts)
        sj=self.tree.selection()        
        xx=[self.tree.set(x) for x in sj]
        if xx=="":
            return
        xxs=r"{}".format(xx[0]["路径"])

        if pd=="1":      
            os.startfile(xxs)
        elif pd=="2":
            os.startfile(os.path.dirname(xxs))
        elif pd=="3":
            if xxs.endswith(".py"):
                with open(xxs, 'w', encoding='utf-8', errors='ignore') as f:  
                        f.write(texts) 
        elif pd=="4":
            exec(texts)
        
   
    def 导出(self):
        xx=[self.tree.set(x) for x in self.tree.get_children()]
        print("共{}个表:{}".format(len(xx),xx))#[{}]
        sjgsh=str(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        bcljs="路径_{}.xlsx".format(sjgsh)      
        dd=pd.DataFrame(xx)  
        #header=None,index=False,      
        dd.to_excel(bcljs,engine='openpyxl')
        print("完成！")
    def btk(self,parent):
        """1标题"""
        parent.geometry("800x480+10+10")   #窗口大小x
        parent.title('word转pdf_v{}_文峰'.format(BBH))        
        # 使得这个窗口实例一直保持置顶
        parent.attributes('-topmost', False)
    
    #控件函数=====================
    #排序----------------
    def treeview_sort_column(self,tv, col, reverse):  # Treeview、列名、排列方式
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        # print(tv.get_children(''))
        # print(col)
        # l.sort(reverse=reverse)  # 排序方式
        # l.sort(key=lambda t: int(t[0]), reverse=reverse)  # 排序方式,先转换成数字再排序
        try:
            l.sort(key=lambda t: int(t[0]), reverse=reverse)  # 排序方式,先转换成数字再排序
        except ValueError:
            l.sort(reverse=reverse)  # 排序方式,按文本排序
        for index, (val, k) in enumerate(l):  # 根据排序后索引移动
            tv.move(k, '', index)
            # print(k)li1
        # print(1) # 测试是否死循环递归
        # 重写标题，使之成为再点倒序的标题，lambda千万不能少，否则就是死循环递归了
        tv.heading(col, text=col, command=lambda: self.treeview_sort_column(tv, col, not reverse))
    #单击-----------------------------------
    def bd_单击(self,event):
        print ('单击',self.tree.selection())
        for item in self.tree.selection():
            item_text = self.tree.item(item,"values")
            # print(item_text)
       
    
    # 表格鼠标左键双击触发
    def bd_双击(self,event):
        print("鼠标左键双击触发",event.widget)
        if str(event.widget).find(".!treeview")!=-1:  # 双击触发的是否为表格
            self.tree = event.widget
            for item in self.tree.selection():              # 取消表格选取
                self.tree.selection_remove(item)
            global row
            row = self.tree.identify_row(event.y)         # 点击的行#I002
            global column
            column = self.tree.identify_column(event.x)   # 点击的列#2
            print("行：{}，列：{}".format(row,column))
            col = int(str(self.tree.identify_column(event.x)).replace('#', ''))  # 列号
            if row != "":
                text = self.tree.item(row, 'value')[col - 1]  # 单元格内容        
                x = self.tree.bbox(row, column=col - 1)[0]    # 单元格x坐标
                y = self.tree.bbox(row, column=col - 1)[1]    # 单元格y坐标
                width = self.tree.bbox(row, column=col - 1)[2]  # 单元格宽度
                height = self.tree.bbox(row, column=col - 1)[3] # 单元格高度
                self.entry.focus_set()  # 输入条获取焦点
                self.entry.delete(0, "end")  # 清除输入条中的内容
                self.entry.place(x=x, y=y, width=width, height=height)  # 设置输入条位置及长宽
                self.entry.insert(0, text)  # 输入条插入内容
    # 表格焦点在输入条时触发
    def bd_焦点输入(self,event):
        pass
    # 表格焦点离开输入条时触发
    def bd_焦点离开(self,event):
        text = self.entry.get()    # 获取输入条内容
        self.tree.set(row, column, text) # 表格数据设置为输入条内容
        self.entry.place_forget()  # 隐藏输入条
    # 表格回车键触发
    def bd_回车(self,event):
        if self.entry.winfo_viewable() == 1:  # 如果输入条可见
            self.entry.place_forget()  # 隐藏输入条
            text = self.entry.get()  # 获取输入条内容
            self.tree.set(row, column, text)  # 表格数据设置为输入条内容
    
    def bghs_查询(self,dx=False):
        if dx==True:
            #点选
            sj=self.tree.selection()
        else:
            sj=self.tree.get_children()
        xx=[self.tree.set(x) for x in sj]
        # print(xx)
        return xx
    def bghs_删除(self,dx=False):
        if dx==True:
            #点选
            sj=self.tree.selection()
        else:
            sj=self.tree.get_children()
        for item in sj:
            self.tree.delete(item)
   
    def bghs_插入(self,lbnr=None,zj=False): 
        """lbnr:[[]],zj:是否追加[True|False]]"""
        if zj==False:
            self.bghs_删除(dx=False)
        # print(lbnr)
        if lbnr:
            for xlb in lbnr:
                self.tree.insert('','end',values=xlb)  
    def bghs_插入分页(self, page=1,pd=False):
        """显示指定页的数据"""
        
        # self.rows_per_page = 100
        # self.current_page = 1
        sjgs=len(self.data)#共多少条
        self.total_pages = (sjgs + self.rows_per_page - 1) // self.rows_per_page  # 向上取整
        # 清空Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 计算当前页的数据范围
        start = (page - 1) * self.rows_per_page
        end = start + self.rows_per_page
        for row in self.data[start:end]:
            self.tree.insert("", tk.END, values=row)
        if pd==True:
            self.current_page=page
        
        # 更新当前页码显示
        self.page_label.config(text=f"第{self.current_page}页，共{self.total_pages}页，合计{sjgs}条")   
    def bghs_修改(self,lbnr=None):
        #('I003',)行#[["#1",""]]
        x=self.tree.selection()
        for i in lbnr:
            self.tree.set(x, i[0],i[1]) # 表格数据设置为输入条内容
       
    
    #时间格式化->str
    def sjgsh(self):
        return str(datetime.now().strftime("%Y%m%d%H%M%S"))
    
       

    def wjsx(self,i):
        """文件名，大小，文件夹，文件路径"""
        wjm=os.path.basename(i)
        dx="{:.2f}kb".format(os.path.getsize(i)/1024)
        wjj=os.path.abspath(os.path.dirname(i))  
        return [wjm,dx,wjj,i]
    def path_uis(self,files=None,pd="1"): 
        """1.2打开文件路径或拖拽"""
        dlbs=[]
        if pd=="1":
            # p1=[item.decode('gbk') for item in files]#获得选择好的文件 
            p1=[os.path.basename(item.decode('gbk')) for item in files]#获得选择好的文件  
        elif pd=="2":
            wj=filedialog.askopenfilenames()#获得选择好的文件
            if wj:
                p1=[os.path.basename(item) for item in wj]#获得选择好的文件          
            else:
                return              
        elif pd=="3":
            #获得选择好的文件夹
            wjj=filedialog.askdirectory()
            if wjj:
                p1=[os.path.basename(wjj)]#获得选择好的文件          
            else:
                return
            # p1=[]
            # wjj=filedialog.askdirectory()
            # for root, dirs, files in os.walk(wjj):
            #     for file in files:
            #         wj=os.path.join(root,file)
            #         if wj.endswith(".doc") or wj.endswith(".docx") or wj.endswith(".DOC") or wj.endswith(".DOCX")  :               
            #             if os.path.isfile(wj):
            #                 p1.append(wj)
        
        
        # for i in p1:            
        #     dlb=self.wjsx(i)
        #     dlbs.append(dlb)
        print(p1)
        # self.bghs_删除(dx=False)
        self.bghs_插入(lbnr=p1,zj=True) 
            
            
           
    
   
   


#----------------------------------
if __name__ == '__main__':
    
    window = tk.Tk()
    bt=["路径"]
    nr=[['欢','迎','使','用']]
    #树
    app1 = App(window,bt,nr,jbkj=False,fy=False,pdshu=True)

    bt=["文件名","大小","文件夹","文件路径"]
    #非树
    app = App(window,bt,nr,jbkj=False,fy="不分页",pdshu=False)
    app.btk(window)
    window.mainloop()
