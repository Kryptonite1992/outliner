# 只保留无错误的滑动窗口分块函数
def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list:
	"""
	基于字符滑动窗口分块，支持重叠。
	"""
	if not text:
		return []
	chunks = []
	step = max_chars - overlap if max_chars > overlap else max_chars
	i = 0
	while i < len(text):
		chunk = text[i:i+max_chars]
		chunks.append(chunk)
		if i + max_chars >= len(text):
			break
		i += step
	return chunks

def chunk_text(text: str, max_chars: int = 3000, overlap: int = 200) -> list:
	"""
	基于字符滑动窗口分块，支持重叠。
	"""
	if not text:
		return []
	chunks = []
	step = max_chars - overlap if max_chars > overlap else max_chars
	i = 0
	while i < len(text):
		chunk = text[i:i+max_chars]
		chunks.append(chunk)
		if i + max_chars >= len(text):
			break
		i += step
	return chunks


def call_outline_llm(client: OllamaClient, text: str) -> Dict[str, List[Dict[str, object]]]:
	system = ChatMessage(
		role="system",
		content=OUTLINE_JSON_GUIDE.strip(),
	)
	user = ChatMessage(role="user", content=text)
	raw = client.chat([system, user], temperature=0.1, top_p=0.9)
	if not raw:
		return {"headings": []}
	# Try to extract JSON from raw
	json_str = extract_json(raw)
	if not json_str:
		return {"headings": []}
	try:
		obj = json.loads(json_str)
	except json.JSONDecodeError:
		return {"headings": []}
	if not isinstance(obj, dict) or "headings" not in obj:
		return {"headings": []}
	headings = obj.get("headings")
	if not isinstance(headings, list):
		return {"headings": []}
	norm: List[Dict[str, object]] = []
	for h in headings:
		if not isinstance(h, dict):
			continue
		title = str(h.get("title", "")).strip()
		level = h.get("level")
		try:
			level_i = int(level)
		except Exception:
			level_i = 1
		if not title:
			continue
		level_i = min(6, max(1, level_i))
		norm.append({"level": level_i, "title": title})
	return {"headings": norm}


def extract_json(text: str) -> Optional[str]:
	"""Extract the first top-level JSON object from text."""
	# quick fence handling
	fence = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```", text)
	if fence:
		return fence.group(1)
	# bracket matching fallback
	start = text.find("{")
	if start == -1:
		return None
	depth = 0
	for i in range(start, len(text)):
		ch = text[i]
		if ch == "{":
			depth += 1
		elif ch == "}":
			depth -= 1
			if depth == 0:
				return text[start : i + 1]
	return None


def merge_headings(seqs: Sequence[Dict[str, List[Dict[str, object]]]]) -> List[Dict[str, object]]:
	"""Merge lists while removing near-duplicates and preserving order."""
	out: List[Dict[str, object]] = []
	seen: set = set()

	def norm_title(t: str) -> str:
		t2 = re.sub(r"\s+", " ", t.strip().lower())
		t2 = re.sub(r"^[\d.()\-\s]+", "", t2)
		return t2

	for obj in seqs:
		for h in obj.get("headings", []):
			title = str(h.get("title", ""))
			level = int(h.get("level", 1))
			key = (level, norm_title(title))
			if not title or key in seen:
				continue
			seen.add(key)
			out.append({"level": max(1, min(6, level)), "title": title})
	return out


def outline_text(text: str, *, model: str = "qwen3", endpoint: str = "http://127.0.0.1:11434") -> List[Dict[str, object]]:
	client = OllamaClient(model=model, endpoint=endpoint)
	chunks = chunk_text(text)
	results: List[Dict[str, List[Dict[str, object]]]] = []
	for c in chunks:
		results.append(call_outline_llm(client, c))
	merged = merge_headings(results)
	return merged


def render_markdown(headings: List[Dict[str, object]]) -> str:
	lines: List[str] = []
	for h in headings:
		level = int(h.get("level", 1))
		title = str(h.get("title", "")).strip()
		if not title:
			continue
		lines.append(f"{'#' * level} {title}")
	return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
	parser = argparse.ArgumentParser(description="Extract hierarchical outline from text using Ollama qwen3 (ReAct style prompt)")
	parser.add_argument("input", help="Input text file path")
	parser.add_argument("-o", "--output", help="Output markdown file path; if omitted, prints to stdout")
	parser.add_argument("--model", default="qwen3", help="Ollama model name (default: qwen3)")
	parser.add_argument("--endpoint", default="http://127.0.0.1:11434", help="Ollama endpoint (default: http://127.0.0.1:11434)")
	args = parser.parse_args(list(argv) if argv is not None else None)

	with open(args.input, "r", encoding="utf-8") as f:
		text = f.read()

	headings = outline_text(text, model=args.model, endpoint=args.endpoint)
	md = render_markdown(headings)

	if args.output:
		with open(args.output, "w", encoding="utf-8") as f:
			f.write(md + "\n")
	else:
		print(md)
	return 0


if __name__ == "__main__":  # pragma: no cover
	raise SystemExit(main())

