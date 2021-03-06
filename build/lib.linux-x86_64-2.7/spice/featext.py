#!/usr/bin/env python

"""
.. module:: featext

.. moduleauthor:: Bastiaan van den Berg <b.a.vandenberg@gmail.com>

"""

import os

import numpy

from spice import featmat
from spice import data_set
from spice import protein
from spice import mutation
from biopy import file_io


class FeatureCategory():

    def __init__(self, fc_id, fc_name, feature_func, param_names, param_types,
                 required_data, model_object):

        assert(len(param_names) == len(param_types))

        self._fc_id = fc_id
        self._fc_name = fc_name
        self._feature_func = feature_func
        self._param_names = param_names
        self._param_types = param_types
        self._required_data = required_data
        self._model_object = model_object

    @property
    def fc_id(self):
        return self._fc_id

    @property
    def fc_name(self):
        return self._fc_name

    @property
    def feature_func(self):
        return self._feature_func

    @property
    def param_names(self):
        return self._param_names

    @property
    def param_types(self):
        return self._param_types

    @property
    def required_data(self):
        return self._required_data

    @property
    def model_object(self):
        return self._model_object

    def param_values(self, param_id):
        '''
        This function turns a parameter id into a list of its parameter values.
        '''
        param_tokens = param_id.split('-')

        if(len(param_tokens) == 1 and param_tokens[0] == ''):
            return []
        else:
            assert(len(param_tokens) == len(self.param_types))
            return [t(p) for t, p in zip(self.param_types, param_tokens)]

    def param_str(self, param_id):
        '''
        This function rurns a parameter id into a readable parameters string.
        '''
        param_tokens = param_id.split('-')

        if(len(param_tokens) == 1 and param_tokens[0] == ''):
            return ''
        else:

            assert(len(param_tokens) == len(self.param_names))
            param_strings = ['%s: %s' % (p, v) for p, v in
                             zip(self.param_names, param_tokens)]
            return ', '.join(param_strings)

    def full_feat_ids(self, param_id):
        fids, _ = self.feat_id_name_list(param_id)
        full_ids = []
        for fid in fids:
            if not(param_id == '' or param_id is None):
                full_ids.append('%s_%s_%s' % (self.fc_id, param_id, fid))
            else:
                full_ids.append('%s_%s' % (self.fc_id, fid))
        return full_ids

    def feat_id_name_list(self, param_id):
        args = [self.model_object]
        args.extend(self.param_values(param_id))
        kwargs = {'feature_ids': True}
        return self.feature_func(*args, **kwargs)

    def feat_id_name_dict(self, param_id):
        fids, fnames = self.feat_id_name_list(param_id)
        return dict(zip(fids, fnames))


