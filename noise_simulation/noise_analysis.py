import numpy as np
from collections import defaultdict
import sys
import os
from tqdm import tqdm

def wagner_fischer(word_1, word_2):
    n = len(word_1) + 1  # counting empty string
    m = len(word_2) + 1  # counting empty string

    # initialize D matrix
    D = np.zeros(shape=(n, m), dtype=np.int64)
    D[:, 0] = range(n)
    D[0, :] = range(m)

    # B is the backtrack matrix. At each index, it contains a triple
    # of booleans, used as flags. if B(i,j) = (1, 1, 0) for example,
    # the distance computed in D(i,j) came from a deletion or a
    # substitution. This is used to compute backtracking later.
    B = np.zeros(shape=(n, m), dtype=[("del", 'b'),
                                      ("sub", 'b'),
                                      ("ins", 'b')])
    B[1:, 0] = (1, 0, 0)
    B[0, 1:] = (0, 0, 1)

    for i, l_1 in enumerate(word_1, start=1):
        for j, l_2 in enumerate(word_2, start=1):
            deletion = D[i - 1, j] + 1
            insertion = D[i, j - 1] + 1
            substitution = D[i - 1, j - 1] + (0 if l_1 == l_2 else 1)

            mo = np.min([deletion, insertion, substitution])

            B[i, j] = (deletion == mo, substitution == mo, insertion == mo)
            D[i, j] = mo
    return D, B

def modified_wagner_fischer(word_1, word_2):
    n = len(word_1) + 1  # counting empty string
    m = len(word_2) + 1  # counting empty string

    # initialize D matrix
    D = np.zeros(shape=(n, m), dtype=np.int64)
    D[:, 0] = range(n)
    D[0, :] = range(m)

    # B is the backtrack matrix. At each index, it contains a triple
    # of booleans, used as flags. if B(i,j) = (1, 1, 0) for example,
    # the distance computed in D(i,j) came from a deletion or a
    # substitution. This is used to compute backtracking later.
    B = np.zeros(shape=(n, m), dtype=[("del", 'b'),
                                      ("sub", 'b'),
                                      ("ins", 'b')])
    B[1:, 0] = (1, 0, 0)
    B[0, 1:] = (0, 0, 1)

    for i, l_1 in enumerate(word_1, start=1):
        for j, l_2 in enumerate(word_2, start=1):
            deletion = D[i - 1, j] + 1
            insertion = D[i, j - 1] + 1
            substitution = D[i - 1, j - 1] + (0 if l_1 == l_2 else 1)
            if l_2 == "i" or l_2 == 'y':
                insertion = D[i, j - 1] + 0.5

            mo = np.min([deletion, insertion, substitution])

            B[i, j] = (deletion == mo, substitution == mo, insertion == mo)
            D[i, j] = mo
    return D, B

def naive_backtrace(B_matrix):
    i, j = B_matrix.shape[0] - 1, B_matrix.shape[1] - 1
    backtrace_idxs = [(i, j)]

    while (i, j) != (0, 0):
        if B_matrix[i, j][1]:
            i, j = i - 1, j - 1
        elif B_matrix[i, j][0]:
            i, j = i - 1, j
        elif B_matrix[i, j][2]:
            i, j = i, j - 1
        backtrace_idxs.append((i, j))

    return backtrace_idxs

diff_table = {}
search_table = {}
pre_insert_table = {}
total_num_chars=0
insert_table1 = {}
insert_table2 = {}

