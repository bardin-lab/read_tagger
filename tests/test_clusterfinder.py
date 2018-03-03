from collections import namedtuple
from readtagger.findcluster import (
    ClusterFinder,
    ClusterManager
)
from readtagger.cli import findcluster

from .helpers import (  # noqa: F401
    namedtuple_to_argv,
    reference_fasta
)

INPUT = 'tagged_dm6.bam'
CORNERCASE = 'cornercase.bam'
CORNERCASE2 = 'cornercase2.bam'
CORNERCASE3 = 'cornercase3.bam'
EXTENDED = 'extended_and_annotated_roi.bam'
GENOME_FRAGMENT = 'genome_fragment.fa'
COMPLEX = 'extended_annotated_updated_all_reads.bam'
HOMOZYGOUS_COPIA = 'homozygous_copia.bam'
REORGANIZE_CLUSTER = 'reorganize_cluster.bam'
NON_SUPPORT = 'non_support_test.bam'
MATE_SUPPORT_REFERENCE_GENOTYPE = 'mate_support_reference_genotype.bam'
REFINE_COORD = 'refine_coord.bam'
REASSEMBLE = 'reassemble_input.bam'
SPLIT_CLUSTER = 'hum3_false_merge.bam'
SPLIT_CLUSTER_OPT = 'split_cluster_opt.bam'
SPLIT_CLUSTER_OPT2 = 'improve_clustering.bam'
MULTIPROCESSING = 'pasteurianus.bam'
NANOPORE_ROVER = 'long_rover_insert_heterozygous.bam'
DONT_MERGE = 'do_not_merge.bam'
DONT_MERGE_5 = 'dont_merge_5.bam'
DONT_MERGE_6 = 'dont_merge_6.bam'
DONT_MERGE_7 = 'dont_merge_back7.bam'
DECOY = 'decoy.bam'
DONT_SPLIT = 'dont_split.bam'
REFINE_TSD = 'wrong_tsd.bam'

DEFAULT_MAX_PROPER_PAIR_SIZE = 700


