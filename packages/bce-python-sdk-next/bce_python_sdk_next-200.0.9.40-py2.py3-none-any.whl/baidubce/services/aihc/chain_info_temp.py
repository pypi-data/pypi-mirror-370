import os
import json
import sys

cur_path = os.path.dirname(os.path.realpath(__file__))

job1_convert_checkpoint = r"""
#! /bin/bash

echo "LOAD: ${LOAD}"
echo "SAVE: ${SAVE}"
echo "MODEL_BOS_PATH: ${MODEL_BOS_PATH}"
echo "MODEL_NAME: ${MODEL_NAME}"
echo "TP: ${TP}"
echo "PP: ${PP}"

# 如果SAVE文件夹已存在，则终止启动，打印提示信息
if [ -d "${SAVE}" ]; then
    echo "The SAVE folder ${SAVE} already exists, you can use it directly. Or you can delete it and run this script again."
    exit 1
else
    echo "The SAVE folder ${SAVE} does not exist, start to convert checkpoint."
fi

# 检查/mnt/cluster/huggingface.co/meta-llama/Llama-2-70b-hf是否存在，不存在则下载
if [ ! -d "${LOAD}" ]; then
    # 下载bcecmd程序
    wget https://doc.bce.baidu.com/bce-documentation/BOS/linux-bcecmd-0.4.5.zip
    # 解压
    unzip linux-bcecmd-0.4.5.zip
    cd linux-bcecmd-0.4.5
    echo "Start to download checkpoint..."
    ./bcecmd  bos sync ${MODEL_BOS_PATH} ${LOAD}
    echo "Download checkpoint done."
else
    echo "The LOAD folder ${LOAD} already exists,no need to download."
fi

echo "Start to convert checkpoint..."

AIAK_TRAINING_PATH=/workspace/AIAK-Training-LLM
CONVERT_CHECKPOINT_PATH="$AIAK_TRAINING_PATH/tools/convert_checkpoint"
MEGATRON_PATH=${MEGATRON_PATH:-"/workspace/AIAK-Megatron"}

# 当前不支持 optim 部分转换，通过 --no_save_optim 和 --no_load_optim 关闭；
python $CONVERT_CHECKPOINT_PATH/model.py \
    --load_platform=huggingface \
    --save_platform=mcore \
    --common_config_path=$CONVERT_CHECKPOINT_PATH/config/${MODEL_NAME}.json \
    --tensor_model_parallel_size=${TP} \
    --pipeline_model_parallel_size=${PP} \
    --load_ckpt_path=$LOAD \
    --save_ckpt_path=$SAVE \
    --megatron_path=$MEGATRON_PATH \
    --no_save_optim \
    --no_load_optim \
    --safetensors

echo "Convert checkpoint done."
echo "The converted checkpoint is saved in: \n ${SAVE}."
"""

job2_pretrain_data_preprocess = r"""

#!/bin/bash

echo "INPUT_DATA: ${INPUT_DATA}"
echo "OUTPUT_PREFIX: ${OUTPUT_PREFIX}"
echo "DATASET_BOS_PATH: ${DATASET_BOS_PATH}"
echo "TOKENIZER_PATH: ${TOKENIZER_PATH}"
echo "JSON_KEYS: ${JSON_KEYS}"

# 如果INPUT_DATA文件已存在，则终止启动，打印提示信息
if [ -f "${INPUT_DATA}" ]; then
    echo "The INPUT_DATA file ${INPUT_DATA} already exists, you can use it directly. Or you can delete it and run this script again."
    exit 1
fi

# 下载测试数据集
# 检查INPUT_DATA是否存在，不存在则下载
if [ ! -f "${INPUT_DATA}" ]; then
    # 下载bcecmd程序
    wget https://doc.bce.baidu.com/bce-documentation/BOS/linux-bcecmd-0.4.5.zip
    # 解压
    unzip linux-bcecmd-0.4.5.zip
    cd linux-bcecmd-0.4.5

    echo "Start to download data..."
    ./bcecmd bos cp ${DATASET_BOS_PATH} ${INPUT_DATA} --restart --quiet --yes
fi

echo "Download data done."

MEGATRON_PATH=/workspace/AIAK-Megatron
AIAK_TRAINING_PATH=${AIAK_TRAINING_PATH:-"/workspace/AIAK-Training-LLM"}

PYTHONPATH=$MEGATRON_PATH:$AIAK_TRAINING_PATH:$PYTHONPATH \
    python ${AIAK_TRAINING_PATH}/tools/data_preprocess/preprocess_pretrain_data.py \
        --input ${INPUT_DATA} \
        --output-prefix ${OUTPUT_PREFIX} \
        --tokenizer-type HFTokenizer \
        --hf-tokenizer-path $TOKENIZER_PATH \
        --json-keys $JSON_KEYS \
        --workers 50 \
        --append-eod
echo "Data preprocess done."
"""

