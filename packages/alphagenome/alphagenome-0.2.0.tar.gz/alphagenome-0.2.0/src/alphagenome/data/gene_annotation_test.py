# Copyright 2024 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from absl.testing import absltest
from absl.testing import parameterized
from alphagenome.data import gene_annotation
import numpy as np
import pandas as pd


class ExtractTSSTest(absltest.TestCase):

  def test_extract_tss(self):
    gtf = pd.DataFrame({
        'Start': [101, 102, 103, 0],
        'End': [200, 200, 200, 107],
        'Strand': ['+', '+', '+', '-'],
        'transcript_id': ['T1', 'T2', 'T2', 'T4'],
    })
    gtf['Feature'] = 'transcript'
    tss = gene_annotation.extract_tss(gtf)
    self.assertSequenceEqual(list(tss.Start), [101, 102, 103, 107])
    self.assertSequenceEqual(list(tss.End), [101, 102, 103, 107])
    self.assertSequenceEqual(list(tss.Strand), list(gtf.Strand))
    self.assertSequenceEqual(list(tss.transcript_id), list(gtf.transcript_id))


class UpgradeAnnotationIdsTest(absltest.TestCase):

  def test_upgrade_annotation_ids(self):
    old_ids = ['T1.1', 'T2.2', 'T3.3', 'T3.3_PAR_Y']
    new_ids = ['T0.3', 'T1.2', 'T2.2', 'T3.1', 'T3.4_PAR_Y', 'T4.2']
    upgrade_ids = gene_annotation.upgrade_annotation_ids(
        pd.Series(old_ids), pd.Series(new_ids)
    )
    self.assertSequenceEqual(
        list(upgrade_ids), ['T1.2', 'T2.2', 'T3.1', 'T3.4_PAR_Y']
    )

  def test_upgrade_annotation_ids_missing(self):
    old_ids = ['T1.1', 'T2.2', 'T3.3_PAR_Y']
    new_ids = ['T1.2', 'T2.2']
    upgrade_ids = gene_annotation.upgrade_annotation_ids(
        pd.Series(old_ids), pd.Series(new_ids)
    )
    self.assertSequenceEqual(list(upgrade_ids), ['T1.2', 'T2.2', np.nan])

  def test_upgrade_annotation_ids_missing_patch(self):
    old_ids = ['T1.1', 'T2', 'T3.3_PAR_Y']
    new_ids = ['T1.2', 'T2.2']
    with self.assertRaises(ValueError):
      gene_annotation.upgrade_annotation_ids(
          pd.Series(old_ids), pd.Series(new_ids)
      )

  def test_upgrade_annotation_ids_not_unique(self):
    old_ids = ['T1.1', 'T2.1', 'T2.2', 'T3.3_PAR_Y']
    new_ids = ['T1.2', 'T2.2']
    with self.assertRaises(AssertionError):
      gene_annotation.upgrade_annotation_ids(
          pd.Series(old_ids), pd.Series(new_ids)
      )

  def test_upgrade_annotation_ids_patchless(self):
    old_ids = ['T1', 'T2', 'T3', 'T3PAR_Y']
    new_ids = ['T0.3', 'T1.2', 'T2.2', 'T3.1', 'T3.4_PAR_Y', 'T4.2']
    upgrade_ids = gene_annotation.upgrade_annotation_ids(
        pd.Series(old_ids), pd.Series(new_ids), True
    )
    self.assertSequenceEqual(
        list(upgrade_ids), ['T1.2', 'T2.2', 'T3.1', 'T3.4_PAR_Y']
    )


