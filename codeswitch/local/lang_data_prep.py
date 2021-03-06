#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import codecs
import re
import os

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

#### default file structure ####
# put this file under the local folder (codeswitch/local)
# put two dictionaries (cmu one and TH one) under the local folder (codeswitch/local)
# have the unziped corpus folder under the main folder (so you have codeswitch/LDC2015S04/seame_d1/data/conversation/transcript/ etc.)
# have the essential folders made. here we need codeswitch/data/local/lang/

parent_path = os.path.split(os.getcwd())[0]
test_short_ids_i = ['01MA', '03FA','08MA', '29FA','29MB','42FB','44MB','45FB','67MB','55FB']
test_short_ids_c = ['01NC01FB', '01NC02FB','06NC11MA', '06NC12MA']

#### settings ####
dirs = ['/LDC2015S04/seame_d1/data/conversation','/LDC2015S04/seame_d2/data/interview']
oldfolder = '/transcript/'
newfolder = '/transcript_filtered/'
dir_lang = '/data/local/lang/'
dir_dicsource = ''



#### functions ####
# modified from https://segmentfault.com/q/1010000000732038
# to detect english character and hyphen and ' and . ONLY
def isAlphahyphen(word):
    try:
        float(word)
        return True
    except:
        if word == '-':
            return True
        elif word == "'":
            return True
        elif word == "'":
            return True   
        else:
            try:
                return word.replace('-','').replace("'",'').replace('.','').encode('ascii').isalnum()
            except UnicodeEncodeError:
                if word == '-':
                    return True
                else:
                    return False
   
        
# copied from http://www.cnblogs.com/kaituorensheng/p/3554571.html
def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 12288:                              #全角空格直接转换            
            inside_code = 32 
        elif (inside_code >= 65281 and inside_code <= 65374): #全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring
    
# split chinese words concatenated with english words
# input a pure chinese string or english string (adapted to - or ') will return itself
# output: a list of split words
def splitMix(word):
    res = []
    idx_b = 0
    for i in range(len(word)):
        if i == 0:
            char_b = isAlphahyphen(word[i])
        else:
            if char_b == isAlphahyphen(word[i]):
                next
            else:
                char_b = isAlphahyphen(word[i])
                res += [word[idx_b:i]]
                idx_b = i
    res += [word[idx_b:]]
    return res    

    
def oov(words_all_uniq,d_cmu,d_th):
    d = dict()
    words_oov_english = []
    words_oov_chinese = []
    for word in words_all_uniq:
        try:
            d[word] = d_cmu[word]
            for i in range(1,max_num+1):
                try:
                    d[word+"(i)"] = d_cmu[word+"(i)"]
                except:
                    break
        except:
            try:
                d[word] = d_th[word]
            except:
                if isAlphahyphen(word):
                    words_oov_english += [word]
                else:
                    words_oov_chinese += [word]
                continue
    return d,words_oov_english,words_oov_chinese
    
    
#### read lexicons ####
filename_cmu = "cmudict-0.7b"
d_cmu = dict()
max_num = 0 # max number of (x) <-- a word with multiple pronunciations
f = open(dir_dicsource+filename_cmu,"r")
for line in f.readlines():
    if line[0:3] != ";;;":
        line = line[:-1]
        line = line.split("  ",1)
        d_cmu[line[0]] = line[1]
        if line[0][-1] == ")":
            try: 
                num_cur = int(line[0][-2])      
                if int(line[0][-2]) > max_num:
                    max_num = num_cur
            except:
                continue

print("Finish loading cmu dictionary")
print("Number of English lexicon: " + str(len(d_cmu)))


filename_th = "thchs30-lexicon.txt"
d_th = dict()
with codecs.open(dir_dicsource+filename_th, 'r', 'utf-8') as f:
    for line in f.readlines():
        line = line.split()
        d_th[line[0]] = ' '.join(line[1:])
print("Finish loading thchs30 dictionary")
print("Number of Chinese lexicon: " + str(len(d_th)))


