SUPPORTED_VERSION = [">=35.0.0"]

def get_algorithms():
    from atlas_rucio_policy_package.scope import ATLASScopeExtractionAlgorithm
    from atlas_rucio_policy_package.non_deterministic_pfn import ATLASNonDeterministicPFNAlgorithm
    from atlas_rucio_policy_package.pfn2lfn import ATLASRSEDeterministicScopeTranslation

    return {
        'non_deterministic_pfn': {
            'atlas_t0_non_deterministic_pfn': ATLASNonDeterministicPFNAlgorithm.construct_non_deterministic_pfn_t0,
            'atlas_dq2_non_deterministic_pfn': ATLASNonDeterministicPFNAlgorithm.construct_non_deterministic_pfn_dq2
            },
         'pfn2lfn': {
             'atlas_pfn2lfn': ATLASRSEDeterministicScopeTranslation.pfn2lfn_atlas
            },
         'scope': {
             'atlas_extract_scope': ATLASScopeExtractionAlgorithm.extract_scope_atlas
            }
    }
