# LIBRISPEECH Study Note


### Fixing Errors 
to avoid 
```
Please intall 'flac' on ALL worker nodes!
```
install flac codec:
```
sudo apt-get install flac
```

### Word-level Language Model
Look at the language model directory 
```
less data/lang/words.txt
```
shows
```
<eps> 0
!SIL 1
<SPOKEN_NOISE> 2
<UNK> 3
A 4
A''S 5
A'BODY 6
A'COURT 7
A'D 8
A'GHA 9
A'GOIN 10
A'LL 11
A'M 12
A'MIGHTY 13
A'MIGHTY'S 14
```
```
less data/lang/phones.txt
```
shows
```
<eps> 0
SIL 1
SIL_B 2
SIL_E 3
SIL_I 4
SIL_S 5
SPN 6
SPN_B 7
SPN_E 8
SPN_I 9
SPN_S 10
OY_B 11
OY_E 12
OY_I 13
OY_S 14
OY0_B 15
```
word boundries
```
less data/lang/phones/word_boundry.txt
```
shows
```
SIL nonword
SIL_B begin
SIL_E end
SIL_I internal
SIL_S singleton
SPN nonword
SPN_B begin
SPN_E end
SPN_I internal
SPN_S singleton
OY_B begin
OY_E end
OY_I internal
OY_S singleton
OY0_B begin
OY0_E end
OY0_I internal
OY0_S singleton
OY1_B begin
OY1_E end
OY1_I internal
OY1_S singleton
OY2_B begin
```
relates to the lexicon
```
less data/lang/phones/align_lexicon.txt
```
shows
```
!SIL !SIL SIL_S
<SPOKEN_NOISE> <SPOKEN_NOISE> SPN_S
<UNK> <UNK> SPN_S
<eps> <eps> SIL
A A AH0_S
A A EY1_S
A''S A''S EY1_B Z_E
A'BODY A'BODY EY1_B B_I AA2_I D_I IY0_E
A'COURT A'COURT EY1_B K_I AO2_I R_I T_E
A'D A'D EY1_B D_E
A'GHA A'GHA EY1_B G_I AH0_E
A'GOIN A'GOIN EY1_B G_I OY1_I N_E
A'LL A'LL EY1_B L_E
A'M A'M EY1_B M_E
A'MIGHTY A'MIGHTY EY1_B M_I AY1_I T_I IY0_E
A'MIGHTY'S A'MIGHTY'S EY1_B M_I AY1_I T_I IY0_I Z_E
A'MOST A'MOST EY1_B M_I OW2_I S_I T_E
A'N'T A'N'T EY1_B AH0_I N_I T_E
A'PENNY A'PENNY EY1_B P_I EH2_I N_I IY0_E
A'READY A'READY EY1_B R_I IY1_I D_I IY0_E
```
for word based language model, each utterance is mapped to a word instead of phones which we see in TIMIT
```
less data/train_10k/text
```
shows
```
103-1240-0002 FOR NOT EVEN A BROOK COULD RUN PAST MISSUS RACHEL LYNDE'S DOOR WIT
HOUT DUE REGARD FOR DECENCY AND DECORUM IT PROBABLY WAS CONSCIOUS THAT MISSUS RA
CHEL WAS SITTING AT HER WINDOW KEEPING A SHARP EYE ON EVERYTHING THAT PASSED FRO
M BROOKS AND CHILDREN UP
```

### Train a Triphone model
train_deltas.sh trains triphone models on top of MFCC+delta+delta-delta features. 
```
steps/train_deltas.sh 
Usage: steps/train_deltas.sh <num-leaves> <tot-gauss> <data-dir> <lang-dir> <alignment-dir> <exp-dir>
```
actual usage
```
# train a first delta + delta-delta triphone system on a subset of 5000 utterances
steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
    2000 10000 data/train_5k data/lang_nosp exp/mono_ali_5k exp/tri1
```
to check feature dimensions
```
feat-to-dim scp:data/train_10k/feats.scp -

13
```
use **add-deltas** to expand features from static to delta+deltadelta
```
add-deltas scp:data/train_10k/feats.scp ark:- | feat-to-dim ark:- -

39
```