#filename_ce = "cedict_1_0_ts_utf-8_mdbg.txt"
#
#d_ce = dict()
#with codecs.open(filename_ce, 'r', 'utf-8') as f:
#    for line in f.readlines():
#        if line[0] != "#":
#            line = line.split()
#            d_ce[line[1]] = re.findall(r'''\[(.+?)\]''', ' '.join(line[2:]))
#print("Finish loading thchs30 dictionary")
#print("Number of Chinese lexicon: " + str(len(d_ce)))


#### update lexicon ####

english_part1 = ['DEATH','CITY','JACK','ROBO','RED','RED','SOCIO','PSYCHO','PSYCHO','PSYCHO','UN','UN','UN','UN',
                'NET','TROUBLE','QUEENS','WIND','HAND','MAT','PSYCHO','TORCH','KUNG','NORTH','NORTH','TIME','EASY',
                'TELE','CAR','POST','HOUSE','BLOG','GREY','GRAY','TIME','MOON','JOB','MAY','HOME','WEB','HYPER','BACK','BACK',
                'SNOW','BIO','BIO','HOT','ROBO','DRAGON','DREAM','HERBAL','NET','ROAD','CUT','COURSE','WIND','PHOTO',
                'SOFT','BLUE','FOUR','WAKE','GROUP','BACK','SKIN','PRE','SHORT','SHORT','MAL','MEDIA','UN','PHOTO','COURSE',
                'SUN','CLUB','UN','CYBER','IN','GROUP','NON','NEWS','MEGA','COS','GOOGLE','DIFFERENT','INTER','EMOTION',
                'HOUSE','IN','IN']
english_part2 = ['NOTE','HALL','FRUIT','CUP','HILL','BOX','LINGUISTICS','LINGUISTIC','LINGUISTICS','MOTOR','INSTALL','INSTALLED','BLOCK','FRUITFUL',
                'BOOK','SHOOT','BAY','SCREEN','PHONE','LAB','METRIC','LIGHT','FU','VILLE','POINT','FLOW','LINK',
                'GRAPHIC','PARK','DOC','MATES','SPOT','SCALE','SCALE','SLOT','CAKE','STREET','BANK','PAGE','MAIL','TRADING','STAB','STABBING',
                'BOARDING','INFORMATICS','PLASTIC','MAIL','SOCCER','BOAT','WEAVER','LIFE','BALL','MAP','LET','WORK','SURF','SHOOT',
                'COPY','RAY','DAYS','BOARDING','MATE','STREET','FOOD','ORDER','LISTING','LISTED','FUNCTIONAL','CORP','COUNTABLE','SKIP','MATE',
                'WAY','SNAP','SOLVE','JAVA','BOX','MATES','SPEECH','WRITING','WALL','PLAY',"'S","'S",'SPEECH','LESS',
                'FLY','CHARGED','DEPTH']

for a,b in zip(english_part1,english_part2):
    d_cmu[(a+b)] = d_cmu[a]+" " +d_cmu[b]
    #print(a+b+": "+d_cmu[(a+b)])

print("Finish creating new words by concatenating existent words in English dictionary")
print("Number of English lexicon now: " + str(len(d_cmu)))

'''
chinese_part1 = ['每个','小','早','上','讲','有','整','名','进','进','每','这','那','就','之','不','算','有','去','做','就',
                '读','明','开','第','在','有','有','打','三','毕','不','过','整','八','比如','这','浪','女','过','前','靠',
                '对','不','小','是','要']
chinese_part2 = ['人','时','上','面','话','没有','个','字','来','去','次','边','边','可以','前','一样','是','什么','了','工','在',
                '书','年','心','一个','那边','一点','很多','算','年','业','可以','了','天','点','说','样子','费','生','来','面','近',
                '不对','可能','时候','不是','不要']

for a,b in zip(chinese_part1,chinese_part2):
    print(d_th[a]+" " +d_th[b])
    d_th[(a+b)] = d_th[a]+" " +d_th[b]
    #print(a+b+": "+d_th[(a+b)])

print("Finish creating new words by concatenating existent words in Chinese dictionary")
print("Number of English lexicon now: " + str(len(d_th)))
'''


