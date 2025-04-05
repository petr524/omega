import pickle
model_file = "models/omega_neuron_model.dat"  # upravte dle výběru
try:
    with open(model_file, "rb") as f:
        model = pickle.load(f)
    print("Model byl úspěšně načten.")
except Exception as e:
    print("Chyba při načítání modelu:", e)
