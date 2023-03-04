# Enhanced awesome-align for low-resource languages
## About this repository
`Enhanced awesome-align` is a word alignment tool built upon on [awesome-align](https://github.com/neulab/awesome-align). 
It is specifically designed for noisy ***low-resource languages***. 
This repo contains the instruction and code for noise simulation and extracting the alignment. 

We also release the ***gold*** word alignment pairs between an endangered language, Griko, and translations in Italian. The gold alignment data can be found on `alignment_data/griko-italian`

👉 See our paper [Noisy Parallel Data Alignment](https://arxiv.org/abs/2301.09685) for more details 👈

### Installation
Install the requirements by running the following command:
```bash
pip install -r requirements.txt
python3 setup.py install
```

## Noise simulation
To simulate text noise, we need to *first* calculate the noise probability and *then* generate synthetic data. 

First, run the following command to calculate noise probability:
    
```bash
python3 noise_simulation/noise_analysis.py <parallel_data> <noisy_probability_data> 
```
`parallel_data` is the clean and noisy version of the same text that is split by ` ||| `. Example can be found on `noise_simulation/example/griko_clean_noisy.txt` 

`noisy_probability_data` is the produced noise probability file that will be used for the next step to create synthetic data. 

Next, to generate synthetic noisy data, run the following command:
```bash
python3 noise_simulation/noise_adding.py <clean_input_file> <output_file> <noisy_probability_data> 
```

`clean_input_file` is the clean text that will be adding text noise. Example can be found on `noise_simulation/example/griko_clean.txt`.

`output_file` is the output file that will contain the synthetic data.

`noisy_probability_data` is the noise probability file from the previous step.


## Running enhanced awesome-align
#### Input format
Similar to original `awesome-align`, the inputs data should be *tokenized* parallel data. 
The source and target sentences are separated by ` ||| `. 
Example data can be found on `alignment_data/griko-italian/all.txt`.

#### Extracting alignments
To extract alignment, please edit the path information and run the command:
```bash
DATA_FILE=/path/to/alignment_data/file
MODEL_NAME_OR_PATH=bert-base-multilingual-cased
OUTPUT_FILE=/path/to/output/file

python3 model/run_align.py \
    --output_file=$OUTPUT_FILE \
    --model_name_or_path=$MODEL_NAME_OR_PATH \
    --data_file=$DATA_FILE \
    --extraction 'softmax' \
    --batch_size 32 \
    --bias=1
```

#### Unsupervised fine-tuning
If gold alignment file is not available, you can finetune the model with only parallel data. For example,
 using the synthetic noisy data from the previous step can generate better alignment for noisy and low-resource languages. Please edit the path information and run the command:
```bash
TRAIN_FILE=/path/to/alignment_data/file
MODEL_NAME_OR_PATH=bert-base-multilingual-cased
OUTPUT_DIR=/path/to/output/dir

python3 model/run_train.py \
    --output_dir=$OUTPUT_DIR \
    --model_name_or_path=$MODEL_NAME_OR_PATH \
    --extraction 'softmax' \
    --do_train \
    --train_tlm \
    --train_so \
    --train_data_file=$TRAIN_FILE \
    --per_gpu_train_batch_size 2 \
    --gradient_accumulation_steps 4 \
    --num_train_epochs 1 \
    --learning_rate 2e-5 \
    --save_steps 4000 \
    --max_steps 20000 
```


#### Supervised fine-tuning
If gold alignment file is available, you can fine-tune the model with the gold alignment file to achieve better alignment quality. Example gold alignment file can be found on `alignment_data/griko-italian/alignment.gold`. Please edit the path information and run the command:
```bash
TRAIN_FILE=/path/to/alignment_data/file
MODEL_NAME_OR_PATH=bert-base-multilingual-cased
OUTPUT_DIR=/path/to/output/dir
TRAIN_GOLD_FILE=/path/to/gold/alignment/file

python3 model/run_train.py \
    --output_dir=$OUTPUT_DIR \
    --model_name_or_path=$MODEL_NAME_OR_PATH \
    --extraction 'softmax' \
    --do_train \
    --train_so \
    --train_data_file=$TRAIN_FILE \
    --train_gold_file=$TRAIN_GOLD_FILE \
    --per_gpu_train_batch_size 2 \
    --gradient_accumulation_steps 4 \
    --num_train_epochs 5 \
    --learning_rate 1e-4 \
    --save_steps 40000
```

### Evaluation
To evaluate the alignment quality, use the following command:
```bash
python3 evaluate.py <alignment_output> <gold_alignment>
```

### Citation

If you use our tool or data, we'd appreciate if you cite the following paper:

```
@inproceedings{xie-anastasopoulos-23-noisy,
    title = "Noisy Parallel Data Alignment",
    author = "Xie, Ruoyu  and
      Anastasopoulos, Antonios",
    booktitle = "Findings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)",
    month = may,
    year = "2023",
    address = "Dubrovnik, Croatia",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/2301.09685",
    abstract = {An ongoing challenge in current natural language processing is how its major advancements tend to disproportionately favor resource-rich languages, leaving a significant number of under-resourced languages behind. Due to the lack of resources required to train and evaluate models, most modern language technologies are either nonexistent or unreliable to process endangered, local, and non-standardized languages. Optical character recognition (OCR) is often used to convert endangered language documents into machine-readable data. However, such OCR output is typically noisy, and most word alignment models are not built to work under such noisy conditions. In this work, we study the existing word-level alignment models under noisy settings and aim to make them more robust to noisy data. Our noise simulation and structural biasing method, tested on multiple language pairs, manages to reduce the alignment error rate on a state-of-the-art neural-based alignment model up to 59.6%.},
}
```