job2_sft_data_preprocess = r"""

#!/bin/bash

# 检查INPUT_DATA是否存在，不存在则下载
if [ ! -d "${INPUT_DATA}" ]; then
    # 下载bcecmd程序
    wget https://doc.bce.baidu.com/bce-documentation/BOS/linux-bcecmd-0.4.5.zip
    # 解压
    unzip linux-bcecmd-0.4.5.zip
    cd linux-bcecmd-0.4.5

    echo "Start to download data..."
    # 下载测试数据集
    ./bcecmd bos cp ${DATASET_BOS_PATH} ${INPUT_DATA} --restart --quiet --yes
fi

echo "Download data done."

MEGATRON_PATH=/workspace/AIAK-Megatron
AIAK_TRAINING_PATH=${AIAK_TRAINING_PATH:-"/workspace/AIAK-Training-LLM"}

PYTHONPATH=$MEGATRON_PATH:$AIAK_TRAINING_PATH:$PYTHONPATH \
    python ${AIAK_TRAINING_PATH}/tools/data_preprocess/preprocess_sft_data.py \
        --input ${INPUT_DATA} \
        --output ${OUTPUT_PATH} \
        --seq-length 2048 \
        --chat-template ${CHAT_TEMPLATE} \
        --tokenizer-type HFTokenizer \
        --hf-tokenizer-path $TOKENIZER_PATH \
        --workers 50 \
        --split 100,0,0
        # --packing-sft-data \
        # --train-on-prompt \
        # --eod-mask-loss \
        # --sft-dataset-config /workspace/AIAK-Training-LLM/configs/sft_dataset_config.json \
        # --sft-dataset custom_dataset \
echo "Data preprocess done."
"""

commands = {
    "job1_convert_checkpoint": job1_convert_checkpoint,
    "job2_pretrain_data_preprocess": job2_pretrain_data_preprocess,
    "job2_sft_data_preprocess": job2_sft_data_preprocess
}

datasets = {
    "pile_llama_test": "bos:/cce-ai-datasets/cce-ai-datasets.bj.bcebos.com/megatron_llama/pile_llama_test/pile_test_jsonl/test.jsonl",
    "WuDaoCorpus2.0_base_sample": "bos:/cce-ai-datasets/datasets/aiak/WuDaoCorpus2.0_base_sample.jsonl",
    "alpaca_zh-llama3-train": "bos:/cce-ai-datasets/datasets/aiak/alpaca_zh-llama3-train.json",
    "alpaca_zh-llama3-valid": "bos:/cce-ai-datasets/datasets/aiak/alpaca_zh-llama3-valid.json"
}

