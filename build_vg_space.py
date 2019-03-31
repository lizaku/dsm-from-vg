import re
import numpy as np
from nltk.corpus import wordnet as wn
import sys
import os
import argparse

minfreq = 50    #Min frequency of predicates 

def read_entities(path):
    entities = {}
    with open(path + os.sep + "entities.txt") as f:
        lines = f.read().splitlines()
    for pair in lines:
        eid,etype = pair.split()
        entities[eid] = etype
    return entities

def write_dictionary(m, filename):
    f = open(filename,'w',encoding='utf-8')
    for k,v in m.items():
       v_string = ' '.join([str(val) for val in v])
       f.write('%s %s\n' %(k,v_string))
    f.close()

def write_numpy_matrix(m,i_to_predicates,filename):
    f = open(filename,'w',encoding='utf-8')
    for i,p in i_to_predicates.items():
       row = p
       v_string = ' '.join([str(val) for val in m[i]])
       f.write('%s %s\n' %(p,v_string))
    f.close()

def make_predicates(path, use_attributes, use_relations, use_hypernyms, use_situations):
    predicate_count = 0
    i_to_predicates = {}
    predicates_to_i = {}
    
    def record_predicates(filename, predicate_count):
        with open(filename) as f:
            lines = f.read().splitlines()
        for pair in lines:
            pred,freq = pair.split('\t')
            if int(freq) > minfreq:
                if use_hypernyms == 'True':
                    try:
                        hypernym = wn.synset(pred).hypernyms()[0].name()
                    except:
                        hypernym = None
                    if hypernym and hypernym not in predicates_to_i:
                        i_to_predicates[predicate_count] = hypernym
                        predicates_to_i[hypernym] = predicate_count
                        predicate_count += 1
                if pred not in predicates_to_i:
                    i_to_predicates[predicate_count] = pred
                    predicates_to_i[pred] = predicate_count
                    predicate_count+=1
        return predicate_count
        
    predicate_count = record_predicates(path + os.sep + "synset_freqs.txt", predicate_count)
    if use_attributes == 'True':
        predicate_count = record_predicates(path + os.sep + "attribute_freqs.txt", predicate_count)
    if use_relations == 'True':
        predicate_count = record_predicates(path + os.sep + "relation_freqs.txt", predicate_count)
    return i_to_predicates, predicates_to_i


def aggregation(entity_matrix, inverse_entity_matrix, predicates_to_i):
    size = len(entity_matrix.keys())
    predicate_matrix = np.zeros((size,size))
    for pred,entities in entity_matrix.items():
        for e in entities:
            e_preds = inverse_entity_matrix[e]
            for e_pred in e_preds:
                predicate_matrix[predicates_to_i[pred]][predicates_to_i[e_pred]]+=1
    return predicate_matrix


def prob_interpretation(predicate_matrix):
    prob_matrix = np.zeros(predicate_matrix.shape)
    for i in range(predicate_matrix.shape[0]):
        prob_matrix[i] = predicate_matrix[i] / predicate_matrix[i][i]
    return prob_matrix