### Logs
logs are stored in: 
```
less exp/word/tri1/log/acc.1.1.long 
```

### Triphone Model: a Closer Look
in the following command:
```
steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" \
    2000 10000 data/train_5k data/lang_nosp exp/mono_ali_5k exp/tri1
```
2000 specifies the number of leaves in the decision tree, and 10000 specifies the total number of Gaussians across all states in the model. 
The use of decision tree is to cluster triphones. If we have a seperate model for each triphone (say 48 phones in total, and that makes it 48^3 > 110,000 models), the total size is too large to store. The solution is to cluster them and store them in the decision tree. **the number of leaves** set the maximum number of leaves in the decision tree and **number of gaussians** set the maxium number of Gaussians distributed across the leaves. On average, we have  **number of gaussians**/ **the number of leaves** Gaussians per leaf.  

steps/train_deltas.sh actual part that build the decision tree: 
```
if [ $stage -le -2 ]; then
  echo "$0: getting questions for tree-building, via clustering"
  # preparing questions, roots file...
  cluster-phones $context_opts $dir/treeacc $lang/phones/sets.int \
    $dir/questions.int 2> $dir/log/questions.log || exit 1;
  cat $lang/phones/extra_questions.int >> $dir/questions.int
  compile-questions $context_opts $lang/topo $dir/questions.int \
    $dir/questions.qst 2>$dir/log/compile_questions.log || exit 1;

  echo "$0: building the tree"
  $cmd $dir/log/build_tree.log \
    build-tree $context_opts --verbose=1 --max-leaves=$numleaves \
    --cluster-thresh=$cluster_thresh $dir/treeacc $lang/phones/roots.int \
    $dir/questions.qst $lang/topo $dir/tree || exit 1;

  $cmd $dir/log/init_model.log \
    gmm-init-model  --write-occs=$dir/1.occs  \
      $dir/tree $dir/treeacc $lang/topo $dir/1.mdl || exit 1;
  if grep 'no stats' $dir/log/init_model.log; then
     echo "** The warnings above about 'no stats' generally mean you have phones **"
     echo "** (or groups of phones) in your phone set that had no corresponding data. **"
     echo "** You should probably figure out whether something went wrong, **"
     echo "** or whether your data just doesn't happen to have examples of those **"
     echo "** phones. **"
  fi
  ```
cluster-phones: cluster similar phones. These clusters will be the basis for the questions in the decision tree. cluster-phones write clusters using the numeric phone indentities to a file called exp/word/tri1/questions.int 

```
less exp/word/tri1/questions.int 
```
gives you the numeric phone indentities
```
1 2 3 4 5 6 7 8 9 10 47 48 49 50 147 148 149 150 151 152 153 154 155 156 157 158 159 160 161 162 163 164 165 166 167 168 169 170 207 208 209 210 211 212 213 214 231 232 233 234 235 236 237 238 259 260 261 262 323 324 325 326 327 328 329 330 335 336 337 338 339 340 341 342 343 344 345 346
```
to map numeric phone identities to phone names
```
utils/int2sym.pl data/lang/phones.txt exp/tri1/questions.int | less
```
shows
```
SIL SIL_B SIL_E SIL_I SIL_S SPN SPN_B SPN_E SPN_I SPN_S DH_B DH_E DH_I DH_S F_B F_E F_I F_S G_B G_E G_I G_S CH_B CH_E CH_I CH_S S_B S_E S_I S_S K_B K_E K_I K_S SH_B SH_E SH_I SH_S TH_B TH_E TH_I TH_S HH_B HH_E HH_I HH_S JH_B JH_E JH_I JH_S P_B P_E P_I P_S Z_B Z_E Z_I Z_S V_B V_E V_I V_S ZH_B ZH_E ZH_I ZH_S T_B T_E T_I T_S D_B D_E D_I D_S B_B B_E B_I B_S 
```
the block displayed above is a line in the file and itself is a cluster. 

