# Python Go Session Manager Plugin 

Python bindings for AWS Session Manager Plugin.

## Usage

```python
import go_smp
import boto3

instance='i-1234567890abcdefg'

session = boto3.Session(profile_name='your-profile')
client = session.client('ssm')

ssm_session = client.start_session(
    Target=instance
)

go_smp.start_session(
    ssm_session["SessionId"],
    ssm_session["StreamUrl"],
    ssm_session["TokenValue"],
    f"https://ssm.{session.region_name}.amazonaws.com",
    "some-unique-id",
    instance
)
```

## Roadmap

- [ ] Implement more methods to support ssm-cli
- [ ] Add pipelines to build cross platforms
- [ ] Add some tests