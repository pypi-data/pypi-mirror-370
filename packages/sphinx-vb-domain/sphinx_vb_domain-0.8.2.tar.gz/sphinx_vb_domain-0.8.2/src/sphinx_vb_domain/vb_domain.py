import re

from docutils import nodes
from docutils.nodes import Element, Node
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.addnodes import desc_content, desc_signature, pending_xref
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.directives import ObjDescT, ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util.docfields import DocFieldTransformer, Field, TypedField
from sphinx.util.nodes import make_refnode

from .utils import to_safe_label


class VBXRefRole(XRefRole):
    '''For VBDomain's cross-reference e.g. func role (vb:func).
    '''
    # Visual Basic 固有のリンク処理が必要な場合は process_link() を
    # オーバーライドする。
    # TODO: 不要ならこのクラスを削除する。
    pass


class VBFunction(ObjectDescription):
    '''For function directive (vb:function).
    '''
    # Class variables are function directive's specs.
    has_content = True  # for function summary or details.
    required_arguments = 1  # 1 arg is enough as whole declaration.
    option_spec = {
        'module': directives.unchanged,
    }

    doc_field_types = [
        TypedField(
            'parameter', label='パラメータ',
            names=('param', 'parameter', 'arg', 'argument'),
            typerolename='vbtype', typenames=('type',)),
        Field('returnvalue', label='戻り値', has_arg=False,
              names=('returns', 'return')),
        Field('returntype', label='戻り値の型', has_arg=False,
              names=('rtype',)),
    ]

    def handle_signature(
            self, sig: str, signode: desc_signature) -> ObjDescT:
        '''Parse the function signature and add nodes to the signode.

        This function will be called from autodoc.

        Parameters
        ----------
        sig : str
            Function declaration from VB source code.
        signode : desc_signature
            Node for signature structure.

        Returns
        -------
        obj_id : ObjDescT
            Object identifier.
        '''
        # Split signature into 3 parts.
        match = re.match(r'^(.*?)\s*(\(.*?\))?\s*(As\s+.+)?$', sig)
        if not match:
            raise ValueError(f"Invalid signature: {sig}")

        # Part 1: access modifier and function name.
        access_and_name = match.group(1).strip()
        # Part 2: parameters (without ()).
        parameters = match.group(2).strip("()") if match.group(2) else ""
        if parameters:
            args = [arg.strip() for arg in parameters.split(',')]
        else:
            args = []
        # Part 3: return type.
        return_type = match.group(3).removeprefix("As").strip() \
            if match.group(3) else ""

        # Extract access modifier.
        valid_modifiers = [
            'Public', 'Private', 'Protected', 'Friend', 'Protected Friend',
            'Private Protected']

        parts = access_and_name.split()

        if len(parts) >= 2 and ' '.join(parts[:2]) in valid_modifiers:
            access_modifier = ' '.join(parts[:2])
            parts = parts[2:]
        elif parts[0] in valid_modifiers:
            access_modifier = parts.pop(0)
        else:
            access_modifier = ''

        # Extract function type ("Function" or "Sub").
        func_type = parts.pop(0) if len(parts) > 0 else ''
        if func_type not in ('Function', 'Sub'):
            raise ValueError(f'No "Function" or "Sub" in "{sig}".')

        # Extract function name.
        func_name = parts.pop(0) if len(parts) > 0 else ''
        if not func_name:
            raise ValueError(f'No Function name in "{sig}".')

        # Add access modifier to signode (e.g. 'Public ').
        if access_modifier:
            signode += addnodes.desc_annotation(
                access_modifier + ' ', access_modifier + ' ')

        # Add function type to signode (e.g. 'Function ').
        signode += addnodes.desc_annotation(func_type + ' ', func_type + ' ')

        # Add function name to signode (e.g. 'MyFunc').
        signode += addnodes.desc_name(func_name, func_name)

        # Add param list to signode.
        paramlist = addnodes.desc_parameterlist()
        for arg in args:
            # Add param (e.g. 'ByVal arg1 As Integer').
            param = addnodes.desc_parameter('', arg)
            paramlist += param
        signode += paramlist

        # Add return type to signode (e.g. ' As String').
        if return_type:
            signode += nodes.emphasis(
                ' As ' + return_type, ' As ' + return_type)

        # Return Object identifier.
        module_name = self.options.get('module', '')
        obj_id = f'{module_name}.{func_name}' if module_name else func_name
        return obj_id

    def transform_content(self, contentnode: desc_content):
        super().transform_content(contentnode)

        # Transform field lists.
        transformer = DocFieldTransformer(self)
        transformer.transform_all(contentnode)

        # Change line-breaks in top-level paragraphs into <br> nodes.
        for node in contentnode:
            if not isinstance(node, nodes.paragraph):
                continue

            line_broken = []
            for child in node.children:
                if isinstance(child, nodes.Text):
                    lines = child.astext().split('\n')
                    for i, line in enumerate(lines):
                        line_broken.append(nodes.Text(line))
                        if i < len(lines) - 1:
                            line_broken.append(
                                nodes.raw('', '<br />', format='html'))
                else:
                    line_broken.append(child)

            node.children = line_broken

    def run(self) -> list[Node]:
        # 親クラスの run() メソッドを呼び出す
        result = super().run()

        # signature parsing failed
        if not self.names:
            return result

        # Generate a target id for the function.
        encode_ = self.env.config.vb_encode_invalid_labels
        target_id = to_safe_label(self.names[0], encode_)

        # 表示用の関数名を作成
        function_name = str(self.names[0]).split('.')[-1] + '()'

        # 見出しを含むセクションノードを作成
        section_node = nodes.section()
        if self.env.config.vb_add_function_labels:
            # Add label to section node.
            if self.env.config.vb_add_docname_to_labels:
                delimiter = self.env.config.vb_docname_label_delimiter
                docname = self.env.docname.replace('/', delimiter)
                target_id = docname + delimiter + target_id
            section_node['names'].append(target_id)  # クロスリファレンス用
            section_node['ids'].append(target_id)    # HTML アンカー用
            section_node['label'] = target_id        # カスタム用途
        section_node += nodes.title(text=function_name)
        section_node += result

        # Add target to enable using implicit text (function_name)
        objects = self.env.domaindata['vb']['objects']
        objects[target_id] = (
            self.env.docname, target_id, 'function', function_name)

        # TODO:
        # これでローカルなターゲット id を作っているつもりだが上手く行かない。
        # グローバルなターゲット id はこれをしなくてもできている。
        # これの効果が不明。
        # ローカルなターゲット id は MyST でないと作られないのかも知れない。
        self.state.document.note_explicit_target(section_node)

        return [section_node]


