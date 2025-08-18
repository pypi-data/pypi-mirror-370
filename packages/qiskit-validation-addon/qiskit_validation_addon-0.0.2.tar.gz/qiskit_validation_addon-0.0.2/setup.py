from setuptools import setup, find_packages

setup(
    name="qiskit_validation_addon",
    version="0.1.0",
    description="Classify quantum circuits as Malicious or Benign using a finetuned LLM adapter.",
    author="Justin Woodring",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "peft",
        "bitsandbytes"
    ],
    python_requires='>=3.8',
)
