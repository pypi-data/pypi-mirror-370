import hashlib
import re
from pathlib import Path

from docutils.nodes import make_id


def to_safe_label(name: str, encode_: bool) -> str:
    '''Generate a valid label by encoding invalid characters with md5.'''
    invalid_symbols = re.compile(r'[!-/:-@\[-`{-~]')
    target_ptn = re.compile(r'[a-zA-Z0-9_\-]+')

    # Split name into parts.
    # e.g. 'Module1.Function1' -> ['Module1', 'Function1']
    name_parts = name.split('.')

    target_parts = []
    for name_part in name_parts:
        # ラベルに使えない記号をハイフンに置き換える。
        name_part = invalid_symbols.sub('-', name_part)

        # エンコードしない、またはする必要がない場合
        if not encode_ or target_ptn.fullmatch(name_part):
            target_part = name_part
        else:
            # ハッシュダイジェストを生成
            digest = hashlib.md5(name_part.encode('utf-8')).hexdigest()[:8]
            # 先頭が数字の場合に接頭辞を付ける
            target_part = f'x{digest}' if digest[0].isdigit() else digest

        target_parts.append(make_id(target_part))

    return '.'.join(target_parts)


def notes_from_template(
    template_file: str, encode_keys: bool = True, templates_dir: str = "_templates"
) -> dict:
    '''Parse a Jinja2 template and return a dictionary of blocks.

    Parameters
    ----------
    template_file : str
        File name or relative path to the Jinja2 template file
        (relative to the templates directory).
    encode_keys : bool, optional
        Whether to encode keys using `to_safe_label`.
    templates_dir : str, optional
        Path to the templates directory (default is "_templates").

    Returns
    -------
    dict
        A dictionary mapping keys to their corresponding content.
    '''
    # Resolve the template path
    templates_path = Path(templates_dir).resolve()
    template_path = Path(template_file)

    # If template_file is not an absolute path, resolve it relative to templates_path
    if not template_path.is_absolute():
        template_path = templates_path / template_file

    if not template_path.is_file():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    # Read the raw content of the template
    with open(template_path, 'r', encoding='utf-8') as f:
        rst_content = f.read()

    # Parse the content manually (e.g., split by headings)
    notes = {}
    current_key = None
    current_value = []
    previous_line = ""

    for line in rst_content.splitlines():
        # Detect headings (e.g., lines followed by "----" or "~~~~")
        if line.strip() and all(c in "-=~^" for c in line.strip()):
            # Save the current key-value pair
            if current_key and current_value:
                notes[current_key] = "\n".join(current_value[:-1]).strip()
                current_value = []

            # Update the current key (use the previous line as the key)
            current_key = previous_line.strip()
        else:
            # Collect content for the current key
            if current_key:
                current_value.append(line)

        previous_line = line

    # Save the last key-value pair
    if current_key and current_value:
        notes[current_key] = "\n".join(current_value).strip()

    return notes
