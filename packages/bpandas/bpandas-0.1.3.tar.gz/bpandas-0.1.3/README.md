[tool.poetry]
name = "bpandas"
version = "0.1.0"
description = "Funções utilitárias para facilitar o uso do pandas"
readme = "README.md"
license = "MIT"
authors = ["David Closs <davidcloss@live.com>"]
packages = [{ include = "bpandas" }]

# (opcional, deixa a página do PyPI mais completa)
keywords = ["pandas", "dataframe", "frequencies", "statistics", "utility"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.13",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  "Topic :: Scientific/Engineering :: Information Analysis"
]

[tool.poetry.urls]
Homepage = "https://github.com/davidcloss/bpandas"
Repository = "https://github.com/davidcloss/bpandas"
Issues = "https://github.com/davidcloss/bpandas/issues"

[tool.poetry.dependencies]
python = ">=3.13"
pandas = ">=2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
