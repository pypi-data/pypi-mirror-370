from nrgrank import process_ligands, process_target, nrgrank_main
from getcleftpy import run_getcleft
import os

result = run_getcleft(pdb_file='/Users/thomasdescoteaux/Downloads/nrgrank_test/target.pdb', num_clefts=1)
result_target = process_target(target_mol2_path='/Users/thomasdescoteaux/Downloads/nrgrank_test/target.mol2',
                               binding_site_file_path=result.file_path_dict['SPH'][0])
result_ligand = process_ligands(ligand_path='/Users/thomasdescoteaux/Downloads/nrgrank_test/ligand.mol2',
                                output_dir=os.path.dirname(result_target),
                                conformers_per_molecule=1)
nrgrank_main(target_name='bd_site_1',
             preprocessed_target_path=result_target,
             preprocessed_ligand_path=result_ligand,
             result_folder_path='/Users/thomasdescoteaux/Downloads/nrgrank_test/results',
             result_csv_and_pose_name='nrgrank_test',
             write_info=False,
             write_csv=False
             )
