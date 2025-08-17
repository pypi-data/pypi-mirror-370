# skimly (Python)

```python
from skimly import Skimly
client = Skimly.from_env()
blob_id = client.create_blob("long text")
res = client.chat(provider="openai", model="gpt-4.1-mini",
                  messages=[{"role":"user","content":[
                    {"type":"text","text":"Summarize"},
                    {"type":"pointer","blob_id": blob_id}
                  ]}])
print(res["skimly"])
```
