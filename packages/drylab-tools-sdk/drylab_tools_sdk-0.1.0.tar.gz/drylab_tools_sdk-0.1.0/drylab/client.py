from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import requests


class _FileWriter:
    @staticmethod
    def write_files(entries: Iterable[Dict[str, Any]], target_dir: Path) -> List[Path]:
        target_dir.mkdir(parents=True, exist_ok=True)
        written: List[Path] = []
        for entry in entries:
            rel_path = entry.get("path") or f"file_{len(written)}"
            content_b64 = entry.get("content_b64") or entry.get("contentBase64")
            try:
                data = base64.b64decode(content_b64 or b"")
            except Exception:
                data = b""
            safe_name = Path(rel_path).name
            out_path = target_dir / safe_name
            try:
                out_path.write_bytes(data)
                written.append(out_path)
            except Exception:
                # Best-effort: skip file if cannot write
                pass
        return written


class BaseServiceClient:
    def __init__(self, base_url: str, timeout: int = 1800, session: Optional[requests.Session] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    def _post_json(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, json=body, timeout=self.timeout)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise requests.HTTPError(f"POST {url} -> {resp.status_code}: {detail}")
        return resp.json()

    def _post_form(self, path: str, data: Dict[str, Any], files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = self.session.post(url, data=data, files=files or {}, timeout=self.timeout)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise requests.HTTPError(f"POST {url} -> {resp.status_code}: {detail}")
        return resp.json()


class BoltzClient(BaseServiceClient):
    def predict_unified(
        self,
        sequences: Dict[str, Dict[str, str]],
        target_dir: Path | str,
        *,
        ligands: Optional[List[Dict[str, Any]]] = None,
        binder_sequence: Optional[str] = None,
        pocket_restraints: Optional[str] = None,
        covalent_restraints: Optional[str] = None,
        cyclic_biopolymers: Optional[str] = None,
        residue_modifications: Optional[str] = None,
        msa_mode: Optional[str] = None,
        custom_msa_zip: Optional[Path | str] = None,
        number_recycles: Optional[int] = None,
        sampling_steps: Optional[int] = None,
        diffusion_samples: Optional[int] = None,
        sampling_steps_affinity: Optional[int] = None,
        diffusion_samples_affinity: Optional[int] = None,
        step_scale: Optional[float] = None,
        use_potentials: Optional[bool] = None,
        affinity_mw_correction: Optional[bool] = None,
    ) -> List[Path]:
        data: Dict[str, Any] = {"Input Sequences": json.dumps(sequences)}
        if ligands is not None:
            data["Input Molecules"] = json.dumps(ligands)
        if binder_sequence:
            data["Binder Sequence"] = binder_sequence
        if pocket_restraints:
            data["Pocket Restraints"] = pocket_restraints
        if covalent_restraints:
            data["Covalent Restraints"] = covalent_restraints
        if cyclic_biopolymers:
            data["Cyclic Biopolymers"] = cyclic_biopolymers
        if residue_modifications:
            data["Residue Modifications"] = residue_modifications
        if msa_mode:
            data["MSA Mode"] = msa_mode
        if number_recycles is not None:
            data["Number Recycles"] = str(number_recycles)
        if sampling_steps is not None:
            data["Sampling Steps"] = str(sampling_steps)
        if diffusion_samples is not None:
            data["Diffusion Samples"] = str(diffusion_samples)
        if sampling_steps_affinity is not None:
            data["Sampling Steps Affinity"] = str(sampling_steps_affinity)
        if diffusion_samples_affinity is not None:
            data["Diffusion Samples Affinity"] = str(diffusion_samples_affinity)
        if step_scale is not None:
            data["Step Scale"] = str(step_scale)
        if use_potentials is not None:
            data["Use Inference Time Potentials"] = "true" if use_potentials else "false"
        if affinity_mw_correction is not None:
            data["Molecular Weight Correction"] = "true" if affinity_mw_correction else "false"

        files = None
        if custom_msa_zip is not None:
            p = Path(custom_msa_zip)
            files = {"Custom MSA": (p.name, p.read_bytes(), "application/zip")}

        payload = self._post_form("/predict/boltz", data=data, files=files)
        files_list = payload.get("files", [])
        return _FileWriter.write_files(files_list, Path(target_dir))


class CellposeClient(BaseServiceClient):
    def segment_image_b64(self, image_b64: str, target_dir: Path | str, **kwargs: Any) -> List[Path]:
        body = {"image_b64": image_b64}
        body.update(kwargs)
        payload = self._post_json("/cellpose/segment", body)
        # Write a JSON manifest for convenience
        target = Path(target_dir)
        target.mkdir(parents=True, exist_ok=True)
        manifest = target / "cellpose_response.json"
        manifest.write_text(json.dumps(payload, indent=2))
        return [manifest]


class UniMolV2Client(BaseServiceClient):
    def predict(self, protein_pdb_b64: str, ligand_sdf_b64: str, target_dir: Path | str, *, grid_json_b64: Optional[str] = None, batch_size: Optional[int] = None, grid_margin: Optional[float] = None) -> List[Path]:
        body: Dict[str, Any] = {
            "protein_pdb_b64": protein_pdb_b64,
            "ligand_sdf_b64": ligand_sdf_b64,
        }
        if grid_json_b64 is not None:
            body["grid_json_b64"] = grid_json_b64
        if batch_size is not None:
            body["batch_size"] = int(batch_size)
        if grid_margin is not None:
            body["grid_margin"] = float(grid_margin)
        payload = self._post_json("/unimolv2/predict", body)
        return _FileWriter.write_files(payload.get("files", []), Path(target_dir))


class RFDiffusionClient(BaseServiceClient):
    def _call(self, endpoint: str, body: Dict[str, Any], target_dir: Path | str) -> List[Path]:
        payload = self._post_json(endpoint, body)
        files = payload.get("files", [])
        return _FileWriter.write_files(files, Path(target_dir))

    def basic(self, contigs: str, target_dir: Path | str, *, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body = {"contigs": contigs, "options": options or {}}
        return self._call("/predict/rfdiffusion/basic", body, target_dir)

    def motif(self, input_pdb_b64: str, contigs: str, target_dir: Path | str, *, inpaint_seq: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body: Dict[str, Any] = {"input_pdb_b64": input_pdb_b64, "contigs": contigs, "options": options or {}}
        if inpaint_seq is not None:
            body["inpaint_seq"] = inpaint_seq
        return self._call("/predict/rfdiffusion/motif", body, target_dir)

    def binder(self, input_pdb_b64: str, contigs: str, hotspot_res: Iterable[str], target_dir: Path | str, *, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body = {"input_pdb_b64": input_pdb_b64, "contigs": contigs, "ppi_hotspot_res": ",".join(hotspot_res), "options": options or {}}
        return self._call("/predict/rfdiffusion/binder", body, target_dir)

    def symmetric(self, contigs: str, symmetry: str, target_dir: Path | str, *, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body = {"contigs": contigs, "symmetry": symmetry, "options": options or {}}
        return self._call("/predict/rfdiffusion/symmetric", body, target_dir)

    def partial(self, input_pdb_b64: str, contigs: str, partial_T: float | int, target_dir: Path | str, *, provide_seq: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body: Dict[str, Any] = {"input_pdb_b64": input_pdb_b64, "contigs": contigs, "partial_T": partial_T, "options": options or {}}
        if provide_seq is not None:
            body["provide_seq"] = provide_seq
        return self._call("/predict/rfdiffusion/partial", body, target_dir)

    def fold_conditioning(self, scaffold_dir: str, contigs: str, target_dir: Path | str, *, use_target: bool = False, target_pdb_path: Optional[str] = None, target_ss_path: Optional[str] = None, target_adj_path: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body: Dict[str, Any] = {
            "scaffold_dir": scaffold_dir,
            "use_target": use_target,
            "contigs": contigs,
            "options": options or {},
        }
        if use_target:
            body.update({
                "target_pdb_path": target_pdb_path,
                "target_ss_path": target_ss_path,
                "target_adj_path": target_adj_path,
            })
        return self._call("/predict/rfdiffusion/fold_conditioning", body, target_dir)

    def macrocycle(self, contigs: str, target_dir: Path | str, *, cyc_chains: Optional[str] = None, input_pdb_b64: Optional[str] = None, hotspot_res: Optional[Iterable[str]] = None, options: Optional[Dict[str, Any]] = None) -> List[Path]:
        body: Dict[str, Any] = {"contigs": contigs, "options": options or {}}
        if cyc_chains is not None:
            body["cyc_chains"] = cyc_chains
        if input_pdb_b64 is not None:
            body["input_pdb_b64"] = input_pdb_b64
        if hotspot_res is not None:
            body["hotspot_res"] = list(hotspot_res)
        return self._call("/predict/rfdiffusion/macrocycle", body, target_dir)


class ProteinMPNNClient(BaseServiceClient):
    def design(
        self,
        pdb_b64: str,
        target_dir: Path | str,
        *,
        design_chains: Optional[List[str]] = None,
        ca_only: Optional[bool] = None,
        use_soluble_model: Optional[bool] = None,
        model_name: Optional[str] = None,
        num_seq_per_target: Optional[int] = None,
        batch_size: Optional[int] = None,
        sampling_temp: Optional[str] = None,
        seed: Optional[int] = None,
        omit_AAs: Optional[str] = None,
    ) -> List[Path]:
        body: Dict[str, Any] = {"pdb_b64": pdb_b64}
        if design_chains is not None:
            body["design_chains"] = design_chains
        if ca_only is not None:
            body["ca_only"] = bool(ca_only)
        if use_soluble_model is not None:
            body["use_soluble_model"] = bool(use_soluble_model)
        if model_name is not None:
            body["model_name"] = str(model_name)
        if num_seq_per_target is not None:
            body["num_seq_per_target"] = int(num_seq_per_target)
        if batch_size is not None:
            body["batch_size"] = int(batch_size)
        if sampling_temp is not None:
            body["sampling_temp"] = str(sampling_temp)
        if seed is not None:
            body["seed"] = int(seed)
        if omit_AAs is not None:
            body["omit_AAs"] = str(omit_AAs)
        payload = self._post_json("/proteinmpnn/design", body)
        return _FileWriter.write_files(payload.get("files", []), Path(target_dir))


class LigandMPNNClient(BaseServiceClient):
    def design(
        self,
        pdb_b64: str,
        target_dir: Path | str,
        *,
        design_chains: Optional[List[str]] = None,
        temperature: Optional[float] = None,
        batch_size: Optional[int] = None,
        number_of_batches: Optional[int] = None,
        seed: Optional[int] = None,
        omit_AA: Optional[str] = None,
        ligand_mpnn_use_atom_context: Optional[int] = None,
        ligand_mpnn_use_side_chain_context: Optional[int] = None,
        ligand_mpnn_cutoff_for_score: Optional[float] = None,
        pack_side_chains: Optional[int] = None,
        number_of_packs_per_design: Optional[int] = None,
        pack_with_ligand_context: Optional[int] = None,
        checkpoint_ligand_mpnn: Optional[str] = None,
    ) -> List[Path]:
        body: Dict[str, Any] = {"pdb_b64": pdb_b64}
        if design_chains is not None:
            body["design_chains"] = design_chains
        if temperature is not None:
            body["temperature"] = float(temperature)
        if batch_size is not None:
            body["batch_size"] = int(batch_size)
        if number_of_batches is not None:
            body["number_of_batches"] = int(number_of_batches)
        if seed is not None:
            body["seed"] = int(seed)
        if omit_AA is not None:
            body["omit_AA"] = str(omit_AA)
        if ligand_mpnn_use_atom_context is not None:
            body["ligand_mpnn_use_atom_context"] = int(ligand_mpnn_use_atom_context)
        if ligand_mpnn_use_side_chain_context is not None:
            body["ligand_mpnn_use_side_chain_context"] = int(ligand_mpnn_use_side_chain_context)
        if ligand_mpnn_cutoff_for_score is not None:
            body["ligand_mpnn_cutoff_for_score"] = float(ligand_mpnn_cutoff_for_score)
        if pack_side_chains is not None:
            body["pack_side_chains"] = int(pack_side_chains)
        if number_of_packs_per_design is not None:
            body["number_of_packs_per_design"] = int(number_of_packs_per_design)
        if pack_with_ligand_context is not None:
            body["pack_with_ligand_context"] = int(pack_with_ligand_context)
        if checkpoint_ligand_mpnn is not None:
            body["checkpoint_ligand_mpnn"] = str(checkpoint_ligand_mpnn)
        payload = self._post_json("/ligandmpnn/design", body)
        return _FileWriter.write_files(payload.get("files", []), Path(target_dir))


class AntiFoldClient(BaseServiceClient):
    def predict(
        self,
        pdb_b64: str,
        target_dir: Path | str,
        *,
        heavy_chain: Optional[str] = None,
        light_chain: Optional[str] = None,
        antigen_chain: Optional[str] = None,
        nanobody_chain: Optional[str] = None,
        regions: Optional[str] = None,
        num_seq_per_target: Optional[int] = None,
        sampling_temp: Optional[str] = None,
        limit_variation: Optional[bool] = None,
        extract_embeddings: Optional[bool] = None,
        batch_size: Optional[int] = None,
        num_threads: Optional[int] = None,
        seed: Optional[int] = None,
        esm_if1_mode: Optional[bool] = None,
        model_path: Optional[str] = None,
    ) -> List[Path]:
        body: Dict[str, Any] = {"pdb_b64": pdb_b64}
        if heavy_chain is not None:
            body["heavy_chain"] = str(heavy_chain)
        if light_chain is not None:
            body["light_chain"] = str(light_chain)
        if antigen_chain is not None:
            body["antigen_chain"] = str(antigen_chain)
        if nanobody_chain is not None:
            body["nanobody_chain"] = str(nanobody_chain)
        if regions is not None:
            body["regions"] = str(regions)
        if num_seq_per_target is not None:
            body["num_seq_per_target"] = int(num_seq_per_target)
        if sampling_temp is not None:
            body["sampling_temp"] = str(sampling_temp)
        if limit_variation is not None:
            body["limit_variation"] = bool(limit_variation)
        if extract_embeddings is not None:
            body["extract_embeddings"] = bool(extract_embeddings)
        if batch_size is not None:
            body["batch_size"] = int(batch_size)
        if num_threads is not None:
            body["num_threads"] = int(num_threads)
        if seed is not None:
            body["seed"] = int(seed)
        if esm_if1_mode is not None:
            body["esm_if1_mode"] = bool(esm_if1_mode)
        if model_path is not None:
            body["model_path"] = str(model_path)
        payload = self._post_json("/antifold/predict", body)
        return _FileWriter.write_files(payload.get("files", []), Path(target_dir))


class DiffDockPPClient(BaseServiceClient):
    def dock(
        self,
        receptor_pdb_b64: str,
        ligand_pdb_b64: str,
        target_dir: Path | str,
        *,
        pair_id: Optional[str] = None,
        num_samples: Optional[int] = None,
        batch_size: Optional[int] = None,
        use_confidence_model: Optional[bool] = None,
        visualize_steps: Optional[int] = None,
    ) -> List[Path]:
        body: Dict[str, Any] = {
            "receptor_pdb_b64": receptor_pdb_b64,
            "ligand_pdb_b64": ligand_pdb_b64,
        }
        if pair_id is not None:
            body["pair_id"] = str(pair_id)
        if num_samples is not None:
            body["num_samples"] = int(num_samples)
        if batch_size is not None:
            body["batch_size"] = int(batch_size)
        if use_confidence_model is not None:
            body["use_confidence_model"] = bool(use_confidence_model)
        if visualize_steps is not None:
            body["visualize_steps"] = int(visualize_steps)
        payload = self._post_json("/diffdockpp/dock", body)
        return _FileWriter.write_files(payload.get("files", []), Path(target_dir))


class ThermoMPNNClient(BaseServiceClient):
    def ssm(self, pdb_b64: str, target_dir: Path | str, *, chain: Optional[str] = None, model_path: Optional[str] = None) -> List[Path]:
        body: Dict[str, Any] = {"pdb_b64": pdb_b64}
        if chain is not None:
            body["chain"] = str(chain)
        if model_path is not None:
            body["model_path"] = str(model_path)
        payload = self._post_json("/thermompnn/ssm", body)
        # Save response manifest including predictions
        target = Path(target_dir)
        target.mkdir(parents=True, exist_ok=True)
        manifest = target / "thermompnn_ssm_response.json"
        try:
            manifest.write_text(json.dumps(payload, indent=2))
        except Exception:
            pass
        written = _FileWriter.write_files(payload.get("files", []), target)
        return [manifest] + written

    def predict(
        self,
        pdb_b64: str,
        mutations: Sequence[Dict[str, Any]],
        target_dir: Path | str,
        *,
        chain: Optional[str] = None,
        model_path: Optional[str] = None,
    ) -> List[Path]:
        body: Dict[str, Any] = {"pdb_b64": pdb_b64, "mutations": list(mutations)}
        if chain is not None:
            body["chain"] = str(chain)
        if model_path is not None:
            body["model_path"] = str(model_path)
        payload = self._post_json("/thermompnn/predict", body)
        target = Path(target_dir)
        target.mkdir(parents=True, exist_ok=True)
        manifest = target / "thermompnn_predict_response.json"
        try:
            manifest.write_text(json.dumps(payload, indent=2))
        except Exception:
            pass
        written = _FileWriter.write_files(payload.get("files", []), target)
        return [manifest] + written


class ESM3Client(BaseServiceClient):
    def score(self, sequence: str, *, structure_pdb_b64: Optional[str] = None, return_per_residue: Optional[bool] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"sequence": sequence, "structure_pdb_b64": structure_pdb_b64}
        if return_per_residue is not None:
            body["return_per_residue"] = bool(return_per_residue)
        return self._post_json("/esm3/score", body)

    def generate_unconditional(self, length: Any, *, num_samples: Optional[int] = None, temperature: Optional[float] = None, top_p: Optional[float] = None, seed: Optional[int] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"length": length}
        if num_samples is not None:
            body["num_samples"] = int(num_samples)
        if temperature is not None:
            body["temperature"] = float(temperature)
        if top_p is not None:
            body["top_p"] = float(top_p)
        if seed is not None:
            body["seed"] = int(seed)
        return self._post_json("/esm3/generate/unconditional", body)

    def generate_prompted(self, prompt_sequence: str, *, num_samples: Optional[int] = None, temperature: Optional[float] = None, top_p: Optional[float] = None, seed: Optional[int] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"prompt_sequence": prompt_sequence}
        if num_samples is not None:
            body["num_samples"] = int(num_samples)
        if temperature is not None:
            body["temperature"] = float(temperature)
        if top_p is not None:
            body["top_p"] = float(top_p)
        if seed is not None:
            body["seed"] = int(seed)
        return self._post_json("/esm3/generate/prompted", body)

    def generate_structure_conditioned(self, scaffold_pdb_b64: str, *, num_samples: Optional[int] = None, temperature: Optional[float] = None, top_p: Optional[float] = None, seed: Optional[int] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"scaffold_pdb_b64": scaffold_pdb_b64}
        if num_samples is not None:
            body["num_samples"] = int(num_samples)
        if temperature is not None:
            body["temperature"] = float(temperature)
        if top_p is not None:
            body["top_p"] = float(top_p)
        if seed is not None:
            body["seed"] = int(seed)
        return self._post_json("/esm3/generate/structure_conditioned", body)

    def generate_guided(self, prompt_sequence: str, *, guidance: Optional[List[Dict[str, Any]]] = None, num_samples: Optional[int] = None, steps: Optional[int] = None, temperature: Optional[float] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"prompt_sequence": prompt_sequence}
        if guidance is not None:
            body["guidance"] = guidance
        if num_samples is not None:
            body["num_samples"] = int(num_samples)
        if steps is not None:
            body["steps"] = int(steps)
        if temperature is not None:
            body["temperature"] = float(temperature)
        return self._post_json("/esm3/generate/guided", body)


class ImmuneBuilderClient(BaseServiceClient):
    def predict(self, model_type: str, sequences: Dict[str, str], target_dir: Path | str) -> List[Path]:
        body: Dict[str, Any] = {"model_type": model_type, "sequences": sequences}
        payload = self._post_json("/immunebuilder/predict", body)
        return _FileWriter.write_files(payload.get("files", []), Path(target_dir))


class DryLabClient:
    def __init__(self, *, timeout: int = 1800) -> None:
        # Domains per service
        self.boltz = BoltzClient(base_url=os.environ.get("DRYLAB_BOLTZ_URL", "https://boltz.tools.thedrylab.com"), timeout=timeout)
        self.cellpose = CellposeClient(base_url=os.environ.get("DRYLAB_CELLPOSE_URL", "https://cellpose.tools.thedrylab.com"), timeout=timeout)
        self.unimolv2 = UniMolV2Client(base_url=os.environ.get("DRYLAB_UNIMOLV2_URL", "https://unimolv2.tools.thedrylab.com"), timeout=timeout)
        self.rfdiffusion = RFDiffusionClient(base_url=os.environ.get("DRYLAB_RFDIFFUSION_URL", "https://rfdiffusion.tools.thedrylab.com"), timeout=timeout)
        self.proteinmpnn = ProteinMPNNClient(base_url=os.environ.get("DRYLAB_PROTEINMPNN_URL", "https://proteinmpnn.tools.thedrylab.com"), timeout=timeout)
        self.ligandmpnn = LigandMPNNClient(base_url=os.environ.get("DRYLAB_LIGANDMPNN_URL", "https://ligandmpnn.tools.thedrylab.com"), timeout=timeout)
        self.antifold = AntiFoldClient(base_url=os.environ.get("DRYLAB_ANTIFOLD_URL", "https://antifold.tools.thedrylab.com"), timeout=timeout)
        self.diffdockpp = DiffDockPPClient(base_url=os.environ.get("DRYLAB_DIFFDOCKPP_URL", "https://diffdockpp.tools.thedrylab.com"), timeout=timeout)
        self.thermompnn = ThermoMPNNClient(base_url=os.environ.get("DRYLAB_THERMOMPNN_URL", "https://thermompnn.tools.thedrylab.com"), timeout=timeout)
        self.esm3 = ESM3Client(base_url=os.environ.get("DRYLAB_ESM3_URL", "https://esm3.tools.thedrylab.com"), timeout=timeout)
        self.immunebuilder = ImmuneBuilderClient(base_url=os.environ.get("DRYLAB_IMMUNEBUILDER_URL", "https://immunebuilder.tools.thedrylab.com"), timeout=timeout)