def align(word_1, word_2, bt):

    global total_num_chars

    aligned_word_1 = []
    aligned_word_2 = []
    operations = []
    backtrace = bt[::-1]  # make it a forward trace

    for k in range(len(backtrace) - 1):
        i_0, j_0 = backtrace[k]
        i_1, j_1 = backtrace[k + 1]

        w_1_letter = None
        w_2_letter = None
        op = None

        if i_1 > i_0 and j_1 > j_0:  # either substitution or no-op
            if word_1[i_0] == word_2[j_0]:  # no-op, same symbol
                w_1_letter = word_1[i_0]
                w_2_letter = word_2[j_0]
                op = " "
            else:  # cost increased: substitution
                w_1_letter = word_1[i_0]
                w_2_letter = word_2[j_0]
                op = "s"
        elif i_0 == i_1:  # insertion
            w_1_letter = " "
            w_2_letter = word_2[j_0]
            op = "i"

        else:  # j_0 == j_1,  deletion
            w_1_letter = word_1[i_0]
            w_2_letter = " "
            op = "d"

        aligned_word_1.append(w_1_letter)
        aligned_word_2.append(w_2_letter)
        operations.append(op)


        if op != " ":
            if op =="i":
                temp_c = word_2[j_0-1]
                if len(aligned_word_2) == 1:
                    temp_c = 'begin'
                if temp_c not in insert_table2:
                    insert_table2[temp_c] =1
                elif temp_c in insert_table2:
                    insert_table2[temp_c] +=1

                if ((temp_c,w_2_letter) not in pre_insert_table):
                    if temp_c == 'begin':
                        pre_insert_table['begin', w_2_letter] = 1
                        insert_table1['begin'] = 1
                    else:
                        pre_insert_table[temp_c,w_2_letter] = 1
                        insert_table1[temp_c] = 1

                else:
                    if temp_c == 'begin':
                        pre_insert_table['begin', w_2_letter] += 1
                        insert_table1['begin'] += 1
                    else:
                        pre_insert_table[temp_c, w_2_letter] += 1
                        insert_table1[temp_c] += 1

        if op != " ":
            if op == "d":
                if (w_1_letter, '') not in diff_table:
                    diff_table[w_1_letter, ''] = 1
                else:
                    diff_table[(w_1_letter, '')] += 1
            else:
                if (w_1_letter,w_2_letter) not in diff_table:
                    diff_table[(w_1_letter,w_2_letter)]= 1
                else: diff_table[(w_1_letter, w_2_letter)] += 1

            if w_1_letter not in search_table :

                search_table[w_1_letter] = 1
                total_num_chars = len(corpus) - corpus.count('\n')
            else: search_table[w_1_letter] +=1

    return aligned_word_1, aligned_word_2, operations

# read the user input for parallel alignment_data file
input_file = sys.argv[1]
output_file = sys.argv[2]

# if the user input is not correct
if not os.path.exists(input_file):
    print("The alignment_data file does not exist")
    print("Usage: python3 noise_analysis.py <alignment_data file> <output probability file>")
    sys.exit()

# make sure the input file is given
if len(sys.argv) < 3:
    print("Please provide the correct path to the alignment_data file")
    print("Usage: python3 noise_analysis.py <alignment_data file> <output probability file>")
    sys.exit()

with open(input_file, encoding="utf-8") as inp: # both side, clean ||| nosiy
    lines = inp.readlines()

corpus = ''
for s in lines:
    tem = s.split('|||')
    corpus += (tem[0].strip() + '\n')
corpus = corpus.rstrip()


costsum = 0
count = 0
count2 = 0

max_list = []
min_list = []

insert_counts = defaultdict(lambda: 0)
delete_counts = defaultdict(lambda: 0)
sub_counts = defaultdict(lambda: 0)

modified_cost = 0

found = False
for i, l in tqdm(enumerate(lines)):
    l = l.strip().split('|||')
    eng = l[0].strip()
    kin = l[1].strip()
    if eng.isdigit() or kin.isdigit():
        continue
    count += 1

    D, B = wagner_fischer(eng, kin)
    Dm, Bm = modified_wagner_fischer(eng, kin)
    bt = naive_backtrace(B)
    cost = D[-1, -1]

    alignment_table = align(eng, kin, bt)

    s1 = alignment_table[0]
    s2 = alignment_table[1]
    s3 = alignment_table[2]
    for c1, c2, c3 in zip(s1, s2, s3):
        if c3 == 'i':
            insert_counts[c2] += 1
        elif c3 == 'd':
            sub_counts[c1, ""] += 1
        elif c3 == 's':
            sub_counts[c1, c2] += 1

    costsum += cost
    modified_cost += Dm[-1, -1]
    if cost == 10:
        max_list.append((eng, kin))
    if cost == 0:
        min_list.append((eng, kin))


