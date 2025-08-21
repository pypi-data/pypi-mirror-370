import json
import os
import requests
import logging
from typing import Dict
from .file_utils import FileUtils

logger = logging.getLogger(__name__)


class CommitAnalyzer:
    def __init__(self, config: dict, file_utils: FileUtils):
        self.config = config
        self.file_utils = file_utils
        self.commit_patterns = self._load_commit_patterns()

    def _load_commit_patterns(self) -> Dict[str, Dict]:
        """Load commit patterns with emojis."""
        return {
            'feat': {'emoji': '✨', 'keywords': ['add', 'create', 'implement', 'introduce', 'new']},
            'fix': {'emoji': '🐛', 'keywords': ['fix', 'resolve', 'correct', 'repair', 'bug', 'error']},
            'docs': {'emoji': '📚', 'keywords': ['readme', 'documentation', 'comment', 'doc']},
            'style': {'emoji': '💅', 'keywords': ['format', 'style', 'lint', 'prettier']},
            'refactor': {'emoji': '♻️', 'keywords': ['refactor', 'restructure', 'reorganize', 'rename', 'move']},
            'perf': {'emoji': '⚡', 'keywords': ['performance', 'optimize', 'speed', 'faster']},
            'test': {'emoji': '🧪', 'keywords': ['test', 'spec', 'unittest', 'testing']},
            'chore': {'emoji': '🔧', 'keywords': ['config', 'build', 'deps', 'dependency']},
            'security': {'emoji': '🔒', 'keywords': ['security', 'auth', 'permission']},
            'update': {'emoji': '🔄', 'keywords': ['update', 'upgrade', 'bump', 'change', 'modify', 'version']},
            'remove': {'emoji': '🗑️', 'keywords': ['remove', 'delete', 'clean']},
            'init': {'emoji': '🎉', 'keywords': ['initial', 'first', 'setup']}
        }

    def _analyze_diff_content(self, diff_content: str) -> str:
        """Analyze diff content to determine commit type based on content."""
        diff_lower = diff_content.lower()

        # Compter les lignes ajoutées vs supprimées
        added_lines = diff_content.count('\n+')
        removed_lines = diff_content.count('\n-')

        # Analyser le contenu pour détecter le type de changement

        # Fix - mots-clés de correction
        if any(keyword in diff_lower for keyword in ['fix', 'bug', 'error', 'correct', 'repair']):
            return 'fix'

        # Refactor - renommage, restructuration
        if any(keyword in diff_lower for keyword in ['refactor', 'rename', 'reorganize', 'restructure']):
            return 'refactor'

        # Update - modification de valeurs, versions
        if any(keyword in diff_lower for keyword in ['version', 'update', 'change', 'modify', 'bump']):
            return 'update'

        # Test - ajout de tests
        if any(keyword in diff_lower for keyword in ['test', 'assert', 'unittest', 'spec']):
            return 'test'

        # Performance
        if any(keyword in diff_lower for keyword in ['optimize', 'performance', 'faster', 'speed']):
            return 'perf'

        # Security
        if any(keyword in diff_lower for keyword in ['security', 'auth', 'password', 'token']):
            return 'security'

        # Remove
        if any(keyword in diff_lower for keyword in ['remove', 'delete', 'clean']) or removed_lines > added_lines * 1.5:
            return 'remove'

        # Si beaucoup plus d'ajouts que de suppressions = feat
        if added_lines > removed_lines * 2 and added_lines > 5:
            return 'feat'

        # Si modification équilibrée = refactor
        if added_lines > 0 and removed_lines > 0 and abs(added_lines - removed_lines) < 3:
            return 'refactor'

        # Par défaut
        return 'chore'

    def analyze_changes(self, repo) -> Dict:
        """Analyze changes to determine commit type."""
        try:
            diff = repo.git.diff('HEAD')
            staged_files = [item.a_path for item in repo.index.diff("HEAD")]
            new_files = repo.untracked_files

            analysis = {
                'files_modified': staged_files,
                'files_added': new_files,
                'commit_type': 'chore',
                'scope': '',
                'breaking_change': False,
                'diff_content': diff
            }

            all_files = staged_files + new_files

            # 1. Analyser d'abord par type de fichier
            if any('test' in f.lower() for f in all_files):
                analysis['commit_type'] = 'test'
            elif any(f.endswith(('.md', '.txt', '.rst')) for f in all_files):
                analysis['commit_type'] = 'docs'
            elif any('config' in f.lower() or f.endswith(('.json', '.yml', '.yaml', '.toml', '.ini')) for f in
                     all_files):
                analysis['commit_type'] = 'chore'
            elif any('package' in f.lower() or 'requirements' in f.lower() for f in all_files):
                analysis['commit_type'] = 'update'

            # 2. Si pas de classification par fichier, analyser le diff
            elif diff:
                analysis['commit_type'] = self._analyze_diff_content(diff)

            # 3. Cas particuliers pour nouveaux fichiers
            elif new_files and not staged_files:
                # Nouveau fichier mais analyser son nom
                if any('test' in f.lower() for f in new_files):
                    analysis['commit_type'] = 'test'
                elif any(f.endswith(('.md', '.txt')) for f in new_files):
                    analysis['commit_type'] = 'docs'
                else:
                    analysis['commit_type'] = 'feat'

            # Detect scope
            if all_files:
                try:
                    common_path = os.path.commonpath([os.path.dirname(f) for f in all_files if f])
                    if common_path and common_path != '.':
                        analysis['scope'] = f"({os.path.basename(common_path)})"
                except ValueError:
                    # Chemins sur différents drives Windows
                    pass

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing changes: {e}")
            return {'commit_type': 'chore', 'scope': '', 'breaking_change': False, 'diff_content': ''}

    def generate_smart_commit_message(self, analysis: Dict) -> str:
        """Generate a smart commit message using AI."""
        try:
            headers = {
                "Authorization": f"Bearer {self.config['openrouter_api_key']}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.config.get('site_url', ''),
                "X-Title": self.config.get('site_name', ''),
            }

            commit_type = analysis['commit_type']
            emoji = self.commit_patterns[commit_type]['emoji']

            prompt = f"""You are a Git expert generating perfect commit messages.

CONTEXT:
- Detected type: {commit_type}
- Modified files: {', '.join(analysis['files_modified'][:5])}
- New files: {', '.join(analysis['files_added'][:5])}
- Scope: {analysis['scope']}

DIFF:
{analysis['diff_content'][:1500]}

INSTRUCTIONS:
1. Generate a commit message in {self.config.get('language', 'français')}
2. Use template: {self.config.get('commit_template')}
3. Max 72 characters
4. Be precise and professional
5. Use EXACTLY the detected type: {commit_type}
6. Keywords for {commit_type}: {', '.join(self.commit_patterns[commit_type]['keywords'])}

Example: {emoji} {commit_type}(auth): add JWT authentication

Commit message:"""

            payload = {
                "model": self.config.get('model', 'openai/gpt-4o'),
                "messages": [
                    {"role": "system",
                     "content": f"You are a Git expert. Always use the commit type '{commit_type}' with emoji '{emoji}'."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 80,
                "temperature": 0.2
            }

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()

            commit_message = response.json()["choices"][0]["message"]["content"].strip()

            # Clean the message
            commit_message = commit_message.replace('Commit message:', '').strip()
            if commit_message.startswith('"') and commit_message.endswith('"'):
                commit_message = commit_message[1:-1]

            # S'assurer que le type détecté est respecté
            if not commit_message.startswith(emoji):
                commit_message = f"{emoji} {commit_type}: {commit_message.split(':', 1)[-1].strip()}"

            return commit_message[:72] if commit_message else f"{emoji} {commit_type}: modifications"

        except Exception as e:
            logger.error(f"Error generating AI commit message: {e}")
            emoji = self.commit_patterns[analysis['commit_type']]['emoji']
            return f"{emoji} {analysis['commit_type']}: modifications automatiques"