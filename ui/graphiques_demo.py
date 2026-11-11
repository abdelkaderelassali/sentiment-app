"""Deux graphiques de la section 2.5, vérifiés avec streamlit.testing (AppTest)."""
import pandas as pd
import streamlit as st

# ce que produit l'onglet « Un fichier d'avis » après predire_lot() : un verdict et une confiance par avis
avis = pd.DataFrame({"verdict": ["Avis positif", "Avis négatif", "Avis positif", "Je ne sais pas", "Avis négatif"],
                     "confiance": [0.78, 0.75, 0.66, 0.56, 0.91]})

st.subheader("Répartition des verdicts")
st.bar_chart(avis["verdict"].value_counts())

st.subheader("Distribution de la confiance")
tranches = pd.cut(avis["confiance"], bins=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                  labels=["0,5 à 0,6", "0,6 à 0,7", "0,7 à 0,8", "0,8 à 0,9", "0,9 à 1"])
st.bar_chart(tranches.value_counts().sort_index())
st.caption("Sous 0,6 : avis renvoyés à un humain.")
