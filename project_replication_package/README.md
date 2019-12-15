# RealmFit Replication Repository

- [RealmFit Replication Repository](#realmfit-replication-repository)
  - [Library Dependencies](#library-dependencies)
  - [Data Acquisition: Stackoverflow](#data-acquisition-stackoverflow)
  - [Data Acquisition: Buggy/Non Buggy Code](#data-acquisition-buggynon-buggy-code)
  - [Data Acquisition: Comments](#data-acquisition-comments)
  - [Building Vocabulary](#building-vocabulary)
  - [Training Model](#training-model)
  - [Hardware Used](#hardware-used)

## Library Dependencies
- Python3 Package dependencies are provided in [requirements.txt](requirements.txt)
- Dockerfile is provided at [Dockerfile](Dockerfile)

## Data Acquisition: Stackoverflow
The original query we executed was on October 3rd, 2019.
Number of results we received was: 56942

The original SQL query is:

```sql
SELECT
  questions.title,
  questions.Id as 'q_id',
  questions.body as 'q_body',
  questions.score as 'q_score',
  (case 
    when questions.AcceptedAnswerId = answers.Id
    then 1
    else 0 end) as 'acc_a',
  answers.Id as 'a_id',
  answers.body as 'a_body',
  answers.score as 'a_score'
FROM Posts answers
INNER JOIN Posts questions ON answers.parentid = questions.id
WHERE questions.title like '%how%'
AND questions.tags like '%java%'
AND questions.tags not like '%javascript%'
AND answers.score > 0
order by questions.id asc
OFFSET 50000 ROWS
FETCH FIRST 50000 ROWS ONLY;
```

The query was executed in [StackOverflow Data Explorer](https://data.stackexchange.com/).

Please adjust it accordingly based on execution date for reproducibility.   For replication, no changes are necessary as it will return results till the latest day.

Furthermore, StackOverFlow returns only 50,000 entries at a time; therefore you may need to adjust the offset while executing the query.
The processing steps include cleaning all html tags except <code></code> tags.

Then, the data is saved in (query, response) format in csv file.

Our version of CSV files are provided under `data.zip/so` directory in this [link](https://drive.google.com/drive/folders/1sQeS4KYrSla83GOqzuwo-eGGdFX9d7gM?usp=sharing). 

## Data Acquisition: Buggy/Non Buggy Code

The buggy/non buggy data was collected from Tufano et al.'s paper [An Empirical Study on Learning Bug-Fixing Patches in the
Wild via Neural Machine Translation](https://arxiv.org/pdf/1812.08693.pdf). The preprocessing that was done included:

- Converting buggy/non buggy pairs into dataset of methods and their classification as either buggy or non buggy

All the steps are available under [main/src/prep/prep.ipynb](main/src/prep/prep.ipynb) file.

The exact data used is provided into splits of training, validation, and testing  once the data.zip file is downloaded under `data.zip/buggy` directory in this [link](https://drive.google.com/drive/folders/1sQeS4KYrSla83GOqzuwo-eGGdFX9d7gM?usp=sharing)..


## Data Acquisition: Comments

The comments data are collected from [CodeSearchNet](https://github.com/github/CodeSearchNet). The preprocessing steps include:

- Downloading the dataset
- extracting the jsonl.gz files
- extracting the code and relevant docstrings
- putting them back in a csv in (query, response) format.
  
All these steps are available under [main/src/prep/prep.ipynb](main/src/prep/prep.ipynb) file.

All the data are spilt into training, validation and testing set at 80-10-10 ratio.

Our version of CSV files are provided under `data.zip/mthds_cmts` directory in this [link](https://drive.google.com/drive/folders/1sQeS4KYrSla83GOqzuwo-eGGdFX9d7gM?usp=sharing).

## Building Vocabulary

We used Google SentencePiece for building the vocabulary. For that, the data are loaded through DataFrames. Using SentencePiece, we create the models and vocabularies of data and then frame it as FastAI Databunch objects for further processing. These are then saved as pkl files after processing. 
These are done in [main/src/proc.ipynb](main/src/proc.ipynb) file.

## Training Model

To train model such as awd_lstm, we load the data as dataframe. Futhermore, the vocabulary model is also loaded. We determine a batch size of 8 which allows faster parallel processing without shutting down the server. Then, we use FastAI language_model_learner to train the model. While doing that, we rely on FastAI's learning rate finder to establish a learning rate, which we determine to be $5e^-4$. For learning, we also define two callbacks. One callback is to save model every time the performance is improved. The other callback is to stop the training when validation loss starts going up. For the validation loss,establish patience as 3, which means it will train for at least 3 epochs, and a min-delta of 0.01; which means it will accept validation loss at a 0.01 level. The performance metric here is accuracy. 
These details are available under `main/nbs/mdling/`. For example, awd_lstm is available under [main/nbs/mdling/awd_lstm/awd_lstm.ipynb](main/nbs/mdling/awd_lstm/awd_lstm.ipynb).

Our version of CSV files are provided under `data.zip/buggy` directory in this [link](https://drive.google.com/drive/folders/1sQeS4KYrSla83GOqzuwo-eGGdFX9d7gM?usp=sharing).

Furthermore, all the trained models are also provided under `models.zip` file in this [link](https://drive.google.com/drive/folders/1sQeS4KYrSla83GOqzuwo-eGGdFX9d7gM?usp=sharing).

## Hardware Used
All experiments and model training was done on two Linux servers. The server configurations are as follows:  

- Server one
  - CPU: Intel(R) Xeon(R) CPU E5-1607 v3 @ 3.10GHz with 4 cores
  - RAM: 128GB DRAM
  - GPU: Nvidia Titan RTX with 24GB VRAM
- Server Two
  - CPU: Intel(R) Xeon(R) CPU E5- 1603 v3 @ 2.80GHz
  - RAM: 128GBs of DRAM
  - GPU: 11GBs of VRAM
