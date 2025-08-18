"""Command-line interface entrypoint for the `foldifyai` package."""
from __future__ import annotations
import time 
from colorama import Fore, Style
import fsspec

logo = f"{Fore.BLUE}{Style.BRIGHT}[Foldify]{Style.RESET_ALL}"

import base64
import zipfile
import io
import pathlib
import sys
from pathlib import Path
from tqdm import tqdm
import os 
import time 
import json 
from rdkit import Chem
from rdkit.Chem import AllChem
import urllib
from foldifyai.utils import get_type, file_exists
import requests
import fsspec

try: 
    from logmd import LogMD
except:
    pass 


def _usage() -> None:
    """Print a short help message using the actual executable name."""
    prog = pathlib.Path(sys.argv[0]).name or "foldify"
    print(f"Usage: {prog} <path_to_file.fasta>", file=sys.stderr)


def compute_3d_conformer(mol, version: str = "v3") -> bool:
    if version == "v3":
        options = AllChem.ETKDGv3()
    elif version == "v2":
        options = AllChem.ETKDGv2()
    else:
        options = AllChem.ETKDGv2()

    options.clearConfs = False
    conf_id = -1

    options.timeout = 3 # don't spend more than three seconds on AllChem.EmbedMolecule
    #options.maxIterations = 10 # don't spend more than 10 attempts (default is 100?)

    try:
        conf_id = AllChem.EmbedMolecule(mol, options)#, maxAttempts=0)

        if conf_id == -1:
            print(
                f"WARNING: RDKit ETKDGv3 failed to generate a conformer for molecule "
                f"{Chem.MolToSmiles(AllChem.RemoveHs(mol))}, so the program will start with random coordinates. "
                f"Note that the performance of the model under this behaviour was not tested."
            )
            options.useRandomCoords = True
            return False # conf_id = AllChem.EmbedMolecule(mol, options)

        #AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=1000)
        # i set the maxIters=33 to skip more aggressively.
        AllChem.UFFOptimizeMolecule(mol, confId=conf_id, maxIters=33)

    except RuntimeError:
        return False 
        pass  # Force field issue here
    except ValueError:
        return False 
        pass  # sanitization issue here

    if conf_id != -1:
        conformer = mol.GetConformer(conf_id)
        conformer.SetProp("name", "Computed")
        conformer.SetProp("coord_generation", f"ETKDG{version}")
        return True

    return False

def test(seq, affinity=False):
    from pathlib import Path
    import hashlib

    cache_dir = Path.home() / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(seq.encode()).hexdigest()
    f = cache_dir / h
    if f.exists(): 
        print(f'hit ligand test cache {seq}')
        s = f.read_text()
        return "ok" in s, s  # cache mechanism 
    else: 
        print(f"didn't find ligand test cache {seq}, testing...")

    try:
        mol = AllChem.MolFromSmiles(seq)
        mol = AllChem.AddHs(mol)

        # Set atom names
        canonical_order = AllChem.CanonicalRankAtoms(mol)
        for atom, can_idx in zip(mol.GetAtoms(), canonical_order):
            atom_name = atom.GetSymbol().upper() + str(can_idx + 1)
            if len(atom_name) > 4:
                msg = (
                    f"{seq} has an atom with a name longer than "
                    f"4 characters: {atom_name}."
                )
                (cache_dir / h).write_text("fail\n" + msg)
                #raise ValueError(msg)
                return False, msg
            atom.SetProp("name", atom_name)

        success = compute_3d_conformer(mol)
        if not success:
            msg = f"Failed to compute 3D conformer for {seq}"
            (cache_dir / h).write_text("fail\n" + msg)
            return False, msg

        mol_no_h = AllChem.RemoveHs(mol, sanitize=False)
        affinity_mw = AllChem.Descriptors.MolWt(mol_no_h) if affinity else None
        (cache_dir / h).write_text("ok")
        return True, ""
    except Exception as e:
        print(e, seq)
        (cache_dir / h).write_text("fail\n" + str(e))
        return False, str(e)

def wait_on_server(host):
    d = {0: '-', 1: '/', 2: '\\', 3: '|', 4: '.'}
    i = 0 
    t0 = time.time()
    while True:
        url = f"{host}/ping"
        try:
            text = urllib.request.urlopen(url).read().decode()
            j = json.loads(text)
            if j['alive']: return
        except:
            t = time.time()-t0
            print(f'\rWaiting on server: {t:.2f}s {d[i%len(d)]}', end='')
            i+=1
            time.sleep(0.2)

LOCAL = 0
S3 = 1