models = {
    "baichuan-7b": [
        "bos:/cce-ai-datasets/huggingface.co/baichuan-inc/baichuan-7B",
        "#N/A",
        "#N/A"
    ],
    "baichuan-13b": [
        "bos:/cce-ai-datasets/huggingface.co/baichuan-inc/Baichuan-13B-Base",
        "#N/A",
        "#N/A"
    ],
    "baichuan2-7b": [
        "bos:/cce-ai-models/huggingface.co/baichuan-inc/Baichuan2-7B-Base",
        "1",
        "1"
    ],
    "baichuan2-13b": [
        "bos:/cce-ai-models/huggingface.co/baichuan-inc/Baichuan2-13B-Base",
        "1",
        "2"
    ],
    "llama-7b": [
        "bos:/cce-ai-datasets/huggingface.co/decapoda-research/llama-7b-hf",
        "#N/A",
        "#N/A"
    ],
    "llama-13b": [
        "bos:/cce-ai-datasets/huggingface.co/decapoda-research/llama-13b-hf",
        "#N/A",
        "#N/A"
    ],
    "llama-65b": [
        "bos:/cce-ai-datasets/huggingface.co/decapoda-research/llama-65b-hf",
        "#N/A",
        "#N/A"
    ],
    "llama2-7b": [
        "bos:/cce-ai-datasets/huggingface.co/meta-llama/Llama-2-7b-hf",
        "1",
        "1"
    ],
    "llama2-13b": [
        "bos:/cce-ai-datasets/huggingface.co/meta-llama/Llama-2-13b-hf",
        "1",
        "2"
    ],
    "llama2-70b": [
        "bos:/cce-ai-datasets/huggingface.co/meta-llama/Llama-2-70b-hf",
        "4",
        "4"
    ],
    "llama3-8b": [
        "bos:/cce-ai-models/huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct",
        "1",
        "1"
    ],
    "llama3-70b": [
        "bos:/cce-ai-models/meta-llama/Meta-Llama-3-70B-Instruct",
        "4",
        "4"
    ],
    "llama3.1-8b": [
        "bos:/cce-ai-models/huggingface/meta-llama/Meta-Llama-3.1-8B-Instruct",
        "#N/A",
        "#N/A"
    ],
    "llama3.1-70b": [
        "bos:/cce-ai-models/huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct",
        "#N/A",
        "#N/A"
    ],
    "llama3.1-405b": [
        "bos:/cce-ai-models/huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct",
        "#N/A",
        "#N/A"
    ],
    "mixtral-8x7b": [
        "bos:/cce-ai-models/huggingface.co/mistralai/Mixtral-8x7B-v0.1",
        "1",
        "2"
    ],
    "mixtral-8x22b": [
        "bos:/cce-ai-datasets/huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1",
        "2",
        "2"
    ],
    "qwen-1.8b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen-1_8B",
        "1",
        "1"
    ],
    "qwen-7b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen-7B",
        "1",
        "1"
    ],
    "qwen-14b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen-14B",
        "1",
        "2"
    ],
    "qwen-72b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen-72B",
        "2",
        "8"
    ],
    "qwen1.5-0.5b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-0.5B",
        "1",
        "1"
    ],
    "qwen1.5-1.8b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-1.8B-Chat",
        "1",
        "1"
    ],
    "qwen1.5-4b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-4B",
        "1",
        "1"
    ],
    "qwen1.5-7b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-7B-Chat",
        "1",
        "1"
    ],
    "qwen1.5-14b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-14B-Chat",
        "1",
        "2"
    ],
    "qwen1.5-32b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-32B-Chat",
        "2",
        "4"
    ],
    "qwen1.5-72b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen1.5-72B-Chat",
        "2",
        "8"
    ],
    "qwen2-0.5b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen2-0.5B-Instruct",
        "1",
        "1"
    ],
    "qwen2-1.5b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen2-1.5B-Instruct",
        "1",
        "1"
    ],
    "qwen2-7b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen2-7B-Instruct",
        "1",
        "1"
    ],
    "qwen2-72b": [
        "bos:/cce-ai-models/huggingface.co/Qwen/Qwen2-72B-Instruct",
        "8",
        "4"
    ],
    "STDiT-XL/2": [
        "bos:/cce-ai-models/huggingface.co/hpcai-tech/OpenSora-STDiT-v2-stage3",
        "#N/A",
        "#N/A"
    ]
}

