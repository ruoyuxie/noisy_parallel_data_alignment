# -*- coding: utf-8 -*-
import json
import random
import time
import sys
import os
from tqdm import tqdm

input_file = sys.argv[1]
output_file = sys.argv[2]
prob_file = sys.argv[3]

# if the user input is not correct
if not os.path.exists(input_file):
    print("The input alignment_data file does not exist")
    print("Usage: python3 noise_adding.py <clean_input_file> <output_file> <noisy_probability_data> ")
    sys.exit()

if len(sys.argv) < 4:
    print("Please provide the correct alignment_data files")
    print("Usage: python3 noise_adding.py <clean_input_file> <output_file> <noisy_probability_data> ")
    sys.exit()

Insertion_table1 = {}
Insertion_table2 = {}
Substitution_table1 = {}
Substitution_table2 = {}

# read the probability data
with open(prob_file, 'r') as f:
    for line in f:
        line = line.strip()
        line = line.split(" = ")
        if line[0] == 'Substitution_table1':
            Substitution_table1 = line[1]
            Substitution_table1 = eval(Substitution_table1)
        elif line[0] == 'Substitution_table2':
            Substitution_table2 = line[1]
            Substitution_table2 = eval(Substitution_table2)
        elif line[0] == 'Insertion_table1':
            Insertion_table1 = line[1]
            Insertion_table1 = eval(Insertion_table1)
        elif line[0] == 'Insertion_table2':
            Insertion_table2 = line[1]
            Insertion_table2 = eval(Insertion_table2)



with open(input_file, encoding='utf-8') as inp:
    original = inp.read() # clean file

out = open(output_file, 'wb') # synthetic file

length_of_corpus = len(original)
edit_count = 0

def sub1_population_weights():
    sub1_population = []
    sub1_weights = []
    for i in Substitution_table1:
        sub1_population.append(i)
        sub1_weights.append(Substitution_table1[i])
    return sub1_population, sub1_weights

def sub_action(original):
    # choose the potential substitution from sub2 given the sub word
    sub2_population = []
    sub2_weights = []
    for i in Substitution_table2:
        temp_c = i[0]
        if original == temp_c:
            sub2_population.append(i)
            sub2_weights.append(Substitution_table2[i])
    sub_word_choice = (random.choices(sub2_population, sub2_weights, k=1))[0]

    return sub_word_choice

def ins_action(orginal):
    # choose the potential institution from ins2 given the ins word
    ins2_population = []
    ins2_weights = []
    for i in Insertion_table2:
        temp_c = i[0]
        if orginal == temp_c:
            ins2_population.append(i)
            ins2_weights.append(Insertion_table2[i])
    ins_word_choice = (random.choices(ins2_population, ins2_weights, k=1))[0]

    return ins_word_choice

for i in tqdm(original):
    new_char = i
    modify_flag = 0
    decide_error = random.random()
    pro_of_char = 0
    choice_of_sub = " "
    error_type = ' '

    #sub
    if i in Substitution_table1:
        pro_of_char = Substitution_table1[i]
        if decide_error <= pro_of_char:
            error_type = 'sub'
            choice_of_sub = sub_action(i)[1]
            edit_count +=1
            # deletion -> sub with ''
            if choice_of_sub == '':
                new_char = ''
            else:
                new_char = choice_of_sub

            modify_flag = 1


    # ins at beginning
    if (i in Insertion_table1 or i == "\n") and (modify_flag == 0) and 'begin' in Insertion_table1:
        if i == "\n":
            if decide_error <= Insertion_table1['begin'] + pro_of_char:
                error_type = 'ins'
                choice_of_ins = ins_action('begin')[1]
                new_char = new_char + choice_of_ins
                edit_count += 1

        # ins in middle
        else:
            if decide_error <= Insertion_table1[i] + pro_of_char:
                error_type = 'ins'
                choice_of_ins = ins_action(i)[1]
                new_char = new_char + choice_of_ins
                edit_count += 1

    # nothing happen to this character, just write to the out file
    if choice_of_sub != '':
        out.write(new_char.encode("utf8"))

out.close()

CER = edit_count / length_of_corpus
print("--------------------------------------------")
print("edit count:",edit_count)
print("total char:",length_of_corpus),
print("CER:", CER)
