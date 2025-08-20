from setuptools import setup, find_packages

setup(
    name="asfenix-cpu",
    version="0.1.0",
    description="Framework de IA ligero y optimizado para CPU",
    author="Tu Nombre",
    packages=find_packages(),
    install_requires=["numpy", "numba"],
    python_requires=">=3.8",
)