class FeatureExtraction(object):

    PROTEIN_FEATURE_CATEGORY_IDS = [
        'aac', 'dc', 'teraac', 'sigavg', 'sigpeak', 'ac', 'ctd', 'len', 'ssc',
        'ssaac', 'sac', 'saaac', 'cc', 'cu', 'qso', 'paac1', 'paac2'
    ]

    # - name
    # - feature calculation function
    # - parameter names
    # - parameter types
    # - required data sources
    PROTEIN_FEATURE_CATEGORIES = {

        'aac': FeatureCategory(
            'aac',
            'amino acid composition',
            protein.Protein.amino_acid_composition,
            ['number of segments'],
            [int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'dc': FeatureCategory(
            'dc',
            'dipeptide composition',
            protein.Protein.dipeptide_composition,
            ['number of segments'],
            [int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'teraac': FeatureCategory(
            'teraac',
            'terminal end amino acid count',
            protein.Protein.terminal_end_amino_acid_count,
            ['terminal end', 'length'],
            [str, int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'sigavg': FeatureCategory(
            'sigavg',
            'average signal value',
            protein.Protein.average_signal,
            ['scale', 'window', 'edge'],
            [str, int, float],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'sigpeak': FeatureCategory(
            'sigpeak',
            'signal value peaks area',
            protein.Protein.signal_peaks_area,
            ['scale', 'window', 'edge', 'threshold'],
            [str, int, float, float],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'ac': FeatureCategory(
            'ac',
            'autocorrelation',
            protein.Protein.autocorrelation,
            ['type', 'scale', 'lag'],
            [str, str, int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'ctd': FeatureCategory(
            'ctd',
            'property CTD',
            protein.Protein.property_ctd,
            ['property'],
            [str],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'len': FeatureCategory(
            'len',
            'protein length',
            protein.Protein.length,
            [],
            [],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'ssc': FeatureCategory(
            'ssc',
            'secondary structure composition',
            protein.Protein.ss_composition,
            ['number of segments'],
            [int],
            [(protein.Protein.get_secondary_structure_sequence, True)],
            protein.Protein('')),

        'ssaac': FeatureCategory(
            'ssaac',
            'per secondary structure amino acid composition',
            protein.Protein.ss_aa_composition,
            [],
            [],
            [(protein.Protein.get_secondary_structure_sequence, True),
             (protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'sac': FeatureCategory(
            'sac',
            'solvent accessibility composition',
            protein.Protein.sa_composition,
            ['number of segments'],
            [int],
            [(protein.Protein.get_solvent_accessibility_sequence, True)],
            protein.Protein('')),

        'saaac': FeatureCategory(
            'saaac',
            'per solvent accessibility class amino acid composition',
            protein.Protein.sa_aa_composition,
            [],
            [],
            [(protein.Protein.get_solvent_accessibility_sequence, True),
             (protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'cc': FeatureCategory(
            'cc',
            'codon composition',
            protein.Protein.codon_composition,
            [],
            [],
            [(protein.Protein.get_orf_sequence, True)],
            protein.Protein('')),

        'cu': FeatureCategory(
            'cu',
            'codon usage',
            protein.Protein.codon_usage,
            [],
            [],
            [(protein.Protein.get_orf_sequence, True)],
            protein.Protein('')),

        'qso': FeatureCategory(
            'qso',
            'quasi-sequence-order descriptors',
            protein.Protein.quasi_sequence_order_descriptors,
            ['aa distance matrix', 'rank'],
            [str, int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'paac1': FeatureCategory(
            'paac1',
            'pseudo AA composition type 1',
            protein.Protein.pseaac_type1,
            ['amino acid scale', 'lambda'],
            [str, int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein('')),

        'paac2': FeatureCategory(
            'paac2',
            'pseudo AA composition type 2',
            protein.Protein.pseaac_type2,
            ['amino acid scale', 'lambda'],
            [str, int],
            [(protein.Protein.get_protein_sequence, True)],
            protein.Protein(''))
    }

    assert(sorted(PROTEIN_FEATURE_CATEGORY_IDS) ==
           sorted(PROTEIN_FEATURE_CATEGORIES.keys()))

    MUTATION_FEATURE_CATEGORY_IDS = [
        'mutvec', 'mutsigdiff', 'seqenv', 'msa', 'msasigdiff', 'pfam', 'flex',
        'interaction', 'codonvec', 'codonenv'
    ]

    MUTATION_FEATURE_CATEGORIES = {

        'mutvec': FeatureCategory(
            'mutvec',
            'mutation vector',
            mutation.MissenseMutation.mutation_vector,
            [],
            [],
            [],
            mutation.MissenseMutation()),

        'mutsigdiff': FeatureCategory(
            'mutsigdiff',
            'mutation signal difference',
            mutation.MissenseMutation.signal_diff,
            ['scale'],
            [str],
            [],
            mutation.MissenseMutation()),

        'seqenv': FeatureCategory(
            'seqenv',
            'sequence environment amino acid counts',
            mutation.MissenseMutation.seq_env_aa_count,
            ['window'],
            [int],
            [],
            mutation.MissenseMutation()),

        'msa': FeatureCategory(
            'msa',
            'msa-based',
            mutation.MissenseMutation.msa,
            [],
            [],
            [],
            mutation.MissenseMutation()),

        'msasigdiff': FeatureCategory(
            'msasigdiff',
            'msa signal difference',
            mutation.MissenseMutation.msa_signal_diff,
            ['scale'],
            [str],
            [],
            mutation.MissenseMutation()),

        'pfam': FeatureCategory(
            'pfam',
            'pfam annotation',
            mutation.MissenseMutation.pfam_annotation,
            [],
            [],
            [],
            mutation.MissenseMutation()),

        'flex': FeatureCategory(
            'flex',
            'backbone_dynamics',
            mutation.MissenseMutation.residue_flexibility,
            [],
            [],
            [],
            mutation.MissenseMutation()),

        'interaction': FeatureCategory(
            'interaction',
            'protein interaction counts',
            mutation.MissenseMutation.interaction_counts,
            [],
            [],
            [],
            mutation.MissenseMutation()),

        'codonvec': FeatureCategory(
            'codonvec',
            'from codon vector',
            mutation.MissenseMutation.from_codon_vector,
            [],
            [],
            [],
            mutation.MissenseMutation()),

        'codonenv': FeatureCategory(
            'codonenv',
            'sequence environment codon counts',
            mutation.MissenseMutation.seq_env_codon_count,
            ['window'],
            [int],
            [],
            mutation.MissenseMutation()),
    }

    assert(sorted(MUTATION_FEATURE_CATEGORY_IDS) ==
           sorted(MUTATION_FEATURE_CATEGORIES.keys()))

    def __init__(self):

        # define file location if we want to store data
        self.root_dir = None

        # initialize empty feature matrices
        self.fm_protein = featmat.FeatureMatrix()
        self.fm_missense = featmat.FeatureMatrix()

        # initialize protein data set
        self.protein_data_set = data_set.ProteinDataSet()

        # initialize feature vectors
        #self.fv_dict_protein = None
        #self.fv_dict_missense = None

    def set_root_dir(self, root_dir):
        '''
        Set the root dir if you want to load or store the data to file.
        '''

        # store the root dir
        self.root_dir = root_dir

        # set the protein feature matrix root dir
        self.fm_protein_d = os.path.join(root_dir, 'feature_matrix_protein')
        #self.fm_protein.set_root_dir(self.fm_protein_d)

        # set the missense mutation feature matrix root dir
        self.fm_missense_d = os.path.join(root_dir, 'feature_matrix_missense')
        #self.fm_missense.set_root_dir(self.fm_missense_d)

        # set the protein data set root dir
        self.protein_data_set_d = os.path.join(root_dir, 'protein_data_set')
        self.protein_data_set.set_root_dir(self.protein_data_set_d)

    def set_protein_ids(self, protein_ids):
        # use protein ids to initiate protein objects in data set
        self.protein_data_set.set_proteins(protein_ids)
        # use the protein ids as object ids in the protein feature matrix
        self.fm_protein.object_ids = self.protein_data_set.get_protein_ids()

    def load_protein_ids(self, protein_ids_f):
        with open(protein_ids_f, 'r') as fin:
            protein_ids = [i for i in file_io.read_ids(fin)]
        self.set_protein_ids(protein_ids)

    def load_mutation_data(self, mutation_f):

        # add mutation data to protein data set
        self.protein_data_set.load_mutation_data(mutation_f)

        # use the mutation ids as object ids in the mutation feature matrix
        mut_ids = self.protein_data_set.get_mutation_ids()
        self.fm_missense.object_ids = mut_ids

        # and create mutation feature vector object
        #self.fv_dict_missense = MutationFeatureVectorFactory().\
        #    get_feature_vectors(self.protein_data_set.get_mutations())

    def calculate_protein_features(self, featcat_id):
        '''
        Calculates protein features defined by the feature category id. Feature
        values are appended to the protein feature matrix.

        The featcat_id parameter is of the form:

        featcatid_params

        In this featcatid is the feature category id, e.g. aac for amino acid
        composition, and params is a colon separated list of parameters for
        this type of feature. In case of the amino acid composition, the number
        of protein segments should be defined a parameter, e.g. aac_10 means
        the amino acid composition of 10 equal sized protein segments.
        '''

        assert(self.fm_protein.object_ids)

        if('_' in featcat_id):

            # split feature id and paramaters string
            fc_id, params_str = featcat_id.split('_')

            # parse the parameter string to a list of parameters
            param_list = params_str.split('-')

        else:

            fc_id = featcat_id
            param_list = []

        # obtain feature category object for given feature category id
        featcat = self.PROTEIN_FEATURE_CATEGORIES[fc_id]

        assert(len(param_list) == len(featcat.param_types))

        args = []
        for p, pt in zip(param_list, featcat.param_types):
            args.append(pt(p))

        # fetch feature ids and names
        (ids, names) = featcat.feature_func(featcat.model_object, *args,
                                            feature_ids=True)

        # append feature id to feature category id
        feat_ids = ['%s_%s' % (featcat_id, i) for i in ids]

        # initialize empty feature matrix
        fm = numpy.empty((len(self.fm_protein.object_ids), len(feat_ids)))

        # fill the matrix
        for index, o in enumerate(self.protein_data_set.get_proteins()):
            fm[index, :] = featcat.feature_func(o, *args)

        self.fm_protein.add_features(feat_ids, fm, feature_names=names)

    def calculate_missense_features(self, featcat_id):

        assert(self.fm_protein.object_ids)

        if('_' in featcat_id):

            # split feature id and paramaters string
            fc_id, params_str = featcat_id.split('_')

            # parse the parameter string to a list of parameters
            param_list = params_str.split('-')

        else:

            fc_id = featcat_id
            param_list = []

        # obtain feature category object for given feature category id
        featcat = self.MUTATION_FEATURE_CATEGORIES[fc_id]

        assert(len(param_list) == len(featcat.param_types))

        args = []
        for p, pt in zip(param_list, featcat.param_types):
            args.append(pt(p))

        # fetch feature ids and names
        (ids, names) = featcat.feature_func(featcat.model_object, *args,
                                            feature_ids=True)

        # append feature id to feature category id
        feat_ids = ['%s_%s' % (featcat_id, i) for i in ids]

        # initialize empty feature matrix
        fm = numpy.empty((len(self.fm_missense.object_ids), len(feat_ids)))

        # fill the matrix
        for index, m in enumerate(self.protein_data_set.get_mutations()):
            fm[index, :] = featcat.feature_func(m, *args)

        self.fm_missense.add_features(feat_ids, fm, feature_names=names)

    def available_protein_featcat_ids(self):
        '''
        This function returns the set of allready calculated protein feature
        categories, a set with category ids is returned.
        '''

        featcat_ids = set()

        for f in self.fm_protein.feature_ids:
            parts = f.split('_')
            if(len(parts) == 2):
                featcat_ids.add(parts[0])
            elif(len(parts) == 3):
                featcat_ids.add('_'.join(parts[:2]))

        return featcat_ids

    def categorized_protein_feature_ids(self):
        '''
        This function returns all feature ids sorted by feature category and
        category parameter settings. The returned dictionary containes a
        mapping from feature category id to a dictionary. This dictionary
        contains a mapping from parameter settings for this category to the
        list with corresponding feature ids.

        {
            'aac':
            {
                '2' : ['aac_2_A1', 'aac_2_R1', ..., 'aac_2_V2'],
                '5' : ['aac_5_A1', 'aac_5_R1', ..., 'aac_5_V5'],
                ...
            },
            ...
        }

        '''

        cat_feat_dict = {}

        for feat_id in self.fm_protein.feature_ids:

            tokens = feat_id.split('_')

            if(len(tokens) == 2):
                cat, feat = tokens
                params_str = ''
            else:
                cat, params_str, feat = tokens

            # not so easy to read, but works... building dict with dicts
            cat_feat_dict.setdefault(cat, {})\
                         .setdefault(params_str, []).append(feat_id)

        return cat_feat_dict

    def load(self):

        assert(self.root_dir)

        # load the feature matrices
        fmp = featmat.FeatureMatrix.load_from_dir(self.fm_protein_d)
        self.fm_protein = fmp

        fmm = featmat.FeatureMatrix.load_from_dir(self.fm_missense_d)
        self.fm_missense = fmm

        # load protein data set
        self.protein_data_set.load()

        '''
        # create protein feature vectors object
        if(self.protein_data_set.get_proteins()):
            self.fv_dict_protein = ProteinFeatureVectorFactory().\
                    get_feature_vectors(self.protein_data_set.get_proteins())

        # create mutation feature vector object
        if(self.protein_data_set.get_mutations()):
            self.fv_dict_missense = MutationFeatureVectorFactory().\
                    get_feature_vectors(self.protein_data_set.get_mutations())
        '''

    def save(self):

        assert(self.root_dir)

        # create root dir, if not available
        if not(os.path.exists(self.root_dir)):
            os.makedirs(self.root_dir)

        # save feature matrix
        self.fm_protein.save_to_dir(self.fm_protein_d)
        self.fm_missense.save_to_dir(self.fm_missense_d)

        # save protein data set
        self.protein_data_set.save()

    def __str__(self):
        return '%s\n%s\n' % (str(self.fm_protein), str(self.fm_missense))


#if __name__ == '__main__':
# TODO add test runs