class GetGeneIntervalTest(parameterized.TestCase):

  @parameterized.parameters([
      dict(gene_symbol='TP53'),
      dict(gene_symbol='tp53'),  # Should handle gene symbol case differences.
      dict(gene_symbol='EGFR'),
      dict(gene_symbol='TNF'),
      dict(gene_id='ENSG01.1'),
      dict(gene_id='ENSG01'),
  ])
  def test_get_gene_interval(self, gene_symbol=None, gene_id=None):
    gtf = pd.DataFrame({
        'gene_id': ['ENSG01.1', 'ENSG02.2', 'ENSG03.1'],
        'gene_name': ['TP53', 'EGFR', 'TNF'],
        'Chromosome': ['chr1', 'chr2', 'chr3'],
        'Start': [101, 150, 101],
        'End': [200, 200, 200],
        'Strand': ['+', '+', '-'],
        'Feature': 'gene',
    })
    interval = gene_annotation.get_gene_interval(
        gtf=gtf, gene_symbol=gene_symbol, gene_id=gene_id
    )
    self.assertIsNotNone(interval)

  @parameterized.parameters([
      dict(
          gene_symbol='FOO',
          gene_id=None,
          expected_error='No interval found for gene "FOO".',
      ),
      dict(
          gene_id='BAR',
          gene_symbol=None,
          expected_error='No interval found for gene "BAR".',
      ),
      dict(
          gene_id=None,
          gene_symbol=None,
          expected_error='Exactly one of gene_symbol or gene_id must be set.',
      ),
      dict(
          gene_id='ENSG01.1',
          gene_symbol=None,
          expected_error='Multiple intervals found for gene "ENSG01.1".',
      ),
  ])
  def test_invalid_gene_raises_error(
      self, gene_symbol, gene_id, expected_error
  ):
    gtf = pd.DataFrame({
        'gene_id': ['ENSG01.1', 'ENSG01.1', 'ENSG03.1'],
        'gene_name': ['TP53', 'EGFR', 'TNF'],
        'Chromosome': ['chr1', 'chr2', 'chr3'],
        'Start': [101, 150, 101],
        'End': [200, 200, 200],
        'Strand': ['+', '+', '-'],
        'Feature': 'gene',
    })
    with self.assertRaisesRegex(ValueError, expected_error):
      gene_annotation.get_gene_interval(
          gtf=gtf, gene_symbol=gene_symbol, gene_id=gene_id
      )


class FilterGTFTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    # Gene A has 3 transcripts, A1, A2, A3. A1 and A3 are the same length but
    # the first should be returned.
    # Gene B has 1 transcript, B1. It is the max length transcript due to being
    # the only one.
    # Gene C has 2 transcripts, C1, C2. C1 is the max length transcript.
    self.gtf = pd.DataFrame({
        'gene_id': ['A', 'A', 'A', 'B', 'C', 'C'],
        'transcript_id': ['A1', 'A2', 'A3', 'B1', 'C1', 'C2'],
        'Start': [101, 150, 101, 300, 500, 515],
        'End': [200, 200, 200, 420, 560, 560],
        'Strand': ['+', '+', '+', '-', '-', '-'],
        'Feature': 'transcript',
        'transcript_support_level': ['1', '2', '3', '1', '1', '2'],
    })

  def test_filter_to_longest_transcript(self):
    longest_transcript_gtf = gene_annotation.filter_to_longest_transcript(
        self.gtf
    )
    self.assertSequenceEqual(
        list(longest_transcript_gtf.transcript_id), ['A1', 'B1', 'C1']
    )

  @parameterized.parameters([
      dict(
          support_level=['1'],
          expected=['A1', 'B1', 'C1'],
      ),
      dict(
          support_level='1',
          expected=['A1', 'B1', 'C1'],
      ),
      dict(
          support_level=['1', '2'],
          expected=['A1', 'A2', 'B1', 'C1', 'C2'],
      ),
  ])
  def test_filter_transcript_support_level(self, support_level, expected):
    support_level1_gtf = gene_annotation.filter_transcript_support_level(
        self.gtf, support_level
    )
    self.assertSequenceEqual(list(support_level1_gtf.transcript_id), expected)

  def test_filter_transcript_support_level_invalid(self):
    # Test expected error if any invalid support level is requested.
    with self.assertRaises(ValueError):
      gene_annotation.filter_transcript_support_level(self.gtf, ['1', '6'])


if __name__ == '__main__':
  absltest.main()
