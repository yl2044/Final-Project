import pandas as pd
import matplotlib.pyplot as plt

# 读取CSV文件
data = pd.read_csv(r'C:\Users\86181\Desktop\Informer2020-main\results.csv')

# 提取真实值和预测值列
real_values = data['real']
pred_values = data['pred']

# 绘制对比图
plt.figure(figsize=(10, 6))
plt.plot(real_values, label='Real')
plt.plot(pred_values, label='Predicted')

# 添加标题和标签
plt.title('Real vs Predicted Comparison')
plt.xlabel('Data Points')
plt.ylabel('Values')

# 添加图例
plt.legend()
plt.savefig('real_vs_predicted_comparison.png')
# 显示图形
plt.show()