#### waste word collection ####
# to get the full word list
words = []
for dir in dirs:
    filenames = os.listdir(parent_path+dir+oldfolder)
    for filename in filenames:
        if filename[-4:] == ".txt":
            with codecs.open(parent_path+dir+oldfolder+filename, 'r', 'utf-8') as f:
                for line in f.readlines():
                    sentence = line.split() # 1st element -- audio file id, 2nd element -- start time, 3rd element -- end time
                    words_cur = sentence[3:]   
                    words += words_cur
                f.close()

print("Finish concatenating words")
print("Number of words: " + str(len(words)))
print("Number of unique words: " + str(len(set(words))))

# create a dictionary of waste words
words_waste = []
words_1 = [] # [x]
words_2 = [] # (x)
        
for word in words:
    if word[-1] == "]" or word[0] == "[":
        word = re.findall(r'''(\[.+?\])''',word)
        words_1 += word
    elif word[-1] == ")" or word[0] == "(":
        word = re.findall(r'''(\(.+?\))''',word)
        words_2 += word
        
words_waste = words_1 + words_2

d_waste = dict()
for word in words_waste:
    try:
        d_waste[word] += 1
    except:
        d_waste[word] = 1

d_waste2idx = dict()
idx = -1
for k in d_waste.keys():
    idx += 1
    #d_waste2idx[k] = 'SIL' + str(idx)
    
    if k[0] == '(':
        d_waste2idx[k] = 'SIL1'
    elif k[0] == '[':
        d_waste2idx[k] = 'SIL2'
    

d_idx2waste = {v:k for k,v in d_waste2idx.items()}

print("Finish creating waste word dictionary")
print("Number of waste word type: " + str(len(set(words_waste))))


#### correct misspelling ####

mis_ori = ['ADMINISTATOR','AVALABLE','BELIEVEABLE','BULETIN','COMPLUSORY','CONTINUOS','DISSAPOINT','EMBARASSING','EXHIBITON','FULFIL','INTENATIONAL','INSTRUNMENT','SINAGPORE','STEALL','SYCHOLOGY','YOGHURT','GITAR','NEWTWORK','DONT','UNIVERSITI','BUBLE','ACTIVTIES','INSTITUITION','LAB.','WHEAREAS','PERMANET','ORIENTAION','EFFICICIENT','MULITPLED','POLLUTATNTS','THAILLAND','CRYSTALIZED','TOLIET','ENGINEEERING','EXPEIMENTAL','CONCIOUSLY',
           'PRACTISING','COTENT','DORMITRIES','OCCATION','AUTHORISATION','PROGRAMMES','CINDERALLA','GOVERNENMENT','HABOUR','ORIENATION','NEWPAPER','RESEULT','DEPAND','EQUIMENT','VENTERAN','DEGREDATION','POSTDOC.','COLLEGUE','FAS','STOLVE','LEAPARD','NEWSCASTLE','FEND',
           'AUTHORISE','CATEGORISE','CENTRALISED','DEVELOPE','FLAVOURS','FLAVOURFUL','FINALISED','SUBSIDISE','ORGANISING','ORGANISES','ORGANISATIONAL','SPECIALISATION','SPECIALISATIONS','SPECIALISED','UTILISE','DEMORALISED','COLOURFUL','SOCIALISE','MEMORISE','PRIORITISE','ANALYSE','STANDARDISED','DEVELOPEMENT','EAZY','FLAVOURED','OPTIMISE','CONVENTIONALISED','STOREYS','HONOURS','ORGANISE','HOSPITALISED','CRITICISE', 'SPECIALISE',
           'EMPHASISE',
           'VOCALISE','ORGANICE','INDOEUROPEAN',
           '1','2','3','4']

