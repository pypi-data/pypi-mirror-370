# fluidattacks-tracks

[![PyPI version](https://img.shields.io/pypi/v/fluidattacks-tracks.svg)](https://pypi.org/project/fluidattacks-tracks/)

<p align="center">
  <a href="https://fluidattacks.com/" rel="noopener" target="_blank">
  <img width="460px" src="https://res.cloudinary.com/fluid-attacks/image/upload/v1728418266/airs/logo/logo_full.png" alt="Fluid Attacks logo">
  </a>
</p>

This library provides a convenient way to report usage analytics from any Python 3.11+
application.

All operations run in a background thread, and errors are logged but don't propagate to the caller, ensuring your application's flow isn't interrupted.

## Usage

```python
from datetime import datetime, UTC
from fluidattacks_tracks import Tracks
from fluidattacks_tracks.resources.event import Event

client = Tracks()
client.event.create(
    Event(
        action="CREATE",
        author="author",
        date=datetime.now(UTC),
        mechanism="API",
        metadata={"foo": "bar"},
        object="object",
        object_id="object_id",
    )
)
```
