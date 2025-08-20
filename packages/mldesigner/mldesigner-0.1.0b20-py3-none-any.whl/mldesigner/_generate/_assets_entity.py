# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument

from os import PathLike
from pathlib import Path
from typing import Dict, Union, List

from mldesigner._constants import BASE_PATH_CONTEXT_KEY
from mldesigner._exceptions import UserErrorException
from mldesigner._generate._assets_schema import PackageAssetsSchema
from mldesigner._utils import load_yaml


class PackageAssets(dict):
    @classmethod
    def _get_schema(cls, context) -> PackageAssetsSchema:
        return PackageAssetsSchema(context=context)

    @property
    def components(self) -> dict:
        return self["components"]

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str] = None,
        **kwargs,
    ) -> "PackageAssets":
        yaml_dict = load_yaml(path)
        if yaml_dict is None:
            msg = "Target yaml file is empty: {}"
            raise UserErrorException(msg.format(path))
        if not isinstance(yaml_dict, dict):
            msg = "Expect dict but get {} after parsing yaml file: {}"
            raise UserErrorException(msg.format(type(yaml_dict), path))
        return cls._load(data=yaml_dict, yaml_path=path)

    @classmethod
    def _load(cls, data: Dict = None, yaml_path: Union[PathLike, str] = None, **kwargs):
        data = data or {}
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
        }
        # pylint: disable=no-member
        return PackageAssets(**cls._get_schema(context=context).load(data))

    def split(self, n: int) -> List["PackageAssets"]:
        """Try to split components into n pieces and generate n PackageAssets for them. Each new PackageAssets will
        contain several keys in components and their corresponding assets.
        Note that, each key in components will be in and only in one PackageAssets. So if n is larger than the number
        of keys in components, only len(components) PackageAssets will be returned.
        On the other hand, the function will try to split assets evenly.

        :param n: number of pieces to split.
        :type n: int
        :return: A list of PackageAssets. Each PackageAssets will contain part of keys in components.
        :rtype: List[PackageAssets]
        """
        if len(self.components) <= n:
            return [PackageAssets(components={key: assets}) for key, assets in self.components.items()]

        pieces = []
        for _ in range(n):
            pieces.append({})

        for key, assets in self.components.items():
            min_piece = min(pieces, key=lambda piece: sum(map(len, piece.values())))
            min_piece[key] = assets

        return [PackageAssets(components=piece) for piece in pieces]
