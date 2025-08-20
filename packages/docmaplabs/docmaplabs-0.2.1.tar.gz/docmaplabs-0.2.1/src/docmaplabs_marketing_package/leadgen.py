from typing import List, Tuple, Dict, Any
from .models import HealthcareAnalysis, HealthcareInsight, Lead
from .config import settings


def extract_leads(analysis: HealthcareAnalysis, min_relevance: float = 0.6) -> List[Lead]:
    leads: List[Lead] = []
    seen = set()
    for ins in analysis.insights:
        handle_candidates = ins.contacts or []
        if not handle_candidates and ins.author:
            handle_candidates = [ins.author]
        for h in handle_candidates:
            key = (h, ins.tweetId)
            if key in seen:
                continue
            seen.add(key)
            if ins.relevance >= min_relevance:
                leads.append(Lead(handle=h, name=None, sourceTweetId=ins.tweetId, relevance=ins.relevance, notes=ins.text[:120]))
    return leads


# -----------------------------
# Optional: Hugging Face leads classifier client
# -----------------------------

_hf_env: Dict[str, Any] | None = None


def _ensure_hf_loaded():
    global _hf_env
    if _hf_env is not None:
        return _hf_env
    if not settings.leads.repo_id:
        raise RuntimeError("HF_LEADS_REPO_ID is not set; cannot use Hugging Face classifier")
    # Lazy imports to keep base install light
    try:
        import json  # noqa: WPS433
        import torch  # type: ignore
        import torch.nn as nn  # type: ignore
        from transformers import AutoTokenizer, AutoModel  # type: ignore
        from huggingface_hub import hf_hub_download  # type: ignore
        try:
            from safetensors.torch import load_file as safe_load_file  # type: ignore
        except Exception:
            safe_load_file = None  # type: ignore
    except Exception as e:  # pragma: no cover - optional dependency
        raise RuntimeError("Install optional extras: pip install docmaplabs-marketing-package[ml]") from e

    cfg_path = hf_hub_download(settings.leads.repo_id, "label_config.json")
    with open(cfg_path, "r", encoding="utf-8") as f:
        label_cfg = json.load(f)

    class LeadsClassifier(nn.Module):  # type: ignore
        def __init__(self, base_model_name: str, num_intents: int, num_symptoms: int, num_specialties: int):
            super().__init__()
            self.encoder = AutoModel.from_pretrained(base_model_name)
            hidden = self.encoder.config.hidden_size
            self.dropout = nn.Dropout(0.1)
            self.intent_head = nn.Linear(hidden, num_intents)
            self.sym_head = nn.Linear(hidden, num_symptoms)
            self.spec_head = nn.Linear(hidden, num_specialties)
        def forward(self, input_ids=None, attention_mask=None):
            out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
            cls = self.dropout(out.last_hidden_state[:, 0, :])
            return {
                "intent_logits": self.intent_head(cls),
                "sym_logits": self.sym_head(cls),
                "spec_logits": self.spec_head(cls),
            }

    # Device
    device = (
        "cuda" if settings.leads.device == "auto" and hasattr(__import__("torch"), "cuda") and __import__("torch").cuda.is_available() else (settings.leads.device or "cpu")
    )
    tokenizer = AutoTokenizer.from_pretrained(settings.leads.repo_id)
    model = LeadsClassifier(
        base_model_name=settings.leads.base_model,
        num_intents=len(label_cfg["intents"]),
        num_symptoms=len(label_cfg["symptoms"]),
        num_specialties=len(label_cfg["specialties"]),
    ).to(device)
    sd_path = hf_hub_download(settings.leads.repo_id, "model.safetensors")
    if sd_path.endswith(".safetensors") and safe_load_file is not None:
        state_dict = safe_load_file(sd_path)
    else:
        # Fallback for bin or older torch
        state_dict = __import__("torch").load(sd_path, map_location="cpu", weights_only=False)
    model.load_state_dict(state_dict, strict=True)
    model.to(device)
    model.eval()
    _hf_env = {"tokenizer": tokenizer, "model": model, "cfg": label_cfg, "device": device}
    return _hf_env


def classify_posts_with_hf(texts: List[str], threshold: float | None = None) -> List[Dict[str, Any]]:
    env = _ensure_hf_loaded()
    tokenizer = env["tokenizer"]
    model = env["model"]
    cfg = env["cfg"]
    device = env["device"]
    thr = float(threshold if threshold is not None else settings.leads.threshold)

    out_list: List[Dict[str, Any]] = []
    # Batched inference
    for i in range(0, len(texts), 32):
        encoded = tokenizer(texts[i:i+32], padding=True, truncation=True, max_length=256, return_tensors="pt").to(device)
        inputs = {k: v for k, v in encoded.items() if k in ("input_ids", "attention_mask")}
        with __import__("torch").no_grad():
            out = model(**inputs)
            intent = __import__("torch").softmax(out["intent_logits"], dim=-1).argmax(dim=-1).cpu().tolist()
            sym_prob = __import__("torch").sigmoid(out["sym_logits"]).cpu().tolist()
            spec_prob = __import__("torch").sigmoid(out["spec_logits"]).cpu().tolist()
        for idx in range(len(intent)):
            intent_label = cfg["intents"][intent[idx]]
            sym = [cfg["symptoms"][j] for j, p in enumerate(sym_prob[idx]) if p >= thr]
            spec = [cfg["specialties"][j] for j, p in enumerate(spec_prob[idx]) if p >= thr]
            out_list.append({"intent": intent_label, "symptoms": sym, "specialties": spec})
    return out_list

