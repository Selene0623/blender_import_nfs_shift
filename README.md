Blender 5.x addons for importing models from Slightly Mad Studios' Chameleon engine (NFS Shift, Shift 2 Unleashed, Project CARS).

Port of the [SMS Importer 3.1c 3DSMax script by Chipicao and vagos21](https://www.tapatalk.com/groups/kottons_chop_shop/ti-scp-ti-sms-model-importer-t3217.html). Mesh import rewritten using `from_pydata()` + bmesh (no OBJ intermediary — pattern from [ForzaTech-extraction-tools](https://github.com/Doliman100/ForzaTech-extraction-tools)).

## Addons

| Addon | Menu | Purpose |
|-------|------|---------|
| `meb_import/` | File > Import > Shift 2 mesh (.meb) | Imports `.meb` / `.imb` meshes with UVs, normals, vertex colors, materials |
| `vhf_import/` | File > Import > Shift 2 transform (.vhf) | Applies `.vhf` XML position/orientation to already-imported meshes |

## Workflow

1. Extract `.BFF` game archives with QuickBMS + `nfsshift.bms`
2. `File > Import > Shift 2 mesh (.meb)` — supports batch folder import
3. To position parts: `File > Import > Shift 2 transform (.vhf)` — reads XML matrix data, applies transforms to meshes in a named collection

## Format notes

- `.meb` / `.imb` — binary mesh files (verts, UV channels, normals, vertex colors, bone weights)
- `.vhf` — XML with per-part transformation matrices
- `.bml` — car definition container (BLMY chunk format referencing .meb files)
- Chameleon engine (Slightly Mad Studios): also used by Project CARS.

## RE references

- Original 3DSMax script by Chipicao/vagos21 — https://www.tapatalk.com/groups/kottons_chop_shop/ti-scp-ti-sms-model-importer-t3217.html
- QuickBMS: `aluigi.org/bms/nfsshift.bms`