def fold(args):
    folder = args.input
    log = args.logmd 

    mode = None 
    if args.s3 != '':
        fs = fsspec.filesystem(
            "s3",
            profile="r2",
            client_kwargs={
                "endpoint_url": args.s3,
                "use_ssl": True,
            },
            config_kwargs={
                "s3": {"addressing_style": "path"} 
            }
        )
        print("{logo} Using s3 filesystem (not local). ")
        mode = S3
        path = args.input[5:]
    else: 
        print("{logo} Using local filesystem (not s3). ")
        fs = fsspec.filesystem("file")
        path = args.input
        mode = LOCAL


    # single file 
    if args.input.endswith('.fasta'):
        files = [args.input]
        folder = folder.replace('.fasta', '')
    # directory 
    else:
        files = fs.glob(f"{path}*.fasta")
        files = sorted(files, key=lambda p: int(fs.size(p)))
        path = path.split('/')
        path = path[:1] + ['foldify_' + path[1]] + path[2:]
        path = "/".join(path)
        done = fs.glob(f"{path}*.zip")
        zip_ids = {x.split('/')[-1].rsplit('.', 1)[0] for x in done}

        if mode == S3:      left = [f"s3://{f}" for f in files if f.split('/')[-1].rsplit('.', 1)[0] not in zip_ids]
        elif mode == LOCAL: left = [f for f in files if f.split('/')[-1].rsplit('.', 1)[0] not in zip_ids]

        print("{logo} Total: \t", len(files))
        print("{logo} Done: \t", len(done))
        print("{logo} Left: \t", len(left))
        files = left


    if log: l = LogMD()

    wait_on_server(args.host)

    pbar = tqdm(files[::-1])
    for c,p in enumerate(pbar):

        # handle single file vs folder. 
        if args.s3 != '': 
            s3_path = path + p.split('/')[-1].replace('.fasta', '.zip')
        else: 
            parts = p.split('/')
            middle = ["foldify_" + parts[-2]] if args.output == '' else [args.output]
            path = parts[:-2] + middle + [parts[-1].replace('.fasta', '')]
            path = "/".join(path) + '/'

        try: 
            skip = False 

            p = str(p)
            #content = open(p).read()
            content = fs.open(p, "rt").read()

            num_tokens = sum([len(line) for line in content.split('\n') if not line.startswith('>')])

            for line in content.split('\n'):
                if line.startswith('>'): continue 
                if line == '': continue 
                if get_type(line) == 'SMILES': 
                    if not test(line): 
                        print(f"Skipping {p}. RDKit didn't like {line}. ")
                        #open(new_path, 'w').write(f"Skipping {p}. RDKit didn't like {line}. ")
                        skip = True 
                    else: print('ok')
            if skip: continue 
            encoded = urllib.parse.quote(content, safe="")
            if len(content) == 0: 
                continue 

            url = f"{args.host}/fold?ui=False&only_return_zip=True&seq={encoded}&{args.args}&gpu={args.gpu}&get_msa_from_server={args.msa}"

            # Open connection with progress reporting
            response = urllib.request.urlopen(url)
            block_size = 1024
            
            result = ''
            while True:
                data = response.read(block_size)
                if not data:
                    break
                result += data.decode('utf-8')
                pbar.set_description(f"{logo} {time.strftime('%H:%M:%S')} {p} tokens={num_tokens} {len(result)/1000}KB")

            jsons = [json.loads(a) for a in result.split('\n@\n') if a != '']
            b64_zip_data = jsons[-1]['data']

            zip_bytes = base64.b64decode(b64_zip_data)
            zip_in_memory = io.BytesIO(zip_bytes)
            with zipfile.ZipFile(zip_in_memory, 'r') as zip_ref:
                if mode == LOCAL: 
                    os.makedirs(path, exist_ok=True)
                    zip_ref.extractall(path) 

                elif mode == S3: 
                    with fs.open(f"{s3_path}", 'wb') as f:
                        f.write(zip_bytes)

        except Exception as e: 
            print('something wrong', e)
            print(url)
            pass 

        print('')
        wait_on_server(args.host)


def main() -> None:  # pragma: no cover

    import argparse

    parser = argparse.ArgumentParser(description='Foldify.ai CLI', add_help=False)
    parser.add_argument('-input', '-i', type=str, help='')
    parser.add_argument('-args', type=str, help='')
    parser.add_argument('-logmd', action='store_true', help='Log with LogMD')
    #parser.add_argument('-host', '-h', type=str, default='https://gpu1.foldify.org', help='Host URL for Foldify API')
    parser.add_argument('-host', '-h', type=str, default='http://0.0.0.0:8000', help='Host URL for Foldify API')
    parser.add_argument('-output', '-o', type=str, default='', help='Output directory for results')
    parser.add_argument('-gpu', '-g', type=int, default=0, help='GPU')
    parser.add_argument('-y', action='store_true', help='Pre-accept using remote host. ')
    parser.add_argument('-s3', type=str, default='', help='S3 endpoint (developed for cloudflared to lower cost).')
    parser.add_argument('-override', action='store_true', help='Override existing files')
    parser.add_argument('-msa', type=str, default='', help='Get msa from other ip. ')

    args = parser.parse_args()

    if args.host == 'https://gpu1.foldify.org' and not args.y:
        print("You didn't specify host. The default is a remote. ")
        print("Reply `REMOTE` if you want to send sequences. ")
        if input() != 'REMOTE': 
            print('Exiting.')
            exit()
        else: 
            print("Using remote host. ")
            print("You can skip this check with `foldify -y`")

    fold(args)


if __name__ == "__main__":  # pragma: no cover
    sys.argv = ['foldifyai','cofactors/']
    main() 
