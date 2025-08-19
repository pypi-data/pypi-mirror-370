# json-file-split
Split a json or jsonl file into different chunks.

## Installation 
```shell
pip install json-file-split
```

## Usage
```shell
json-file-split \
--input_file_path ./tests/data/test.jsonl \
--save_to_dir /tmp/output/ \
--output_file_name test.jsonl \
--split_by number_of_buckets \
--batch_size 10
```