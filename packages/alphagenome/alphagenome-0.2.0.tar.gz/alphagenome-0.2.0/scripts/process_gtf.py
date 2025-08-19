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

"""Script to process GTF into feather file."""

from absl import app
from absl import flags
from absl import logging
import pyranges


_GTF_PATH = flags.DEFINE_string(
    'gtf_path', None, 'Path to GTF file.', required=True
)
_OUTPUT_PATH = flags.DEFINE_string(
    'output_path', None, 'Path to output feather file.', required=True
)


def main(_) -> None:
  logging.info('Reading GTF from %s', _GTF_PATH.value)
  gtf = pyranges.read_gtf(_GTF_PATH.value, as_df=True)

  gtf['gene_id_nopatch'] = gtf['gene_id'].str.split('.', expand=True)[0]

  logging.info('Writing GTF to %s', _OUTPUT_PATH.value)
  gtf.to_feather(_OUTPUT_PATH.value)


if __name__ == '__main__':
  app.run(main)
