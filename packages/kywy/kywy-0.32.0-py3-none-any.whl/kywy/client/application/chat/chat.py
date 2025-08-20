from .source_code_utils import extract_sections, extract_between_marker_lines, extract_before_marker_line, \
    extract_between_fence
from anthropic import Anthropic
import os
import tempfile
import importlib
import uuid
import io
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

MODEL = 'claude-sonnet-4-20250514'
MARKERS = [
    '-- DATA SECTION',
    '-- MODEL SECTION',
    '-- DASHBOARD SECTION'
]
SYSTEM_PROMPT_PATHS = {
    'create': f'{script_dir}/prompts/full-prompt.md',
    'edit': f'{script_dir}/prompts/edit-prompt.md',
}


class NotebookChat:

    def __init__(self):
        self._initial_script = None
        self._conversation = []
        self._patches = []
        self._anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def reset(self):
        self._initial_script = None
        self._conversation = []
        self._patches = []

    def execute_code(self):
        merged_code = self._merged_code()
        with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tmp_file:
            extracted_code = extract_between_fence(merged_code)
            tmp_file.write(extracted_code)
            tmp_path = tmp_file.name

        stdout_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = StreamDuplicator(original_stdout, stdout_buffer)

        try:
            module_name = f"mod_{uuid.uuid4().hex}"
            spec = importlib.util.spec_from_file_location(module_name, tmp_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        finally:
            os.remove(tmp_path)
            sys.stdout = original_stdout
            captured_output = stdout_buffer.getvalue()

            error_section = extract_between_marker_lines(
                captured_output,
                marker='# ERROR SECTION'
            ).strip()

            if error_section:
                return error_section

    def generate_code(self, prompt):

        is_first_iteration = self._first_iteration()
        action = 'create' if is_first_iteration else 'edit'
        system_prompt = self._build_system_prompt(action)

        self._conversation.append({
            "role": "user",
            "content": prompt
        })

        generated_content = ''
        with self._anthropic_client.messages.stream(
                model=MODEL,
                max_tokens=50_000,
                system=system_prompt,
                messages=self._conversation,
        ) as stream:
            for text in stream.text_stream:
                generated_content += text
                print(text, end="", flush=True)

        self._conversation.append({
            "role": "assistant",
            "content": generated_content
        })

        if is_first_iteration:
            self._initial_script = generated_content
        else:
            extractions = extract_sections(
                source=generated_content,
                markers=MARKERS,
                patch_name=prompt
            )
            self._patches.append(extractions)

        return generated_content

    def _merged_code(self):
        sections = extract_sections(self._initial_script, markers=MARKERS)
        for marker in MARKERS:
            if marker not in sections:
                raise Exception(f'The initial script is missing this section: {marker}')

        for patch in self._patches:
            sections.update(patch)

        script_header = extract_before_marker_line(self._initial_script, MARKERS[0])
        final_script = script_header

        for marker in MARKERS:
            content = sections[marker]['content']
            patch_name = sections[marker]['patch']

            final_script += f'## 📝 Applied from patch "{patch_name}"'
            final_script += '\n'
            final_script += content
            final_script += '\n'

        final_script += '\n\napp.publish()\n```'
        return final_script

    def _first_iteration(self):
        return len(self._conversation) == 0

    def _build_system_prompt(self, create_or_edit):

        print('Using the prompt to ' + create_or_edit)
        main_task = self._load_prompt_file(create_or_edit, 'main-task')
        kawa_sdk_documentation = self._load_prompt_file('common', 'sdk-documentation')
        mistakes_to_avoid = self._load_prompt_file('common', 'mistakes-to-avoid')
        example = self._load_prompt_file(create_or_edit, 'examples')
        guidelines = self._load_prompt_file('common', 'additional-guidelines')

        system_prompt = f'''

        # Main task

        {main_task}


        # Kawa SDK Documentation

        {kawa_sdk_documentation}


        # Additional guidelines
        
        {guidelines}
        
        
        # Mistakes to avoid

        {mistakes_to_avoid}


        # Full working example

        {example}
        '''

        return system_prompt

    @staticmethod
    def _load_prompt_file(directory, name):
        full_path = f'{script_dir}/prompts/{directory}/{name}.md'
        print(f'Loading prompt:{name} from {full_path}')

        with open(full_path, "r", encoding="utf-8") as file:
            prompt = file.read()

        return prompt


class StreamDuplicator:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()
