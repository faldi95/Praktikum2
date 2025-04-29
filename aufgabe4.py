import fitz  # PyMuPDF
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# PDF öffnen und Text extrahieren
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Liste der PDF-Dateien
pdf_files = [
    "m_mhb_po2021_ba_scm_2425.pdf",
     # <- Achte auf .pdf-Endung
]

# Text aus allen PDFs zusammenführen
combined_text = ""
for pdf in pdf_files:
    combined_text += extract_text_from_pdf(pdf) + " "

# Wordcloud erstellen
wordcloud = WordCloud(width=800, height=400, background_color="white", collocations=False).generate(combined_text)

# Wordcloud anzeigen
plt.figure(figsize=(15, 8))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.title("Wordcloud aus ein  PDF-Dokument", fontsize=20)
plt.show()

# --- Neuer Teil: Wortsuche ---

# Benutzer nach Wort fragen
gesuchtes_wort = input("Gib ein Wort ein, um zu zählen, wie oft es vorkommt: ")

# Zählen (ohne auf Groß-/Kleinschreibung zu achten)
anzahl = combined_text.lower().count(gesuchtes_wort.lower())

print(f"Das Wort '{gesuchtes_wort}' kommt {anzahl} mal in diesen Dokumenten vor.")