mis_fix = ['ADMINISTRATOR','AVAILABLE','BELIEVABLE','BULLETIN','COMPULSORY','CONTINUOUS','DISAPPOINT','EMBARRASSING','EXHIBITION','FULFILL','INTERNATIONAL','INSTRUMENT','SINGAPORE','STEAL','PSYCHOLOGY','YOGURT','GUITAR','NETWORK',"DON'T",'UNIVERSITY','BUBBLE','ACTIVITIES','INSTITUTION','LAB','WHEREAS','PERMANENT','ORIENTATION','EFFICIENT','MULTIPLIED','POLLUTANTS','THAILAND','CRYSTALLIZED','TOILET','ENGINEERING','EXPERIMENTAL','CONSCIOUSLY',
           'PRACTICING','CONTENT','DORMITORIES','OCCASION','AUTHORIZATION','PROGRAMS','CINDERELLA','GOVERNMENT','HARBOR','ORIENTATION','NEWSPAPER','RESULT','DEPEND','EQUIPMENT','VETERAN','DEGRADATION','POSTDOC','COLLEAGUE','GAS','STOVE','LEOPARD','NEWCASTLE','FUND',
           'AUTHORIZE','CATEGORIZE','CENTRALIZED','DEVELOP','FLAVORS','FLAVORFUL','FINALIZED','SUBSIDIZE','ORGANIZING','ORGANIZES','ORGANIZATIONAL','SPECIALIZATION','SPECIALIZATIONS','SPECIALIZED','UTILIZE','DEMORALIZED','COLORFUL','SOCIALIZE','MEMORIZE','PRIORITIZE','ANALYZE','STANDARDIZED','DEVELOPMENT','EASY','FLAVORED','OPTIMIZE','CONVENTIONALIZED','STORIES','HONORS','ORGANIZE','HOSPITALIZED','CRITICIZE', 'SPECIALIZE',
           'EMPHASIZE',
           'VOCALIZE','ORGANIZE','INDO-EUROPEAN',
           'one','two','three','four']

d_mis2fix = {k:v for k,v in zip(mis_ori,mis_fix)}


#### to collect SIL words without [] or () ####

waste_detect_1 = ['PPB','PPC','PPL','PPO']
waste_detect_2 = ['ORH','ORR','AR','ARR','EH','EM','EMM','ERR','ERM','HOR','HORR','LORH',
                  'ER','LA','LEH','LOR','LAH','MEH',
                  #'ERRR',
                  'ORK']


#### fix, filter, output text transcript ####
# fix and output the transcript text going to be used
words_all = []
words_train = []
words_test = []
text_all = []
text_train = []
text_test = []
text_unparse = []

time_all = 0
time_train = 0
time_test = 0



