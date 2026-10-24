"""Reference boundaries and conditional output must preserve source meaning."""
import copy
import unittest

import anne
import bena
from catalog import Catalog
from data_class import Buff, Node
from document_model import document_rows, reference_parts


class ReferenceSafetyTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog(['buff'])
        for category in ('buff', 'buff_template', 'global_buff', 'rogue_item'):
            self.catalog.add(category, 'same_id', Buff('same_id', {}))
        self.catalog.add('buff_template', 'damage_resistance', Buff('damage_resistance', {}))
        self.catalog.add('buff', 'only_buff', Buff('only_buff', {}))
        relic = Buff('rogue_6_relic_fight_7', {})
        relic.display_name = '“庇护”'
        self.catalog.add('rogue_item', relic.buff_key, relic)
        self.catalog.install()

    def assertLiteral(self, text):
        parts = reference_parts(text, self.catalog)
        self.assertEqual(''.join(label for label, _ in parts), text)
        self.assertFalse(any(target for _, target in parts))

    def test_comparisons_markup_and_unknown_references_are_literal(self):
        for text in ('1 < 2 and 3 > 0', '<color=#ff0000>重点</color>',
                     '<b>重点</b>', '<@ba.vup>加成</>', '<color=same_id>文字</color>',
                     '说明 <enemy_damage>', '<missing_id>', '<年代之刺>'):
            with self.subTest(text=text):
                self.assertLiteral(text)

    def test_typed_references_use_the_declared_category(self):
        for category in self.catalog.groups:
            with self.subTest(category=category):
                parts = reference_parts('<' + category + '|same_id>', self.catalog,
                                        'buff.same_id')
                self.assertEqual([t for _, t in parts if t], [category + '.same_id'])

    def test_invalid_and_missing_typed_targets_do_not_fall_back(self):
        for text in ('<bogus|same_id>', '<|same_id>', '<global_buff|only_buff>',
                     '<rogue_item|buff.same_id>', '<buff|>', '<buff||same_id>'):
            with self.subTest(text=text):
                self.assertLiteral(text)

    def test_typed_relic_name_stays_in_relic_category(self):
        parts = reference_parts('<rogue_item|“庇护”>', self.catalog)
        self.assertEqual([t for _, t in parts if t], ['rogue_item.rogue_6_relic_fight_7'])

    def test_plain_chinese_names_and_relic_titles_are_not_links(self):
        for text in ('庇护', '“庇护”', '收藏品【“庇护”】', '获得庇护效果',
                     '<庇护>', '同_id'):
            with self.subTest(text=text):
                self.assertLiteral(text)
        self.assertEqual([t for _, t in reference_parts('<buff_template|庇护>', self.catalog) if t],
                         ['buff_template.damage_resistance'])

    def test_bare_ids_link_without_translating_plain_text(self):
        text = 'same_id / only_buff / xsame_id / same_id_tail / [same_id]'
        parts = reference_parts(text, self.catalog)
        self.assertEqual(''.join(label for label, _ in parts), text)
        self.assertEqual([t for _, t in parts if t], ['buff.same_id', 'buff.only_buff'])

    def test_markers_can_still_choose_a_template(self):
        parts = reference_parts('<same_id>', self.catalog, 'buff_template.same_id')
        self.assertEqual([t for _, t in parts if t], ['buff_template.same_id'])

    def test_legacy_translation_preserves_unknown_text(self):
        for text in ('<missing>', '<enemy_damage>', '1 < 2 and 3 > 0', '<b>重点</b>'):
            with self.subTest(text=text):
                self.assertEqual(bena.translate_buff_name_in_text(text), text)
        self.assertEqual(bena.translate_buff_name_in_text('<damage_resistance>'), '庇护')


class ConditionalOutputTests(unittest.TestCase):
    def setUp(self):
        self.translator = anne.AnneNode()
        self.check = {'$type': 'CheckAbnormalCombo', '_targetType': 'TARGET',
                      '_abnormalCombo': 'SLEEPING', '_isUnset': False}
        self.success = {'$type': 'Dummy', '_dummy': '成功效果'}
        self.failure = {'$type': 'Dummy', '_dummy': '失败效果'}

    def rows(self, nodes):
        raw = copy.deepcopy(nodes)
        result = self.translator.translate_all([Node(n) for n in raw], {})
        self.assertEqual(raw, nodes)
        return document_rows(result)

    def test_sequential_check_has_one_explicit_continuation(self):
        rows = self.rows([self.check, self.success])
        guards = [r for r in rows if r.text.startswith('若')]
        self.assertEqual([r.text for r in guards], ['若持有沉睡异常组合，则继续执行后续节点'])
        self.assertEqual(guards[0].role, 'condition')

    def test_reversed_checks_have_only_the_reversed_guard(self):
        for nodes in ([dict(self.check, _isUnset=True), self.success],
                      [self.check, {'$type': 'IfNot'}, self.success]):
            with self.subTest(nodes=nodes):
                guards = [r.text for r in self.rows(nodes) if r.text.startswith('若')]
                self.assertEqual(guards, ['若不持有沉睡异常组合或免疫该异常组合，则继续执行后续节点'])

    def test_last_check_has_no_continuation(self):
        self.assertFalse(any(r.text.startswith('若') for r in self.rows([self.check])))

    def test_explicit_branches_keep_their_own_children(self):
        for success, failure in (([self.success], [self.failure]), ([self.success], []),
                                 ([], [self.failure])):
            with self.subTest(success=success, failure=failure):
                rows = self.rows([{'$type': 'IfElse', '_conditionNode': self.check,
                                   '_succeedNodes': success, '_failNodes': failure}])
                guards = [r for r in rows if r.text.startswith('若')]
                self.assertEqual(len(guards), bool(success) + bool(failure))
                for effect in (r for r in rows if r.text in ('成功效果', '失败效果')):
                    parent = next(r for r in guards if effect.path[:-1] == r.path)
                    self.assertEqual(effect.depth, parent.depth + 1)
                    self.assertEqual(parent.text.startswith('若不持有'), effect.text == '失败效果')


if __name__ == '__main__':
    unittest.main()