def test_clusterfinder_single_cluster(datadir_copy):  # noqa: D103
    input_path = str(datadir_copy[INPUT])
    cf = ClusterFinder(input_path=input_path,
                       max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 1
    assert cf.cluster[0].nalt == 19


def test_clusterfinder_include_duplicates(datadir_copy):  # noqa: D103
    input_path = str(datadir_copy[INPUT])
    cf = ClusterFinder(input_path=input_path,
                       include_duplicates=True,
                       max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 1
    assert cf.cluster[0].nalt == 26


def test_clusterfinder_remove_supplementary(datadir_copy):  # noqa: D103
    input_path = str(datadir_copy[INPUT])
    cf = ClusterFinder(input_path=input_path,
                       include_duplicates=True,
                       remove_supplementary_without_primary=True,
                       max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 1
    assert cf.cluster[0].nalt == 24


def test_clusterfinder_reassemble(datadir_copy, tmpdir, reference_fasta):   # noqa: D103, F811
    input_path = str(datadir_copy[REASSEMBLE])
    genome_reference_fasta = str(datadir_copy[GENOME_FRAGMENT])
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=tmpdir.join('output.gff').strpath,
                             genome_reference_fasta=genome_reference_fasta,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=480)
    assert len(clusters.cluster) == 1
    assert clusters.cluster[0].valid_tsd


def test_clusterfinder_split_cluster(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[SPLIT_CLUSTER])
    cf = ClusterFinder(input_path=input_path, output_bam=tmpdir.join('output.bam').strpath,
                       include_duplicates=False,
                       remove_supplementary_without_primary=False,
                       output_gff=tmpdir.join('out.gff').strpath,
                       max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 3
    assert len(cf.cluster[1]) == 39
    assert len(cf.cluster[2]) == 27


def test_clusterfinder_refine_split(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[SPLIT_CLUSTER_OPT])
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=tmpdir.join('output.gff').strpath,
                             transposon_reference_fasta=None,
                             max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    cluster = clusters.cluster[0]
    genotype = cluster.genotype_likelihoods
    assert genotype.nref == 73
    assert genotype.nalt == 117
    assert genotype.genotype == 'heterozygous'


def test_clusterfinder_refine_split2(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[SPLIT_CLUSTER_OPT2])
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=tmpdir.join('output.gff').strpath,
                             transposon_reference_fasta=None,
                             max_proper_pair_size=1500)
    # Should be 3 clusters -- one mate pointing away from the cluster (1),
    # one read with BD and AD tag (2), which doesn't join with the large cluster to the right (3)
    assert len(clusters.cluster) == 3
    cluster_one, cluster_two, cluster_three = clusters.cluster
    assert cluster_one.nalt == 1
    assert cluster_two.nalt == 134
    assert cluster_three.nalt == 1


def test_cornercase(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[CORNERCASE])
    output_gff = tmpdir.join('output.gff').strpath
    cf = ClusterFinder(input_path=input_path, output_gff=output_gff, min_mapq=-1, max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 1
    input_path = str(datadir_copy[CORNERCASE2])
    cf = ClusterFinder(input_path=input_path, output_gff=output_gff, max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 0
    input_path = str(datadir_copy[CORNERCASE3])
    cf = ClusterFinder(input_path=input_path, output_gff=output_gff, max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)


def test_clusterfinder_multiple_cluster(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[EXTENDED])
    output_bam = tmpdir.join('tagged_clusters.bam')
    cf = ClusterFinder(input_path=input_path, output_bam=output_bam.strpath, max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 2


def test_clusterfinder_multiple_cluster_gff(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[EXTENDED])
    output_gff = tmpdir.join('output.gff')
    cf = ClusterFinder(input_path=input_path, output_gff=output_gff.strpath, max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    assert len(cf.cluster) == 2


def test_clustermanager_single_core(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[EXTENDED])
    output_gff = tmpdir.join('output.gff').strpath
    output_bam = tmpdir.join('output.bam').strpath
    ClusterManager(input_path=input_path,
                   genome_reference_fasta=None,
                   transposon_reference_fasta=None,
                   output_bam=output_bam,
                   output_gff=output_gff,
                   threads=1,
                   max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)


def test_clustermanager_multiprocessing(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[MULTIPROCESSING])
    output_gff = tmpdir.join('output.gff').strpath
    output_bam = tmpdir.join('output.bam').strpath
    ClusterManager(input_path=input_path,
                   genome_reference_fasta=None,
                   transposon_reference_fasta=None,
                   output_bam=output_bam,
                   output_gff=output_gff,
                   threads=2,
                   max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)


def test_clusterfinder_multiple_cluster_gff_cli(datadir_copy, tmpdir, mocker):  # noqa: D103
    input_path = str(datadir_copy[EXTENDED])
    output_bam = tmpdir.join('output.bam').strpath
    output_gff = tmpdir.join('output.gff').strpath
    args_template = namedtuple('ArgumentParser', 'input_path output_gff output_bam')
    args = args_template(input_path=input_path, output_bam=output_bam, output_gff=output_gff)
    argv = namedtuple_to_argv(args)
    mocker.patch('sys.argv', argv)
    mocker.patch('sys.exit')
    findcluster.cli()


def test_clusterfinder_blast(datadir_copy, tmpdir, mocker, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[EXTENDED])
    output_bam = tmpdir.join('output.bam').strpath
    output_gff = tmpdir.join('output.gff').strpath
    args_template = namedtuple('ArgumentParser', 'input_path output_gff output_bam transposon_reference_fasta')
    args = args_template(input_path=input_path, output_bam=output_bam, output_gff=output_gff, transposon_reference_fasta=reference_fasta)
    argv = namedtuple_to_argv(args)
    mocker.patch('sys.argv', argv)
    mocker.patch('sys.exit')
    findcluster.cli()


def test_clusterfinder_homozygous_copia(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[HOMOZYGOUS_COPIA])
    output_bam = tmpdir.join('output.bam').strpath
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    cluster = clusters.cluster[0]
    assert cluster.nalt == 57
    genotype = cluster.genotype_likelihoods
    assert genotype.genotype == 'homozygous'
    assert genotype.nref == 0
    assert genotype.nalt == 57


def test_clusterfinder_complex_genotype(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[COMPLEX])
    output_bam = tmpdir.join('output.bam').strpath
    output_gff = tmpdir.join('output.gff').strpath
    output_fasta = tmpdir.join('output.fasta').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             output_fasta=output_fasta,
                             max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    cluster = clusters.cluster[0]
    assert cluster.nalt == 28
    genotype = cluster.genotype_likelihoods
    assert genotype.nref == 17
    assert genotype.nalt == 28
    assert genotype.genotype == 'heterozygous'
    assert len(open(output_fasta).readlines()) == 4


def test_clusterfinder_nanopore(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[NANOPORE_ROVER])
    output_bam = tmpdir.join('output.bam').strpath
    output_gff = tmpdir.join('output.gff').strpath
    output_fasta = tmpdir.join('output.fasta').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             output_fasta=output_fasta,
                             max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    cluster = clusters.cluster[0]
    assert cluster.nalt == 7
    assert cluster.total_left_count == 1
    assert cluster.total_right_count == 6


def test_clusterfinder_nonsupport(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[NON_SUPPORT])
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=None,
                             transposon_reference_fasta=None,
                             max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    cluster = clusters.cluster[-1]
    assert cluster.nref == 25  # Could also be 26 -- need to figure that out.
    genotype = cluster.genotype_likelihoods
    assert genotype.nref == 25
    assert genotype.nalt == 1
    assert genotype.genotype == 'reference'


def test_clusterfinder_nonsupport_reference_genotype(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[MATE_SUPPORT_REFERENCE_GENOTYPE])
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=None,
                             transposon_reference_fasta=None,
                             max_proper_pair_size=578)
    cluster = clusters.cluster[-1]
    assert cluster.nref == 50  # Could also be 26 -- need to figure that out.
    genotype = cluster.genotype_likelihoods
    assert genotype.nref == 50
    assert genotype.nalt == 2
    assert genotype.genotype == 'reference'


def test_clusterfinder_refine_coord(datadir_copy, tmpdir):  # noqa: D103
    input_path = str(datadir_copy[REFINE_COORD])
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=tmpdir.join('output.gff').strpath,
                             transposon_reference_fasta=None,
                             max_proper_pair_size=480)
    cluster = clusters.cluster[-1]
    genotype = cluster.genotype_likelihoods
    assert genotype.nref == 0
    assert genotype.nalt == 5
    assert genotype.genotype == 'homozygous'


def test_clusterfinder_reorganize_cluster(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[REORGANIZE_CLUSTER])
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=None,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=DEFAULT_MAX_PROPER_PAIR_SIZE)
    cluster = clusters.cluster[-1]
    genotype = cluster.genotype_likelihoods
    assert genotype.genotype == 'homozygous'


def test_clusterfinder_do_not_merge(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[DONT_MERGE])
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=None,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=649)
    cluster_one = clusters.cluster[0]
    assert cluster_one.genotype == 'reference'
    assert cluster_one.nref == 101
    assert cluster_one.nalt == 1
    cluster_two = clusters.cluster[1]
    assert cluster_two.genotype == 'reference'
    assert cluster_two.nref == 81
    assert cluster_two.nalt == 1


def test_clusterfinder_do_not_merge5(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[DONT_MERGE_5])
    output_gff = tmpdir.join('output.gff').strpath
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=649)
    cluster_one = clusters.cluster[0]
    assert cluster_one.genotype == 'reference'
    assert cluster_one.nref == 108
    assert cluster_one.nalt == 4
    cluster_two = clusters.cluster[1]
    assert cluster_two.genotype == 'reference'
    assert cluster_two.nref == 66
    assert cluster_two.nalt == 4


def test_clusterfinder_do_not_merge7(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[DONT_MERGE_7])
    output_gff = tmpdir.join('output.gff').strpath
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=900)
    assert len(clusters.cluster) == 2
    cluster_one, cluster_two = clusters.cluster
    assert cluster_one.genotype == 'heterozygous'
    assert cluster_one.nref == 45
    assert cluster_one.nalt == 71
    assert cluster_two.genotype == 'reference'
    assert cluster_two.nref == 31
    assert cluster_two.nalt == 2


