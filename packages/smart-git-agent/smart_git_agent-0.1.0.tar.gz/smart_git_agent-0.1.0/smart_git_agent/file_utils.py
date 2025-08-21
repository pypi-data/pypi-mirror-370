import logging
import os
import re
import hashlib
from typing import Set, Optional, Dict
import fnmatch
import json

logger = logging.getLogger(__name__)


class FileUtils:
    def __init__(self, repo_path: str, config: dict):
        self.repo_path = repo_path
        self.detected_languages = self._detect_project_languages()
        self.ignored_patterns = self._load_ignored_patterns(config)
        self.file_hashes = {}
        self._ensure_gitignore()

    def _detect_project_languages(self) -> Set[str]:
        """Auto-detect project languages/frameworks based on files present."""
        languages = set()

        # Check for common files in repo root
        root_files = []
        if os.path.exists(self.repo_path):
            root_files = os.listdir(self.repo_path)

        # Python
        if any(f in root_files for f in ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock']):
            languages.add('python')
        elif any(f.endswith('.py') for f in root_files):
            languages.add('python')

        # Node.js/JavaScript
        if 'package.json' in root_files:
            languages.add('nodejs')
            # Try to detect specific frameworks
            try:
                with open(os.path.join(self.repo_path, 'package.json'), 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}

                    if 'next' in deps or 'next.js' in deps:
                        languages.add('nextjs')
                    if 'react' in deps:
                        languages.add('react')
                    if 'vue' in deps:
                        languages.add('vue')
                    if 'svelte' in deps:
                        languages.add('svelte')
                    if 'vite' in deps:
                        languages.add('vite')
                    if 'nuxt' in deps:
                        languages.add('nuxt')
                    if '@angular/core' in deps:
                        languages.add('angular')
                    if 'electron' in deps:
                        languages.add('electron')
            except:
                pass

        # Check for specific config files
        config_files = {
            'vite.config.js': 'vite',
            'vite.config.ts': 'vite',
            'next.config.js': 'nextjs',
            'next.config.mjs': 'nextjs',
            'nuxt.config.js': 'nuxt',
            'nuxt.config.ts': 'nuxt',
            'angular.json': 'angular',
            'vue.config.js': 'vue',
            'svelte.config.js': 'svelte',
        }

        for config_file, lang in config_files.items():
            if config_file in root_files:
                languages.add(lang)

        # Web technologies
        if any(f.endswith(('.html', '.css', '.js', '.ts')) for f in root_files):
            languages.add('web')

        # Rust
        if 'Cargo.toml' in root_files:
            languages.add('rust')

        # Go
        if 'go.mod' in root_files or any(f.endswith('.go') for f in root_files):
            languages.add('go')

        # Java/Kotlin
        if any(f in root_files for f in ['pom.xml', 'build.gradle', 'build.gradle.kts']):
            languages.add('java')

        # C#/.NET
        if any(f.endswith(('.csproj', '.sln')) for f in root_files) or 'Program.cs' in root_files:
            languages.add('csharp')

        # PHP
        if 'composer.json' in root_files or any(f.endswith('.php') for f in root_files):
            languages.add('php')

        # Ruby
        if 'Gemfile' in root_files or any(f.endswith('.rb') for f in root_files):
            languages.add('ruby')

        # Docker
        if any(f in root_files for f in ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml']):
            languages.add('docker')

        # Flutter/Dart
        if 'pubspec.yaml' in root_files:
            languages.add('flutter')

        # Swift
        if any(f.endswith(('.xcodeproj', '.xcworkspace')) for f in root_files) or 'Package.swift' in root_files:
            languages.add('swift')

        logger.info(f"🔍 Detected languages/frameworks: {', '.join(languages) if languages else 'generic'}")
        return languages

    def _get_language_patterns(self) -> Dict[str, Set[str]]:
        """Get ignore patterns for each detected language/framework."""
        patterns = {
            'python': {
                # Python bytecode
                '__pycache__',
                '*.py[cod]',
                '*$py.class',
                '*.so',
                '.Python',
                'pip-log.txt',
                'pip-delete-this-directory.txt',

                # Distribution / packaging
                '.Python',
                'build',
                'develop-eggs',
                'dist',
                'downloads',
                'eggs',
                '.eggs',
                'lib',
                'lib64',
                'parts',
                'sdist',
                'var',
                'wheels',
                'share/python-wheels',
                '*.egg-info',
                '.installed.cfg',
                '*.egg',
                'MANIFEST',

                # Virtual environments
                '.env',
                '.venv',
                'env',
                'venv',
                'ENV',
                'env.bak',
                'venv.bak',
                'pyvenv.cfg',

                # Testing
                '.tox',
                '.nox',
                '.coverage',
                '.coverage.*',
                '.cache',
                'nosetests.xml',
                'coverage.xml',
                '*.cover',
                '*.py,cover',
                '.hypothesis',
                '.pytest_cache',
                '.mypy_cache',
                '.dmypy.json',
                'dmypy.json',

                # Jupyter
                '.ipynb_checkpoints',

                # pyenv
                '.python-version',
            },

            'nodejs': {
                # Dependencies
                'node_modules',
                'npm-debug.log*',
                'yarn-debug.log*',
                'yarn-error.log*',
                'lerna-debug.log*',

                # Runtime data
                'pids',
                '*.pid',
                '*.seed',
                '*.pid.lock',

                # Coverage directory used by tools like istanbul
                'coverage',
                '*.lcov',

                # nyc test coverage
                '.nyc_output',

                # Grunt intermediate storage
                '.grunt',

                # Bower dependency directory
                'bower_components',

                # node-waf configuration
                '.lock-wscript',

                # Compiled binary addons
                'build/Release',

                # Dependency directories
                'jspm_packages',

                # Optional npm cache directory
                '.npm',

                # Optional eslint cache
                '.eslintcache',

                # Output of 'npm pack'
                '*.tgz',

                # Yarn Integrity file
                '.yarn-integrity',

                # parcel-bundler cache
                '.cache',
                '.parcel-cache',

                # yarn v2
                '.yarn/cache',
                '.yarn/unplugged',
                '.yarn/build-state.yml',
                '.yarn/install-state.gz',
                '.pnp.*',
            },

            'nextjs': {
                '.next',
                'next-env.d.ts',
                '.vercel',
                'out',
            },

            'react': {
                'build',
                '.expo',
                '.expo-shared',
            },

            'vue': {
                '.nuxt',
                'dist',
            },

            'nuxt': {
                '.nuxt',
                '.output',
                '.env',
                'dist',
            },

            'vite': {
                'dist',
                'dist-ssr',
                '*.local',
            },

            'angular': {
                'dist',
                'tmp',
                'out-tsc',
                'bazel-out',
                '.angular',
            },

            'svelte': {
                '.svelte-kit',
                'package',
                '.env.*',
                '!.env.example',
            },

            'rust': {
                'target',
                'Cargo.lock',
                '*.rs.bk',
                '*.pdb',
            },

            'go': {
                '*.exe',
                '*.exe~',
                '*.dll',
                '*.so',
                '*.dylib',
                'vendor',
                '*.test',
                '*.out',
                'go.work',
            },

            'java': {
                'target',
                '*.class',
                '*.log',
                '*.ctxt',
                '.mtj.tmp',
                '*.jar',
                '*.war',
                '*.nar',
                '*.ear',
                '*.zip',
                '*.tar.gz',
                '*.rar',
                'hs_err_pid*',
                'replay_pid*',
                '.gradle',
                'build',
                'gradle-app.setting',
                '!gradle-wrapper.jar',
                '.gradletasknamecache',
            },

            'csharp': {
                'bin',
                'obj',
                '*.user',
                '*.userosscache',
                '*.sln.docstates',
                '.vs',
                '[Dd]ebug',
                '[Dd]ebugPublic',
                '[Rr]elease',
                '[Rr]eleases',
                'x64',
                'x86',
                'bld',
                '[Bb]in',
                '[Oo]bj',
                '*.dll',
                '*.exe',
                '*.pdb',
            },

            'php': {
                'vendor',
                'composer.lock',
                '*.log',
                '.env',
                '.env.local',
                '.env.*.local',
            },

            'ruby': {
                '*.gem',
                '*.rbc',
                '.bundle',
                '.config',
                'coverage',
                'InstalledFiles',
                'lib/bundler/man',
                'pkg',
                'rdoc',
                'spec/reports',
                'test/tmp',
                'test/version_tmp',
                'tmp',
                '.yardoc',
                '_yardoc',
                'doc',
            },

            'flutter': {
                '.dart_tool',
                '.flutter-plugins',
                '.flutter-plugins-dependencies',
                '.packages',
                '.pub-cache',
                '.pub',
                'build',
            },

            'swift': {
                'build',
                'DerivedData',
                '*.hmap',
                '*.ipa',
                '*.dSYM.zip',
                '*.dSYM',
                'timeline.xctimeline',
                'playground.xcworkspace',
                '.build',
                'Packages',
                '*.xcodeproj/project.xcworkspace',
                '*.xcodeproj/xcuserdata',
                '*.xcworkspace/xcuserdata',
            },

            'docker': {
                '.dockerignore',
            },

            'web': {
                '*.map',
                'dist',
                'build',
            },
        }

        # Common patterns for all projects
        common_patterns = {
            # IDE and editors
            '.vscode',
            '.idea',
            '*.swp',
            '*.swo',
            '*.tmp',
            '*~',
            '.sublime-project',
            '.sublime-workspace',

            # OS files
            '.DS_Store',
            '.DS_Store?',
            '._*',
            '.Spotlight-V100',
            '.Trashes',
            'ehthumbs.db',
            'Thumbs.db',
            'Desktop.ini',

            # Logs
            '*.log',
            'logs',
            'log',

            # Environment files
            '.env',
            '.env.local',
            '.env.development.local',
            '.env.test.local',
            '.env.production.local',

            # Backup files
            '*.bak',
            '*.backup',
            '*.old',
            '*.orig',

            # Compressed files (generally)
            '*.7z',
            '*.dmg',
            '*.gz',
            '*.iso',
            '*.rar',
            '*.tar',
            '*.zip',
        }

        patterns['common'] = common_patterns
        return patterns

    def _ensure_gitignore(self):
        """Create a comprehensive .gitignore based on detected languages."""
        gitignore_path = os.path.join(self.repo_path, '.gitignore')
        if os.path.exists(gitignore_path):
            return

        language_patterns = self._get_language_patterns()
        gitignore_content = ["# Auto-generated .gitignore", "# Created by Smart Git Agent", ""]

        # Add common patterns first
        if 'common' in language_patterns:
            gitignore_content.extend([
                "# === Common files ===",
                *sorted(language_patterns['common']),
                ""
            ])

        # Add patterns for each detected language
        for lang in sorted(self.detected_languages):
            if lang in language_patterns:
                gitignore_content.extend([
                    f"# === {lang.upper()} ===",
                    *sorted(language_patterns[lang]),
                    ""
                ])

        try:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(gitignore_content))

            detected_langs = ', '.join(sorted(self.detected_languages)) if self.detected_languages else 'generic'
            logger.info(f"✅ Created .gitignore for: {detected_langs}")

        except Exception as e:
            logger.warning(f"Could not create .gitignore: {e}")

    def _load_ignored_patterns(self, config: dict) -> Set[str]:
        """Load all ignore patterns."""
        patterns = set()

        # Get patterns for detected languages
        language_patterns = self._get_language_patterns()

        # Add common patterns
        if 'common' in language_patterns:
            patterns.update(language_patterns['common'])

        # Add patterns for detected languages
        for lang in self.detected_languages:
            if lang in language_patterns:
                patterns.update(language_patterns[lang])

        # Add patterns from existing .gitignore
        patterns.update(self._load_gitignore_patterns())

        # Add custom patterns from config
        patterns.update(self._load_custom_patterns(config))

        return patterns

    def _load_gitignore_patterns(self) -> Set[str]:
        """Load patterns from .gitignore file."""
        gitignore_path = os.path.join(self.repo_path, '.gitignore')
        patterns = set()

        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and line != '/':
                            pattern = line.lstrip('/')
                            if pattern:
                                patterns.add(pattern)
            except Exception as e:
                logger.warning(f"Error reading .gitignore: {e}")

        return patterns

    def _load_custom_patterns(self, config: dict) -> Set[str]:
        """Load custom patterns from config."""
        patterns = set()
        config_patterns = config.get('ignored_patterns', '').split(',')

        for pattern in config_patterns:
            pattern = pattern.strip()
            if pattern:
                patterns.add(pattern)

        return patterns

    def should_ignore_file(self, file_path: str) -> bool:
        """Check if a file should be ignored using glob patterns."""
        try:
            relative_path = os.path.relpath(file_path, self.repo_path)
        except ValueError:
            return True

        relative_path = relative_path.replace(os.sep, '/')

        for pattern in self.ignored_patterns:
            pattern = pattern.replace(os.sep, '/')

            if self._match_pattern(relative_path, pattern):
                logger.debug(f"🚫 Ignoring {relative_path} (matches: {pattern})")
                return True

            path_parts = relative_path.split('/')
            for i in range(len(path_parts)):
                partial_path = '/'.join(path_parts[:i + 1])
                if self._match_pattern(partial_path, pattern):
                    logger.debug(f"🚫 Ignoring {relative_path} (parent {partial_path} matches: {pattern})")
                    return True

        return False

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a gitignore-style pattern."""
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            return path == pattern or path.startswith(pattern + '/')

        if '*' in pattern or '?' in pattern:
            return fnmatch.fnmatch(path, pattern)

        if path == pattern:
            return True

        if '/' in path:
            dir_path = path.split('/')[0]
            if dir_path == pattern:
                return True

        return False

    def calculate_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate the hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (OSError, IOError) as e:
            logger.debug(f"Could not read file {file_path}: {e}")
            return None

    def update_file_hashes(self, repo):
        """Update hashes for all files in the repo."""
        self.file_hashes.clear()
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d != '.git']

            for file in files:
                file_path = os.path.join(root, file)
                if not self.should_ignore_file(file_path):
                    hash_value = self.calculate_file_hash(file_path)
                    if hash_value:
                        self.file_hashes[file_path] = hash_value

    def has_meaningful_changes(self, repo) -> bool:
        """Check if there are significant changes."""
        try:
            diff_files = []
            try:
                diff_files = [item.a_path for item in repo.index.diff("HEAD")]
            except:
                diff_files = [item.a_path for item in repo.index.diff(None)]

            untracked_files = repo.untracked_files

            logger.debug(f"📝 Diff files: {diff_files}")
            logger.debug(f"📄 Untracked files: {untracked_files}")

            if not diff_files and not untracked_files:
                return False

            significant_changes = 0

            for file_path in diff_files:
                full_path = os.path.join(self.repo_path, file_path)

                if self.should_ignore_file(full_path):
                    logger.debug(f"⏭️ Skipping modified file (ignored): {file_path}")
                    continue

                significant_changes += 1
                logger.debug(f"✅ Significant change detected: {file_path}")

            for file_path in untracked_files:
                full_path = os.path.join(self.repo_path, file_path)

                if self.should_ignore_file(full_path):
                    logger.debug(f"⏭️ Skipping untracked file (ignored): {file_path}")
                    continue

                significant_changes += 1
                logger.debug(f"✅ Significant untracked file: {file_path}")

            logger.debug(f"📊 Total significant changes: {significant_changes}")
            return significant_changes > 0

        except Exception as e:
            logger.error(f"Error checking changes: {e}")
            return False