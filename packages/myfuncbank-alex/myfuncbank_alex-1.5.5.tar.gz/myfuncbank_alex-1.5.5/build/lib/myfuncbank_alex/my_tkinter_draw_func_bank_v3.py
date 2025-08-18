import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib as mpl
import matplotlib.pyplot as plt
from markdown_it.rules_core.normalize import NULL_RE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
#from pymunk.examples.matplotlib_util_demo import ax

import myfuncbank_alex.my_func_bank as funcbank
import matplotlib.dates as mdates
import math
from functools import partial
import warnings
from dateutil.relativedelta import relativedelta

#设置支持中文字体
mpl.rc("font",family='STKaiti')
BIGFONT=("STKaiti",20)
NORMFONT=("STKaiti",16)
SMALLFONT=("STKaiti",10)

mpl.use('TkAgg')

def create_scroll_draw_area(frame):
    # 创建一个带有垂直滚动条的框架
    base_frame = ttk.Frame(frame)
    base_frame.pack(fill="both", expand=True)
    # base_frame.grid(row=0, column=0, sticky="nsew")

    canvas = tk.Canvas(base_frame)
    scrollbar = ttk.Scrollbar(base_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # 设置鼠标滚动事件
    canvas.configure(yscrollcommand=scrollbar.set)
    # canvas.bind("<Configure>", on_configure)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    # canvas.bind("<MouseWheel>", on_mousewheel)
    canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    return scrollable_frame


# 默认将excel中的全部行读入dataframe中
# 若传入了nrows参数，则读取excel中指定行数的数据到dataframe中
def readExcel2dataframe(sheetname,filepath,skiprows=0,nrows=0):
    if nrows == 0: #默认将全部excel文件读入
        df = pd.read_excel(filepath, sheet_name=sheetname, skiprows=skiprows)
    elif nrows < 0:
        warnings.warn("readExcel2dataframe函数在调用时传入的参数nrows不能为负值")
        exit(1)
    else: #指定读取excel中指定行数的数据
        df = pd.read_excel(filepath, sheet_name=sheetname, skiprows=skiprows, nrows=nrows)

    if df.size ==0: #空dataframe
        return df,None,None

    # 删除掉表头中没用的行
    if '指标名称' in df.columns:
        df = df[df['指标名称'] != '频率']
        df = df[df['指标名称'] != '更新时间']
        df = df[df['指标名称'] != '单位']
        df = df[df['指标名称'] != '指标ID']

    if '日期' in df.columns:
        df = df[df['日期'] != 'Date']

    df.rename(columns={'指标名称': '日期'}, inplace=True)  # 修改列名
    df['日期'] = df['日期'].astype('datetime64[ns]')  # 改为日期格式
    df.set_index('日期',inplace=True)

    ls=df.index.tolist()
    if len(ls) == 0: #空dataframe
        return df, None, None

    #设置默认起止日期
    e_date = ls[0]
    if(len(ls)< 100):
        s_date = ls[len(ls)-1]
    else:
        s_date = ls[100]

    if s_date < e_date:
        begin_date = s_date
        end_date = e_date
    else:
        begin_date = e_date
        end_date = s_date

    return df,begin_date,end_date


#自定义popups弹出窗口
def popupmsg(message):
    popup=tk.Tk()
    popup.wm_title("Warning!!")
    label=ttk.Label(popup,text=message,font=NORMFONT)
    label.pack(anchor=tk.CENTER,pady=10)
    button=ttk.Button(popup,text="Okay",command=popup.destroy)
    button.pack()
    popup.geometry("300x100")
    popup.mainloop()



def update_chart_show(df,ax,fig,title,**kwargs):
    matplot_draw(df,ax,fig,title,**kwargs)
    fig.canvas.draw_idle()

    height_Mouse(df,ax,fig,**kwargs)



def matplot_draw(df,ax,fig,title,**kwargs):

    #关键字参数实现参数个数不同，从而实现函数重载功能
    if "ax_twin" in kwargs:  #传入副坐标轴
        ax_twin=kwargs["ax_twin"]
        ax_twin.clear()
    else:
        ax_twin=None

    ax.clear()


    x = df.index
    lines=[]

    # 判断当前的dataframe是否有缺失值，如果有，则使用线性填充方法补齐缺失区域数据
    has_missing_values = df.isna().any().any()
    if has_missing_values:
        df=df.astype(float) #将wind为object类型的数据转换为float型
        # 对包含数据缺失的所有列进行线性插值
        df.interpolate(method='linear', limit_area='inside', inplace=True)

    for column in df.columns:
        if "【副轴】"in column:
            # # 从列名中删除【副轴】标记
            # new_colname = column.replace('【副轴】', "")
            # selected_df.rename(columns={column:new_colname}, inplace=True)
            if ax_twin is None:
                warnings.warn("matplot_draw函数在调用有副坐标轴的图形时没有找到副坐标轴的ax_twin")
                exit(1)

            if "【柱状图】" in column:
                #从列名中删除【柱状图】标记
                new_colname=column.replace('【柱状图】',"")
                df.rename(columns={column : new_colname},inplace=True)
                bar=ax_twin.bar(x, df[new_colname], width=10, label=new_colname,color='green')
                lines.append(bar)

            elif "【面积图】" in column:
                # 从列名中删除【面积图】标记
                new_colname = column.replace('【面积图】', "")
                df.rename(columns={column: new_colname}, inplace=True)
                #类型转换，确保数据为数字类型，其他类型会报错
                df[new_colname] = pd.to_numeric(df[new_colname], errors='coerce')
                # 取该列的最小值,指定面积图填充从0.8倍下限值开始向上填充，否则默认下限是从0值开始填充屏幕
                y_min = df[new_colname].min()
                area = ax_twin.fill_between(x, df[new_colname], 0.8 * y_min, alpha=0.5, label=new_colname,
                                            color='green')
                lines.append(area)

            elif "【散点图】" in column:
                # 从列名中删除【面积图】标记
                new_colname = column.replace('【散点图】', "")
                df.rename(columns={column: new_colname}, inplace=True)
                # 类型转换，确保数据为数字类型，其他类型会报错
                df[new_colname] = pd.to_numeric(df[new_colname], errors='coerce')
                line = ax_twin.scatter(x, df[new_colname],alpha=0.8, marker='_',label=new_colname,
                                            color='green')
                lines.append(line)

            elif "【堆叠面积图】" in column:
                new_colname = column.replace('【堆叠面积图】', "")
                #列出该列前的所有列名
                col_index = df.columns.get_loc(column) # 获取目标列的索引位置
                columns_before = df.columns[:col_index] # 获取该列前面的所有列名
                filtered_columns = [col for col in columns_before if "【堆叠面积图】" in col] #选出包含"【堆叠面积图】"的列名

                # 对指定列进行求和
                sum_result = df[filtered_columns].sum(axis=1)  # axis=1 表示按行求和
                new_df = pd.DataFrame(sum_result, columns=['Sum']) # 将结果存储到新的 DataFrame 中
                # 类型转换，确保数据为数字类型，其他类型会报错
                new_df['Sum']=pd.to_numeric(new_df['Sum'],errors='coerce')
                df[column] = pd.to_numeric(df[column], errors='coerce')
                area = ax_twin.fill_between(x, new_df['Sum'], new_df['Sum']+df[column],alpha=0.5, label=new_colname,
                                            color='green')
                lines.append(area)

            else: #折线图
                if "【虚线】" in column:
                    # 从列名中删除【虚线】标记
                    new_colname = column.replace('【虚线】', "")
                    df.rename(columns={column: new_colname}, inplace=True)

                    line,=ax_twin.plot(x, df[new_colname], label=new_colname, color='orange', linestyle='--')
                    lines.append(line)
                else:
                    line, = ax_twin.plot(x, df[column], label=column, color='green')
                    lines.append(line)

        else: #主轴
            if "【柱状图】" in column:
                #从列名中删除【柱状图】标记
                new_colname=column.replace('【柱状图】',"")
                df.rename(columns={column : new_colname},inplace=True)
                bar=ax.bar(x, df[new_colname], width=10, label=new_colname)
                lines.append(bar)

            elif "【面积图】" in column:
                # 从列名中删除【面积图】标记
                new_colname = column.replace('【面积图】', "")
                df.rename(columns={column: new_colname}, inplace=True)
                # 类型转换，确保数据为数字类型，其他类型会报错
                df[new_colname]=pd.to_numeric(df[new_colname],errors='coerce')
                # 取该列的最小值,指定面积图填充从0.8倍下限值开始向上填充，否则默认下限是从0值开始填充屏幕
                y_min = df[new_colname].min()
                area = ax.fill_between(x, df[new_colname], 0.8 * y_min, alpha=0.5, label=new_colname)
                lines.append(area)

            elif "【散点图】" in column:
                # 从列名中删除【面积图】标记
                new_colname = column.replace('【散点图】', "")
                df.rename(columns={column: new_colname}, inplace=True)
                # 类型转换，确保数据为数字类型，其他类型会报错
                df[new_colname] = pd.to_numeric(df[new_colname], errors='coerce')
                line = ax.scatter(x, df[new_colname],alpha=0.8, marker='_', label=new_colname)
                lines.append(line)

            elif "【堆叠面积图】" in column:
                new_colname = column.replace('【堆叠面积图】', "")
                #列出该列前的所有列名
                col_index = df.columns.get_loc(column) # 获取目标列的索引位置
                columns_before = df.columns[:col_index] # 获取该列前面的所有列名
                filtered_columns = [col for col in columns_before if "【堆叠面积图】" in col] #选出包含"【堆叠面积图】"的列名

                # 对指定列进行求和
                sum_result = df[filtered_columns].sum(axis=1)  # axis=1 表示按行求和
                new_df = pd.DataFrame(sum_result, columns=['Sum']) # 将结果存储到新的 DataFrame 中
                # 类型转换，确保数据为数字类型，其他类型会报错
                new_df['Sum']=pd.to_numeric(new_df['Sum'],errors='coerce')
                df[column] = pd.to_numeric(df[column], errors='coerce')
                area = ax.fill_between(x, new_df['Sum'], new_df['Sum']+df[column],alpha=0.5, label=new_colname)
                lines.append(area)

            else: #折线图
                if "【虚线】" in column:
                    # 从列名中删除【虚线】标记
                    new_colname = column.replace('【虚线】', "")
                    df.rename(columns={column: new_colname}, inplace=True)

                    line,=ax.plot(x, df[new_colname], label=new_colname, linestyle='--')
                    lines.append(line)
                else:
                    line, = ax.plot(x, df[column], label=column)
                    lines.append(line)

    ax.set_title(title,fontsize=16)
    ax.set_xlabel("日期")
    if ax_twin is None:
        ax.set_ylabel("数值")
    else:
        ax.set_ylabel("主Y轴", color="blue")
        ax_twin.set_ylabel("副Y轴", color="green")
        #设置副轴标签相对于副轴的位置，确保显示在副轴右侧，其中 (1.05, 0.5) 表示标签位于副轴的右侧，纵向位置居中
        ax_twin.yaxis.set_label_coords(1.06,0.5)

        # 获取副坐标轴的数据范围
        # 这个必须设置，定了取值范围才能和主轴坐标有明确的一对一对应关系，否则副轴标记亮点的显示位置不对
        y1_min, y1_max = ax_twin.get_yaxis().get_data_interval()
        # 使用副坐标轴的数据范围设置副坐标轴的y坐标范围
        if y1_min < 0:
            lower_limit=y1_min*1.3
        else:
            lower_limit=y1_min*0.7

        if y1_max <0:
            upper_limit=y1_max*0.9
        else:
            upper_limit=y1_max*1.1

        ax_twin.set_ylim(lower_limit, upper_limit)


    labels = [line.get_label() for line in lines]
    ax.legend(lines, labels)
    # self.fig.canvas.draw_idle()

    '''
    # 设置x轴的刻度定位器为MonthLocator，并设置日期格式为年月
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    #倾斜x轴标签以避免重叠
    ax.tick_params(axis='x', rotation=90)
    '''


# 功能: 自动识别并点亮离鼠标最近处的数据点，并显示该数据点的数据值
# 最新修改: 加入了随鼠标移动而动态生成的垂直观察线，当函数的输入参数中包含"vertical_line"项，且其值被设置为True时，此功能激活
def height_Mouse(df,ax,fig,**kwargs): # 实现当鼠标悬浮在图形线条上某个位置时，动态显示出此点在x,y轴上的取值
    #解除绑定之前的所有事件处理函数
    fig.canvas.callbacks.callbacks = {}

    df_main=None
    df_twin=None

    # 关键字参数实现参数个数不同，从而实现函数重载功能
    if "ax_twin" in kwargs:  # 传入副坐标轴
        ax_twin = kwargs["ax_twin"]
    else:
        ax_twin = None
        df_twin = None

    # 关键字参数中是否有vertical_line
    if "vertical_line" in kwargs:
        line_flag=kwargs["vertical_line"]
    else:
        line_flag=False

    pure_df=df.dropna(how='all') #删除全是nan的行
    # 标识数据点时，先去除“荣枯线”等辅助线的影响
    if '市场前景荣枯线' in pure_df.columns:
        pure_df = pure_df.drop('市场前景荣枯线', axis=1)
    if '辅助0轴【副轴】【虚线】' in pure_df.columns:
        pure_df = pure_df.drop('辅助0轴【副轴】【虚线】', axis=1)
    if '辅助0轴【虚线】' in pure_df.columns:
        pure_df = pure_df.drop('辅助0轴【虚线】', axis=1)

    # 为on_mouse_move鼠标事件分析当前鼠标位置离主轴/副轴上哪个数据点更近做数据准备
    df_main,df_twin = devide_dfmain_dftwin(pure_df)
    if not df_twin.empty:
        # 副轴df转换为主轴坐标后计算，否则副轴和主轴数据不在一个维度，后面的比较结果会失真
        df_twin_2_df_main_value = funcbank.transfer_dftwin_to_dfmain(ax, ax_twin, df_twin)

    # 主轴标亮点-------------
    # 标亮点的标记
    highlighted_point, = ax.plot([], [], marker='o', markersize=8, color='red', visible=False)

    # 显示坐标信息的文本框
    annotation = ax.annotate('', xy=(0, 0), xytext=(10, 10),
                             textcoords='offset points', visible=False)
    # 副轴标亮点--------------
    if ax_twin is not None:
        highlighted_point_xtwin, = ax_twin.plot([], [], marker='o', markersize=8, color='blue', visible=False)

        # 显示坐标信息的文本框
        annotation_xtwin = ax_twin.annotate('', xy=(0, 0), xytext=(10, 10),
                                            textcoords='offset points', visible=False)

    if line_flag: #为True
        # 主轴画垂直辅助观察虚线---------------
        vertical_line, = ax.plot([], [], color='grey', linestyle='--', alpha=0.5, visible=False)
        # 副轴画垂直辅助观察虚线---------------
        if ax_twin is not None:
            vertical_line_xtwin, = ax_twin.plot([], [], color='grey', linestyle='--', alpha=0.5, visible=False)

    # 鼠标移动事件处理函数
    #def on_mouse_move(event,df_main,df_twin,ax,ax_twin):
    def on_mouse_move(event, ax, ax_twin):
        #print(event.xdata, event.ydata)
        #df_main, df_twin = devide_dfmain_dftwin(pure_df)

        if event.xdata is not None and event.ydata is not None:
            #print(event.xdata, event.ydata)
            if event.inaxes == ax_twin or event.inaxes == ax:
                if ax_twin is None: #鼠标点坐标显示为主坐标轴
                    x_main, y_main = event.xdata, event.ydata
                    nearest_x,nearest_y = funcbank.find_nearest_datapoint(df_main,x_main,y_main)

                    # 更新标亮点的位置
                    highlighted_point.set_data([nearest_x], [nearest_y])
                    highlighted_point.set_visible(True)

                    # 更新文本框的位置和内容
                    annotation.xy = (nearest_x, nearest_y)
                    annotation.set_text(f'({nearest_x.strftime("%Y-%m-%d")}, {nearest_y:.2f})')
                    annotation.set_visible(True)

                    # 如果line_flag为True，则需要更新重绘鼠标点位置的垂直辅助观察虚线
                    if line_flag: #值为True
                        y1_min, y1_max = ax.get_ylim() #取主y轴的坐标范围
                        arr_x=np.full(100,nearest_x)
                        arr_y=np.linspace(y1_min,y1_max,100)
                        vertical_line.set_data(arr_x,arr_y)
                        vertical_line.set_visible(True)


                else:  # 鼠标点坐标显示为副轴坐标
                    #print(df_twin)
                    x_twin, y_twin = event.xdata, event.ydata
                    x_main, y_main = funcbank.twin_axes_to_main_axes(ax, ax_twin, x_twin, y_twin)
                    # 计算主轴上最接近鼠标处的点
                    nearest_x_main,nearest_y_main =funcbank.find_nearest_datapoint(df_main, x_main, y_main)
                    # 计算副轴上最接近鼠标处的点
                    #df_twin_2_df_main_value = funcbank.transfer_dftwin_to_dfmain(ax, ax_twin, df_twin)  #副轴df转换为主轴坐标后计算，否则副轴和主轴数据不在一个维度，后面的比较结果会失真
                    nearest_x_twin,nearest_y_twin_main = funcbank.find_nearest_datapoint(df_twin_2_df_main_value,x_main, y_main)
                    #比较主轴，副轴上离鼠标最近点，看哪个更近
                    dis_main = math.sqrt((x_main - mdates.date2num(nearest_x_main)) ** 2 + (y_main - nearest_y_main) ** 2)
                    dis_twin = math.sqrt((x_main - mdates.date2num(nearest_x_twin)) ** 2 + (y_main - nearest_y_twin_main) ** 2)

                    if dis_main < dis_twin: #主轴近
                        # 更新主坐标轴标亮点的位置
                        highlighted_point.set_data([nearest_x_main], [nearest_y_main])
                        highlighted_point.set_visible(True)

                        # 更新文本框的位置和内容
                        annotation.xy = (nearest_x_main, nearest_y_main)
                        annotation.set_text(f'({nearest_x_main.strftime("%Y-%m-%d")}, {nearest_y_main:.2f})')
                        annotation.set_visible(True)

                        #隐藏副轴亮点
                        if ax_twin is not None:
                            highlighted_point_xtwin.set_visible(False)
                            annotation_xtwin.set_visible(False)

                        # 如果line_flag为True，则需要更新重绘鼠标点位置的垂直辅助观察虚线
                        if line_flag:  # 值为True
                            y1_min, y1_max = ax_twin.get_ylim() # 取副y轴的坐标范围
                            arr_x = np.full(100, nearest_x_main)
                            arr_y = np.linspace(y1_min, y1_max, 100)
                            vertical_line_xtwin.set_data(arr_x, arr_y)
                            vertical_line_xtwin.set_visible(True)

                    else: #副轴近
                        #将主坐标轴坐标转换为副坐标轴坐标
                        cursor_x_twin, nearest_y_twin= funcbank.main_axes_to_twin_axes(ax,ax_twin,nearest_x_twin,nearest_y_twin_main)
                        # 更新副坐标轴标亮点的位置
                        highlighted_point_xtwin.set_data([nearest_x_twin], [nearest_y_twin])
                        highlighted_point_xtwin.set_visible(True)

                        # 更新文本框的位置和内容
                        annotation_xtwin.xy = (nearest_x_twin, nearest_y_twin)
                        annotation_xtwin.set_text(f'({nearest_x_twin.strftime("%Y-%m-%d")}, {nearest_y_twin:.2f})')
                        annotation_xtwin.set_visible(True)

                        #隐藏主轴亮点
                        highlighted_point.set_visible(False)
                        annotation.set_visible(False)

                        # 如果line_flag为True，则需要更新重绘鼠标点位置的垂直辅助观察虚线
                        if line_flag:  # 值为True
                            y1_min, y1_max=ax_twin.get_ylim() # 取副y轴的坐标范围
                            arr_x = np.full(100, nearest_x_twin)
                            arr_y = np.linspace(y1_min, y1_max, 100)
                            vertical_line_xtwin.set_data(arr_x, arr_y)
                            vertical_line_xtwin.set_visible(True)

                fig.canvas.draw_idle()

    # 鼠标离开事件处理函数
    def on_mouse_leave(event):
        #disable高亮数据点
        highlighted_point.set_visible(False)
        annotation.set_visible(False)
        if ax_twin is not None:
            highlighted_point_xtwin.set_visible(False)
            annotation_xtwin.set_visible(False)

        #disable垂直辅助观察线
        if line_flag:
            vertical_line.set_visible(False)
            if ax_twin is not None:
                vertical_line_xtwin.set_visible(False)

        fig.canvas.draw_idle()

    # 连接鼠标移动和离开事件
    #使用了 functools.partial 来创建了一个闭包 callback，将 on_click 函数与额外的参数pure_df绑定在一起。然后，我们使用 mpl_connect 函数将 callback 函数连接到图形的鼠标事件上。
    #callback = partial(on_mouse_move, df_main=df_main, df_twin=df_twin, ax=ax, ax_twin=ax_twin)
    callback = partial(on_mouse_move, ax=ax, ax_twin=ax_twin)
    fig.canvas.mpl_connect('motion_notify_event', callback)
    fig.canvas.mpl_connect('axes_leave_event', on_mouse_leave)

# 按照主轴，副轴将dataframe拆分
def devide_dfmain_dftwin(dataframe):
    # 创建两个空的DataFrame
    main_df = pd.DataFrame()
    twin_df = pd.DataFrame()

    for column in dataframe.columns:
        if "【副轴】" in column:
            twin_df=pd.concat([twin_df, dataframe[column]], axis=1)
        else:
            main_df = pd.concat([main_df, dataframe[column]], axis=1)

    return main_df, twin_df


def drawCombobox(sheet, df, fatherFrame, date_signal):
    def on_select_begindate(event):
        cur_begin_str = combobox.get()

        if cur_begin_str > str(sheet.end_date):
            popupmsg("开始时间不能晚于结束时间")
        else:
            sheet.begin_date = cur_begin_str
            sheet.label_begin.config(text=sheet.begin_date)
            sheet.update_show_total_charts()


    def on_select_enddate(event):
        cur_end = combobox.get()
        if cur_end < str(sheet.begin_date):
            popupmsg("结束时间不能早于开始时间")
        else:
            sheet.end_date = cur_end
            sheet.label_end.config(text=sheet.end_date)
            sheet.update_show_total_charts()

    options = df.index.tolist()
    combobox = ttk.Combobox(fatherFrame, values=options, state="readonly", height=30)

    if (date_signal == "BEGIN"):
        label = tk.Label(fatherFrame, text="开始时间：")
        label.grid(row=0, column=sheet.grid_column)
        combobox.set(sheet.begin_date)
        combobox.bind("<<ComboboxSelected>>", on_select_begindate)
        sheet.grid_column += 1
        combobox.grid(row=0, column=sheet.grid_column)
        sheet.label_begin = tk.Label(fatherFrame, text=sheet.begin_date)
        sheet.grid_column += 1
        sheet.label_begin.grid(row=0, column=sheet.grid_column)
        # 在后面插入空列
        sheet.grid_column += 1
        insertBlankColumn(sheet,fatherFrame, sheet.grid_column)
    else:
        label = tk.Label(fatherFrame, text="结束时间：")
        sheet.grid_column += 1
        label.grid(row=0, column=sheet.grid_column)
        combobox.set(sheet.end_date)
        combobox.bind("<<ComboboxSelected>>", on_select_enddate)
        sheet.grid_column += 1
        combobox.grid(row=0, column=sheet.grid_column)
        sheet.label_end = tk.Label(fatherFrame, text=sheet.end_date)
        sheet.grid_column += 1
        sheet.label_end.grid(row=0, column=sheet.grid_column)

def insertBlankColumn(sheet,fatherFrame,col_num):
    # 在当前列col_num处插入空列
    empty_column = tk.Frame(fatherFrame, width=40)
    empty_column.grid(row=0, column=col_num)



def insert_timespan_button_years(sheet,df,fatherFrame,years):
    def on_button_click():
        reverse_flag = False
        ls = df.index.tolist()
        if ls[0] > ls[len(ls)-1]:
            reverse_flag=True

        #dataframe中的表数据是以逆序时间排列的
        if reverse_flag:
            sheet.end_date=ls[0]
        else:
            sheet.end_date=ls[len(ls)-1]

        # 计算N年前的日期
        if years is not None:
            years_ago = sheet.end_date - relativedelta(years=years)
            # 计算每个索引值与目标时间的差值，并取绝对值
            time_diff = abs(df.index - years_ago)
            index_series = pd.Series(time_diff)
            # 找到差值最小的索引值
            closest_index = index_series.idxmin()
            sheet.begin_date=ls[closest_index]
            #print(self.begin_date)
        else: #全时间区间 years==None
            if reverse_flag:
                sheet.begin_date=ls[len(ls)-1]
            else:
                sheet.begin_date=ls[0]

        #更新开始时间/结束时间label
        sheet.label_begin.config(text=sheet.begin_date)
        sheet.label_end.config(text=sheet.end_date)

        #更新数据
        sheet.update_show_total_charts()

    if years is not None:
        text=str(years)+"年"
    else:
        text = "有史以来"
    button= ttk.Button(fatherFrame,text=text,command=on_button_click)
    sheet.grid_column+=1
    button.grid(row=0,column=sheet.grid_column)


def insert_timespan_button_months(sheet,df,fatherFrame,months):
    def on_button_click():
        reverse_flag = False
        ls = df.index.tolist()
        if ls[0] > ls[len(ls)-1]:
            reverse_flag=True

        #dataframe中的表数据是以逆序时间排列的
        if reverse_flag:
            sheet.end_date=ls[0]
        else:
            sheet.end_date=ls[len(ls)-1]

        # 计算N个月前的日期
        months_ago = sheet.end_date - relativedelta(months=months)
        # 计算每个索引值与目标时间的差值，并取绝对值
        time_diff = abs(df.index - months_ago)
        index_series = pd.Series(time_diff)
        # 找到差值最小的索引值
        closest_index = index_series.idxmin()
        sheet.begin_date=ls[closest_index]
        #print(self.begin_date)


        #更新开始时间/结束时间label
        sheet.label_begin.config(text=sheet.begin_date)
        sheet.label_end.config(text=sheet.end_date)

        #更新数据
        sheet.update_show_total_charts()

    text=str(months)+"个月"
    button= ttk.Button(fatherFrame,text=text,command=on_button_click)
    sheet.grid_column+=1
    button.grid(row=0,column=sheet.grid_column)
