# notes

- `rye init` でプロジェクトを作った。
- `rye add --dev xx` で依存関係をインストールして、`rye sync` した。

## ビルド

1. pyproject.toml の version と、\_\_init__.py の \_\_version__ を合わせておく。
1. rye の build コマンドを実行。
    ```
    > rye build
    ```

## 公開

1. TestPyPI に公開する。
    ```
    > rye publish --repository testpypi --repository-url https://test.pypi.org/legacy/ --username __token__ --token pypi-ToKeN
    ```
1. PyPI に公開する。
    ```
    > rye publish --username __token__ --token pypi-ToKeN
    ```
