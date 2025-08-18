#!/usr/bin/env python

from bisos.sbom import pkgsSeed  # pkgsSeed.plantWithWhich("seedSbom.cs")
ap = pkgsSeed.aptPkg

aptPkgsList = [
    ap("vagrant"),
    ap("packer"),    
]

pkgsSeed.setup(
    aptPkgsList=aptPkgsList,
)