print(f"Total words: {count}")
print(f"Average edit distance: {costsum / count}")

print("Number of times a character is inserted:")
for key in insert_counts:
    print(f"\t{key}: {insert_counts[key]}")

print(f"Number of words with maximum edit distance: {len(max_list)}")
# for k in max_list:
#	print(f"{k[0]} ||| {k[1]}")

print(f"Number of words with minimum edit distance: {len(min_list)}")

print(f"Average modified edit distance: {modified_cost / count}")

total_del =0
total_ins =0
total_sub =0
for x in delete_counts:
    total_del = total_del +delete_counts[x]
for x in insert_counts:
    total_ins = total_ins +insert_counts[x]
for x in sub_counts:
    total_sub = total_sub +sub_counts[x]

char_in_sub = {}
for key in sub_counts:
    c = key[0]
    num_of_c = corpus.count(c)
    if num_of_c != 0:
        pro = sub_counts[key] / num_of_c
    if c not in char_in_sub:
        char_in_sub[c] = pro
    else: char_in_sub[c] +=pro

total_edit = total_del+total_ins+total_sub

pro_table_sub = {} # ("something" -> "some other thing")
pro_table_ins = {} # (" " -> "something")
pro_of_sub = total_sub/total_edit
pro_of_ins = total_ins/total_edit
# pro_of_del = total_del/total_edit
pro_of_edit = total_edit/total_num_chars

for s in sub_counts:
    ch1 = [s][0]
    pro1 = diff_table[ch1] / search_table[ch1[0]]
    pro_table_sub[ch1] = pro1

for s1 in insert_table2:
    if s1 == 'begin':
        pro2 = insert_table2[s1] / (corpus.count('\n')+1)
    else:
        num_of_s1 = corpus.count(s1)
        if num_of_s1 != 0:
            pro2 =  insert_table2[s1]/ num_of_s1
        if num_of_s1 == 0:
            print(s1)
    pro_table_ins[s1] = pro2

pro_pre_insert_table = {}
for i in pre_insert_table:
    temp_c = i[0]
    if temp_c == 'begin':
        pro = pre_insert_table[i] / insert_table2[temp_c]
    else:
        pro = pre_insert_table[i] / insert_table2[temp_c]
    pro_pre_insert_table[i] =pro

print("\nTotal number of edited characters:           ", total_edit)
print("Total number of character:                   ", total_num_chars)
print("Number of times a character is substituted:  ", total_sub)
print("Number of times a character is inserted:     ", total_ins)

print("\nSubstitution_table1 = ",char_in_sub)
print("Substitution_table2 = ",pro_table_sub)
print("Insertion_table1    = ",pro_table_ins)
print("Insertion_table2    = ",pro_pre_insert_table)

# write the char_in_sub, pro_table_sub, pro_table_ins, pro_pre_insert_table to a file
with open(output_file, 'w', encoding="utf-8") as out:
    out.write("Substitution_table1 = " + str(char_in_sub) + " \n")
    out.write("Substitution_table2 = " + str(pro_table_sub) + " \n")
    out.write("Insertion_table1    = " + str(pro_table_ins) + " \n")
    out.write("Insertion_table2    = " + str(pro_pre_insert_table) + " \n")



print("\nProbability_of_getting_edited=   ", pro_of_edit)
print("Probability_of_substitution=     ", pro_of_sub)
print("Probability_of_insertion=        ", pro_of_ins)




