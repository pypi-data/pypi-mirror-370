## What is AgentBox?
[AgentBox](https://agentbox.lingyiwanwu.net/) is an infrastructure that allows you to run AI-generated code in secure isolated android sandboxes in the cloud.

## Run your first Sandbox

### 1. Install SDK

```
pip install agentbox-python-sdk
```

### 2. Get your AgentBox API key
1. Sign up to AgentBox [here](https://agentbox.lingyiwanwu.net).
2. Get your API key [here](https://agentbox.lingyiwanwu.net/dashboard?tab=keys).
3. Set environment variable with your API key 

### 3. Execute code with code interpreter inside Sandbox

```py
from agentbox import Sandbox

sbx = Sandbox(api_key="e2b_xxx_xxx_xxx",
              template="tpl_xxx_xxx_xxx",
              timeout=120)
sbx.commands.run(cmd="ls /")
```

### 4. Check docs
Visit [AgentBox documentation](https://agentbox.lingyiwanwu.net/docs).