class VBModule(Directive):
    '''For module directive (vb:module).

    Notes
    -----
    Not in use, just declared.
    '''
    # Class variables are module directive's specs.
    has_content = True  # for module summary or details.
    required_arguments = 1  # 1 arg is enough as whole declaration.
    option_spec = {}

    # def run(self):
    #     pass

    # def parse_arguments(self):
    #     pass

    # def parse_options(self):
    #     pass


class VBDomain(Domain):
    '''Domain for Visual Basic.
    '''
    name = 'vb'
    label = 'Visual Basic'

    object_types = {
        'function': ObjType('function', 'func', 'obj'),
    }
    directives = {
        'function': VBFunction,
        'module': VBModule,
    }
    roles = {
        'vbtype': XRefRole(innernodeclass=nodes.emphasis),
        'function': VBXRefRole(),
    }

    # autodoc で使われる情報を保持する辞書の、初期値
    initial_data = {
        # "functions": {},  # function name -> (docname, synopsis)
        # "classes": {},    # class name -> (docname, synopsis)
        # "modules": {},    # module name -> (docname, synopsis)
        "objects": {},    # object name -> (docname, objtype, signature)
    }

    def resolve_xref(
            self, env: BuildEnvironment, fromdocname: str, builder: Builder,
            typ: str, target: str, node: pending_xref, contnode: Element,
            ) -> Element | None:

        if target not in self.data['objects']:
            return None

        obj = self.data['objects'][target]
        if obj[2] != typ:  # obj[2] は登録時に指定したオブジェクトタイプ
            return None

        title = obj[3] if obj[2] == 'function' else target
        if 'refexplicit' in node.attributes and node.attributes['refexplicit']:
            child = contnode
        else:
            child = nodes.literal(text=title)

        result = make_refnode(
            builder, fromdocname, obj[0], obj[1], child, title)
        return result

    def resolve_any_xref(
            self, env: BuildEnvironment, fromdocname: str, builder: Builder,
            target: str, node: pending_xref, contnode: Element
            ) -> list[tuple[str, Element]]:
        results = []

        # 再利用: resolve_xref() の結果を取得
        result = self.resolve_xref(
            env, fromdocname, builder, '', target, node, contnode)
        if result:
            results.append(('vb:function', result))  # ドメインとロールを指定

        return results


def setup(app: Sphinx):
    '''Set up vb_domain feature.
    '''
    app.add_domain(VBDomain)

    # Config parameter to add function labels as reference targets.
    # This should be False if user enables sphinx.ext.autosectionlabel.
    app.add_config_value('vb_add_function_labels', True, 'env', bool)

    # Config parameter to encode labels that contain invalid characters.
    app.add_config_value('vb_encode_invalid_labels', True, 'env', bool)

    # Config parameter to add docname to function labels.
    # This should be True if there are multiple modules with same function
    # names.
    app.add_config_value('vb_add_docname_to_labels', False, 'env', bool)

    # Config parameter to set delimiter between module name and function name.
    app.add_config_value('vb_docname_label_delimiter', '-', 'env', str)
