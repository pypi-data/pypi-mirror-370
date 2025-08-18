from setuptools import setup
import re

def derive_version() -> str:
    version = ''
    with open('discord_py_role_panel_lib/__init__.py', encoding='utf-8') as f:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

    if not version:
        raise RuntimeError('version is not set')

    if version.endswith(('a', 'b', 'rc')):
        # append version identifier based on commit count
        try:
            import subprocess

            p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                version += out.decode('utf-8').strip()
            p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out:
                version += '+g' + out.decode('utf-8').strip()
        except Exception:
            pass

    return version

NAME = 'discord-py-role-panel-lib'

PACKAGES = [
    'discord_py_role_panel_lib',
    'discord_py_role_panel_lib.utils',
    'discord_py_role_panel_lib.cm',
    'discord_py_role_panel_lib.cmds',
    'discord_py_role_panel_lib.events',
    'discord_py_role_panel_lib.events.buttons',
    'discord_py_role_panel_lib.events.components'
]

setup(
    name=NAME,
    version=derive_version(),
    packages=PACKAGES,
    install_requires=[
        'discord.py>=2.5.2',
        # Add other dependencies here
    ],
    author='hashimotok',
    author_email='contact@hashimotok.dev',
    url=f'https://github.com/hashimotok-ecsv/{NAME}',
    download_url=f'https://github.com/hashimotok-ecsv/{NAME}',
    python_requires=">=3.10.6",
    description='A library to assist with Discord.py development',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    keywords='discord.py role panel library',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'discord-py-role-panel-lib=discord_py_role_panel_lib.__main__:main',
        ],
    },
    project_urls={
        'Documentation': f'https://{NAME}.readthedocs.io/',
        'Source': f'https://github.com/hashimotok-ecsv/{NAME}',
        'Tracker': f'https://github.com/hashimotok-ecsv/{NAME}/issues',
    },
    license='MIT',
    license_files=('LICENSE',),
)