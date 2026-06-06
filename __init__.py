# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning

# ==========================================
# LANGUAGE MANAGEMENT (i18n)
# ==========================================

STRINGS = {
    "en": {
        "menu_action": "Karo Magic Again Sorter...",
        "dialog_title": "Karo Magic Again Sorter",
        "select_deck": "Select the Superdeck:",
        "info_text": (
            "This tool sorts your cards by Total Agains into 4 Buckets.\n"
            "Cards are tagged so you can safely restore them later."
        ),
        "btn_run": "Sort into 4 Buckets",
        "btn_restore": "Restore Original Subdecks",
        "btn_cancel": "Cancel",
        "warn_no_deck": "Please select a deck.",
        "progress_label": "Tagging and sorting cards...",
        "progress_restore": "Restoring original structure...",
        "err_not_found": "Could not find the selected deck.",
        "err_no_cards": "The deck '{deck}' contains no cards.",
        "err_less_than_4": "There are fewer than 4 cards in the deck.",
        "success_msg": "Success! {n} cards were sorted into 4 Buckets.",
        "success_restore": "Success! {n} cards were returned to their original subdecks.",
        "err_general": "An error occurred during the operation:\n{err}",
        "b1": "1_Bucket_High_Agains",
        "b2": "2_Bucket_Medium_High",
        "b3": "3_Bucket_Medium_Low",
        "b4": "4_Bucket_Low_Zero"
    },
    "it": {
        "menu_action": "Karo Magic Again Sorter...",
        "dialog_title": "Karo Magic Again Sorter",
        "select_deck": "Seleziona il Superdeck:",
        "info_text": (
            "Ordina le carte per 'Total Agains' spostandole in 4 Buckets.\n"
            "Le carte vengono taggate per poterle ripristinare in futuro."
        ),
        "btn_run": "Ordina in 4 Buckets",
        "btn_restore": "Ripristina Subdeck Originali",
        "btn_cancel": "Annulla",
        "warn_no_deck": "Per favore, seleziona un deck.",
        "progress_label": "Tagging e smistamento carte in corso...",
        "progress_restore": "Ripristino della struttura originale...",
        "err_not_found": "Impossibile trovare il deck selezionato.",
        "err_no_cards": "Il deck '{deck}' non contiene carte.",
        "err_less_than_4": "Ci sono meno di 4 carte nel deck.",
        "success_msg": "Successo! {n} carte sono state smistate nei 4 Buckets.",
        "success_restore": "Successo! {n} carte sono state riportate ai deck originali.",
        "err_general": "Si è verificato un errore:\n{err}",
        "b1": "1_Bucket_Agains_Alti",
        "b2": "2_Bucket_Medio_Alti",
        "b3": "3_Bucket_Medio_Bassi",
        "b4": "4_Bucket_Bassi_Zero"
    },
    "es": {
        "menu_action": "Karo Magic Again Sorter...",
        "dialog_title": "Karo Magic Again Sorter",
        "select_deck": "Selecciona el Superdeck:",
        "info_text": (
            "Ordena las tarjetas por 'Total Agains' en 4 Buckets.\n"
            "Las tarjetas se etiquetan para poder restaurarlas luego."
        ),
        "btn_run": "Ordenar en 4 Buckets",
        "btn_restore": "Restaurar Submazos Originales",
        "btn_cancel": "Cancelar",
        "warn_no_deck": "Por favor, selecciona un mazo.",
        "progress_label": "Etiquetando y clasificando tarjetas...",
        "progress_restore": "Restaurando la estructura original...",
        "err_not_found": "No se pudo encontrar el mazo seleccionado.",
        "err_no_cards": "El mazo '{deck}' no contiene tarjetas.",
        "err_less_than_4": "Hay menos de 4 tarjetas en el mazo.",
        "success_msg": "¡Éxito! {n} tarjetas fueron clasificadas en 4 Buckets.",
        "success_restore": "¡Éxito! {n} tarjetas volvieron a sus mazos originales.",
        "err_general": "Ocurrió un error:\n{err}",
        "b1": "1_Bucket_Agains_Altos",
        "b2": "2_Bucket_Medio_Altos",
        "b3": "3_Bucket_Medio_Bajos",
        "b4": "4_Bucket_Bajos_Cero"
    }
}

