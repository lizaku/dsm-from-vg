import json
import zipfile
from collections import Counter

PATH_OBJ = 'objects.json.zip'
PATH_REL = 'relationships.json.zip'
PATH_ATTR = 'attributes.json.zip'

def extract_rels(filepath):
    all_rels = []
    full_rels = []
    zfile = zipfile.ZipFile(filepath)
    for finfo in zfile.infolist():
        ifile = zfile.open(finfo)
        data = json.loads(ifile.read().decode('utf-8'))
        for image in data:
            for rel in image['relationships']:
                try:
                    obj = rel['object']['names']
                except:
                    try:
                        obj = [rel['object']['name']]
                    except:
                        obj = '-'
                pred = rel['predicate']
                try:
                    subj = [rel['subject']['name']]
                except:
                    try:
                        subj = rel['subject']['names']
                    except:
                        subj = '-'
                all_rels.append(pred)
                full_rels.append(', '.join(subj) + ' ' + pred + ' ' + ', '.join(obj))
    counts = Counter(all_rels)
    with open('relations_freq.txt', 'w', encoding='utf-8') as w:
        for pair in counts.most_common():
            w.write(pair[0] + '\t' + str(pair[1]) + '\n')
    with open('relations.txt', 'w', encoding='utf-8') as w:
        for rel in full_rels:
            w.write(rel + '\n')

def extract_objects(filepath):
    all_objects = []
    zfile = zipfile.ZipFile(filepath)
    for finfo in zfile.infolist():
        ifile = zfile.open(finfo)
        data = json.loads(ifile.read().decode('utf-8'))
        for image in data:
            for obj in image['objects']:
                objects = obj['names']
                all_objects.extend(objects)
    counts = Counter(all_objects)
    with open('objects_freq.txt', 'w', encoding='utf-8') as w:
        for pair in counts.most_common():
            w.write(pair[0] + '\t' + str(pair[1]) + '\n')
            
def extract_attributes(filepath):
    all_attributes = []
    full_attributes = []
    zfile = zipfile.ZipFile(filepath)
    for finfo in zfile.infolist():
        ifile = zfile.open(finfo)
        data = json.loads(ifile.read().decode('utf-8'))
        for image in data:
            for attr in image['attributes']:
                try:
                    obj = attr['names']
                except:
                    try:
                        obj = [attr['name']]
                    except:
                        obj = '-'
                try:
                    att = [attr['attribute']]
                except:
                    try:
                        att = attr['attributes']
                    except:
                        att = []
                all_attributes.extend(att)
                full_attributes.append(', '.join(att)+ ' ' + ', '.join(obj))
    counts = Counter(all_attributes)
    with open('attributes_freq.txt', 'w', encoding='utf-8') as w:
        for pair in counts.most_common():
            w.write(pair[0] + '\t' + str(pair[1]) + '\n')
    with open('attributes.txt', 'w', encoding='utf-8') as w:
        for att in full_attributes:
            w.write(att + '\n')
        
                

#extract_objects(PATH_OBJ)
#extract_rels(PATH_REL)
extract_attributes(PATH_ATTR)