for dir in dirs:
    if "conversation" in dir:
        test_id = test_short_ids_c
    elif "interview" in dir:
        test_id = test_short_ids_i
        
    filenames = os.listdir(parent_path+dir+oldfolder)
    for filename in filenames:
        if filename[-4:] == ".txt":
            with codecs.open(parent_path+dir+oldfolder+filename, 'r', 'utf-8') as f:
                text = []

                for line in f.readlines():
                    sentence_origin = line.strip()
                    sentence_origin += " " # to better detect and fix the last word
                
                    # deal with situations like 'co[mm]on' and 'co[mm]unication'
                    words_mm_cur = set(re.findall(r'''o(\[.+?\])''',line))
                    if len(words_mm_cur) > 0:
                        sentence_origin = sentence_origin.replace('o[mm]','omm')
                
                    # replace waste words with SILx; space after ] or before [ to avoid situations like co[mm]on or co[mm]unication
                    words_waste_cur = set(re.findall(r'''(\[.+?\])''',line) + re.findall(r'''(\(.+?\))''',line))
                    for element in words_waste_cur:
                        if element in ['[ppb]','[ppl]','[ppc]','[ppo]']:
                            element.replace('[','(').replace(']',')')
                        try:
                            sentence_origin = sentence_origin.replace(element,' ' + d_waste2idx[element] + ' ')
                        except:
                            continue

                    # Q2B
                    sentence_chars = list(sentence_origin)
                    for char_idx in range(len(sentence_chars)):
                        sentence_chars[char_idx] = strQ2B(sentence_chars[char_idx])
                    sentence_origin = "".join(sentence_chars)

                    # split chinese words concatenated with english words
                    words_fix = []
                    info_cur = sentence_origin.split()[:3]
                    words_cur = sentence_origin.split()[3:]
                    for word_cur in words_cur:
                        word_cur = splitMix(word_cur)
                        if isinstance(word_cur,list):
                            words_fix += word_cur
                        else:
                            words_fix += [word_cur]                
                    sentence_origin = " ".join(info_cur+words_fix)        
                            
                    # get rid of "#"
                    # get rid of "="
                    # deal with %word% like %chelsia%
                    # deal with "word" like "william"
                    # cancel: deal with pronunciation of single letter, for which the trascript is like P. S., I. T., etc. --> this is how cmu dictionary documents them
                    # deal with a single period ' .'
                    # deal with x.y. like u.s.
                    # deal with [ chinese char ] like [ 啊 ]
                    sentence_origin = sentence_origin.replace('#',' ').replace('=',' ').replace('%',' ').replace('"',' ').replace(' .',' ').replace('.','. ').replace('[',' ').replace(']',' ')
                     
                    # correct misspelling phrases
                    sentence_origin = sentence_origin.replace(' abit ',' a bit ').replace('\tabit',' a bit ')
                    sentence_origin = sentence_origin.replace(' aboutforensic ',' about forensic ')
                    sentence_origin = sentence_origin.replace(' somemore ',' some more ')
                    sentence_origin = sentence_origin.replace('orang-utan',' orangutan ')
                    '''
                    sentence_origin = sentence_origin.replace('它是','它 是')
                    sentence_origin = sentence_origin.replace('你是','你 是')
                    sentence_origin = sentence_origin.replace('他是','他 是')
                    sentence_origin = sentence_origin.replace('她是','她 是')
                    sentence_origin = sentence_origin.replace('我是','我 是')
                    sentence_origin = sentence_origin.replace('这是','这 是')
                    sentence_origin = sentence_origin.replace('我在','我 在')
                    sentence_origin = sentence_origin.replace('他在','他 在')
                    sentence_origin = sentence_origin.replace('我们是','我们 是')
                    sentence_origin = sentence_origin.replace('他们是','他们 是')
                    sentence_origin = sentence_origin.replace('的时候','的 时候')
                    sentence_origin = sentence_origin.replace('我觉得','我 觉得')
                    sentence_origin = sentence_origin.replace('是一个','是 一个')
                    sentence_origin = sentence_origin.replace('是什么','是 什么')
                    sentence_origin = sentence_origin.replace('也没有',' 也 没有')
                    '''
                    
                    # remove pounctuation
                    sentence_origin = sentence_origin.replace('?',' ').replace(')',' ').replace(' - ',' ')

                    
                    # trim again incase the substitution brings in space
                    sentence_origin = sentence_origin.strip()
                              
                    sentence = sentence_origin.split() # 1st element -- audio file id, 2nd element -- start time, 3rd element -- end time
                    info_cur = sentence[:3] # idx: 0~2
                    words_cur = sentence[3:] # idx: 3~
                    unparse = False
    
                    for word in words_cur: # filter out concatenated characters having Chinese characters, with length over 4
          
                        # filter out unsegmented element (unparse = F -> unparse = T)
                        # for example, [leh]每次上学的时候daddy都会买糕点给我吃买马来糕#kuih# (idx: 53628)
                        if not isAlphahyphen(word): 
                            try:
                                d_th[word] # if the word is a recorded Chinese word
                                continue
                            except:
                                if len(word) > 4:
                                    unparse = True
                                    break

                    if unparse:
                        text_unparse += [sentence_origin]
                    else:
                        # split chinese words into characters if not in dictionary to decrease oov rate
                        words_cur_fix = []
                        for word_cur in words_cur:
                            word_cur = word_cur.upper()
                            if not isAlphahyphen(word_cur): # if is not a english word
                                try:
                                    d_th[word_cur]
                                    words_cur_fix += [word_cur]
                                except:
                                    if len(word_cur)>1: # if length of word > 1, or more than 1 chinese character
                                        needtosplit = True
                                        for char_idx in range(len(word_cur)):
                                            words_cur_fix += word_cur[char_idx]
                                    else: # if only has one chinese character
                                        words_cur_fix += [word_cur]                                            
                            else: # if is not chinese word
                                if '-' in word_cur:
                                    try:
                                        d_cmu[word_cur]
                                        words_cur_fix += [word_cur]
                                    except:
                                        word_cur = word_cur.split('-') 
                                                                         
                                        for i in range(len(word_cur)):
                                            try:
                                                word_cur[i] = d_mis2fix[word_cur[i]]
                                            except:
                                                word_cur[i] = word_cur[i]   
                                                                        
                                        words_cur_fix += word_cur
                                else:
                                    # to collect SIL phones without [] or ()
                                    if word_cur in waste_detect_1:
                                        word_cur = d_waste2idx[('('+word_cur.lower()+')')]
                                    elif word_cur in waste_detect_2:
                                        word_cur = d_waste2idx[('['+word_cur.lower()+']')]
                                        
                                    else:
                                        try:
                                            word_cur = d_mis2fix[word_cur]
                                        except:
                                            word_cur = word_cur    
                                                               
                                 
                                    words_cur_fix += [word_cur]
                        
                        
                        if len(words_cur_fix) > 0: # to avoid transcripts without even a single word... yes they exsit:(                 
                            sentence_cur = " ".join(info_cur) + " " + " ".join(words_cur_fix)
                            text += [sentence_cur]
                            text_all += [sentence_cur]
                            words_all += words_cur_fix
                            time_all += float(info_cur[2]) - float(info_cur[1])
                        
                            isTest = False
                            for short_id in test_id:
                                if short_id in filename:
                                    isTest = True
                        
                            if isTest:
                                text_test += [sentence_cur]
                                words_test += words_cur_fix
                                time_test += float(info_cur[2]) - float(info_cur[1])
                            else:
                                text_train += [sentence_cur]
                                words_train += words_cur_fix
                                time_train += float(info_cur[2]) - float(info_cur[1])

                f.close()
            
            #save files without unparsed lines
            dir_save = parent_path + dir + newfolder
            if not os.path.exists(dir_save):
                os.makedirs(dir_save)
            with codecs.open(dir_save+filename, 'w', 'utf-8') as f:
                for line in text:
                    f.write(line + "\n")
            f.close()

