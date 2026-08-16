Este repositorio toma como supuesto que se está corriendo dentro de una máquina Linux y que la data está en `assets/20260806_prueba_tecnica_dataset.csv`; para cambiar este supuesto cambia el file `cleanData.py` línea 4, por el path correcto.
``` python
df = pd.read_csv("assets/20260806_prueba_tecnica_dataset.csv", parse_dates=["date"], dayfirst=True)
```

Dependencias: `pandas`, `numpy`, `statsmodels`, `scikit-learn`.
```bash
pip install pandas numpy statsmodels scikit-learn
```

Todos los retos se corren de la siguiente forma: 
```bash 
python retoA.py 
python retoB.py 
python retoC.py 
```