The decision tree is stored in exp/tri1/tree
to view this tree, type
```
copy-tree --binary=false exp/tri1/tree - | less
```
shows the entire clustering tree. 
```
{ SE 0 [ 1 2 3 4 5 ]
```
SE stands for SplitEventMap, which is splitting point of the tree. 0, 1 or 2 following SE stands for left, center, and right. 
```
{ SE 0 [ 1 2 3 4 5 ]
{ CE 614 SE 0 [ 323 324 325 326 ]
{ CE 1398 CE 1460 } 
```
here, CE 1398 means if left [ 323 324 325 326 ] is evaluated as true, we choose pdf-id 1398, if not true, we choose pdf-id 1460. CE stands for a ConstantEventMap and indicates a leaf of the tree. 

After running steps/train_deltas.sh, we can create a decoding graph and decode the triphone system using utils/mkgraph.sh, followed with steps/decode.sh

### LDA+MLLT: stronger acoustic model, better alignment 
Align the system, use
```
steps/align_si.sh 
usage: steps/align_si.sh <data-dir> <lang-dir> <src-dir> <align-dir>
```
for example:
```
# Align a 10k utts subset using the tri2b model
steps/align_si.sh  --nj 16 --cmd "$train_cmd" --use-graphs true \
  data/train_10k data/lang_nosp exp/tri2b exp/tri2b_ali_10k
```
here, the \<align-dir> could also take a normal training experiment directory e.g. tri1 instead of tri1_ali. 
Typically, between each training phase, there will be a pass of alignment. So it is not necessary to perform alignment in a seperate step, but it is a good practice to ensure we have the absolute latest alignments for the latest model. 

To even strengthen the acoustic model, we shall train a system on top of LDA_MLLT features using the tri1_ali. 
```
# train an LDA+MLLT system.
steps/train_lda_mllt.sh --cmd "$train_cmd" \
   --splice-opts "--left-context=3 --right-context=3" 2500 15000 \
   data/train_10k data/lang_nosp exp/tri1_ali_10k exp/tri2b
```
looks like  MLLT (Maximum Likelihood Linear Transform) allows sharing a few full covariance matrices across many distributions without storing and computing all. This adds to basic MFCC features+GMM in a way that GMM models use diagonal covariances matrics to get the emission probability. Given only diagonal covariance matrics are used, not full covairances, GMM assumes each element of the feature vectors (MFCCs) are independent. Here MLLT loosens this assumption by adding a few full covairances matrics to the system. 

then aligns the system to get teh latest possible alignment for the neural networks:
```
# Align a 10k utts subset using the tri2b model
steps/align_si.sh  --nj 10 --cmd "$train_cmd" --use-graphs true \
  data/train_10k data/lang_nosp exp/tri2b exp/tri2b_ali_10k
```
tri2b_ali_10k/ali.\*.gz stores transition id  

### Neural Networks: Data Prep and Train
split the dataset into train and validation set:
```
dir=data/train_words
utils/subset_data_dir_tr_cv.sh $dir ${dir}_tr90 ${dir}_cv10
```
This will create the following directories:
```
data/train_words_tr90  
data/train_words_cv10   
```
Kaldi has three neural network toolkits, to train a neural network, use
```
steps/nnet/train.sh 
Usage: steps/nnet/train.sh <data-train> <data-dev> <lang-dir> <ali-train> <ali-dev> <exp-dir>
```
an example:
```
steps/nnet/train.sh --....
```

*GPU is 10-20x faster than CPU

The ###### PREPARE ALIGNMENTS ###### section in the steps/nnet/train.sh will create 1. target labels using the above alignment 2. counts of the pdfs corresponding to the phones in the alignments. 


