import glob
import io
import re
import subprocess
import sys
from enum import Enum
from typing import Tuple

__version__ = '0.3.0'


def get_output(*args):
    return subprocess.check_output(args, universal_newlines=True).strip()


def sh(*args):
    return subprocess.check_call(args)


def compile_string_decl_regex(var_name):
    return re.compile(
        r'^({}\s*=\s*)([\'"])(.*?)\2$'.format(var_name), re.MULTILINE
    )


class VersionFile:
    def __init__(self, file_name, version_re):
        self.file_name = file_name
        self.version_re = version_re

    def get_version(self):
        return find_string_declaration(self.file_name, self.version_re)

    def replace_version(self, new_version):
        with io.open(self.file_name, "rt", encoding="utf8") as f:
            new_content = self.version_re.sub(
                r'\g<1>\g<2>{}\g<2>'.format(new_version), f.read()
            )

        with io.open(self.file_name, "wt", encoding="utf8") as f:
            f.write(new_content)


def get_setup_version():
    return get_output('python', 'setup.py', '--version')


def get_version_file():
    # Try __version__ in separate VERSION_FILE
    file_name = find_string_declaration(
        'setup.py', compile_string_decl_regex('VERSION_FILE')
    )
    if file_name:
        return VersionFile(file_name, compile_string_decl_regex('__version__'))

    # Try VERSION directly in setup.py
    just_version_re = compile_string_decl_regex('VERSION')
    if find_string_declaration('setup.py', just_version_re):
        return VersionFile('setup.py', just_version_re)

    raise ValueError('Cannot figure out where your version is set')


def find_string_declaration(python_file, string_decl_re):
    with io.open(python_file, "rt", encoding="utf8") as f:
        match = string_decl_re.search(f.read())
        if match:
            return match.group(3)


def tag(version, message):
    sh('git', 'tag', '-a', 'v{}'.format(version), '-m', message)


def build_and_upload():
    # We want to release at the very end. That ensures that whatever
    # we release is already properly tracked in the git remote.
    # Otherwise, changes in the git remote could prevent us from
    # pushing the exact changes we released to PyPI.
    sh('python', 'setup.py', 'sdist')
    sh('git', 'push')
    sh('git', 'push', '--tags')
    sh('twine', 'upload', *glob.glob('dist/*'))


def prepare() -> Tuple[str, VersionFile]:
    assert (
        get_output('git', 'symbolic-ref', 'HEAD') == 'refs/heads/master'
    ), 'Must be on master branch'
    assert (
        len(get_output('git', 'status', '-uno', '--porcelain=2').splitlines())
        == 0
    ), 'Working directory is not clean'

    sh('git', 'fetch', 'origin', 'master')
    assert get_output('git', 'rev-parse', 'HEAD') == get_output(
        'git', 'rev-parse', 'refs/remotes/origin/master'
    ), 'The branch must be up to date with origin'

    ver_file = get_version_file()
    assert ver_file, 'No VERSION_FILE defined in setup.py'
    old_file_version = ver_file.get_version()
    assert get_setup_version() == old_file_version, 'Version does not match'
    return old_file_version, ver_file


VERSION_SEPARATOR = '.'


class VersionComponent(Enum):
    Major = 'major'
    Minor = 'minor'
    Patch = 'patch'

    def bump(self, old_version: str) -> str:
        parts = [int(part) for part in old_version.split(VERSION_SEPARATOR)]
        index = self._index
        new_parts = (
            parts[:index]
            + [parts[index] + 1]
            + ([0] * (len(parts) - index - 1))
        )
        return VERSION_SEPARATOR.join(str(part) for part in new_parts)

    @property
    def _index(self) -> int:
        return list(VersionComponent).index(self)


FORMAT_HELP = 'Version should be in format 1.2.3, major, minor, or patch'


def get_new_version(old_version: str, requested_version: str) -> str:
    if re.match(r'^[\d.]+$', requested_version):
        return requested_version

    try:
        component = VersionComponent(requested_version)
    except ValueError as e:
        raise ValueError(FORMAT_HELP) from e

    return component.bump(old_version)


def release_with_version(requested_version):
    if requested_version.startswith('v'):
        requested_version = requested_version[1:]
    old_version, ver_file = prepare()
    assert old_version != requested_version, 'Already on {}'.format(
        requested_version
    )

    version = get_new_version(old_version, requested_version)

    ver_file.replace_version(version)

    assert (
        ver_file.get_version() == version
    ), 'File version does not match after update'
    assert (
        get_setup_version() == ver_file.get_version()
    ), 'Setup.py version does not match after update'
    message = 'Version bump to v{}'.format(version)

    sh('git', 'add', ver_file.file_name)
    sh('git', 'commit', '-m', message)

    tag(version, message)
    build_and_upload()

    print('Updated version to {}.'.format(version))


def main():
    if len(sys.argv) != 2:
        print('Usage: {} new_version'.format(sys.argv[0]))
        sys.exit(1)
    try:
        release_with_version(sys.argv[1])
    except AssertionError as e:
        print(e.args[0])
        sys.exit(1)


if __name__ == '__main__':
    main()
