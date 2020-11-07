#python 3.9.0
#python套件 pandas 1.1.4
#輸入：
#	traffic/201907*.txt
#	test.txt
#輸出：
#	result.csv
#0.55033999
import pandas

訓練表 = None
for 甲 in range(1, 31):
	檔案 = open("traffic/201907%02d.txt" % 甲)
	道路標識清單 = []
	標籤清單 = []
	當前時間片清單 = []
	待測時間片清單 = []

	for 列 in 檔案:
		列分割 = 列.split(";")
		列分割0分割 = 列分割[0].split(" ")
		道路標識清單 += [int(列分割0分割[0])]
		標籤清單 += [int(列分割0分割[1])]
		當前時間片清單 += [int(列分割0分割[2])]
		待測時間片清單 += [int(列分割0分割[3])]

	訓練表 = pandas.concat((訓練表, pandas.DataFrame({"日序": 甲 - 31, "道路標識": 道路標識清單, "標籤": 標籤清單, "當前時間片": 當前時間片清單, "待測時間片": 待測時間片清單})))
	檔案.close()
訓練表 = 訓練表.loc[訓練表.標籤 > 0].reset_index(drop=True)
訓練表.loc[訓練表.標籤 > 3, "標籤"] = 3

檔案 = open("test.txt")
道路標識清單 = []
標籤清單 = []
當前時間片清單 = []
待測時間片清單 = []
for 列 in 檔案:
	列分割 = 列.split(";")
	列分割0分割 = 列分割[0].split(" ")
	道路標識清單 += [int(列分割0分割[0])]
	標籤清單 += [int(列分割0分割[1])]
	當前時間片清單 += [int(列分割0分割[2])]
	待測時間片清單 += [int(列分割0分割[3])]
測試表 = pandas.DataFrame({"日序": 0, "道路標識": 道路標識清單, "標籤": 標籤清單, "當前時間片": 當前時間片清單, "待測時間片": 待測時間片清單})
檔案.close()

測訓交叉表 = 測試表.loc[:, ["道路標識", "當前時間片", "待測時間片"]].merge(訓練表.rename({"當前時間片": "訓練當前時間片", "待測時間片": "訓練待測時間片"}, axis=1), on="道路標識")
測訓交叉表["權重"] = 1 / (1 + abs(測訓交叉表["待測時間片"] - 測訓交叉表["訓練待測時間片"]))
測訓交叉表 = 測訓交叉表.groupby(["道路標識", "當前時間片", "待測時間片", "標籤"]).aggregate({"權重": "sum"}).reset_index().rename({"權重": "打分"}, axis=1)

預測表 = 測試表
for 甲 in range(1, 4):
	預測表 = 預測表.merge(測訓交叉表.loc[測訓交叉表.標籤 == 甲, ["道路標識", "當前時間片", "待測時間片", "打分"]].rename({"打分": "打分%d" % 甲}, axis=1), on=["道路標識", "當前時間片", "待測時間片"], how="left")
預測表 = 預測表.fillna(0)

係數 = [(訓練表.標籤 == 3).sum() / 訓練表.shape[0], (訓練表.標籤 > 1).sum() / 訓練表.shape[0]]
預測表["預測"] = 1
預測表 = 預測表.sort_values("打分3", ascending=False).reset_index(drop=True)
預測表.loc[:int(係數[0] * 預測表.shape[0]), "預測"] = 3
預測表 = 預測表.sort_values(["預測", "打分2"], ascending=False).reset_index(drop=True)
預測表.loc[int(係數[0] * 預測表.shape[0]):int(係數[1] * 預測表.shape[0]), "預測"] = 2
預測表 = 預測表.loc[:, ["道路標識", "當前時間片", "待測時間片", "預測"]]

提交表 = 預測表.loc[:, ["道路標識", "當前時間片", "待測時間片", "預測"]].copy()
提交表.columns = ["link", "current_slice_id", "future_slice_id", "label"]
提交表.to_csv("result.csv", index=False)
