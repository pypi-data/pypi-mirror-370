"""
Preprocessor for Foliant documentation authoring tool.

Check chapters for untracked and missing files
"""
import os

from foliant.preprocessors.utils.preprocessor_ext import BasePreprocessorExt
from foliant.utils import output

from json import load

from pathlib import Path


class Preprocessor(BasePreprocessorExt):
    defaults = {
        'not_in_chapters': [],
        'strict_check': [
            'not_exist',
        ],
        'disable_warnings': [],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('checksources')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')
        self.src_dir = self.project_path / self.config['src_dir']
        self.critical_error = []
        if isinstance(self.options['strict_check'], bool):
            if self.options['strict_check']:
                self.options['strict_check'] = self.defaults['strict_check']
            else:
                self.options['strict_check'] = []
        if not isinstance(self.options['disable_warnings'], list):
            self.options['disable_warnings'] = self.defaults['disable_warnings']

        self.files_list = []

    def apply(self):
        self.logger.info('Applying preprocessor')
        self.logger.debug(f'Not warn for files: {self.options["not_in_chapters"]}')

        def _recursive_process_chapters(chapters_subset):
            if isinstance(chapters_subset, dict):
                new_chapters_subset = {}
                for key, value in chapters_subset.items():
                    new_chapters_subset[key] = _recursive_process_chapters(value)

            elif isinstance(chapters_subset, list):
                new_chapters_subset = []
                for item in chapters_subset:
                    new_chapters_subset.append(_recursive_process_chapters(item))

            elif isinstance(chapters_subset, str):
                if chapters_subset.endswith('.md'):
                    chapter_file_path = (self.src_dir / chapters_subset).resolve()
                    if os.path.exists(chapter_file_path):
                        self.logger.debug(f'Adding file to the list of mentioned in chapters: {chapter_file_path}')
                    else:
                        self.logger.debug('Not exist, throw warning')
                        msg = f'{os.path.relpath(chapter_file_path)} does not exist'
                        if 'not_exist' in self.options['strict_check']:
                            self.logger.error(msg)
                            self.critical_error.append(msg)
                            output(f'ERROR: {msg}')
                        else:
                            if not 'not_exist' in self.options['disable_warnings']:
                                self._warning(msg)
                    if chapters_subset in self.files_list:
                        msg = f'{os.path.relpath(chapter_file_path)} duplicated in chapters'
                        if 'duplicate' in self.options['strict_check']:
                            self.logger.error(msg)
                            self.critical_error.append(msg)
                            output(f'ERROR: {msg}')
                        else:
                            if not 'duplicate' in self.options['disable_warnings']:
                                self._warning(msg)
                    else:
                        self.files_list.append(chapters_subset)

                    chapters_files_paths.append(chapter_file_path)

                new_chapters_subset = chapters_subset

            else:
                new_chapters_subset = chapters_subset

            return new_chapters_subset

        chapters_files_paths = []

        _recursive_process_chapters(self.config.get('chapters', []))

        self.logger.debug(f'List of files mentioned in chapters: {chapters_files_paths}')

        def _fill_not_in_chapters():

            for not_in_chapters in self.options['not_in_chapters']:
                not_in_chapters_paths.append((self.src_dir / not_in_chapters).resolve())

        not_in_chapters_paths = []

        _fill_not_in_chapters()

        self.logger.debug(f'List of files mentioned in not_in_chapters: {not_in_chapters_paths}')

        def _fill_included_files():

            with open(f'{self.working_dir}/static/includes_map.json', 'r',encoding='utf8') as f:
                data = load(f)
            files_paths=set()
            for map_item in data:
                files_paths|=set(map_item['includes'])
            files_paths=list(files_paths)
            for path in files_paths:
                included_files_paths.append(Path(path).resolve())
            
        included_files_paths=[]

        if os.path.exists(f'{self.working_dir}/static/includes_map.json'):
            _fill_included_files()
        
        self.logger.debug(f'List of files mentioned in includes map: {included_files_paths}')

        for markdown_file_path in self.src_dir.rglob('*.md'):
            markdown_file_path = markdown_file_path.resolve()

            self.logger.debug(f'Checking if the file is mentioned in chapters: {markdown_file_path}')

            if markdown_file_path in chapters_files_paths or markdown_file_path in not_in_chapters_paths or markdown_file_path in included_files_paths:
                self.logger.debug('Mentioned, keeping')

            else:
                self.logger.debug('Not mentioned, throw warning')
                self._warning(f'{os.path.relpath(markdown_file_path)} does not mentioned in chapters')
        if len(self.critical_error) > 0:
            self.logger.info('Critical errors have occurred')
            errors = '\n'.join(self.critical_error)
            output(f'\nBuild failed: checksources preprocessor errors: \n{errors}\n')
            os._exit(2)
        else:
            self.logger.info('Preprocessor applied')
