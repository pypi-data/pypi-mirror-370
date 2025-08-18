import pandas as pd
import my_tkinter_draw_func_bank_v3 as bank
import matplotlib as mpl
import matplotlib.pyplot as plt




def test_plot():
    # 创建一个简单的 DataFrame
    data = {
        'A': [1, 2, 3],
        'B': [4, 5, 6],
        'C': [7, 8, 9],
        'D': [10, 11, 12]
    }

    df = pd.DataFrame(data)

    # 指定目标列名
    target_column = 'A'

    # 获取目标列的索引位置
    col_index = df.columns.get_loc(target_column)

    # 获取该列前面的所有列名
    columns_before_target = df.columns[:col_index]

    # 对指定列进行求和
    sum_result = df[columns_before_target].sum(axis=1)  # axis=1 表示按行求和

    # 将结果存储到新的 DataFrame 中
    new_df = pd.DataFrame(sum_result, columns=['Sum'])

    # 打印新的 DataFrame

    fig1=plt.figure(figsize=(16, 8), dpi=100)
    ax1=fig1.add_subplot(111)

    postfix = "【堆叠面积图】"  # 所有列名后加标注
    df.columns = [col + postfix for col in df.columns]

    bank.matplot_draw(df,ax1,fig1,"test")
    fig1.show()
    print("111")


def test_func_readExcel2dataframe(sheetname,filepath):
    bank.readExcel2dataframe(sheetname,filepath)

filepath = 'D:\OneDrive\交易相关\研究\A股\市场中期方向判断（1周-几个月）\创近1年新高，新低股票占比\创近一年新高新低股票占比 V1.0.xlsx'
sheetname = "近一年新高（新低）股票占比"
test_func_readExcel2dataframe(sheetname,filepath)
#test_plot()
