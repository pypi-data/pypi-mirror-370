# Fatorial2K

Projeto Fatorial 2K Automatizado

## Generate examples

3 factors, 1 response, 1 replicate (default)

```shell
python gen.py examples/fatorial.csv
```

Custom factor names

```shell
python gen.py examples/fatorial.csv -k 3 -fn A B C -r Y Z
```

4 factors, 2 responses, 3 replicates, semicolon separator

```shell
python gen.py examples/fatorial.csv -k 4 -r Tempo Performance -rep 3 -s ";"
```

## Testing

```shell
python main.py examples/fatorial.csv
```
