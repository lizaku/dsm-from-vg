import sys
sys.path.append('..')
import utils
from scipy.stats import spearmanr

dm_dict = utils.readDM(sys.argv[1])
eval_dataset = sys.argv[2]
system = []
gold = []
if eval_dataset == 'men':
    lines = open("MEN_dataset_lemma_form_full",'r')
    sep = ' '
elif eval_dataset == 'simlex':
    with open("SimLex-999.txt",'r') as f:
        lines = f.read().splitlines()[1:]
    sep = '\t'

for l in lines:
    fields = l.rstrip('\n').split(sep)
    w1 = fields[0][:-2]
    w2 = fields[1][:-2]
    score = float(fields[2])
    if w1 in dm_dict and w2 in dm_dict:
        try:
            cos = utils.cosine_similarity(dm_dict[w1],dm_dict[w2])
            system.append(cos)
            gold.append(score)
            print(w1,w2,cos,score)
        except:
            continue
f.close()

print("SPEARMAN:",spearmanr(system,gold))
print("("+str(len(system))+" pairs out of the original 3000 could be processed, due to vocabulary size.)")