chain_info_temp = {
    "resourcePoolId": "cce-e0isdmib",
    "jobs": [
        {
            "name": "pretrain-qwen2-72b-ck-v1",
            "jobSpec": {
                    "command": "",
                    "image": "registry.baidubce.com/aihc-aiak/aiak-training-llm:ubuntu22.04-cu12.3-torch2.2.0-py310-bccl1.2.7.2_v2.1.1.5_release",
                    "replicas": 1,
                    "envs": []
            },
            "labels": [
                {
                    "key": "aijob.cce.baidubce.com/ai-user-id",
                    "value": "69bb4999b2044af8bbda25aec2f1e1f2"
                },
                {
                    "key": "aijob.cce.baidubce.com/ai-user-name",
                    "value": "zhangsan"
                }
            ],
            "datasources": [
                {
                    "type": "pfs",
                    "name": "pfs-oYQuh4",
                    "mountPath": "/root/pfs"
                }
            ],
            "queue": "default",
            "priority": "normal",
            "jobFramework": "PyTorchJob"
        },
        {
            "queue": "default",
            "priority": "normal",
            "jobFramework": "PyTorchJob",
            "name": "pretrain-qwen2-72b-dp-v1",
            "jobSpec": {
                    "command": "",
                    "image": "registry.baidubce.com/aihc-aiak/aiak-training-llm:ubuntu22.04-cu12.3-torch2.2.0-py310-bccl1.2.7.2_v2.1.1.5_release",
                    "replicas": 1,
                    "envs": []
            },
            "labels": [
                {
                    "key": "aijob.cce.baidubce.com/ai-user-id",
                    "value": "69bb4999b2044af8bbda25aec2f1e1f2"
                },
                {
                    "key": "aijob.cce.baidubce.com/ai-user-name",
                    "value": "zhangsan"
                }
            ],
            "datasources": [
                {
                    "type": "pfs",
                    "name": "pfs-oYQuh4",
                    "mountPath": "/root/pfs"
                }
            ]
        },
        {
            "queue": "default",
            "priority": "normal",
            "jobFramework": "PyTorchJob",
            "name": "pretrain-qwen2-72b-train-v1",
            "jobSpec": {
                    "command": "bash /workspace/AIAK-Training-LLM/examples/qwen2/pretrain/pretrain_qwen2_72b.sh",
                    "image": "registry.baidubce.com/aihc-aiak/aiak-training-llm:ubuntu22.04-cu12.3-torch2.2.0-py310-bccl1.2.7.2_v2.1.1.5_release",
                    "replicas": 4,
                    "resources": [
                        {
                            "name": "baidu.com/a800_80g_cgpu",
                            "quantity": 8
                        }
                    ],
                "enableRDMA": True,
                "envs": []
            },
            "labels": [
                {
                    "key": "aijob.cce.baidubce.com/ai-user-id",
                    "value": "69bb4999b2044af8bbda25aec2f1e1f2"
                },
                {
                    "key": "aijob.cce.baidubce.com/ai-user-name",
                    "value": "zhangsan"
                }
            ],
            "datasources": [
                {
                    "type": "pfs",
                    "name": "pfs-oYQuh4",
                    "mountPath": "/root/pfs"
                }
            ]
        }
    ]
}


def load_config(config_file):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"File {config_file} not found.")
    with open(config_file, 'r') as f:
        return json.load(f)


def get_models():
    return models


def get_datasets():
    return datasets


def get_command(file_path):
    return commands[file_path]


