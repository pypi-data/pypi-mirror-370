# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="SkillsManager",
    version="0.2.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyperclip",
        "pyautogui",
        "python-dotenv",
        "google-genai",
        "uv",
        "SkillLink",
        "SyncLink",
        "SynMem",
        "SynLrn",
        "BitSig",
    ],
    author="Tristan McBride Sr.",
    author_email="TristanMcBrideSr@users.noreply.github.com",
    description="Modern manager for AI skills, tools, loading, execution, and automation.",
)