with codecs.open(parent_path+dir_lang+'unparsed.txt', 'w', 'utf-8') as f:
    for line in text_unparse:
        f.write(line + "\n")
    f.close()

with codecs.open(parent_path+dir_lang+'text.txt', 'w', 'utf-8') as f:
    for line in text_all:
        f.write(line + "\n")
    f.close()
            
print("Finish reading lines")
print("Number of segmented utterance: "+str(len(text_all)))
print("Number of unsegmented utterance: "+str(len(text_unparse)))
print("Size of full set: "+str(time_all/1000/60/60)+" hours")
print("***** train and test *****")
print("Number of utterance in training set: "+str(len(text_train)))
print("Size of training set: "+str(time_train/1000/60/60)+" hours")
print("Number of utterance in test set: "+str(len(text_test)))
print("Size of test set: "+str(time_test/1000/60/60)+" hours")

#### output phones ####
# output silence_phones.txt
with codecs.open(parent_path+dir_lang+'silence_phones.txt', 'w', 'utf-8') as f:
    f.write('SIL\n')
    #for k,v in d_waste2idx.items():
    #    f.write(v + "\n")
    f.write('SIL1\n')
    f.write('SIL2\n')
    f.close()
print("Finish writing silence_phones.txt")

# nonsilence phones can be generated using shell script code

#### filter and output lexicon ####
words_all = [word.upper() for word in words_all]
words_all_uniq = list(set(words_all))
words_train_uniq = list(set(words_train))

d_all,words_oov_all_english,words_oov_all_chinese = oov(words_all_uniq,d_cmu,d_th)
d_train,words_oov_train_english,words_oov_train_chinese = oov(words_train_uniq,d_cmu,d_th)

