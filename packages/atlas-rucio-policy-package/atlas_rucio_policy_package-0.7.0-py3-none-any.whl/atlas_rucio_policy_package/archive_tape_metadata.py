from typing import Any, Optional, Union

import rucio.core.did
from rucio.db.sqla.constants import DIDType
from rucio.transfertool.fts3_plugins import FTS3TapeMetadataPlugin

class ATLASArchiveMetadataPlugin(FTS3TapeMetadataPlugin):
    """
    Specification: https://codimd.web.cern.ch/bmEXKlYqQbu529PUdAFfYw#
    """

    def __init__(self) -> None:
        policy_algorithm = 'atlas'
        self.register(
            policy_algorithm,
            func=lambda x: self.get_atlas_archive_metadata(x)
        )
        super().__init__(policy_algorithm)

    @staticmethod
    def get_atlas_archive_metadata(**hints: dict[str, Any]) -> dict[str, Any]:
        archive_metadata = {
            'file_metadata': ATLASArchiveMetadataPlugin._get_file_metadata(**hints),
            'additional_hints': {
                'activity': hints.get('activity'),
            },
            'schema_version': 1
        }

        scope, name = hints['scope'], hints['name']
        did_metadata = rucio.core.did.get_metadata(scope, name)

        datatype = did_metadata['datatype'] or None

        # RAW is the only datatype with a collocation template for the moment
        if datatype == 'RAW':

            parent_did = ATLASArchiveMetadataPlugin._get_parent_did(scope, name)

            archive_metadata['collocation_hints'] = ATLASArchiveMetadataPlugin._get_collocation_hints(did_metadata=did_metadata, parent_did_name=parent_did.get('name'))

            if parent_did:
                dataset_did = rucio.core.did.get_did(parent_did['scope'], parent_did['name'], dynamic_depth=DIDType.DATASET)
                archive_metadata['additional_hints']['3'] = ATLASArchiveMetadataPlugin._get_additional_dataset_hints(dataset_did)

        return archive_metadata

    @staticmethod
    def _get_parent_did(scope: str, name: str) -> Optional[dict[str, Any]]:
        parent_dids = rucio.core.did.list_parent_dids(scope, name, order_by=['created_at'])
        # Get first parent DID (if it exists)
        if parent_dids:
            parent_did = next(parent_dids)
            return parent_did
        return None

    @staticmethod
    def _get_file_metadata(**hints: dict[str, Any]) -> dict[str, Any]:
        return {
            'size': hints.get('filesize'),
            'md5': hints.get('md5'),
            'adler32': hints.get('adler32'),
        }

    @staticmethod
    def _get_collocation_hints(did_metadata: dict[str, Any], parent_did_name: Optional[str]) -> dict[str, Optional[Union[str, dict[str, Any]]]]:
        """
        Example filename:
        data23_13p6TeV.00452799.physics_Main.daq.RAW._lb0777._SFO-19._0001.data

        Levels:
        0 - datatype (e.g. "RAW")
        1 - project (e.g. "data23_13p6TeV")
        2 - stream_name (e.g. "physics_Main")
        3 - dataset (e.g. "data23_13p6TeV.00452799.physics_Main.daq.RAW")
        """

        return {
                "0": did_metadata['datatype'] or None,
                "1": did_metadata['project'] or None,
                "2": did_metadata['stream_name'] or None,
                "3": parent_did_name,
            }


    @staticmethod
    def _get_additional_dataset_hints(dataset_did: dict[str, Any]) -> dict[str, Any]:
        return {
            'length': dataset_did.get('length'),
            'size': dataset_did.get('bytes'),
        }

# Trigger registration
ATLASArchiveMetadataPlugin()
