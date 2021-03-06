"""
对指定文本进行翻译质量评估
现有评估指标：
- BLEU指标

"""

from common import eval_bleu
import config.get_config as _config
from model import translator
from common import preprocess


# BLEU指标计算
def calc_bleu():
    # 导入评估文本计算BLEU
    path_to_eval_file = _config.path_to_eval_file  # 评估文本路径
    num_eval = _config.num_eval  # 用来评估的句子数量
    # 对英文句子进行预处理，中文句子不预处理,因为将用en用来翻译
    en, ch = preprocess.create_dataset(path_to_eval_file, num_eval, ch=False, en=True)
    print('开始计算BLEU指标...')
    bleu_sum = 0
    for i in range(num_eval):
        candidate_sentence = translator.translate(en[i])
        print('-' * 20)
        print('第%d个句子：' % (i + 1))
        print('Input:' + en[i])
        print('Translate:' + candidate_sentence)
        print('Reference:' + ch[i])
        bleu_i = eval_bleu.sentence_bleu(candidate_sentence, [ch[i]], ch=True)
        print('此句子BLEU:%.2f' % bleu_i)
        bleu_sum += bleu_i
    bleu = bleu_sum / num_eval
    print('-' * 20)
    print('平均BLEU指标为：%.2f' % bleu)


if __name__ == '__main__':
    pass