def get_command_from_sh(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found.")
    with open(file_path, 'r') as f:
        return f.read()


def write_chain_info(ak, sk, host):
    chain_info_temp['jobs'][0]['jobSpec']['envs'] = [
        {
            "name": "AK",
            "value": ak
        },
        {
            "name": "SK",
            "value": sk
        },
        {
            "name": "HOST",
            "value": host
        }]
    chain_info_temp['jobs'][1]['jobSpec']['envs'] = [
        {
            "name": "AK",
            "value": ak
        },
        {
            "name": "SK",
            "value": sk
        },
        {
            "name": "HOST",
            "value": host
        }]


def read_chain_info():
    return chain_info_temp


def generate_aiak_parameter(chain_job_config=None, aiak_job_config=None):
    args = sys.argv[1:]
    if chain_job_config is None or aiak_job_config is None:
        if len(args) < 2:
            print("Usage: python job_chain.py <config_file> [index]")
            return
        else:
            chain_job_config = args[0]
            aiak_job_config = args[1]

    # print('=============================\n')
    # print('chain_job_config:', chain_job_config)
    # print('aiak_job_config:', aiak_job_config)
    # print('=============================\n')

    try:
        aiak_job_config_json = json.loads(aiak_job_config)
        # print(json.dumps(aiak_job_config_json, indent=4, ensure_ascii=False))
        if 'MODEL_NAME' not in aiak_job_config_json:
            with open(aiak_job_config, mode='r', encoding='utf-8') as file:
                aiak_job_info = json.load(file)
        else:
            aiak_job_info = aiak_job_config_json
    except json.JSONDecodeError:
        with open(aiak_job_config, mode='r', encoding='utf-8') as file:
            aiak_job_info = json.load(file)

    # print(json.dumps(aiak_job_info, indent=4, ensure_ascii=False))
    # AIAK任务参数
    VERSION = aiak_job_info['VERSION']
    DATASET_NAME = aiak_job_info['DATASET_NAME']
    MODEL_NAME = aiak_job_info['MODEL_NAME']
    if aiak_job_info['TP'] and aiak_job_info['PP']:
        TP = aiak_job_info['TP']
        PP = aiak_job_info['PP']
    JSON_KEYS = aiak_job_info['JSON_KEYS'] if 'JSON_KEYS' in aiak_job_info else ''
    IMAGE = aiak_job_info['IMAGE']
    TRAINING_PHASE = aiak_job_info['TRAINING_PHASE']
    REPLICAS = aiak_job_info['REPLICAS']
    MOUNT_PATH = aiak_job_info['MOUNT_PATH']
    MODEL_URL = aiak_job_info['MODEL_URL'] if 'MODEL_URL' in aiak_job_info else ''
    DATASET_URL = aiak_job_info['DATASET_URL'] if 'DATASET_URL' in aiak_job_info else ''

    # print(json.dumps(models, indent=4, ensure_ascii=False))
    MODEL_BOS_PATH = MODEL_URL if MODEL_URL else models[MODEL_NAME][0]
    TP = models[MODEL_NAME][1]
    PP = models[MODEL_NAME][2]
    if aiak_job_info['TP'] and aiak_job_info['PP']:
        TP = aiak_job_info['TP']
        PP = aiak_job_info['PP']
    else:
        TP = models[MODEL_NAME][1]
        PP = models[MODEL_NAME][2]
    # print('MODEL_BOS_PATH：', MODEL_BOS_PATH)

    save_path = '/'.join(MODEL_BOS_PATH.split('/')[2:])

    LOAD = f'{MOUNT_PATH}/models/{MODEL_NAME}/hf/{save_path}'
    # print('LOAD：', LOAD)

    TOKENIZER_PATH = LOAD
    # print('TOKENIZER_PATH：', TOKENIZER_PATH)

    CHECKPOINT_PATH = f'{MOUNT_PATH}/models/{MODEL_NAME}/mcore/{save_path}/tp{TP}_pp{PP}'
    # print('CHECKPOINT_PATH：', CHECKPOINT_PATH)

    DATASET_BOS_PATH = DATASET_URL if DATASET_URL else datasets[DATASET_NAME]
    # print('DATASET_BOS_PATH：', DATASET_BOS_PATH)

    save_path = '/'.join(DATASET_BOS_PATH.split('/')[2:])
    INPUT_DATA = f'{MOUNT_PATH}/datasets/{save_path}'
    # print('INPUT_DATA_PATH：', INPUT_DATA)

    save_path = '.'.join(INPUT_DATA.split('.')[0:-1])

    DATA_CACHE_PATH = f'{save_path}_cache'

    # INPUT_DATA去掉最后的文件名后缀
    OUTPUT_PREFIX = save_path
    # OUTPUT_PREFIX = INPUT_DATA

    # print('OUTPUT_PREFIX：', OUTPUT_PREFIX)

    DATA_PATH = f'{OUTPUT_PREFIX}_text_document'
    # print('DATA_PATH：', DATA_PATH)

    # CHECKPOINT_SAVE_PATH = f'{CHECKPOINT_PATH}/{VERSION}'

    CK_JOB_NAME = f'{TRAINING_PHASE}-{MODEL_NAME}-ck2mc-{VERSION}'
    DP_JOB_NAME = f'{TRAINING_PHASE}-{MODEL_NAME}-dp-{VERSION}'
    TRAIN_JOB_NAME = f'{TRAINING_PHASE}-{MODEL_NAME}-train-{VERSION}'

    chain_info = read_chain_info()
    # print(json.dumps(chain_info, indent=4, ensure_ascii=False))

    ck_job = chain_info['jobs'][0]
    ck_job['jobSpec']['image'] = IMAGE
    ck_job['name'] = CK_JOB_NAME

    ck_job['jobSpec']['command'] = get_command('job1_convert_checkpoint')
    envs = ck_job['jobSpec']['envs']
    ck_job['jobSpec']['envs'] = envs + [
        {
            'name': 'MODEL_BOS_PATH',
            'value': MODEL_BOS_PATH
        },
        {
            'name': 'MODEL_NAME',
            'value': MODEL_NAME
        },
        {
            'name': 'TP',
            'value': TP
        },
        {
            'name': 'PP',
            'value': PP
        },
        {
            'name': 'LOAD',
            'value': LOAD
        },
        {
            'name': 'SAVE',
            'value': CHECKPOINT_PATH
        }
    ]

    # print(json.dumps(ck_job, indent=4, ensure_ascii=False))

    dp_job = chain_info['jobs'][1]
    dp_job['jobSpec']['image'] = IMAGE
    dp_job['name'] = DP_JOB_NAME

    sh_path = f'job2_{TRAINING_PHASE}_data_preprocess'
    CHAT_TEMPLATE = (MODEL_NAME.split('-')[0]
                     if MODEL_NAME.startswith('qwen') is not True
                     else 'qwen')
    dp_job['jobSpec']['command'] = get_command(sh_path)
    envs = dp_job['jobSpec']['envs']
    if TRAINING_PHASE == 'sft':
        dp_job['jobSpec']['envs'] = envs + [
            {
                'name': 'DATASET_BOS_PATH',
                'value': DATASET_BOS_PATH
            },
            {
                'name': 'TOKENIZER_PATH',
                'value': TOKENIZER_PATH
            },
            {
                'name': 'INPUT_DATA',
                'value': INPUT_DATA
            },
            {
                'name': 'OUTPUT_PATH',
                'value': OUTPUT_PREFIX
            },
            {
                'name': 'CHAT_TEMPLATE',
                'value': CHAT_TEMPLATE
            }
        ]
    else:
        dp_job['jobSpec']['envs'] = [
            {
                'name': 'DATASET_BOS_PATH',
                'value': DATASET_BOS_PATH
            },
            {
                'name': 'TOKENIZER_PATH',
                'value': TOKENIZER_PATH
            },
            {
                'name': 'INPUT_DATA',
                'value': INPUT_DATA
            },
            {
                'name': 'OUTPUT_PREFIX',
                'value': OUTPUT_PREFIX
            },
            {
                'name': 'JSON_KEYS',
                'value': JSON_KEYS
            }
        ]

    # print(json.dumps(dp_job, indent=4, ensure_ascii=False))

    train_job = chain_info['jobs'][2]
    train_job['jobSpec']['image'] = IMAGE
    train_job['name'] = TRAIN_JOB_NAME

    if TRAINING_PHASE == 'sft':
        train_job['jobSpec']['envs'] = [
            {
                'name': 'CUDA_DEVICE_MAX_CONNECTIONS',
                'value': '1'
            },
            {
                'name': 'DATA_PATH',
                'value': INPUT_DATA
            },
            {
                'name': 'DATA_CACHE_PATH',
                'value': DATA_CACHE_PATH
            },
            {
                'name': 'TOKENIZER_PATH',
                'value': TOKENIZER_PATH
            },
            {
                'name': 'CHECKPOINT_PATH',
                'value': CHECKPOINT_PATH
            },
        ]

    else:
        train_job['jobSpec']['envs'] = [
            {
                "name": "CUDA_DEVICE_MAX_CONNECTIONS",
                "value": "1"
            },
            {
                'name': 'DATA_PATH',
                'value': DATA_PATH
            },
            {
                'name': 'TOKENIZER_PATH',
                'value': TOKENIZER_PATH
            },
            {
                'name': 'CHECKPOINT_PATH',
                'value': CHECKPOINT_PATH
            }
        ]

    SH_PATH = (
        f'/workspace/AIAK-Training-LLM/examples/{MODEL_NAME.split("-")[0]}/pretrain/pretrain_{MODEL_NAME.replace("-", "_")}.sh'
    )
    if TRAINING_PHASE == 'sft':
        SH_PATH = '/workspace/AIAK-Training-LLM/examples/' + \
            MODEL_NAME.split('-')[0] \
            + f'/finetuning/sft_{MODEL_NAME.replace("-", "_")}.sh'
    # print('SH_PATH：', SH_PATH)

    train_job['jobSpec']['command'] = f'bash {SH_PATH}'
    train_job['jobSpec']['replicas'] = int(REPLICAS)

    # print(json.dumps(train_job, indent=4, ensure_ascii=False))

    chain_info['jobs'][0] = ck_job
    chain_info['jobs'][1] = dp_job
    chain_info['jobs'][2] = train_job

    # print(chain_info)
    # print(json.dumps(chain_info, indent=4, ensure_ascii=False))

    chain_job_config_file = f'{chain_job_config}/{TRAIN_JOB_NAME}.json'
    with open(chain_job_config_file, 'w') as f:
        json.dump(chain_info, f, indent=4, ensure_ascii=False)

    one_job_command = (
        '#!/bin/bash\n\n'
        f'# 任务名称: {TRAIN_JOB_NAME}\n'
        f'# 镜像: {IMAGE}\n'
        f'# 环境变量: CUDA_DEVICE_MAX_CONNECTIONS=1\n'
        f'# 挂载路径: {MOUNT_PATH}\n'
        f'# 实例数量: {REPLICAS}\n\n'
        f'export MODEL_BOS_PATH="{MODEL_BOS_PATH}"\n'
        f'export MODEL_NAME="{MODEL_NAME}"\n'
        f'export TP={TP}\n'
        f'export PP={PP}\n'
        f'export LOAD="{LOAD}"\n'
        f'export SAVE="{CHECKPOINT_PATH}"\n'
        f'export TOKENIZER_PATH="{TOKENIZER_PATH}"\n'
        f'export DATASET_BOS_PATH="{DATASET_BOS_PATH}"\n'
        f'export INPUT_DATA="{INPUT_DATA}"\n'
        f'export OUTPUT_PREFIX="{OUTPUT_PREFIX}"\n'
        f'export OUTPUT_PATH="{OUTPUT_PREFIX}"\n'
        f'export DATA_PATH="{DATA_PATH}"\n'
        f'export DATA_CACHE_PATH="{DATA_CACHE_PATH}"\n'
        f'export JSON_KEYS="{JSON_KEYS}"\n'
        f'export CHAT_TEMPLATE="{CHAT_TEMPLATE}"\n'
        f'export CHECKPOINT_PATH="{CHECKPOINT_PATH}"\n'
        f'export CUDA_DEVICE_MAX_CONNECTIONS=1\n\n'
        f'{ck_job["jobSpec"]["command"].replace("#!/bin/bash", "")}\n'
        f'{dp_job["jobSpec"]["command"].replace("#!/bin/bash", "")}\n'
        f'{train_job["jobSpec"]["command"]}\n'
    )

    one_job_command_config_file = f'{chain_job_config}/{TRAIN_JOB_NAME}.sh'
    print(one_job_command_config_file)
    # print(one_job_command)
    with open(one_job_command_config_file, 'w') as f:
        f.write(one_job_command)

    run_command = f'python job_chain.py {chain_job_config_file}'
    print('=============================\n')
    print('任务配置信息：', json.dumps(aiak_job_info, ensure_ascii=False))
    print('任务配置文件已生成：', chain_job_config_file)
    print('任务启动命令：', one_job_command_config_file)
    print('启动任务：', run_command)
    print('\n=============================')

    return {
        "one_job_command_config": one_job_command_config_file,
        "chain_job_config": chain_job_config,
        "run_command": run_command
    }


def validate_index(index, jobs_count):
    if index < 0 or index >= jobs_count:
        raise IndexError(f"Index {index} is out of range.")


def build_command(job_chain_info, config_dir, index):
    jobs = job_chain_info['jobs']
    job_info = jobs[index]
    jobs_count = len(jobs)

    command = job_info['jobSpec']['command']
    if 'scriptFile' in job_info['jobSpec']:
        scriptFile = job_info['jobSpec']['scriptFile']
        command = get_command_from_sh(f'{config_dir}/{scriptFile}')
        del job_info['jobSpec']['scriptFile']

    if index != jobs_count - 1:
        jobs_str = json.dumps(job_chain_info)

        # 保存配置文件
        command_save_chain_info = f"cat << 'EOF' > /workspace/chain_info.json\n{jobs_str}\nEOF"

        command_pip_install = r"""
echo "job_chain:The previous task has been completed."
pip install future
pip install pycryptodome
pip install bce-python-sdk-next --index-url https://pypi.org/simple
pip install python-dotenv
echo "job_chain:Next job is to be continued..."
"""

        with open(f'{cur_path}/job_chain.py', 'r') as f:
            py_str = f.read()

        command_save_py = f"cat << 'EOF' > /workspace/job_chain.py\n{py_str}\nEOF"
        command_call_py = f'python /workspace/job_chain.py /workspace/chain_info.json {index + 1}'

        command = f'{command}\n{command_save_chain_info}\n{command_pip_install}\n{command_save_py}\n{command_call_py}'

    return command
