# -*- coding: utf-8 -*-

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, showWarning

class KaroMagicLapseSorterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Karo Magic Lapse Sorter")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Label
        label = QLabel("Seleziona il Superdeck da smistare:")
        layout.addWidget(label)

        # Combo box per i deck
        self.deck_combo = QComboBox()
        self.populate_decks()
        layout.addWidget(self.deck_combo)

        # Info text
        info = QLabel(
            "Questo strumento ordinerà tutte le carte per numero di errori (lapses)\n"
            "e le smisterà fisicamente in 4 nuovi subdeck ordinati dal peggiore al migliore.\n\n"
            "I nuovi subdeck erediteranno il Deck Preset del Superdeck selezionato."
        )
        info.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info)

        # Button box
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Ordina e Smista Carte")
        self.run_btn.clicked.connect(self.run_distribution)
        self.cancel_btn = QPushButton("Annulla")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def populate_decks(self):
        # Prende tutti i deck disponibili in Anki
        decks = [d.name for d in mw.col.decks.all_names_and_ids()]
        decks.sort()
        self.deck_combo.addItems(decks)

    def run_distribution(self):
        selected_deck = self.deck_combo.currentText()
        if not selected_deck:
            showWarning("Per favore, seleziona un deck.")
            return

        # Avvia processo
        self.accept()
        distribute_cards_by_lapses(selected_deck)


def distribute_cards_by_lapses(superdeck_name):
    mw.progress.start(label="Calcolo statistiche e smistamento carte...")
    try:
        all_decks = mw.col.decks.all_names_and_ids()
        deck_ids = [str(d.id) for d in all_decks if d.name == superdeck_name or d.name.startswith(superdeck_name + "::")]
        
        if not deck_ids:
            mw.progress.finish()
            showWarning("Impossibile trovare il deck selezionato.")
            return

        did_str = ",".join(deck_ids)

        query = f"SELECT id, lapses FROM cards WHERE did IN ({did_str})"
        cards_data = mw.col.db.all(query)

        if not cards_data:
            mw.progress.finish()
            showWarning(f"Il deck '{superdeck_name}' non contiene carte.")
            return
            
        if len(cards_data) < 4:
            mw.progress.finish()
            showWarning("Ci sono meno di 4 carte nel deck. Impossibile dividere in 4 buckets.")
            return

        cards_data.sort(key=lambda x: x[1], reverse=True)

        n = len(cards_data)
        q1 = n // 4
        q2 = 2 * n // 4
        q3 = 3 * n // 4

        buckets_data = [
            cards_data[:q1],          # Bucket 1: Maggior numero di Lapses
            cards_data[q1:q2],        # Bucket 2
            cards_data[q2:q3],        # Bucket 3
            cards_data[q3:]           # Bucket 4: Minor numero di Lapses
        ]

        superdeck_id = mw.col.decks.id(superdeck_name)
        superdeck_dict = mw.col.decks.get(superdeck_id)
        conf_id = superdeck_dict.get('conf', 1)

        bucket_names = [
            f"{superdeck_name}::1_Bucket_High_Lapses",
            f"{superdeck_name}::2_Bucket_Medium_High",
            f"{superdeck_name}::3_Bucket_Medium_Low",
            f"{superdeck_name}::4_Bucket_Low_Zero"
        ]

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
        showInfo(f"Operazione completata con successo!\n{n} carte sono state smistate in 4 Buckets sotto '{superdeck_name}'.")

    except Exception as e:
        mw.progress.finish()
        showWarning(f"Si è verificato un errore durante l'operazione:\n{str(e)}")


def show_sorter_dialog():
    dialog = KaroMagicLapseSorterDialog(mw)
    dialog.exec()

# Aggiungi il pulsante al menu "Strumenti" di Anki
action = QAction("Karo Magic Lapse Sorter...", mw)
action.triggered.connect(show_sorter_dialog)
mw.form.menuTools.addAction(action)