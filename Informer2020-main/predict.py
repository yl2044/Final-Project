import numpy as np
import pandas as pd
# 指定.npy文件路径:Specify the .npy file path 
file_path1 = r"C:\Users\Administrator\Desktop\Informer2020-main\results\informer_custom_ftMS_sl96_ll48_pl24_dm512_nh8_el2_dl1_df2048_atprob_fc5_ebtimeF_dtTrue_mxTrue_test_1\pred.npy"
file_path2 = r"C:\Users\Administrator\Desktop\Informer2020-main\results\informer_custom_ftMS_sl96_ll48_pl24_dm512_nh8_el2_dl1_df2048_atprob_fc5_ebtimeF_dtTrue_mxTrue_test_1\true.npy"
 
# 使用NumPy加载.npy文件: Loading .npy files with NumPy
true_value = []
pred_value = []
 
data1 = np.load(file_path1)
data2 = np.load(file_path2)
print(data2)
for i in range(24):
    true_value.append(data2[0][i][0])
    pred_value.append(data1[0][i][0])
 
# 打印内容: Print content
print(true_value)
print(pred_value)
 
df = pd.DataFrame({'real': true_value, 'pred': pred_value})
 
df.to_csv('results1.csv', index=False)