def test_clusterfinder_estimate_coverage(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[DONT_MERGE_5])
    output_gff = tmpdir.join('output.gff').strpath
    output_bam = tmpdir.join('output.bam').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=output_bam,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=1500)
    assert len(clusters.cluster) == 1
    cluster_one = clusters.cluster[0]
    assert cluster_one.genotype == 'reference'
    assert cluster_one.nref == 174
    assert cluster_one.nalt == 8


def test_clusterfinder_check_consistency(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[DONT_MERGE_6])
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=None,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=649)
    cluster_one = clusters.cluster[0]
    assert cluster_one.genotype == 'reference'
    assert cluster_one.nref == 69
    assert cluster_one.nalt == 3
    cluster_two = clusters.cluster[1]
    assert cluster_two.genotype == 'reference'
    assert cluster_two.nref == 64
    assert cluster_two.nalt == 1


def test_clusterfinder_decoy_chromosome(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    input_path = str(datadir_copy[DECOY])
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=None,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=649)
    assert len(clusters.cluster) == 85


def test_clusterfinder_refine_tsd(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    # This cluster should not be split, since there is a small deletion
    # associated with a TE insertion.
    input_path = str(datadir_copy[REFINE_TSD])
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=None,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=649)
    cluster = clusters.cluster[0]
    assert cluster.valid_tsd


def test_clusterfinder_dont_split(datadir_copy, tmpdir, reference_fasta):  # noqa: D103, F811
    # This cluster should not be split, since there is a small deletion
    # associated with a TE insertion.
    input_path = str(datadir_copy[DONT_SPLIT])
    output_gff = tmpdir.join('output.gff').strpath
    clusters = ClusterFinder(input_path=input_path,
                             output_bam=None,
                             output_gff=output_gff,
                             transposon_reference_fasta=reference_fasta,
                             max_proper_pair_size=649)
    assert len(clusters.cluster) == 1
    cluster = clusters.cluster[0]
    assert cluster.nref == 18
    assert cluster.nalt == 37
