### SWC Utils
> This repository contains a collection of utilities for SWC projects.

`pip install swc_utils`

`pip install swc_utils[extras]` (for all extras)

#### Email Login with united-domains
```python
from swc_utils.mail.smtp_client import SMTPClient

client = SMTPClient(
    "smtp.udag.de",
    465,
    "<default>@example.com",
    "<system name>",
    "<user>",
    "<password>"
)

client.send(
    ["<mail1>", "<mail2>"],
    "<content>",
    "<subject>",
    sender_email="sender@example.com"
)
```
