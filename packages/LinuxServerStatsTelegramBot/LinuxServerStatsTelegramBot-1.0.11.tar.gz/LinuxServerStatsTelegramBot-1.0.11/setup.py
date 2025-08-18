from setuptools import setup, find_packages
import subprocess

git_command_result: subprocess.CompletedProcess = subprocess.run(
    ["git", "describe", "--tags"], capture_output=True, encoding="utf-8"
)
actual_version: str = git_command_result.stdout.strip("\n") or "1.0.1"

setup(
    name="LinuxServerStatsTelegramBot",
    version=actual_version,
    packages=find_packages(),
    url="",
    license="MIT",
    author="Juares Vermelho Diaz",
    author_email="j.vermelho@gmail.com",
    description="Telegram bot manager to show linux server stats",
    entry_points={
        "console_scripts": [
            "send_stats_by_telegram = LinuxServerStatsTelegramBot.cli:notify_server_stats",
            "start_bot = LinuxServerStatsTelegramBot.bot:main",
        ]
    },
    package_data={"": ["assets/*.webp"]},
    include_package_data=True,
    install_requires=[
        "anyio==4.10.0; python_version >= '3.9'",
        "certifi==2025.8.3; python_version >= '3.7'",
        "charset-normalizer==3.4.3; python_version >= '3.7'",
        "click==8.1.8; python_version >= '3.7'",
        "croniter==6.0.0; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "decorator==5.2.1; python_version >= '3.8'",
        "exceptiongroup==1.3.0; python_version < '3.11'",
        "future==1.0.0; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "geocoder==1.38.1",
        "gps==3.19",
        "h11==0.16.0; python_version >= '3.8'",
        "httpcore==1.0.9; python_version >= '3.8'",
        "httpx==0.28.1; python_version >= '3.8'",
        "idna==3.10; python_version >= '3.6'",
        "pillow==11.3.0; python_version >= '3.9'",
        "python-crontab==3.3.0",
        "python-dateutil==2.9.0.post0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-nmap==0.7.1",
        "python-telegram-bot==22.3; python_version >= '3.9'",
        "pytz==2025.2",
        "ratelim==0.1.6",
        "requests==2.32.4; python_version >= '3.8'",
        "six==1.17.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "sniffio==1.3.1; python_version >= '3.7'",
        "typing-extensions==4.14.1; python_version < '3.13'",
        "urllib3==2.5.0; python_version >= '3.9'",
    ],
)
