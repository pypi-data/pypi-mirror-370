
# descartcan

### LLM

#### Step1

llm_config.yaml

```yaml
openai:
  keys:
    - name: "openai_key1"
      api_key: "XXX"
  models:
    gpt4: "gpt-4-0125-preview"
    gpt40: "gpt-4o"

bedrock:
  keys:
    - name: "bedrock"
      api_key: "XXX"
      api_secret: "XXXXX"
  models:
      haiku35: "us.anthropic.claude-3-5-haiku-20241022-v1:0"

```

#### Step2 

load models

```python
from descartcan.llm.factory import LLModelFactory
model_factory = LLModelFactory.from_config(config="llm_config.yaml")
model = model_factory.get_model("openai.gpt4")

# 单轮对话
response = await model.chat(
    question="Show Python",
    system="你是一个编程专家"
)
print(f"回复: {response.content}")
print(f"Token统计: 提示词{response.prompt_tokens}, 生成{response.completion_tokens}, 总计{response.total_tokens}")

# 多轮对话
history = [
    {"role": "user", "content": "Python和Java的区别是什么？"},
    {"role": "assistant", "content": "Python和Java有以下主要区别：..."}
]

response = await model.chat(
    question="哪个更适合初学者？",
    system="你是一个编程专家",
    history=history
)
print(f"多轮对话回复: {response.content}")
```
