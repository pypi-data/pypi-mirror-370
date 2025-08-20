# sphinx-vb-domain

## 概要

Visual Basic の関数ディレクティブを処理する Sphinx 拡張機能です。VB のソースコード内のドキュメントコメントからそれらのディレクティブを作ることもできます。

これは実験的なプロジェクトです。以下に述べる機能がありますが、いつも正しく動くという保証はありません。

## インストール

### pip

```
pip install sphinx-vb-domain
```

### rye

```
rye add --dev sphinx-vb-domain
```

## 使い方

### conf.py

`extensions` に追加します。

```python
# conf.py

extensions = [
    'sphinx_vb_domain',
]
```

### 関数ディレクティブ

例

```restructuredtext
.. vb:function:: Private Function getId(ByVal name As String, ByVal age As Integer) As Integer
   :module: Module1

   これは単純な private 関数です。

   :param name: 名前
   :type name: String
   :param age: 年齢
   :type age: Integer
   :returns: Id
   :rtype: Integer

   ここに注意事項などを書きます。
```

### コンフィグ

conf.py の中で以下の設定が使えます。

#### vb_add_function_labels

```python
vb_add_function_labels = False  # Default: True
```

`False` にすると、関数ディレクティブにターゲットラベルをつけなくなります。  
`sphinx.ext.autosectionlabel` を使っているなら `False` にしても良いでしょう。  
ただし、sphinx-vb-domain のターゲットラベルは `{モジュール名}.{関数名}` という形になるため、複数のモジュールに同じ名前の関数がある場合はこちらを使う方が良いです。

#### vb_encode_invalid_labels

```python
vb_encode_invalid_labels = False  # Default: True
```

`False` にすると、関数名が Sphinx のターゲットラベルとして無効な文字列を含む場合のハッシュエンコードをしなくなります。  
この設定は Autodoc でモジュール見出しにつける明示的なラベルに対しても作用します。

#### vb_add_docname_to_labels

```python
vb_add_docname_to_labels = True  # Default: False
```

`True` にすると、関数ディレクティブにつくターゲットラベルを `{ファイルパス}-{モジュール名}.{関数名}` という形にして、複数ファイルに同じ名前のモジュールと関数があっても区別できるようにします。  
`{ファイルパス}` 部分のディレクトリの区切りは `'-'` になります。  
この設定は Autodoc でモジュール見出しにつける明示的なラベルに対しても作用します。

#### vb_docname_label_delimiter

```python
vb_docname_label_delimiter = '__'  # Default: '-'
```

`vb_add_docname_to_labels` でディレクトリやファイル名の後ろに付く区切り文字を設定します。  
Sphinx のターゲットラベルとして有効な文字を指定する必要があります。  
Autodoc でモジュール見出しにつける明示的なラベルに対しても作用します。

#### vb_autodoc_module_labels

```python
vb_autodoc_module_labels = True  # Default: False
```

`True` にすると、Autodoc で生成するモジュール見出しに明示的なラベルをつけるようになります。

### Autodoc

VB のドキュメントコメントからドキュメントを作成するには、以下の設定が必要です。

```python
# conf.py

vb_autodoc_paths = [
    (vb_src_dir, page_path, page_title, notes),
]
```

- `vb_src_dir`
    - VBソースを含むディレクトリへの、conf.py からの相対パス (e.g. '../../macros')。
- `page_path`
    - 生成する reST ファイルの、source ディレクトリからの相対パス。'modules' と書くと 'modules.rst' が生成される。
- `page_title`
    - reST ファイルに追加されるタイトル (レベル1の見出し)。
- `notes`
    - 補足説明を追加したい場合に指定する辞書。以下のターゲット (キー) に対応する。
        - `'__page__'`: ページタイトルの下に追加される補足説明。
        - `'<モジュール名>'`: モジュールのタイトルの下に追加される補足説明。
        - `'<モジュール名>.<関数名>'`: 関数ディレクティブの下に追加される補足説明。
    ```python
    # 例
    # ※値は reST で書けるが、見出しは追加できない。
    notes = {
        '__page__': 'これはページの補足説明です。',
        'Module1': 'これは Module1 の補足説明です。',
        'Module1.MyFunction': 'これは MyFunction の補足説明です。',
    }
    ```

設定を書いたら `-D vb_autodoc=1` という引数をつけて sphinx-build を実行します。

`page_path` で指定した reST ファイル (e.g. 'modules.rst') に、`vb_src_dir` ディレクトリ内の VB ファイルごとに「モジュール」(レベル2の見出し) が作られ、その下に関数ディレクティブが作られます。

#### Notes from template

reSTでテンプレートを作成し、それをノートとしてdictに変換することができます。

```restructuredtext
__page__
========

This is note for the page.

Module1
-------

This is note for Module1.

Module1.MyFunction
~~~~~~~~~~~~~~~~~~

This is note for MyFunction.
```

このようなテンプレートを _templates フォルダーに置き、`notes_from_template()` 関数を呼び出します。

```python
# conf.py
from sphinx_vb_domain.utils import notes_from_template

notes = notes_from_template('notes.rst')

vb_autodoc_paths = [
    (vb_src_dir, page_path, page_title, notes),
]
```

### クロスリファレンス

関数ディレクティブには見出しが付くので、toctree に含まれるようになります。  
また、`vb_add_function_labels` が `True` (デフォルト) の場合は、クロスリファレンスのターゲットとして使えます。

#### reStructuredText

```restructuredtext
* :vb:function:`module_name.function_name`
* :any:`module_name.function_name`
* :any:`Link text <module_name.function_name>`
```

#### MyST

```markdown
- {vb:function}`module_name.function_name`
- <project:#module_name.function_name>
- [Link text](#module_name.function_name)
```

## 既知の問題

- 関数ディレクティブは、言語設定に関わらず以下のように日本語でレンダリングされます。
    ```
    Private Function getId(ByVal name As String, ByVal age As Integer) As Integer
    
        A simple private function.

        パラメータ: ・name (String) -- Name
                    ・age (Integer) -- Age
        戻り値: Id
        戻り値の型: Integer

        Remarks here.
    ```
    - これを変えたい場合は、`VBFunction` クラスの `doc_field_types` の内容を書き換えてください。
