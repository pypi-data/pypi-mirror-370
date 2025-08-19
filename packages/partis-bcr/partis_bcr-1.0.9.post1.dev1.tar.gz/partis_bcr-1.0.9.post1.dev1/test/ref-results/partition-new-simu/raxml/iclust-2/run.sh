#!/bin/bash
/home/runner/work/partis/partis/bin/raxml-ng-linux --model GTR+G --msa /home/runner/work/partis/partis/test/ref-results/partition-new-simu/raxml/iclust-2/input-seqs.fa --msa-format FASTA
/home/runner/work/partis/partis/bin/raxml-ng-linux --model GTR+G --msa /home/runner/work/partis/partis/test/ref-results/partition-new-simu/raxml/iclust-2/input-seqs.fa --msa-format FASTA --ancestral --tree /home/runner/work/partis/partis/test/ref-results/partition-new-simu/raxml/iclust-2/input-seqs.fa.raxml.ancestralTree
