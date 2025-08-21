    

# Persian Text Normalizer (Hazm Fork)

This project is a lightweight fork of the Hazm library, focusing solely on the **Normalizer** class to normalize Persian text. It is designed for easy installation with minimal dependencies, avoiding the issues of deprecated packages and version mismatches.

### Features:

* Normalizes Persian text by removing unnecessary characters and correcting common text issues.
* No external dependencies or conflicting libraries, making it a lightweight option for Persian text processing.

### Installation:

To install this package, clone the repository and install the required dependencies using:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

or just use the pip-installable package
```bash
python -m venv env
source env/bin/activate
pip install pip_installable_package/hazm_normalizer-0.1.0-py3-none-any.whl
```
### Example Usage:

```python
from hazm_normalizer import Normalizer

# Initialize the Normalizer class
normalizer = Normalizer()

# Persian text to normalize
text = """
اصلاح نويسه‌ها و استفاده از نیم‌فاصله پردازش را آسان می‌کند و حروف عربي استفاده شده غلط مانند کُ و ي را حذف می‌کند.
"""

# Normalize the text
result = normalizer.normalize(text)

print(result)
'اصلاح نویسه‌ها و استفاده از نیم‌فاصله پردازش را آسان می‌کند و حروف عربی استفاده‌شده غلط مانند ک و‌ ی را حذف می‌کند. '

```

### License:

This project is a fork of the [Hazm project](https://github.com/roshan-research/hazm) and is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

### Future Work:

* Plan to publish this as a package on **PyPI** for easy installation via `pip`.
