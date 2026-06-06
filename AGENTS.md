# NFS Shift / Shift 2 Unleashed Blender Tools

Blender 5.x addons for importing models from Slightly Mad Studios' Chameleon engine (NFS Shift, Shift 2 Unleashed, Project CARS).

## Addons

| Addon | File | Purpose |
|-------|------|---------|
| `meb_import/` | File > Import > Shift 2 mesh (.meb) | Imports `.meb` / `.imb` mesh files |
| `vhf_import/` | File > Import > Shift 2 transform (.vhf) | Applies `.vhf` XML position/orientation to meshes |

## Workflow

1. **Extract archives**: QuickBMS + `nfsshift.bms` on `.BFF` files
2. **Import meshes**: `File > Import > Shift 2 mesh (.meb)` — supports batch folder import
3. **Position parts**: `File > Import > Shift 2 transform (.vhf)` — reads XML matrix data

## Format notes

- `.meb` = binary mesh file (verts, UVs, normals, colors, bone weights)
- `.imb` = intermediate mesh (same format as .meb)
- `.vhf` = XML with position/orientation matrices per part
- `.bml` = car definition container (BLMY chunk format → ATTRIB/NUMB/STRS → references .meb files)
- `.bmt` = texture definition (BLMY format)
- Chameleon engine — also used by NFS Hot Pursuit 2010, Project CARS

## RE references

- Original 3DSMax script: `~/Documents/Design/SMS_Importer_3.1c.zip` (Chipicao/vagos21)
- auvy Blender port: `https://github.com/auvy/nfs-shift-to-blender`
- ForzaTech blender pattern: `~/Documents/Code/game-tools/ForzaTech-extraction-tools/scripts/carbin_importer.py`
- QuickBMS: `/home/selene/Documents/Code/re/tools/forza-studio/quickbms.exe`, script at `aluigi.org/bms/nfsshift.bms`
- ZModeler filter: `re/tools/zmodeler-2.2.6/Filters/nfsshift.zmf`