Uses all-MiniLM-L6-v2 to index a folder of books (PDFs, DOCX, HMTLs, TXTs) with improved chunking, and chat with them using Ollama's Qwen3 model.

Requires Python and Ollama pre-installed.

```bash
pip3 install --no-cache-dir llama-index-core llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-readers-file python-docx beautifulsoup4 pypdf tqdm "unstructured[local-inference]" pytesseract pillow_heif
ollama pull qwen3:14b
brew install tesseract
brew install poppler
```

# First, generate the index

Do this once, or every time you add new books to the folder.

```bash
python3 index_books.py
```

# Then, chat with the indexed books

```bash
python3 chat_with_books.py
```

# Example

```bash
You: is there a remedy for stomach pain, please also mention the book

AI: Yes, there is a remedy for stomach pain mentioned in the text. Under the section **"STOMACHACHES"**, it states:

> *"A strong stomach ache is relieved with water and sand. The water and the sand are mixed and put to boil. Afterwards, strain it and drink the remedy. The stomach aches disappear instantaneously."*

This remedy is documented in the book:
**"12_1978-treatise-of-occult-medicine-and-practical-magic.pdf"** (full title: *Treatise of Occult Medicine and Practical Magic*, 1978).

No other remedies for general stomach pain are explicitly mentioned in the provided text.

You: and for problems with the liver?

AI: Yes, several remedies for liver problems are mentioned in the text. Below are the specific references from the book **"12_1978-treatise-of-occult-medicine-and-practical-magic.pdf"** (full title: *Treatise of Occult Medicine and Practical Magic*, 1978):

---

### 1. **Purslane (Portulaca oleracea L.)**
> *"The sick person will eat the plant called Purslane (Portulaca oleracea L.) for nine days. Purslane in salads is effective for the healing of the liver."*
- **Context**: This is explicitly stated as a remedy for liver ailments.

---

### 2. **Herbal Tea for the Liver**
> *"The sick liver can be cured with the following tea:
A bunch of Boldo leaves (Peumus boldo), another bunch of Lemon Verbena leaves, roots of the plant called ‘Mil Hombres’ (Cissampelos pareira L.)"*
- **Context**: This tea is described as a treatment for "sick liver."

---

### 3. **Tincture Formula for Liver Issues**
> *"The sicknesses of the liver [...] are cured with the following simple, yet effective formula:
Tincture of Boldo [...] 2 ounces
Tincture of Gentian [...] 2 ounces
Mint Essence [...] 2 ounces
Sugared Water [...] 1 liter"*
- **Context**: This formula is explicitly tied to curing liver ailments.

---

### 4. **Boldo Leaves for Liver Function**
> *"The Boldo leaves cure the liver, make the bile flow and excite the hepatic functions."*
- **Context**: This directly attributes liver-healing properties to Boldo leaves.

---

### 5. **Jaundice Remedy (Liver-Related)**
> *"The sick person must inhale the vapors and also must be enveloped within the vapors of vinegar [...] cooked with Maidenhair Fern [...] Oregano [...] Sage [...] Pennyroyal. [...] This remedy of Osmosis-Therapy is extraordinary in order to cure jaundice."*
- **Context**: Jaundice is a liver-related condition, and this remedy is described as effective for it.

---

### Notes:
- All remedies are documented in the same book: **"12_1978-treatise-of-occult-medicine-and-practical-magic.pdf"**.
- The text emphasizes the use of **herbal tinctures, teas, and specific plants** (e.g., Boldo, Purslane) for liver healing.
- No other liver-specific remedies are explicitly mentioned in the provided text.
```