def get_anki_lang():
    """Detects Anki's UI language (returns 'en', 'it', 'es', etc.)"""
    if not getattr(mw, "pm", None):
        return "en"
    
    meta = getattr(mw.pm, "meta", {})
    lang_code = meta.get("defaultLang") or meta.get("lang") or getattr(mw.pm, "lang", "en")
    
    if isinstance(lang_code, str) and len(lang_code) >= 2:
        return lang_code[:2].lower()
    
    return "en"

def _(key, **kwargs):
    """Helper function to get the translated string."""
    lang = get_anki_lang()
    if lang not in STRINGS:
        lang = "en"  # Fallback to English
    
    text = STRINGS[lang].get(key, STRINGS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

# ==========================================
# ADD-ON INTERFACE
# ==========================================

class KaroMagicAgainSorterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("dialog_title"))
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Label
        label = QLabel(_("select_deck"))
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        # Combo box for decks
        self.deck_combo = QComboBox()
        self.populate_decks()
        layout.addWidget(self.deck_combo)

        # Info text
        info = QLabel(_("info_text"))
        info.setStyleSheet("color: gray; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(info)

        # Buttons
        self.run_btn = QPushButton(_("btn_run"))
        self.run_btn.setStyleSheet("background-color: #007BFF; color: white; padding: 6px; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_distribution)
        
        self.restore_btn = QPushButton(_("btn_restore"))
        self.restore_btn.setStyleSheet("padding: 6px;")
        self.restore_btn.clicked.connect(self.run_restore)
        
        self.cancel_btn = QPushButton(_("btn_cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        
        layout.addWidget(self.run_btn)
        layout.addWidget(self.restore_btn)
        
        # Separator line for the cancel button
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        layout.addWidget(self.cancel_btn)

    def populate_decks(self):
        decks = [d.name for d in mw.col.decks.all_names_and_ids()]
        decks.sort()
        self.deck_combo.addItems(decks)

    def run_distribution(self):
        selected_deck = self.deck_combo.currentText()
        if not selected_deck:
            showWarning(_("warn_no_deck"))
            return
        self.accept()
        distribute_cards_by_agains(selected_deck)
        
    def run_restore(self):
        selected_deck = self.deck_combo.currentText()
        if not selected_deck:
            showWarning(_("warn_no_deck"))
            return
        self.accept()
        restore_original_structure(selected_deck)


# ==========================================
# SORTING AND TAGGING LOGIC
# ==========================================

def distribute_cards_by_agains(superdeck_name):
    mw.progress.start(label=_("progress_label"))
    try:
        all_decks = mw.col.decks.all_names_and_ids()
        deck_ids = [str(d.id) for d in all_decks if d.name == superdeck_name or d.name.startswith(superdeck_name + "::")]
        
        if not deck_ids:
            mw.progress.finish()
            showWarning(_("err_not_found"))
            return

        did_str = ",".join(deck_ids)

        # Get cards and their history (Total Agains via revlog)
        query = f"""
            SELECT c.id, 
                   (SELECT count(*) FROM revlog WHERE cid = c.id AND ease = 1) as total_agains
            FROM cards c
            WHERE c.did IN ({did_str})
        """
        cards_data = mw.col.db.all(query)

        if not cards_data:
            mw.progress.finish()
            showWarning(_("err_no_cards", deck=superdeck_name))
            return
            
        if len(cards_data) < 4:
            mw.progress.finish()
            showWarning(_("err_less_than_4"))
            return

        # PHASE 1: Tagging cards with their original deck name
        # Note: Anki tags cannot contain spaces. We replace spaces with '_sp_'
        for row in cards_data:
            cid = row[0]
            card = mw.col.get_card(cid)
            note = card.note()
            
            orig_deck_name = mw.col.decks.name(card.did)
            safe_name = orig_deck_name.replace(" ", "_sp_")
            tag_name = f"Karo_Orig_{safe_name}"
            
            # Remove any old Karo tags to avoid conflicts if the user runs the add-on multiple times
            tags_to_remove = [t for t in note.tags if t.startswith("Karo_Orig_")]
            for t in tags_to_remove:
                note.remove_tag(t)
            
            note.add_tag(tag_name)
            note.flush()

        # PHASE 2: Sorting and binning (Rank-Based Quartiles)
        cards_data.sort(key=lambda x: x[1], reverse=True)

        n = len(cards_data)
        q1 = n // 4
        q2 = 2 * n // 4
        q3 = 3 * n // 4

        buckets_data = [
            cards_data[:q1],          # Bucket 1
            cards_data[q1:q2],        # Bucket 2
            cards_data[q2:q3],        # Bucket 3
            cards_data[q3:]           # Bucket 4
        ]

        superdeck_id = mw.col.decks.id(superdeck_name)
        superdeck_dict = mw.col.decks.get(superdeck_id)
        conf_id = superdeck_dict.get('conf', 1)

        bucket_names = [
            f"{superdeck_name}::{_('b1')}",
            f"{superdeck_name}::{_('b2')}",
            f"{superdeck_name}::{_('b3')}",
            f"{superdeck_name}::{_('b4')}"
        ]

        # PHASE 3: Physical movement to the new buckets
        for i, b_name in enumerate(bucket_names):
            new_did = mw.col.decks.id(b_name)
            deck_dict = mw.col.decks.get(new_did)
            deck_dict['conf'] = conf_id
            mw.col.decks.save(deck_dict)
            
            card_ids_to_move = [card[0] for card in buckets_data[i]]
            if card_ids_to_move:
                mw.col.set_deck(card_ids_to_move, new_did)

        mw.col.save()
        mw.progress.finish()
        mw.reset()
        showInfo(_("success_msg", n=n))

    except Exception as e:
        mw.progress.finish()
        showWarning(_("err_general", err=str(e)))


# ==========================================
# RESTORE STRUCTURE LOGIC
# ==========================================

def restore_original_structure(superdeck_name):
    mw.progress.start(label=_("progress_restore"))
    try:
        # Find all cards in the superdeck or its subdecks
        all_decks = mw.col.decks.all_names_and_ids()
        deck_ids = [str(d.id) for d in all_decks if d.name == superdeck_name or d.name.startswith(superdeck_name + "::")]
        
        if not deck_ids:
            mw.progress.finish()
            showWarning(_("err_not_found"))
            return

        did_str = ",".join(deck_ids)
        query = f"SELECT id FROM cards WHERE did IN ({did_str})"
        cards_data = mw.col.db.all(query)
        
        restored_count = 0
        
        for row in cards_data:
            cid = row[0]
            card = mw.col.get_card(cid)
            note = card.note()
            
            # Search for the special Karo tag
            karo_tags = [t for t in note.tags if t.startswith("Karo_Orig_")]
            if karo_tags:
                orig_tag = karo_tags[0]
                
                # Decode the deck name (remove prefix and replace _sp_ with spaces)
                safe_name = orig_tag.replace("Karo_Orig_", "")
                restored_deck_name = safe_name.replace("_sp_", " ")
                
                # Create or get the original deck ID
                target_did = mw.col.decks.id(restored_deck_name)
                
                # Move the card back
                mw.col.set_deck([cid], target_did)
                
                # Remove the tracking tag to clean up
                note.remove_tag(orig_tag)
                note.flush()
                
                restored_count += 1

        mw.col.save()
        mw.progress.finish()
        mw.reset()
        showInfo(_("success_restore", n=restored_count))

    except Exception as e:
        mw.progress.finish()
        showWarning(_("err_general", err=str(e)))


def show_again_sorter_dialog():
    dialog = KaroMagicAgainSorterDialog(mw)
    dialog.exec()

# Add the button to the "Tools" menu in Anki
action = QAction(_("menu_action"), mw)
action.triggered.connect(show_again_sorter_dialog)
mw.form.menuTools.addAction(action)