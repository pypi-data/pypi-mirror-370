import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def process_data(
    input_file_path,
    output_file_path,
    version_col='版本ID',
    topic_col='对话主题',
    linked_col='是否获联',
    valid_conversation_col='是否有效对话',
    visitor_msg_count_col='访客消息数',
    dialog_id_col='对话ID'
):
    df = pd.read_excel(input_file_path, sheet_name=0)
    df[topic_col] = df[topic_col].fillna('无主题')
    df[version_col] = df[version_col].fillna('未知版本')

    required_columns = [dialog_id_col, topic_col, version_col, linked_col, visitor_msg_count_col, valid_conversation_col]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''

    df[linked_col] = df[linked_col].map({'已获联': True, '未获联': False})
    df[valid_conversation_col] = df[valid_conversation_col].map({'有效对话': True, '无效对话': False})

    df[visitor_msg_count_col] = pd.to_numeric(df[visitor_msg_count_col], errors='coerce').fillna(0).astype(int)

    results = []

    grouped = df.groupby([version_col, topic_col])
    for (version, topic), group in grouped:
        valid_conversations = group[group[valid_conversation_col]]
        conversations_with_visitors = group[group[visitor_msg_count_col] > 0]

        total_valid = len(valid_conversations)
        linked_valid = valid_conversations[valid_conversations[linked_col]].shape[0]
        valid_conversion_rate = round(linked_valid / total_valid if total_valid > 0 else 0, 4)

        total_visitor = len(conversations_with_visitors)
        linked_visitor = conversations_with_visitors[conversations_with_visitors[linked_col]].shape[0]
        visitor_conversion_rate = round(linked_visitor / total_visitor if total_visitor > 0 else 0, 4)

        linked_ids = valid_conversations[valid_conversations[linked_col]][dialog_id_col].tolist()
        non_linked_ids = valid_conversations[~valid_conversations[linked_col]][dialog_id_col].tolist()

        results.append({
            '版本号': version,
            '主题': topic,
            '有效对话数': total_valid,
            '有效留联数': linked_valid,
            '访客消息>0的对话数': total_visitor,
            '留联对话数': linked_visitor,
            '一句话对话留联率': f"{visitor_conversion_rate:.2%}",
            '有效对话留联率': f"{valid_conversion_rate:.2%}",
            '留联对话ID': linked_ids,
            '未留联有效对话ID': non_linked_ids
        })

    results_df = pd.DataFrame(results)
    results_df.to_excel(output_file_path, index=False)
    print(f"✅ 数据统计完成，已保存至: {output_file_path}")


def plot_comparison(
    file1_path,
    file2_path,
    prefix1="kicp固定流程",
    prefix2="GPT",
    font_name='WenQuanYi Zen Hei',
    min_valid_conversations=5,
    save_path="./留联率对比_kicp_vs_gpt.jpg",
    dpi=300,
    bar_width=0.35,
    figsize=(14, 8)
):
    plt.rcParams['font.sans-serif'] = [font_name]
    plt.rcParams['axes.unicode_minus'] = False

    file1_data = pd.read_excel(file1_path)
    file2_data = pd.read_excel(file2_path)

    filtered_file1_data = file1_data[file1_data['有效对话数'] > min_valid_conversations]
    filtered_file2_data = file2_data[file2_data['有效对话数'] > min_valid_conversations]

    # 获取共同主题
    common_themes = np.intersect1d(
        filtered_file1_data['主题'].unique(),
        filtered_file2_data['主题'].unique()
    )

    if len(common_themes) == 0:
        raise ValueError("没有共同的主题可用于对比，请检查输入数据")

    # 初始化留联率数据列表
    one_sentence_rate_file1 = []
    three_sentences_rate_file1 = []
    one_sentence_rate_file2 = []
    three_sentences_rate_file2 = []

    for theme in common_themes:
        # 获取每个主题的留联率数据，如果不存在则填充0
        row_f1 = filtered_file1_data[filtered_file1_data['主题'] == theme]
        row_f2 = filtered_file2_data[filtered_file2_data['主题'] == theme]

        def get_rate(row, col_name):
            return row[col_name].str.rstrip('%').astype(float).values[0] if not row.empty else 0

        one_sentence_rate_file1.append(get_rate(row_f1, '一句话对话留联率'))
        three_sentences_rate_file1.append(get_rate(row_f1, '有效对话留联率'))

        one_sentence_rate_file2.append(get_rate(row_f2, '一句话对话留联率'))
        three_sentences_rate_file2.append(get_rate(row_f2, '有效对话留联率'))

    index = np.arange(len(common_themes))

    fig, ax = plt.subplots(figsize=figsize)

    bars1 = ax.bar(index, one_sentence_rate_file1, bar_width, label=f'一句话留联率_{prefix1}')
    bars2 = ax.bar(index + bar_width, three_sentences_rate_file1, bar_width, label=f'有效对话留联率_{prefix1}')

    bars3 = ax.bar(index + 0.05, one_sentence_rate_file2, bar_width, label=f'一句话留联率_{prefix2}', alpha=0.6)
    bars4 = ax.bar(index + bar_width + 0.05, three_sentences_rate_file2, bar_width, label=f'有效对话留联率_{prefix2}', alpha=0.6)

    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    add_labels(bars1)
    add_labels(bars2)
    add_labels(bars3)
    add_labels(bars4)

    ax.set_xlabel('主题')
    ax.set_ylabel('留联率 (%)')
    ax.set_title(f'有效对话数大于{min_valid_conversations}的主题的一句话与有效对话留联率对比')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(common_themes, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi)
    plt.close()
    print(f"✅ 图表已保存至: {save_path}")

# # 第一步：处理原始数据
# process_data(
#     input_file_path='./接入数据-对话流.xlsx',
#     output_file_path='./版本_主题_对话流.xlsx'
# )

# 第二步：绘制对比图
# plot_comparison(
#     file1_path='./版本_主题_候选话术库_kicp_gpt.xlsx',
#     file2_path='./版本_主题_kicp-GPT.xlsx',
#     prefix1='候选话术库_kicp_gpt',
#     prefix2='kicp-GPT',
#     save_path='./留联率对比.jpg',
#     min_valid_conversations=5,
# )