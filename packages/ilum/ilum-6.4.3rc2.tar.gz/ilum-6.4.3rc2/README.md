# Ilum Job API Python Package

![PyPI - Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10-blue)
![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)

This package provides an interface for interacting with Ilum's Job API using Python. With this package, you can create your own interactive spark job.
## Installation
Use pip to install the ilum-job-api package:

```bash
pip install ilum
```

## Usage
Here's a simple example of how to use it:

```python
from ilum.api import IlumJob
from random import random
from operator import add


class SparkPiInteractiveExample(IlumJob):

    def run(self, spark, config):
        partitions = int(config.get('partitions', '5'))
        n = 100000 * partitions

        def f(_: int) -> float:
            x = random() * 2 - 1
            y = random() * 2 - 1
            return 1 if x ** 2 + y ** 2 <= 1 else 0

        count = spark.sparkContext.parallelize(range(1, n + 1), partitions).map(f).reduce(add)

        return "Pi is roughly %f" % (4.0 * count / n)
```

For more detailed usage instructions, see our [Documentation](https://ilum.cloud/docs/) and [API Reference](https://ilum.cloud/docs/api/).

## License
This project is licensed under the terms of the Apache License 2.0.

## Contact
If you have any issues or feature requests, please [create an idea](https://roadmap.ilum.cloud/boards/feature-requests) on our board. For general questions or discussions, post a question [here](https://roadmap.ilum.cloud/boards/questions).
