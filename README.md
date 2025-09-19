

# ArtifactsBench: Bridging the Visual-Interactive Gap in LLM Code Generation Evaluation


### Environment Setup

```bash
pip install vllm==0.8.3
pip install pytest-playwright
playwright install
playwright install-deps
pip install transformers
pip install requests
pip install tqdm
```

### Data format
You can use your own model to perform inference based on the "question" field in the `dataset/artifacts_bench.json` file, and save the results in the "answer" field.
```JSON
{
    "index": "unique identifier in the dataset that corresponds one-to-one with 'question'",
    "question": "each 'question' in ArtifactsBench",
    "answer": "The answer inferred by your model based on the 'question'"
}
```

### Evaluation Using Gemini

```bash
api_key=xxx
model_marker=xxx
api_url=xxx
screenshots_count=3
path_with_index=xxx
save_path=xxx
screenshots_dir=xxx
tokenizer_dir=xxx
num_processes=16
python3 src/infer_gemini.py \
    $path_with_index \
    $save_path \
    $screenshots_dir \
    $screenshots_count \
    $api_key \
    $model_marker \
    $api_url \
    $tokenizer_dir \
    --num_processes $num_processes
```

#### Parameters Description
* **api\_key**: Your API key for accessing the Gemini model.
* **model\_marker**: The specific marker for the model to use in Gemini.
* **api\_url**: The URL endpoint for making the POST request to the server.
* **count**: The number of screenshots to feed into Gemini.
* **path\_with\_index**: The input file. Each entry in this file should include an 'index', 'question', and 'answer'.
* **save\_path**: The path where the results will be saved. Each entry will include two additional fields: `gemini_reason` (the explanation from Gemini) and `gemini_ans` (the score provided by Gemini).
* **screenshots\_dir**: The directory where the screenshots are stored.
* **tokenizer\_dir**: The directory for the tokenizer model, to prevent an excessive number of tokens.
* **num\_processes**: The number of processes to use for inference. For example, `16` processes.

### Evaluation Using Qwen2.5-VL-72B

```bash
# Deploy Qwen2.5-VL-72B-Instruct using vllm
MODEL_DIR="/xxx/Qwen2.5-VL-72B-Instruct"
HOST_IP=$(hostname -i)
model_name=$(basename $MODEL_DIR)
nohup python3 -m vllm.entrypoints.openai.api_server \
    --enforce-eager --swap-space 50 --disable-log-requests \
    --dtype float16 --trust-remote-code \
    --model ${MODEL_DIR} --served-model-name ${model_name} \
    --gpu-memory-utilization 0.9 --port 8088 \
    --max-model-len 32768 --max-seq-len 32768 \
    --limit-mm-per-prompt "image=5"\
    --tensor-parallel-size 8 \
    --seed 1024 > /root/log.ds_server 2> /root/err.ds_server &
sleep 10m

# Evaluate the answers with Qwen2.5-VL-72B-Instruct.
screenshots_count=3
path_with_index=xxx
save_path=xxx
screenshots_dir=xxx
tokenizer_dir=$MODEL_DIR
ip_file_path=$HOST_IP # ip or ip_list_file
num_processes=16
python3 src/infer_qvl.py \
  $path_with_index \
  $save_path \
  $screenshots_dir \
  $screenshots_count \
  $model_name \
  $tokenizer_dir \
  $ip_file_path \
  --num_processes $num_processes
```

#### Parameters Description
* **MODEL\_DIR**: The directory where the `Qwen2.5-VL-72B-Instruct` model is stored.
* **HOST\_IP**: The IP address of the host machine (obtained using `hostname -i`).
* **model\_name**: The name of the model (derived from the basename of `MODEL_DIR`).
* **screenshots\_count**: The number of screenshots to feed into Qwen2.5-VL-72B.
* **path\_with\_index**: The input file. Each entry should include an `index`, `question`, and `answer`.
* **save\_path**: The path where the results will be saved. Each entry will include two additional fields: `qvl_reason` (the explanation from Qwen2.5-VL-72B) and `qvl_ans` (the score provided by Qwen2.5-VL-72B).
* **screenshots\_dir**: The directory where the screenshots are stored.
* **tokenizer\_dir**: The directory for the tokenizer model, to prevent an excessive number of tokens.
* **ip\_file\_path**: The path to the file containing the IP addresses or IP list of the machines for distributed processing (e.g., `pssh.hosts`).
* **num\_processes**: The number of processes to use for inference (e.g., `16` processes).

