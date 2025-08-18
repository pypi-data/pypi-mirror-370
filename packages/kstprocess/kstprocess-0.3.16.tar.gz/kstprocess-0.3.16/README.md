
## 打包和上传pypi命令
```python
python3 setup.py sdist bdist_wheel
twine upload dist/*

pypi-AgEIcHlwaS5vcmcCJDZjMThmNWUzLWQ0ZGQtNGRhNS05ODExLTZhZmEwZmE1MTM2MAACElsxLFsia3N0cHJvY2VzcyJdXQACLFsyLFsiMmRjZmE2ZjQtN2JkOC00N2YzLWFlOGUtYzc0YzNiMDFiNzE3Il1dAAAGIIARMSFEgbe69QXem_vHiWngjpkGz3UDojM1zcF3Pmtc

# pypi-AgEIcHlwaS5vcmcCJGM4OWM3NDRiLWIzNTEtNDJkOS1iNzc2LTQxZjRlNjNmMTJkMwACKlszLCI1MDA1MTkzMy00M2E3LTRmY2QtODNlMi0wYzJlNjlmNGNlY2MiXQAABiCvyx84-INQn769QJhjyDb4TfaM8domuUyQdBbl6ViiIw
```

然后删掉 `build`,`dist`,`kstprocess.egg-info`

## 第一步：处理原始数据

快商通-总后台-机器人-对话记录：导出的文件:2025年07月07日10时15分49秒-对话记录导出.xlsx。

```python


process_data(
    input_file_path='./接入数据-对话流.xlsx',
    output_file_path='./版本_主题_对话流.xlsx'
)
```

## 第二步：绘制对比图
```python

plot_comparison(
    file1_path='./版本_主题_候选话术库_kicp_gpt.xlsx',
    file2_path='./版本_主题_kicp-GPT.xlsx',
    prefix1='候选话术库_kicp_gpt',
    prefix2='kicp-GPT',
    save_path='./留联率对比.jpg',
    min_valid_conversations=5,
)
```

## 动一牵全身的地方

```python
# kstprocess/preferenceDataConstruct/OnlinePreferenceConstructPipeline.pyconvert_my_format_to_center/convert
_, search_text, guide_text = history[0]["content"].replace("你是儿科高级咨询师\n你的核心目标是获取访客联系方式。 ", "").split("\n")
# 如果前面的prompt改了，"你是儿科高级咨询师\n你的核心目标是获取访客联系方式。 "也需要修改
```

## DPO数据构造

- 下一步action修复

- 不同科室的对话生成约束
    - 正样本生成
    - 负样本生成

- dpo二次打分



