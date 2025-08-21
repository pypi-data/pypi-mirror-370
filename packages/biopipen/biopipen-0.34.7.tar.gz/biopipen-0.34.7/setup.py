# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biopipen',
 'biopipen.core',
 'biopipen.ns',
 'biopipen.scripts.bam',
 'biopipen.scripts.bed',
 'biopipen.scripts.cellranger',
 'biopipen.scripts.cnvkit',
 'biopipen.scripts.misc',
 'biopipen.scripts.protein',
 'biopipen.scripts.regulatory',
 'biopipen.scripts.scrna',
 'biopipen.scripts.snp',
 'biopipen.scripts.tcgamaf',
 'biopipen.scripts.tcr',
 'biopipen.scripts.tcr.GIANA',
 'biopipen.scripts.tcr.TESSA_source',
 'biopipen.scripts.vcf',
 'biopipen.scripts.web',
 'biopipen.utils']

package_data = \
{'': ['*'],
 'biopipen': ['reports/*',
              'reports/bam/*',
              'reports/cellranger/*',
              'reports/cnv/*',
              'reports/cnvkit/*',
              'reports/gsea/*',
              'reports/protein/*',
              'reports/scrna/*',
              'reports/scrna_metabolic_landscape/*',
              'reports/snp/*',
              'reports/tcr/*',
              'reports/utils/*',
              'reports/vcf/*',
              'scripts/cnv/*',
              'scripts/delim/*',
              'scripts/gene/*',
              'scripts/gsea/*',
              'scripts/plot/*',
              'scripts/rnaseq/*',
              'scripts/scrna_metabolic_landscape/*',
              'scripts/stats/*']}

install_requires = \
['datar[pandas]>=0.15.8,<0.16.0',
 'pipen-board[report]>=0.17,<0.18',
 'pipen-cli-run>=0.15,<0.16',
 'pipen-deprecated>=0.0,<0.1',
 'pipen-filters>=0.15,<0.16',
 'pipen-poplog>=0.3,<0.4',
 'pipen-verbose>=0.14,<0.15']

extras_require = \
{'runinfo': ['pipen-runinfo>=0.9,<0.10']}

entry_points = \
{'pipen_cli_run': ['bam = biopipen.ns.bam',
                   'bed = biopipen.ns.bed',
                   'cellranger = biopipen.ns.cellranger',
                   'cellranger_pipeline = biopipen.ns.cellranger_pipeline',
                   'cnv = biopipen.ns.cnv',
                   'cnvkit = biopipen.ns.cnvkit',
                   'cnvkit_pipeline = biopipen.ns.cnvkit_pipeline',
                   'delim = biopipen.ns.delim',
                   'gene = biopipen.ns.gene',
                   'gsea = biopipen.ns.gsea',
                   'misc = biopipen.ns.misc',
                   'plot = biopipen.ns.plot',
                   'protein = biopipen.ns.protein',
                   'regulatory = biopipen.ns.regulatory',
                   'rnaseq = biopipen.ns.rnaseq',
                   'scrna = biopipen.ns.scrna',
                   'scrna_metabolic_landscape = '
                   'biopipen.ns.scrna_metabolic_landscape',
                   'snp = biopipen.ns.snp',
                   'stats = biopipen.ns.stats',
                   'tcgamaf = biopipen.ns.tcgamaf',
                   'tcr = biopipen.ns.tcr',
                   'vcf = biopipen.ns.vcf',
                   'web = biopipen.ns.web']}

setup_kwargs = {
    'name': 'biopipen',
    'version': '0.34.7',
    'description': 'Bioinformatics processes/pipelines that can be run from `pipen run`',
    'long_description': 'None',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