def build_space(parameters):
    use_attributes = parameters["use_attributes"]
    use_relations = parameters["use_relations"]
    use_hypernyms = parameters["use_hypernyms"]
    use_situations = parameters["use_situations"]
    path = parameters["path"]
    if not os.path.exists(path):
        os.mkdir(path)

    print("Reading entity record...")
    entities = read_entities(path)
    print("Reading predicate record... keeping predicates with frequency >",minfreq,"...")
    i_to_predicates, predicates_to_i = make_predicates(path, use_attributes=use_attributes,
                                                   use_relations=use_relations,
                                                   use_hypernyms=use_hypernyms,
                                                   use_situations=use_situations)

    print("Processing ideal language... This will take a few minutes...")
    with open(path + os.sep + "vg_parsed.txt") as f:
        lines = f.read().splitlines()

    eid = ''
    entity_matrix = {}
    inverse_entity_matrix = {}
    processed_ids = set()

    if use_situations == 'True':
        entities_together = {}
        together = set()
        for l in lines:
            if "<situation" in l:
                if len(together) > 1:
                    for e in together:
                        if e not in entities_together:
                            entities_together[e] = together
                        else:
                            entities_together[e] = entities_together[e].union(together)
                together = set()
            if "<entity" in l:
                m = re.search('entity id=(.*)>', l)
                if m:
                    eid = m.group(1)
                    together.add(eid)

    for l in lines:
        if "<entity" in l:
            m = re.search('entity id=(.*)>',l)
            if m:
                eid = m.group(1)
                inverse_entity_matrix[eid] = []
        if ".n." in l:
            m = re.search('(\S*\.n\.[0-9]*)\(([0-9]*)\)',l)
            if m.group(2) == eid:
                synset = m.group(1)
            
                if use_hypernyms == 'True':
                    try:
                        hypernym = wn.synset(synset).hypernyms()[0].name()
                    except IndexError:
                        hypernym = None
                    if hypernym in predicates_to_i:
                        if hypernym in entity_matrix:
                            entity_matrix[hypernym].append(eid)
                        else:
                            entity_matrix[hypernym] = [eid]
                        inverse_entity_matrix[eid].append(hypernym)
                    
                if use_situations == 'True':
                    try:
                        for neigh in entities_together[eid]:
                            if neigh != eid and neigh not in processed_ids:
                                etype = entities[neigh]
                                if etype in predicates_to_i:
                                    if etype in entity_matrix:
                                        entity_matrix[etype].append(eid)
                                    else:
                                        entity_matrix[etype] = [eid]
                                    inverse_entity_matrix[eid].append(etype)
                                processed_ids.add(neigh)
                    except:
                        pass
            
                if synset in predicates_to_i:
                    if synset in entity_matrix:
                        entity_matrix[synset].append(eid)
                    else:
                        entity_matrix[synset] = [eid]
                    inverse_entity_matrix[eid].append(synset)
                
        if ".n." not in l:
            m = re.search('(\S*)\(([0-9]*)\)',l)
            if m and m.group(2) == eid:
                att = m.group(1)
                if att in predicates_to_i:
                    if att in entity_matrix:
                        entity_matrix[att].append(eid)
                    else:
                        entity_matrix[att] = [eid]
                    inverse_entity_matrix[eid].append(att)
            m = re.search('(\S*)\(([0-9]*),([0-9]*)\)',l)
            if m:
                if m.group(2) == eid:
                    relation = m.group(1)+'(-,'+entities[m.group(3)]+')'
                if m.group(3) == eid:
                    relation = m.group(1)+'('+entities[m.group(2)]+',-)'
                if relation in predicates_to_i:
                    if relation in entity_matrix:
                        entity_matrix[relation].append(eid)
                    else:
                        entity_matrix[relation] = [eid]
                    inverse_entity_matrix[eid].append(relation)
        

    write_dictionary(entity_matrix, path + os.sep + "entity_matrix.dm")

    predicate_matrix = aggregation(entity_matrix,inverse_entity_matrix, predicates_to_i)
    write_numpy_matrix(predicate_matrix, i_to_predicates, path + os.sep + "predicate_matrix.dm")

    prob_matrix = prob_interpretation(predicate_matrix)
    write_numpy_matrix(prob_matrix, i_to_predicates, path + os.sep + "probabilistic_matrix.dm")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path",
                        help="Path to the parsed files of the VG")
                        
    parser.add_argument("--use_attributes",
                        help="Whether to use attributes of objects in the Visual Genome annotation, True or False",
                        default="True")

    parser.add_argument("--use_hypernyms",
                        help="Whether to use hypernyms of objects in the Visual Genome annotation, extracted from WordNet, True or False",
                        default="True")

    parser.add_argument("--use_relations",
                        help="Whether to use relations between objects in the Visual Genome annotation, True or False",
                        default="True")

    parser.add_argument("--use_situations",
                        help="Whether to use objects cooccurrences within situations in the Visual Genome annotation, True or False",
                        default="True")

    args = parser.parse_args()

    build_space({
        "use_attributes": args.use_attributes.lower() == "true",
        "use_hypernyms": args.use_hypernyms.lower() == "true",
        "use_relations": args.use_relations.lower() == "true",
        "use_situations": args.use_situations.lower() == "true",
        "path": args.path
    }