### Target Labels
to look at the lables in alignment: 
```
 ali-to-pdf exp/tri2b/final.mdl "ark:gunzip -c exp/tri2b/ali.1.gz |" ark:- | ali-to-post ark:- ark,t:- | less
```
shows: 
```
103-1240-0002 [ 0 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [ 44 1 ] [
 44 1 ] [ 44 1 ] [ 43 1 ] [ 164 1 ] [ 164 1 ] [ 164 1 ] [ 164 1 ] [ 164 1 ] [ 164 1 ] [ 1136 1 ] [ 1136 1 ] [ 1136 1 ] [ 758 1 ] [ 
758 1 ] 
```
the first number in each bracket is a phone state. The second number is a weight, which for our cases will always be set to 1. This file sets out, for each frame, which phone state will be on; or equivalently, which output of the neural network will be set to 1, and the rest of the output are just 0. *we are doing frame corss-entrophy training [lab4 p.4](https://www.inf.ed.ac.uk/teaching/courses/asr/2016-17/lab4.pdf)

### the Class Priors P(q) and Posteriors P(q|x)
Use the following command to sum the pdf vectors to counts, this is used to obtain prior counts for decoding. [analyze-counts kaldi doc](http://kaldi-asr.org/doc/analyze-counts_8cc.html#a0ddf1224851353fc92bfbff6f499fa97)
```
ali-to-phones --per-frame=true exp/tri2b/final.mdl ark:"gunzip -c exp/tri2b/ali.1.gz |" ark:- | analyze-counts --verbose=1 ark:- -
```
gives you the count table: 
```
### The sorted count table,
count	(norm),	id
...
15972	(0.0217483),	336	
16170	(0.0220179),	159	
16471	(0.0224278),	333	
17213	(0.0234381),	260	
141395	(0.192531),	1
```
Why do we need the count table (class priors)?:   
In the hybrid model, instead of using GMM, we use NN to estimate posterior probabilities. The output of the neural network is the probability of a phone class given the feature P(q|x). In order to compute the emission probability P(x|q) for HMM, we uses the bayes rule:
```
P(x|q) = P(q|x) * P(x)/ P(q) simplified as 
P(x|q) ~ P(q|x) / P(q), which is okay, as P(x) does not depend on the class q
```
This being said, we need to scale the NN output by class priors P(q) for HMM. 
In nnet/train.sh there is a similar script to compute the class prior P(q) from the alignments and stores them in a file called ali_train_pdf.counts:
```
  # get pdf-counts, used later for decoding/aligning,
  num_pdf=$(hmm-info $alidir/final.mdl | awk '/pdfs/{print $4}')
  analyze-counts --verbose=1 --binary=false --counts-dim=$num_pdf \
    ${frame_weights:+ "--frame-weights=$frame_weights"} \
    ${utt_weights:+ "--utt-weights=$utt_weights"} \
    "$labels_tr_pdf" $dir/ali_train_pdf.counts 2>$dir/log/analyze_counts_pdf.log
```
in nnet/train.sh, we can provide our own counts, if not, it will look for ali_train_pdf.counts:
```
[ -z "$class_frame_counts" -a -f $srcdir/prior_counts ] && class_frame_counts=$srcdir/prior_counts # priority,
[ -z "$class_frame_counts" ] && class_frame_counts=$srcdir/ali_train_pdf.counts
```
in the decoding stage showed as below:
```
# Run the decoding in the queue,
if [ $stage -le 0 ]; then
  $cmd --num-threads $((num_threads+1)) JOB=1:$nj $dir/log/decode.JOB.log \
    nnet-forward $nnet_forward_opts --feature-transform=$feature_transform --class-frame-counts=$class_frame_counts --use-gpu=$use_gpu "$nnet" "$feats" ark:- \| \
    latgen-faster-mapped$thread_string --min-active=$min_active --max-active=$max_active --max-mem=$max_mem --beam=$beam \
    --lattice-beam=$lattice_beam --acoustic-scale=$acwt --allow-partial=true --word-symbol-table=$graphdir/words.txt \
    $model $graphdir/HCLG.fst ark:- "ark:|gzip -c > $dir/lat.JOB.gz" || exit 1;
fi
```
we see that **class-frame-counts** (class probability used for scaling) got passed in as an argument for decoding. 

### Neural Network Wrapping Up
the neural network parameters are stored in exp/tri3_nnet/nnet.proto
you can modify it and generate the initial model with the required parameters in your proto file:
```
cp exp/word/tri3_nnet/nnet.proto my.proto  #copy the proto file
nano my.proto #modify it
nnet-initialize --binary=false my.proto my.init #generate the initial model
```
after the model generation is finished, you can look at the model by typing
```
nnet-info my.init
```
and see the file in details:
```
less my.init
```

decode will be next step, after which score it! 

[GATHERED FROM LAB4](https://www.inf.ed.ac.uk/teaching/courses/asr/2016-17/lab4.pdf)
