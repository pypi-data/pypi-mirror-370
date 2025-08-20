# ANC CLI Tool

## Overview
The ANC CLI tool is a comprehensive command line interface designed to facilitate the management of various resources within the company. Initially, it supports managing datasets and their versions, enabling users to interact seamlessly with a remote server for fetching, listing, and adding datasets.

## Installation

### For User
```bash
# Instructions for installing the ANC CLI tool
sudo pip install anc

```

### For cli Develop
```bash
# Instructions for installing the ANC CLI tool
cd dev/cli
sudo pip install -r requirements.txt
sudo pip install -e .
```

#### for release
For build and release instructions, see [Release Guide](./RELEASE.md).


## Dataset
- **Fetch Datasets**: Retrieve specific versions of datasets from a remote server.
- **List Versions**: View all available versions of a dataset.
- **Add Datasets**: Upload new datasets along with their versions and descriptions to the remote server.

### Usage

#### list
```bash

anc ds list 
# Or you can specify a dataset name.
anc ds list -n <dataset name>

```

#### get
```bash

# According to the above list result, you can download the specific version dataset.
# Ensure that the destination path for downloads is a permanent storage location(e.g. /mnt/weka/xxx). Currently, downloading data to local storage is not permitted.
anc ds get cifar-10-batches-py -v 1.0

```

#### add
```bash

# Upload a specific version of a dataset. The dataset name will be determined based on the file or folder name extracted from the specified path.
# Ensure that the dataset is stored in a permanent location recognized by the server (e.g., /mnt/weka/xxx).
anc ds add /mnt/weka/xug/dvc_temp/cifar-10-batches-py -v 1.0
```


## load-test

### load test with real data
```bash
pip install vllm

# Runload test. this will start the server and send the benchmark requests, save the results to the json file and plot the results
anc loadtest run \
--model /mnt/share/ocean/candidate1 \
--max-model-len 8000 \
--backend vllm \
--port 8004 \
--tensor-parallel-size "4" \
--enable-prefix-caching "True" \
---dataset-name anc \
---dataset-path /mnt/share/infra/hongbo/load_test_data/1000_ocean_prompt_pressure_test_v2_02_25.jsonl \
---num-prompts 300 \
---max-concurrency "1,2,4, 6, 8, 10, 12, 24" \
---dataset-name anc \
---dataset-path /mnt/share/infra/hongbo/load_test_data/1000_ocean_prompt_pressure_test_v2_02_25.jsonl \
---num-prompts 300 \
---max-concurrency "1,2,4, 6, 8, 10, 12, 24" \
--result-dir "./test" \
--gpu-memory-utilization 0.8 \
--seed 10


### you can also plot the results directly from the json file
anc loadtest plot --dataset-name anc ./test/all_results.json
## # if you have multiple json files in the same directory, you can plot all of them by
anc loadtest plot --dataset-name anc ./test
```


### load test with random data
```bash
anc loadtest run \
--model /mnt/project/llm/ckpt/stable_ckpts/Llama-3.2-1B/ \
--max-model-len 200 \
--backend vllm \
--port 8004 \
--dataset-name random \
--num-prompts 1 \
--max-concurrency "1" \
--random-input-len "10" \
--result-dir "./test"  \
--skip-server
```


### load test with remote endpoint
 grid search with server parametgers won't work with this method. as we won't be able to restart the remote server(i.e. TP will be what ever tp used by the endpoint). Also prefix caching will be controlled by server, so you might end up with very high hit rate if your request sample size is small 
```bash
anc loadtest run \
--model /mnt/share/ocean/candidate1 \
 --model-id ocean-llm \
--backend vllm \
 --dataset-name anc \
 --dataset-path /mnt/share/infra/hongbo/load_test_data/1000_ocean_prompt_pressure_test_v2_02_25.jsonl \
 --num-prompts 10 \
 --max-concurrency "1,2, 4" \
 --result-dir "./test" \
 --seed 10 \
 --skip-server \
 --base-url "http://ocean-test-2.serving-prod.va-mlp.anuttacon.com" 
```


### load test with remote endpoint
 grid search with server parametgers won't work with this method. as we won't be able to restart the remote server(i.e. TP will be what ever tp used by the endpoint). Also prefix caching will be controlled by server, so you might end up with very high hit rate if your request sample size is small 
```bash
anc loadtest run \
--model /mnt/share/ocean/candidate1 \
 --model-id ocean-llm \
--backend vllm \
 --dataset-name anc \
 --dataset-path /mnt/share/infra/hongbo/load_test_data/1000_ocean_prompt_pressure_test_v2_02_25.jsonl \
 --num-prompts 10 \
 --max-concurrency "1,2, 4" \
 --result-dir "./test" \
 --seed 10 \
 --skip-server \
 --base-url "http://ocean-test-2.serving-prod.va-mlp.anuttacon.com" 
```