print("Finish calculating oov")
print("Training set: English oov " + str(len(words_oov_train_english)) + "/" + str(len([item for item in words_train_uniq if isAlphahyphen(item)])))
print("Training set: Chinese oov " + str(len(words_oov_train_chinese)) + "/" + str(len([item for item in words_train_uniq if not isAlphahyphen(item)])))


words_test = []
for dir in dirs:
    if "conversation" in dir:
        test_id = test_short_ids_c
    elif "interview" in dir:
        test_id = test_short_ids_i
        
    filenames = os.listdir(parent_path+dir+newfolder)
    for filename in filenames:
        if filename[-4:] == ".txt":
            isTest = False
            for short_id in test_id:
                if short_id in filename:
                    isTest = True
            
            if isTest:
                with codecs.open(parent_path+dir+newfolder+filename, 'r', 'utf-8') as f:
                    text = []

                    for line in f.readlines():
                        sentence_origin = line.strip()                              
                        sentence = sentence_origin.split() # 1st element -- audio file id, 2nd element -- start time, 3rd element -- end time
                        info_cur = sentence[:3] # idx: 0~2
                        words_cur = sentence[3:] # idx: 3~
    
                        for word in words_cur: # filter out concatenated characters having Chinese characters, with length over 4

                        # split chinese words into characters if not in TRAINING dictionary to decrease oov rate
                            words_cur_fix = []
                            for word_cur in words_cur:
                                if not isAlphahyphen(word_cur): # if is not a english word
                                    try:
                                        d_train[word_cur]
                                        words_cur_fix += [word_cur]
                                    except:
                                        if len(word_cur)>1: # if length of word > 1, or more than 1 chinese character
                                            for char_idx in range(len(word_cur)):
                                                words_cur_fix += word_cur[char_idx]
                                        else: # if only has one chinese character
                                            words_cur_fix += [word_cur]                                            
                                else: # if is not chinese word
                                    words_cur_fix += [word_cur]
                                      
                            sentence_cur = " ".join(info_cur) + " " + " ".join(words_cur_fix)

                        text += [sentence_cur]
                        words_test += words_cur_fix



                f.close()
            
                #save files without unparsed lines
                dir_save = parent_path + dir + newfolder
                with codecs.open(dir_save+filename, 'w', 'utf-8') as f:
                    for line in text:
                        f.write(line + "\n")
                f.close()

            
print("Finish fixing test utterances according to training dictionary")

words_test_uniq = list(set(words_test))
d_test,words_oov_test_english,words_oov_test_chinese = oov(words_test_uniq,d_train,d_train)
print("Test set: English oov " + str(len(words_oov_test_english)) + "/" + str(len([item for item in words_test_uniq if isAlphahyphen(item)])))
print("Test set: Chinese oov " + str(len(words_oov_test_chinese)) + "/" + str(len([item for item in words_test_uniq if not isAlphahyphen(item)])))

'''
words_oov = []
d_train = dict()
for word in words_all_uniq:
    try:
        d_train[word] = d_cmu[word]
        for i in range(1,max_num+1):
            try:
                d_train[word+"(i)"] = d[word+"(i)"]
            except:
                break
    except:
        try:
            d_train[word] = d_th[word]
        except:
            words_oov += [word]
            continue
print("Finish lexicon filtering")
print("Number of words used: " + str(len(words_all)))
print("Number of unique words used: " + str(len(words_all_uniq)))
print("Number of unique words in filtered lexicon file: " + str(len(d_train)))

'''

# output lexicon.txt
lexicons = [k + " " + v + "\n" for k,v in d_train.items()]

with codecs.open(parent_path+dir_lang+'lexicon.txt', 'w', 'utf-8') as f:
    f.write('<oov> <oov>\n')
    for lexicon in lexicons:
        f.write(lexicon)
    #for word in words_oov:
    #    f.write(str(word) + " " + "<oov>\n")
    #for k,v in d_waste2idx.items():
    #    f.write(v + " sil" + "\n")
    f.write('SIL1 sil\n')
    f.write('SIL2 sil\n')
        
    f.close()

print("Finish writing lexicon.txt")
print("**********Done!**********")